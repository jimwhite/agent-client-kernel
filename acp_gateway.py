#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from openai import OpenAI

LOG_PATH = os.path.join(os.path.dirname(__file__), "acp_gateway.log")


def log(msg: str) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


# ---------- Mode 1: Kernel shim (used by agent-client-kernel) ----------

def run_kernel_shim() -> None:
    """
    Mode used by agent-client-kernel.
    It just launches the real ACP agent (codex-acp by default).
    """
    cmd = os.environ.get("REAL_AGENT_COMMAND", "codex-acp")
    extra = os.environ.get("REAL_AGENT_ARGS", "")

    args = [cmd]
    if extra:
        args.extend(extra.split())
    # Pass through any arguments from Jupyter
    args.extend(sys.argv[1:])

    log(f"launching: {' '.join(args)}")

    # Replace this process with the real agent
    os.execvp(cmd, args)


# ---------- Mode 2: Simple HTTP server (for future JupyterLite) ----------

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        # CORS headers so browser JS can call us from file:// or other origins
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        # Preflight for CORS
        self._set_headers(204)

    def do_GET(self) -> None:
        # Health check
        if self.path == "/" or self.path == "/health":
            self._set_headers(200)
            self.wfile.write(
                b'{"status":"ok","message":"acp-gateway http mode is running"}'
            )
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not_found"}')

    def do_POST(self) -> None:
        # Very small API: POST /chat with JSON {"prompt": "..."}
        if self.path != "/chat":
            self._set_headers(404)
            self.wfile.write(b'{"error":"not_found"}')
            return

        # Read body
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(b'{"error":"invalid_json"}')
            log("HTTP /chat invalid JSON")
            return

        prompt = payload.get("prompt", "")
        log(f"HTTP /chat prompt={prompt!r}")

        # Call OpenAI chat completion as a stand-in for a real agent.
        try:
            # IMPORTANT: Create client fresh so it uses current env
            client = OpenAI()

            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a concise coding assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            reply_text = completion.choices[0].message.content
            log("HTTP /chat got reply from OpenAI")

            self._set_headers(200)
            self.wfile.write(json.dumps({"reply": reply_text}).encode("utf-8"))

        except Exception as e:
            log(f"HTTP /chat OpenAI error: {e!r}")
            self._set_headers(500)
            self.wfile.write(
                json.dumps({"error": "llm_error", "detail": str(e)}).encode("utf-8")
            )

    def log_message(self, format: str, *args) -> None:
        # Redirect HTTP server logs into our log file
        log("HTTP " + format % args)


def run_http_server(port: int = 8000) -> None:
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHandler)
    log(f"http server starting on port {port}")
    httpd.serve_forever()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        sys.argv.pop(1)
        port = 8000
        if len(sys.argv) > 1 and sys.argv[1] == "--port":
            sys.argv.pop(1)
            port = int(sys.argv.pop(1))
        run_http_server(port)
    else:
        run_kernel_shim()


if __name__ == "__main__":
    main()
