from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from jose import jwt

from sward_shared.auth import (
    build_require_jwt,
    build_require_role,
    build_require_service_key,
)

SECRET = "test-secret-key"
ALGORITHM = "HS256"


def _make_token(
    *,
    rol: str = "estudiante",
    token_type: str = "access",
    expired: bool = False,
    secret: str = SECRET,
) -> str:
    now = datetime.now(UTC)
    exp = now - timedelta(minutes=5) if expired else now + timedelta(minutes=15)
    return jwt.encode(
        {
            "sub": str(uuid4()),
            "rol": rol,
            "permisos": ["leer"],
            "jti": str(uuid4()),
            "iat": now,
            "type": token_type,
            "exp": exp,
        },
        secret,
        algorithm=ALGORITHM,
    )


def _build_app() -> FastAPI:
    app = FastAPI()
    require_jwt = build_require_jwt(SECRET)
    require_admin = build_require_role(SECRET, "administrador")
    require_service = build_require_service_key({"clave-valida"})

    @app.get("/protegido")
    async def protegido(payload: dict = Depends(require_jwt)) -> dict:
        return {"sub": payload["sub"], "rol": payload["rol"]}

    @app.get("/solo-admin")
    async def solo_admin(payload: dict = Depends(require_admin)) -> dict:
        return {"rol": payload["rol"]}

    @app.get("/interno", dependencies=[Depends(require_service)])
    async def interno() -> dict:
        return {"ok": True}

    return app


@pytest.fixture
def client() -> AsyncClient:
    app = _build_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_token_valido_retorna_payload(client: AsyncClient):
    token = _make_token()
    resp = await client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["rol"] == "estudiante"


async def test_token_expirado_retorna_401(client: AsyncClient):
    token = _make_token(expired=True)
    resp = await client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_token_firma_invalida_retorna_401(client: AsyncClient):
    token = _make_token(secret="otra-clave-distinta")
    resp = await client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_token_tipo_incorrecto_retorna_401(client: AsyncClient):
    token = _make_token(token_type="refresh")
    resp = await client.get("/protegido", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_sin_authorization_header_no_autorizado(client: AsyncClient):
    # Sin credenciales el acceso queda bloqueado (401/403 según HTTPBearer).
    resp = await client.get("/protegido")
    assert resp.status_code in (401, 403)


async def test_require_role_correcto(client: AsyncClient):
    token = _make_token(rol="administrador")
    resp = await client.get("/solo-admin", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


async def test_require_role_incorrecto_retorna_403(client: AsyncClient):
    token = _make_token(rol="estudiante")
    resp = await client.get("/solo-admin", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


async def test_service_key_correcta(client: AsyncClient):
    resp = await client.get("/interno", headers={"X-Service-Key": "clave-valida"})
    assert resp.status_code == 200


async def test_service_key_incorrecta_retorna_403(client: AsyncClient):
    resp = await client.get("/interno", headers={"X-Service-Key": "clave-mala"})
    assert resp.status_code == 403


async def test_service_key_ausente_retorna_403(client: AsyncClient):
    resp = await client.get("/interno")
    assert resp.status_code == 403


async def test_service_key_modo_dev_permite_sin_claves():
    app = FastAPI()
    require_service = build_require_service_key(set())

    @app.get("/interno", dependencies=[Depends(require_service)])
    async def interno() -> dict:
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/interno")
    assert resp.status_code == 200
