import json
from dataclasses import dataclass

from sward_shared.events.domain_event import DomainEvent
from sward_shared.events.event_envelope import EventEnvelope


@dataclass
class TestEvent(DomainEvent):
    data: str = ""

    @property
    def event_type(self) -> str:
        return "sward.test.TestEvent"


def test_wrap_genera_payload_json_valido():
    event = TestEvent(data="hello")
    envelope = EventEnvelope.wrap(event, correlation_id="corr-1")
    assert envelope.correlation_id == "corr-1"
    payload = json.loads(envelope.payload_json)
    assert payload["event_type"] == "sward.test.TestEvent"
    assert payload["data"] == "hello"


def test_wrap_serializa_uuid_y_datetime():
    event = TestEvent(data="test")
    envelope = EventEnvelope.wrap(event)
    payload = json.loads(envelope.payload_json)
    assert isinstance(payload["event_id"], str)
    assert isinstance(payload["occurred_at"], str)
