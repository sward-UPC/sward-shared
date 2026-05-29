# PROGRESS — sward-shared

## Sprint 0 — 2026-05-29

### Implementado
- [x] `DomainEvent` — clase base abstracta para eventos de dominio
- [x] `EventEnvelope` — envuelve eventos para publicación en EventBridge/SQS
- [x] `EventBridgeAdapter` — publica eventos en Amazon EventBridge via boto3
- [x] `SqsAdapter` — envía/recibe mensajes en Amazon SQS
- [x] `PaginationParams` / `PaginatedResponse` — paginación genérica con Pydantic v2
- [x] `HealthCheckResponse` — schema de health check estándar
- [x] Tests unitarios para DomainEvent, EventEnvelope, PaginatedResponse
- [x] `pyproject.toml` con dependencias y configuración de ruff/pytest

### Pendiente
- [ ] Tag v0.1.0 en GitHub
- [ ] GitHub Actions CI (lint + test)

### Deuda técnica
- EventBridgeAdapter y SqsAdapter no tienen tests (requieren moto o mocks AWS)
