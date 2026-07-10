"""Legacy workspace-snapshot handler.

Early releases exported a user's workspace as a serialized Python object
(the ``legacy`` snapshot profile). This handler rehydrates such a snapshot
back into a live workspace mapping so it can be re-imported.

Newer profiles use JSON and go through the ``json_decode`` handler instead;
this module exists only for backward compatibility with pre-2.0 exports.
"""

from typing import Any, Dict

from utils.plugin_loader import PluginRegistry
from utils.serializer import deserialize_object


@PluginRegistry.register("state_restore")
def restore_state(blob: str) -> Dict[str, Any]:
    """Rebuild a workspace object from a legacy snapshot blob.

    ``blob`` is the base64 body produced by the matching exporter. The
    integrity of the blob is verified by the caller before it reaches here.
    """
    workspace = deserialize_object(blob)
    return _project(workspace)


def _project(workspace: Any) -> Dict[str, Any]:
    """Return a JSON-serializable view of the restored workspace."""
    if isinstance(workspace, dict):
        return {str(k): _coerce(v) for k, v in workspace.items()}
    return {"value": _coerce(workspace)}


def _coerce(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
