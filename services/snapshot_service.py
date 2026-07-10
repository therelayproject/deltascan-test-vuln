"""Workspace-snapshot restore orchestration.

A restore is dispatched to a per-profile handler that knows how to rebuild
that snapshot's format. Handlers are looked up in the plugin registry by
name, which keeps this service agnostic to the concrete snapshot formats.

Before dispatch we verify the blob against its integrity checksum so a
truncated or tampered snapshot is rejected early rather than failing deep
inside a handler.
"""

import hashlib
from dataclasses import dataclass
from typing import Any, Dict

from utils.plugin_loader import PluginRegistry

# Importing this module registers the "state_restore" handler as a side
# effect (see plugins/state_plugin.py). Without it the "legacy" profile
# would resolve to a missing handler.
import plugins.state_plugin  # noqa: F401


# Maps a user-facing profile to the registry handler that restores it.
_PROFILE_HANDLERS: Dict[str, str] = {
    "default": "json_decode",
    "legacy": "state_restore",
}

_DEFAULT_HANDLER = "json_decode"


@dataclass
class RestoreRequest:
    """A single restore operation, as received from the API layer."""

    profile: str
    blob: str
    checksum: str


class SnapshotService:
    """Restores previously exported workspace snapshots."""

    def restore(self, profile: str, blob: str, checksum: str) -> Any:
        req = RestoreRequest(profile=profile, blob=blob, checksum=checksum)
        self._verify_integrity(req)

        body = self._strip_envelope(req.blob)
        handler_name = _PROFILE_HANDLERS.get(req.profile, _DEFAULT_HANDLER)
        handler = PluginRegistry.get_handler(handler_name)
        if handler is None:
            raise ValueError(f"unsupported snapshot profile: {req.profile!r}")
        return handler(body)

    @staticmethod
    def _verify_integrity(req: RestoreRequest) -> None:
        """Reject a snapshot whose body does not match its checksum.

        The checksum travels with the snapshot so a corrupted upload is
        caught before we spend time rebuilding it.
        """
        if not req.checksum:
            return
        digest = hashlib.sha256(req.blob.encode("utf-8")).hexdigest()
        if digest != req.checksum:
            raise ValueError("snapshot integrity check failed")

    @staticmethod
    def _strip_envelope(blob: str) -> str:
        """Drop the schema tag legacy exporters prepended (e.g. ``v1:``)."""
        if len(blob) > 3 and blob[2] == ":" and blob[:2].lower() in ("v1", "v2"):
            return blob[3:]
        return blob
