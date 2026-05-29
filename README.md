# sward-shared

Librería Python compartida para todos los microservicios del sistema **SWARD** (Sistema Web de Recomendación Adaptativa y Explicable).

## Contenido

- `sward_shared/events/` — `DomainEvent` (base abstracta), `EventEnvelope`
- `sward_shared/adapters/` — `EventBridgeAdapter`, `SqsAdapter`
- `sward_shared/schemas/` — `PaginationParams`, `HealthCheckResponse`

## Instalación

```bash
pip install "sward-shared @ git+https://github.com/sward-UPC/sward-shared.git@v0.1.0"
```

## Stack

- Python 3.11
- boto3 (AWS SDK)
- Pydantic v2

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)  
Taller de Proyecto 1 / 2026
