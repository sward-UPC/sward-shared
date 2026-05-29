import logging
from typing import Any

import boto3

from sward_shared.events.domain_event import DomainEvent
from sward_shared.events.event_envelope import EventEnvelope

logger = logging.getLogger(__name__)


class EventBridgeAdapter:
    def __init__(self, event_bus_name: str, source: str, region: str = "us-east-1"):
        self._bus = event_bus_name
        self._source = source
        self._client = boto3.client("events", region_name=region)

    def publish(self, event: DomainEvent, correlation_id: str = "") -> None:
        envelope = EventEnvelope.wrap(event, correlation_id=correlation_id)
        entry: dict[str, Any] = {
            "Source": self._source,
            "DetailType": event.event_type,
            "Detail": envelope.payload_json,
            "EventBusName": self._bus,
        }
        response = self._client.put_events(Entries=[entry])
        failed = response.get("FailedEntryCount", 0)
        if failed:
            logger.error("EventBridge publish failed: %s", response["Entries"])
            raise RuntimeError(f"EventBridge: {failed} event(s) failed to publish")
        logger.info("Evento publicado: %s | bus=%s", event.event_type, self._bus)
