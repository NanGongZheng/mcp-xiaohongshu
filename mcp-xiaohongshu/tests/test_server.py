"""MCP XHS Server 测试：覆盖 B1 框架 + B2-B6 全部工具。"""

import json
import subprocess
import sys
from pathlib import Path

SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"


def call_server(payload):
    proc = subprocess.run(
        [sys.executable, str(SERVER_PATH)],
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        check=True,
    )
    return proc


def parse_response(proc):
    lines = [line for line in proc.stdout.strip().splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_initialize():
    resp = parse_response(call_server({"jsonrpc": "2.0", "id": 1, "method": "initialize"}))
    assert resp["result"]["serverInfo"]["name"] == "mcp-xiaohongshu"
    assert resp["result"]["protocolVersion"] == "2025-11-25"
    print("✓ B1: initialize")


def test_tools_list():
    resp = parse_response(call_server({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
    names = [t["name"] for t in resp["result"]["tools"]]
    assert len(names) == 5
    assert names == ["search_notes", "get_note_detail", "get_user_profile", "get_user_notes", "get_hot_topics"]
    print("✓ B1: tools/list (5 tools registered)")


def test_search_notes():
    resp = parse_response(call_server({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "search_notes", "arguments": {"keyword": "攻略", "limit": 5, "sort": "popularity"}},
    }))
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["keyword"] == "攻略"
    assert result["count"] >= 1
    print(f"✓ B2: search_notes → {result['count']} results")


def test_get_note_detail():
    resp = parse_response(call_server({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "get_note_detail", "arguments": {"note_id": "6650a1c6000000001d00abcd"}},
    }))
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["note_id"] == "6650a1c6000000001d00abcd"
    assert "title" in result
    assert "url" in result
    print(f"✓ B3: get_note_detail → {result['title']}")


def test_get_user_profile():
    resp = parse_response(call_server({
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "get_user_profile", "arguments": {"user_id": "u_skin_wei"}},
    }))
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["user_id"] == "u_skin_wei"
    assert "nickname" in result
    assert "followers" in result
    print(f"✓ B4: get_user_profile → {result['nickname']} ({result['followers']} followers)")


def test_get_user_notes():
    resp = parse_response(call_server({
        "jsonrpc": "2.0", "id": 6, "method": "tools/call",
        "params": {"name": "get_user_notes", "arguments": {"user_id": "u_travel_deer", "limit": 5}},
    }))
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["user_id"] == "u_travel_deer"
    assert result["count"] >= 1
    print(f"✓ B5: get_user_notes → {result['count']} notes")


def test_get_hot_topics():
    resp = parse_response(call_server({
        "jsonrpc": "2.0", "id": 7, "method": "tools/call",
        "params": {"name": "get_hot_topics", "arguments": {"category": "护肤"}},
    }))
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["category"] == "护肤"
    assert result["count"] >= 1
    print(f"✓ B6: get_hot_topics → {result['count']} topics")


if __name__ == "__main__":
    test_initialize()
    test_tools_list()
    test_search_notes()
    test_get_note_detail()
    test_get_user_profile()
    test_get_user_notes()
    test_get_hot_topics()
    print("\n🎉 All B1-B6 tests passed!")
