# CLAUDE.md — sward-shared

## Qué es este paquete
Librería Python compartida para todos los microservicios del sistema SWARD.
Proporciona clases base para eventos de dominio, adaptadores de infraestructura y schemas Pydantic comunes.

## Stack
- Python 3.11 / Pydantic v2 / boto3

## Estructura de carpetas
```
sward_shared/
  events/         # DomainEvent (base), EventEnvelope
  adapters/       # EventBridgeAdapter, SqsAdapter
  schemas/        # PaginationParams, PaginatedResponse, HealthCheckResponse
tests/
```

## Comandos clave
- Instalar en dev: `pip install -e ".[dev]"`
- Tests: `pytest tests/ -v`
- Lint: `ruff check . && ruff format .`

## Instalación en microservicios
```
sward-shared @ git+https://github.com/sward-UPC/sward-shared.git@v0.1.0
```

## Decisiones de diseño
- `DomainEvent` es una dataclass abstracta (no Pydantic) para mantener el dominio libre de frameworks.
- `EventEnvelope` serializa a JSON para compatibilidad con EventBridge y SQS.
- `EventBridgeAdapter` y `SqsAdapter` son adaptadores concretos — no se usan directamente en el dominio.
