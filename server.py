#!/usr/bin/env python3
import base64
import json
import mimetypes
import os
import threading
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "shared-data"
FILES_DIR = DATA_DIR / "files"
WORKSPACE_FILE = DATA_DIR / "workspace.json"
LOCK = threading.Lock()


def read_workspace():
    if not WORKSPACE_FILE.exists():
        return {"fileRecords": []}
    try:
        return json.loads(WORKSPACE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"fileRecords": []}


def write_workspace(workspace):
    DATA_DIR.mkdir(exist_ok=True)
    temporary = WORKSPACE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(workspace, indent=2))
    temporary.replace(WORKSPACE_FILE)


def revision():
    try:
        return WORKSPACE_FILE.stat().st_mtime_ns
    except FileNotFoundError:
        return 0


class Handler(SimpleHTTPRequestHandler):
    def end_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/workspace":
            with LOCK:
                self.end_json({"workspace": read_workspace(), "revision": revision()})
            return
        if parsed.path.startswith("/api/files/"):
            file_id = unquote(parsed.path.rsplit("/", 1)[-1])
            path = FILES_DIR / file_id
            if not path.is_file():
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(path.stat().st_size))
            self.end_headers()
            with path.open("rb") as file_handle:
                self.wfile.write(file_handle.read())
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(length) or "{}")
        except json.JSONDecodeError:
            self.end_json({"error": "Invalid JSON."}, 400)
            return
        if parsed.path == "/api/workspace":
            with LOCK:
                write_workspace(body)
                self.end_json({"ok": True, "revision": revision()})
            return
        if parsed.path == "/api/files":
            try:
                file_id = uuid.uuid4().hex
                FILES_DIR.mkdir(parents=True, exist_ok=True)
                file_name = str(body.get("name", "download.bin"))
                file_path = FILES_DIR / file_id
                file_path.write_bytes(base64.b64decode(body["data"]))
                self.end_json({"ok": True, "id": file_id, "url": f"/api/files/{file_id}", "name": file_name})
            except (KeyError, ValueError):
                self.end_json({"error": "Invalid file upload."}, 400)
            return
        self.end_json({"error": "Not found."}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/files/"):
            file_id = unquote(parsed.path.rsplit("/", 1)[-1])
            try:
                (FILES_DIR / file_id).unlink()
            except FileNotFoundError:
                pass
            self.end_json({"ok": True})
            return
        self.end_json({"error": "Not found."}, 404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Instructor Desk running on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()