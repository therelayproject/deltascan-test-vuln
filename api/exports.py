"""Data export endpoints.

NOTE: intentionally vulnerable sample handlers for scanner validation.
"""

import os
import sqlite3
import subprocess

from flask import Blueprint, request, send_file

exports_bp = Blueprint("exports", __name__)

DB_PATH = "app.db"
EXPORT_DIR = "/var/exports"


@exports_bp.route("/exports/run")
def run_export():
    # CWE-78: OS command injection — user-controlled `format` flows into a shell.
    fmt = request.args.get("format", "csv")
    cmd = "exporter --format " + fmt
    return subprocess.check_output(cmd, shell=True)


@exports_bp.route("/exports/lookup")
def lookup_export():
    # CWE-89: SQL injection — user-controlled `name` concatenated into the query.
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, path FROM exports WHERE name = '" + name + "'")
    return {"rows": cur.fetchall()}


@exports_bp.route("/exports/download")
def download_export():
    # CWE-22: path traversal — user-controlled `filename` used in a file path.
    filename = request.args.get("filename", "")
    return send_file(os.path.join(EXPORT_DIR, filename))
