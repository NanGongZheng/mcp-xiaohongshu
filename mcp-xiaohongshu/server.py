#!/usr/bin/env python3
"""
MCP 小红书数据 Server

功能：
  B1. MCP Server 框架（JSON-RPC 2.0 / stdio）
  B2. search_notes   搜索笔记
  B3. get_note_detail 获取笔记详情
  B4. get_user_profile 获取用户主页
  B5. get_user_notes  获取用户笔记列表
  B6. get_hot_topics  获取热门话题

数据源通过环境变量切换：
  MCP_XHS_PROVIDER=sample（默认）或 apify

运行：
  python server.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List

from providers import create_datasource
from providers.base import XhsDataSource

MCP_PROTOCOL_VERSION = "2025-11-25"
JSONRPC_VERSION = "2.0"


@dataclass
class MCPTool:
    name: str
    description: str
    inputSchema: Dict[str, Any]


ALL_TOOLS: List[MCPTool] = [
    MCPTool(
        name="search_notes",
        description="搜索小红书笔记，返回标题、作者、点赞数等",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜索关键词"},
                "limit": {"type": "integer", "description": "返回数量上限，默认 10"},
                "sort": {
                    "type": "string",
                    "enum": ["relevance", "popularity", "latest"],
                    "description": "排序方式",
                },
            },
            "required": ["keyword"],
        },
    ),
    MCPTool(
        name="get_note_detail",
        description="获取指定笔记的完整详情（正文、图片、互动数据等）",
        inputSchema={
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "笔记 ID"},
            },
            "required": ["note_id"],
        },
    ),
    MCPTool(
        name="get_user_profile",
        description="获取用户主页信息（粉丝数、获赞数、笔记数等）",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "用户 ID"},
            },
            "required": ["user_id"],
        },
    ),
    MCPTool(
        name="get_user_notes",
        description="获取指定用户发布的笔记列表",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "用户 ID"},
                "limit": {"type": "integer", "description": "数量上限，默认 10"},
            },
            "required": ["user_id"],
        },
    ),
    MCPTool(
        name="get_hot_topics",
        description="获取当前热门话题（可按分类筛选）",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "分类筛选，可选"},
            },
            "required": [],
        },
    ),
]


class MCPServer:
    def __init__(self, datasource: XhsDataSource) -> None:
        self.ds = datasource

    # ── JSON-RPC 路由 ─────────────────────────────────────────
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return self._initialize(request_id)
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return self._tools_list(request_id)
        if method == "tools/call":
            return self._tools_call(request_id, params)
        return self._error(request_id, -32601, f"Method not found: {method}")

    def _initialize(self, request_id: Any) -> Dict[str, Any]:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mcp-xiaohongshu", "version": "0.2.0"},
            },
        }

    def _tools_list(self, request_id: Any) -> Dict[str, Any]:
        tools = [
            {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
            for t in ALL_TOOLS
        ]
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": {"tools": tools}}

    def _tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            result = self._dispatch(tool_name, arguments)
            return {
                "jsonrpc": JSONRPC_VERSION,
                "id": request_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}
                    ]
                },
            }
        except Exception as exc:
            return self._error(request_id, -32602, str(exc))

    def _dispatch(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "search_notes":
            keyword = (args.get("keyword") or "").strip()
            if not keyword:
                raise ValueError("Missing required parameter: keyword")
            return self.ds.search_notes(
                keyword=keyword,
                limit=int(args.get("limit") or 10),
                sort=args.get("sort") or "relevance",
            )
        if tool_name == "get_note_detail":
            note_id = (args.get("note_id") or "").strip()
            if not note_id:
                raise ValueError("Missing required parameter: note_id")
            return self.ds.get_note_detail(note_id)
        if tool_name == "get_user_profile":
            user_id = (args.get("user_id") or "").strip()
            if not user_id:
                raise ValueError("Missing required parameter: user_id")
            return self.ds.get_user_profile(user_id)
        if tool_name == "get_user_notes":
            user_id = (args.get("user_id") or "").strip()
            if not user_id:
                raise ValueError("Missing required parameter: user_id")
            return self.ds.get_user_notes(user_id, limit=int(args.get("limit") or 10))
        if tool_name == "get_hot_topics":
            return self.ds.get_hot_topics(category=args.get("category"))
        raise ValueError(f"Unknown tool: {tool_name}")

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


def main() -> None:
    ds = create_datasource()
    server = MCPServer(ds)
    provider_name = type(ds).__name__
    print(f"MCP XHS Server started (provider={provider_name})", file=sys.stderr)
    print("Waiting for JSON-RPC requests on stdin...", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON: {exc}", file=sys.stderr)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
