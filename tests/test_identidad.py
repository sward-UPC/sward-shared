from uuid import UUID

from sward_shared.identidad import MOODLE_NS, id_sward_desde_moodle, moodle_uuid


def test_es_deterministico():
    assert id_sward_desde_moodle(7) == id_sward_desde_moodle(7)
    assert moodle_uuid("course", 10) == moodle_uuid("course", 10)


def test_distinto_por_tipo_e_id():
    assert moodle_uuid("user", 7) != moodle_uuid("course", 7)
    assert id_sward_desde_moodle(7) != id_sward_desde_moodle(8)


def test_coincide_con_namespace_y_formato():
    # El valor debe ser estable (contrato cross-servicio): uuid5(NS, "user:7").
    from uuid import uuid5

    assert id_sward_desde_moodle(7) == uuid5(MOODLE_NS, "user:7")
    assert isinstance(id_sward_desde_moodle(7), UUID)
