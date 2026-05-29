from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .domain_event import DomainEvent


@dataclass
class EventEnvelope:
    id: UUID = field(default_factory=uuid4)
    correlation_id: str = ""
    payload_json: str = ""
    retry_count: int = 0

    @classmethod
    def wrap(cls, event: DomainEvent, correlation_id: str = "") -> "EventEnvelope":
        import dataclasses
        import json

        def default(obj):
            if isinstance(obj, UUID):
                return str(obj)
            from datetime import datetime

            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        payload = {
            "event_type": event.event_type,
            "event_id": str(event.event_id),
            "occurred_at": event.occurred_at.isoformat(),
            "source": event.source,
            **{
                k: v
                for k, v in dataclasses.asdict(event).items()
                if k not in ("event_id", "occurred_at", "source")
            },
        }
        return cls(
            correlation_id=correlation_id,
            payload_json=json.dumps(payload, default=default),
        )
