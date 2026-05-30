"""Dependencias reutilizables de FastAPI para autenticación entre microservicios SWARD.

El token JWT lo emite ``sward-ms-usuarios`` firmado con HS256 usando un ``SECRET_KEY``
compartido. El payload contiene los claims ``sub``, ``rol``, ``permisos``, ``jti``,
``exp`` y ``type`` (que debe ser ``"access"`` para los tokens de acceso).

Estas factories permiten que cada microservicio proteja sus endpoints sin duplicar la
lógica de validación de tokens ni de claves de servicio.
"""

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

JwtDependency = Callable[..., Awaitable[dict]]
ServiceKeyDependency = Callable[..., Awaitable[None]]

#: Nombre del header usado para autenticación servicio-a-servicio.
SERVICE_KEY_HEADER = "X-Service-Key"


def build_require_jwt(secret_key: str, algorithm: str = "HS256") -> JwtDependency:
    """Construye una dependencia FastAPI que valida un JWT de acceso.

    La dependencia valida la firma, la expiración y que ``type == "access"``.
    Retorna el payload decodificado (``dict``) o lanza ``HTTPException`` 401 si el
    token es inválido, está expirado o tiene un tipo incorrecto.
    """

    bearer = HTTPBearer(auto_error=True)

    async def require_jwt(
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> dict:
        try:
            payload = jwt.decode(
                credentials.credentials,
                secret_key,
                algorithms=[algorithm],
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {exc}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido: se esperaba un token de acceso.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    return require_jwt


def build_require_role(secret_key: str, rol: str, algorithm: str = "HS256") -> JwtDependency:
    """Construye una dependencia que además exige un rol específico.

    Valida el token igual que :func:`build_require_jwt` y luego comprueba que
    ``payload["rol"] == rol``; lanza ``HTTPException`` 403 si no coincide.
    """

    require_jwt = build_require_jwt(secret_key, algorithm=algorithm)

    async def require_role(payload: dict = Depends(require_jwt)) -> dict:
        if payload.get("rol") != rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: rol insuficiente.",
            )
        return payload

    return require_role


def build_require_service_key(
    authorized_keys: set[str],
) -> ServiceKeyDependency:
    """Construye una dependencia que valida el header ``X-Service-Key``.

    Compara el valor del header contra ``authorized_keys`` y lanza
    ``HTTPException`` 403 si no coincide. Si ``authorized_keys`` está vacío
    (modo desarrollo, sin claves configuradas), permite el acceso.
    """

    async def require_service_key(request: Request) -> None:
        if not authorized_keys:
            # Modo desarrollo: sin claves configuradas no se bloquea.
            return

        provided = request.headers.get(SERVICE_KEY_HEADER)
        if provided is None or provided not in authorized_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clave de servicio inválida o ausente.",
            )

    return require_service_key
