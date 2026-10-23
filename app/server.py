"""Minimal standard-library web app for a Docker/CI learning project."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

STATIC_DIR = Path(__file__).resolve().parent / "static"
HEALTH_PAYLOAD = json.dumps(
    {"status": "UP", "service": "dockerwebapp"},
    separators=(",", ":"),
).encode("utf-8")


class WebAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path

        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(HEALTH_PAYLOAD)))
            self.end_headers()
            self.wfile.write(HEALTH_PAYLOAD)
            return

        self.path = "/index.html" if path == "/" else path
        super().do_GET()


def create_server(host="127.0.0.1", port=8080):
    """Create an HTTP server, allowing port 0 for isolated tests."""
    return ThreadingHTTPServer((host, int(port)), WebAppHandler)


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    server = create_server(host, port)
    print(f"dockerwebapp listening on {host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
