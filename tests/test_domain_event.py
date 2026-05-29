from dataclasses import dataclass

from sward_shared.events.domain_event import DomainEvent


@dataclass
class UsuarioRegistradoEvent(DomainEvent):
    usuario_id: str = ""

    @property
    def event_type(self) -> str:
        return "sward.usuarios.UsuarioRegistrado"


def test_domain_event_tiene_id_y_timestamp():
    event = UsuarioRegistradoEvent(usuario_id="u-123")
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.event_type == "sward.usuarios.UsuarioRegistrado"


def test_dos_eventos_tienen_ids_distintos():
    e1 = UsuarioRegistradoEvent(usuario_id="u-1")
    e2 = UsuarioRegistradoEvent(usuario_id="u-2")
    assert e1.event_id != e2.event_id
