import json
import os
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_notes.json"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        notes = []
        if DATA_PATH.exists():
            with DATA_PATH.open("r", encoding="utf-8") as f:
                notes = json.load(f)

        if path == "/search":
            self._json({"data": notes})
            return
        if path == "/note":
            self._json({"data": notes[0] if notes else {}})
            return
        if path == "/user":
            note = notes[0] if notes else {}
            self._json({"data": {"user_id": note.get("user_id", ""), "nickname": note.get("author", ""), "followers": 111, "note_count": 22}})
            return
        if path == "/user/notes":
            self._json({"data": notes[:3]})
            return
        if path == "/topics":
            self._json({"data": [{"title": "旅行", "heat": 999, "category": "生活方式"}]})
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def call_server(payload, env):
    proc = subprocess.run(
        [sys.executable, str(SERVER_PATH)],
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return proc


def test_http_provider_search_and_note():
    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    env = os.environ.copy()
    env["MCP_XHS_PROVIDER"] = "http"
    env["MCP_XHS_API_BASE_URL"] = f"http://127.0.0.1:{port}"

    payload = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "search_notes",
            "arguments": {"keyword": "攻略", "limit": 2, "sort": "popularity"},
        },
    }
    lines = call_server(payload, env).stdout.strip().splitlines()
    response = json.loads(lines[-1])
    result = json.loads(response["result"]["content"][0]["text"])
    assert result["keyword"] == "攻略"
    assert result["count"] >= 1
    note = result["notes"][0]
    assert note.get("note_id")

    payload2 = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "get_note_detail",
            "arguments": {"note_id": note["note_id"]},
        },
    }
    lines2 = call_server(payload2, env).stdout.strip().splitlines()
    response2 = json.loads(lines2[-1])
    result2 = json.loads(response2["result"]["content"][0]["text"])
    assert result2["note_id"] == note["note_id"]

    server.shutdown()


def test_http_provider_user_and_topics():
    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    env = os.environ.copy()
    env["MCP_XHS_PROVIDER"] = "http"
    env["MCP_XHS_API_BASE_URL"] = f"http://127.0.0.1:{port}"

    payload = {
        "jsonrpc": "2.0",
        "id": 21,
        "method": "tools/call",
        "params": {
            "name": "get_user_profile",
            "arguments": {"user_id": "u_travel_deer"},
        },
    }
    lines = call_server(payload, env).stdout.strip().splitlines()
    response = json.loads(lines[-1])
    result = json.loads(response["result"]["content"][0]["text"])
    assert result["user_id"] == "u_travel_deer"
    assert result["followers"] == 111

    payload2 = {
        "jsonrpc": "2.0",
        "id": 22,
        "method": "tools/call",
        "params": {
            "name": "get_hot_topics",
            "arguments": {},
        },
    }
    lines2 = call_server(payload2, env).stdout.strip().splitlines()
    response2 = json.loads(lines2[-1])
    result2 = json.loads(response2["result"]["content"][0]["text"])
    assert result2["count"] >= 1

    server.shutdown()


if __name__ == "__main__":
    test_http_provider_search_and_note()
    test_http_provider_user_and_topics()
    print("HTTP provider tests passed.")
