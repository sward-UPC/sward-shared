# sward-shared

Librería Python compartida por todos los microservicios del sistema **SWARD**
(Sistema Web de Recomendación Adaptativa y Explicable).

Reúne los **contratos transversales** que deben ser idénticos entre micros —el formato de
los eventos de dominio, la vinculación de identidades Moodle→SWARD y la autenticación
entre servicios— para no duplicar lógica ni arriesgar que dos servicios serialicen o
validen de forma distinta.

Principio de diseño: los **contratos de dominio** (`events`, `identidad`) son Python puro,
sin frameworks ni infraestructura. Importarlos no arrastra FastAPI ni boto3. Los
**adaptadores** a infra concreta (AWS) y de entrada (FastAPI) viven aislados en sus propios
subpaquetes, de modo que cada micro importe solo lo que necesita.

## Qué expone

### `sward_shared.events` — contrato de eventos (puro)

El formato de cable común para la mensajería event-driven entre micros.

- **`DomainEvent`** — clase base abstracta (`@dataclass` + `ABC`) para todo evento de
  dominio. Aporta `event_id`, `occurred_at` y `source`; cada subclase implementa la
  propiedad `event_type`.
- **`EventEnvelope`** — envuelve un `DomainEvent` para publicarlo. `EventEnvelope.wrap(event,
  correlation_id=...)` serializa el evento a `payload_json` (UUIDs y datetimes incluidos) y
  añade `correlation_id` y `retry_count` para trazabilidad y reintentos.

```python
from dataclasses import dataclass
from sward_shared.events import DomainEvent, EventEnvelope

@dataclass
class RetroalimentacionEnviada(DomainEvent):
    estudiante_id: str = ""
    docente_id: str = ""

    @property
    def event_type(self) -> str:
        return "retroalimentacion.enviada"

envelope = EventEnvelope.wrap(RetroalimentacionEnviada(estudiante_id="..."), correlation_id="req-123")
```

> Importar `sward_shared.events` **no** carga boto3 ni FastAPI: es seguro usarlo dentro del
> núcleo de dominio de cada micro.

### `sward_shared.identidad` — UUID determinístico Moodle→SWARD (puro)

Deriva el UUID de una entidad SWARD desde su id en Moodle vía `uuid5` con un namespace fijo
compartido. Garantiza que el mismo usuario/curso tenga el **mismo UUID** en ms-usuarios,
ms-trazabilidad, etc.

```python
from sward_shared.identidad import id_sward_desde_moodle, moodle_uuid

uid = id_sward_desde_moodle(moodle_user_id=42)     # UUID estable del usuario
cid = moodle_uuid("course", 7)                      # genérico por tipo de entidad
```

### `sward_shared.auth` — autenticación reutilizable (FastAPI)

Factories que devuelven dependencias FastAPI, para que cada micro proteja endpoints sin
reescribir la validación. El JWT lo emite `ms-usuarios` (HS256 con un `SECRET_KEY`
compartido); el payload trae `sub`, `rol`, `permisos`, `jti`, `exp` y `type`.

- **`build_require_jwt(secret_key)`** — valida firma, expiración y `type == "access"`;
  devuelve el payload o lanza 401.
- **`build_require_role(secret_key, rol)`** — además exige un `rol`; lanza 403 si no coincide.
- **`build_require_service_key(authorized_keys)`** — valida el header `X-Service-Key` para
  llamadas servicio-a-servicio.

```python
from fastapi import Depends, FastAPI
from sward_shared.auth import build_require_jwt, build_require_role

app = FastAPI()
require_jwt = build_require_jwt(SECRET_KEY)
require_docente = build_require_role(SECRET_KEY, rol="docente")

@app.get("/perfil")
async def perfil(payload: dict = Depends(require_jwt)):
    return {"sub": payload["sub"]}
```

### `sward_shared.adapters` — adaptadores de salida AWS

Implementaciones concretas de infraestructura (van en la capa de infra del micro, nunca en
el dominio).

- **`EventBridgeAdapter(event_bus_name, source, region)`** — `publish(event, correlation_id)`
  envuelve con `EventEnvelope` y publica vía `boto3` `put_events`.
- **`SqsAdapter(queue_url, region)`** — `send_message(envelope)` / `receive_messages(...)`.

### `sward_shared.schemas` — DTOs transversales

- **`PaginationParams`** / **`PaginatedResponse[T]`** — paginación genérica (Pydantic v2).
- **`HealthCheckResponse`** / **`HealthStatus`** — respuesta estándar de health check.

## Cómo la consumen los micros

Se instala desde Git, **pinneando un commit SHA**, no una rama:

```
# requirements.txt de un micro
sward-shared @ git+https://github.com/sward-UPC/sward-shared.git@<COMMIT_SHA>
```

### Gotcha importante: pinnea el SHA, no `@main`

Si pinneas `sward-shared @ main`, Docker **cachea la capa** de `pip install` y deja de
reinstalar la librería aunque `main` haya avanzado: el micro se despliega con una versión
vieja de `sward-shared` sin que nada falle visiblemente. Esto ya rompió un despliegue
(trazabilidad quedó con un contrato de eventos desactualizado).

**Regla:** apunta siempre a un **commit SHA concreto** en `requirements`. Al cambiar el SHA,
cambia el contenido del `requirements`, invalida la capa Docker y fuerza la reinstalación.
Cuando publiques cambios en `sward-shared`, actualiza el SHA en cada micro que lo consume.

> Para entornos versionados también sirve un tag inmutable
> (`...@v0.1.0`), por la misma razón: una referencia que no se mueve a tus espaldas.

## Stack

- Python 3.11+
- Pydantic v2
- boto3 (adaptadores AWS) · FastAPI + python-jose (auth)

## Desarrollo y testing

```bash
pip install -e ".[dev]"   # instala extras de desarrollo (pytest, ruff, moto, httpx)

pytest -q                 # suite de tests
ruff check .              # lint
```

Estado actual: **21 tests** en verde, lint limpio. Convención de tests por tipo:
contratos de dominio (`events`, `identidad`) y `schemas` se prueban con tests unitarios
puros; los adaptadores AWS (`adapters/`) están preparados para integrarse con `moto` (deuda
técnica pendiente).

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)
Taller de Proyecto 1 / 2026
