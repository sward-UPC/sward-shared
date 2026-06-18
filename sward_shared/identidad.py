"""Vinculación determinística Moodle → SWARD (compartida entre microservicios).

El UUID de una entidad de SWARD se deriva de su id en Moodle mediante uuid5 con
un namespace fijo. Al vivir en sward-shared, todos los servicios usan el MISMO
namespace, garantizando que el mismo usuario/curso/actividad tenga el mismo UUID
en ms-usuarios, ms-trazabilidad, etc.
"""

from uuid import UUID, uuid5

# Namespace fijo de SWARD para derivar UUIDs determinísticos desde Moodle.
MOODLE_NS = UUID("a9f3e7b5-1234-5678-abcd-ef0123456789")


def moodle_uuid(entity_type: str, moodle_id: int | str) -> UUID:
    """UUID determinístico de una entidad SWARD desde su id de Moodle.

    `entity_type` es el tipo lógico ("user", "course", "activity", ...).
    """
    return uuid5(MOODLE_NS, f"{entity_type}:{moodle_id}")


def id_sward_desde_moodle(moodle_user_id: int | str) -> UUID:
    """UUID del usuario en SWARD a partir de su `moodle_user_id`."""
    return moodle_uuid("user", moodle_user_id)
