"""Workspace snapshot API.

Endpoints for exporting and restoring a user's workspace snapshot. A
snapshot is an opaque, integrity-checked blob previously produced by this
same API; restoring it rebuilds the user's saved workspace state.
"""

from flask import Blueprint, jsonify, request

from services.snapshot_service import SnapshotService

snapshots_bp = Blueprint("snapshots", __name__)

_service = SnapshotService()


@snapshots_bp.route("/snapshots/restore", methods=["POST"])
def restore_snapshot():
    """Restore a workspace from a previously exported snapshot blob."""
    data = request.get_json(force=True, silent=True) or {}

    profile = data.get("profile", "default")
    blob = data.get("state", "")
    checksum = data.get("checksum", "")

    if not blob:
        return jsonify({"error": "missing snapshot state"}), 400

    restored = _service.restore(profile=profile, blob=blob, checksum=checksum)
    return jsonify({"status": "restored", "workspace": restored})
