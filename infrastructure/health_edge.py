"""HTTP health edge for the local dev stack.

The app serves HTTPS-only (self-signed certs; secure cookies require it),
but tooling such as `hermes verify` polls plain HTTP. This tiny sidecar
mirrors the backend's health endpoint over HTTP on port 8001 so readiness
probes can run without weakening the app itself:

    hermes verify --port 8001

Returns 200 + the backend body only when the backend is healthy; 503
otherwise. Stdlib only — runs on python:slim, no pip installs.
"""

import json
import os
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND_URL = os.environ.get("BACKEND_HEALTH_URL", "https://backend:8000/api/v1/health/")
PORT = int(os.environ.get("HEALTH_EDGE_PORT", "8001"))

# Self-signed dev certs: skip verification (loopback network only).
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - http.server API
        try:
            with urllib.request.urlopen(BACKEND_URL, timeout=5, context=_ctx) as resp:
                body = resp.read()
                self.send_response(resp.status)
                self.end_headers()
                self.wfile.write(body)
        except Exception as exc:  # noqa: BLE001 - any failure means unhealthy
            payload = json.dumps({"detail": f"backend unhealthy: {exc}"}).encode()
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:  # keep compose logs quiet
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), _Handler).serve_forever()  # nosec B104 -- container bind
