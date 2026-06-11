"""通用 HTTP API 数据源：适配第三方小红书 API / 聚合网关。

使用前需设置环境变量：
  export MCP_XHS_PROVIDER=http
  export MCP_XHS_API_BASE_URL=https://your-api.example.com

可选配置（覆盖默认路径）：
  export MCP_XHS_SEARCH_PATH=/search
  export MCP_XHS_NOTE_DETAIL_PATH=/note
  export MCP_XHS_USER_PROFILE_PATH=/user
  export MCP_XHS_USER_NOTES_PATH=/user/notes
  export MCP_XHS_HOT_TOPICS_PATH=/topics
  export MCP_XHS_API_KEY=可选鉴权token
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from .base import XhsDataSource


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _request_json(url: str, params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None) -> Any:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    request = urllib.request.Request(f"{url}{query}")
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except Exception:
        return default


def _list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return []


def _pick_note(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "note_id": str(item.get("note_id") or item.get("noteId") or item.get("id") or ""),
        "title": str(item.get("title") or ""),
        "author": str(item.get("author") or item.get("authorName") or item.get("nickname") or ""),
        "user_id": str(item.get("user_id") or item.get("userId") or item.get("authorId") or ""),
        "likes": _int(item.get("likes") or item.get("likedCount")),
        "collects": _int(item.get("collects") or item.get("collectedCount")),
        "comments": _int(item.get("comments") or item.get("commentCount")),
        "tags": _list(item.get("tags")),
        "created_at": str(item.get("created_at") or item.get("createdAt") or item.get("time") or ""),
    }


def _pick_user(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_id": str(item.get("user_id") or item.get("userId") or item.get("id") or ""),
        "nickname": str(item.get("nickname") or item.get("user_name") or item.get("name") or ""),
        "desc": str(item.get("desc") or item.get("description") or ""),
        "followers": _int(item.get("followers") or item.get("fansCount") or item.get("fans")),
        "following": _int(item.get("following") or item.get("followingCount")),
        "total_likes": _int(item.get("total_likes") or item.get("likedCount")),
        "note_count": _int(item.get("note_count") or item.get("noteCount") or item.get("notes_count")),
        "avatar": str(item.get("avatar") or item.get("image") or ""),
        "url": str(item.get("url") or ""),
    }


def _pick_topic(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": str(item.get("title") or item.get("name") or item.get("keyword") or ""),
        "heat": _int(item.get("heat") or item.get("hot") or item.get("count")),
        "category": str(item.get("category") or ""),
    }


class HttpDataSource(XhsDataSource):
    def __init__(self) -> None:
        base_url = _env("MCP_XHS_API_BASE_URL")
        if not base_url:
            raise ValueError("Missing env: MCP_XHS_API_BASE_URL")

        self._api_key = _env("MCP_XHS_API_KEY") or None
        self._search_url = _env("MCP_XHS_SEARCH_PATH") or f"{base_url}/search"
        self._note_url = _env("MCP_XHS_NOTE_DETAIL_PATH") or f"{base_url}/note"
        self._user_url = _env("MCP_XHS_USER_PROFILE_PATH") or f"{base_url}/user"
        self._user_notes_url = _env("MCP_XHS_USER_NOTES_PATH") or f"{base_url}/user/notes"
        self._topics_url = _env("MCP_XHS_HOT_TOPICS_PATH") or f"{base_url}/topics"

    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = _request_json(self._search_url, {"keyword": keyword, "limit": limit, "sort": sort, "category": category}, self._api_key)
        items: List[Dict[str, Any]] = payload if isinstance(payload, list) else payload.get("data", payload.get("notes", []))
        if not isinstance(items, list):
            items = []
        return {"keyword": keyword, "sort": sort, "count": len(items), "notes": [_pick_note(i) for i in items[:limit]]}

    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        payload = _request_json(self._note_url, {"note_id": note_id}, self._api_key)
        data = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(data, dict):
            raise ValueError(f"Invalid response for note_id: {note_id}")
        result = _pick_note(data)
        result.update(
            {
                "content": str(data.get("content") or data.get("desc") or ""),
                "images": _list(data.get("images") or data.get("image_urls")),
                "url": str(data.get("url") or ""),
                "raw": data,
            }
        )
        return result

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        payload = _request_json(self._user_url, {"user_id": user_id}, self._api_key)
        data = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(data, dict):
            raise ValueError(f"Invalid response for user_id: {user_id}")
        user = _pick_user(data)
        user["raw"] = data
        return user

    def get_user_notes(
        self, user_id: str, limit: int = 10
    ) -> Dict[str, Any]:
        payload = _request_json(self._user_notes_url, {"user_id": user_id, "limit": limit}, self._api_key)
        items: List[Dict[str, Any]] = payload if isinstance(payload, list) else payload.get("data", payload.get("notes", []))
        if not isinstance(items, list):
            items = []
        return {"user_id": user_id, "count": len(items), "notes": [_pick_note(i) for i in items[:limit]]}

    def get_hot_topics(
        self, category: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = _request_json(self._topics_url, {"category": category}, self._api_key)
        items: List[Dict[str, Any]] = payload if isinstance(payload, list) else payload.get("data", payload.get("topics", []))
        if not isinstance(items, list):
            items = []
        topics = [_pick_topic(i) for i in items]
        return {"category": category or "全部", "count": len(topics), "topics": topics}
