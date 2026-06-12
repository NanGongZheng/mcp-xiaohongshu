#!/usr/bin/env python3
"""一键演示脚本：向 MCP Server 发送 JSON-RPC 请求，查看小红书能力效果。

使用方式：
  python scripts/demo.py                # 默认使用示例数据
  MCP_XHS_PROVIDER=http MCP_XHS_API_BASE_URL=https://your-api python scripts/demo.py
"""

import json
import subprocess
import sys
from pathlib import Path

SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"


def call_server(payload, env=None):
    proc = subprocess.run(
        [sys.executable, str(SERVER_PATH)],
        input=json.dumps(payload, ensure_ascii=False) + "\n",
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    lines = [line.strip() for line in proc.stdout.strip().splitlines() if line.strip()]
    return json.loads(lines[-1])


def extract_text(response):
    return json.loads(response["result"]["content"][0]["text"])


def main():
    print("🚀 MCP 小红书数据 Server 演示")
    print("=" * 50)

    # 1. initialize
    print("\n[1] initialize")
    resp = call_server({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    print(f"  Server: {resp['result']['serverInfo']['name']} v{resp['result']['serverInfo']['version']}")

    # 2. tools/list
    print("\n[2] tools/list")
    resp = call_server({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = [t["name"] for t in resp["result"]["tools"]]
    print(f"  注册 Tools: {', '.join(tools)}")

    # 3. search_notes
    print("\n[3] search_notes (keyword='攻略', limit=3, sort='popularity')")
    resp = call_server({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "search_notes", "arguments": {"keyword": "攻略", "limit": 3, "sort": "popularity"}},
    })
    result = extract_text(resp)
    print(f"  命中: {result['count']} 条")
    for i, note in enumerate(result["notes"], 1):
        print(f"  [{i}] {note['title']}  ❤️{note.get('likes',0)}  ⭐{note.get('collects',0)}")

    # 4. get_note_detail
    first_note_id = result["notes"][0]["note_id"] if result["notes"] else None
    if first_note_id:
        print(f"\n[4] get_note_detail (note_id={first_note_id})")
        resp = call_server({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "get_note_detail", "arguments": {"note_id": first_note_id}},
        })
        detail = extract_text(resp)
        print(f"  标题: {detail.get('title')}")
        print(f"  作者: {detail.get('author')}")
        print(f"  URL:  {detail.get('url')}")

    # 5. get_user_profile
    first_user_id = result["notes"][0].get("user_id") if result["notes"] else None
    if first_user_id:
        print(f"\n[5] get_user_profile (user_id={first_user_id})")
        resp = call_server({
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "get_user_profile", "arguments": {"user_id": first_user_id}},
        })
        user = extract_text(resp)
        print(f"  昵称: {user.get('nickname')}")
        print(f"  粉丝: {user.get('followers')}")

    # 6. get_hot_topics
    print("\n[6] get_hot_topics")
    resp = call_server({
        "jsonrpc": "2.0", "id": 6, "method": "tools/call",
        "params": {"name": "get_hot_topics", "arguments": {}},
    })
    topics = extract_text(resp)
    print(f"  话题数: {topics.get('count')}")
    for t in topics.get("topics", [])[:3]:
        print(f"  - {t.get('title')} (heat={t.get('heat')})")

    print("\n✅ 演示完成")


if __name__ == "__main__":
    main()
