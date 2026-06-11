from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


SAMPLE_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_notes.json"


def _dig(data: Any, path: Optional[str]) -> Any:
    if not path:
        return data
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _dig_list(data: Any, path: Optional[str]) -> List[Any]:
    value = _dig(data, path)
    if isinstance(value, list):
        return value
    return []


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


def _normalize_note(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "note_id": str(item.get("note_id") or item.get("id") or ""),
        "title": str(item.get("title") or ""),
        "author": str(item.get("author") or item.get("user_name") or ""),
        "user_id": str(item.get("user_id") or ""),
        "likes": _int(item.get("likes")),
        "collects": _int(item.get("collects") or item.get("favorites")),
        "comments": _int(item.get("comments")),
        "tags": _list(item.get("tags")),
        "created_at": str(item.get("created_at") or item.get("publish_time") or ""),
    }


def _normalize_note_detail(item: Dict[str, Any]) -> Dict[str, Any]:
    note = _normalize_note(item)
    note.update(
        {
            "content": str(item.get("content") or item.get("description") or ""),
            "images": _list(item.get("images") or item.get("image_urls")),
            "url": str(item.get("url") or ""),
        }
    )
    return note


def _normalize_user_profile(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_id": str(item.get("user_id") or item.get("id") or ""),
        "user_name": str(item.get("user_name") or item.get("nickname") or ""),
        "fans": _int(item.get("fans") or item.get("follower_count")),
        "notes_count": _int(item.get("notes_count") or item.get("note_count")),
        "desc": str(item.get("desc") or item.get("description") or ""),
        "url": str(item.get("url") or ""),
    }


def _normalize_topic(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(item.get("id") or item.get("topic_id") or ""),
        "name": str(item.get("name") or item.get("title") or ""),
        "heat": _int(item.get("heat") or item.get("hot")),
        "category": str(item.get("category") or ""),
    }


class SampleProvider:
    def __init__(self) -> None:
        if SAMPLE_DATA_PATH.exists():
            with SAMPLE_DATA_PATH.open("r", encoding="utf-8") as f:
                self._notes = json.load(f)
        else:
            self._notes = []

    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
    ) -> Dict[str, Any]:
        key = keyword.lower()
        matched = [
            n for n in self._notes if key in json.dumps(n, ensure_ascii=False).lower()
        ]

        def sort_key(item: Dict[str, Any]):
            if sort == "popularity":
                return (item.get("likes", 0), item.get("collects", 0))
            if sort == "latest":
                return (item.get("created_at", ""),)
            return (key in item.get("title", "").lower(),)

        matched.sort(key=sort_key, reverse=True)
        return {"notes": [_normalize_note(n) for n in matched[:limit]]}

    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        for note in self._notes:
            if str(note.get("note_id")) == note_id:
                detail = dict(note)
                detail.setdefault("content", "")
                detail.setdefault("images", [])
                detail.setdefault("url", "")
                return _normalize_note_detail(detail)
        raise ValueError(f"note_id not found: {note_id}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        for note in self._notes:
            if str(note.get("user_id")) == user_id:
                return _normalize_user_profile(
                    {
                        "user_id": user_id,
                        "user_name": note.get("author"),
                        "fans": 0,
                        "notes_count": 0,
                        "desc": "",
                        "url": "",
                    }
                )
        raise ValueError(f"user_id not found: {user_id}")

    def get_user_notes(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        matched = [n for n in self._notes if str(n.get("user_id")) == user_id]
        if not matched:
            raise ValueError(f"user_id not found: {user_id}")
        return {"notes": [_normalize_note(n) for n in matched[:limit]]}

    def get_hot_topics(self, category: Optional[str] = None) -> Dict[str, Any]:
        topics: List[Dict[str, Any]] = []
        seen = set()
        for note in self._notes:
            for tag in _list(note.get("tags")):
                if tag in seen:
                    continue
                seen.add(tag)
                topic = {"id": tag, "name": tag, "heat": _int(note.get("likes")), "category": category or ""}
                if category and category != topic["category"]:
                    continue
                topics.append(_normalize_topic(topic))
        topics.sort(key=lambda x: x["heat"], reverse=True)
        return {"category": category, "topics": topics}


@dataclass
class EndpointConfig:
    url: str
    data_path: Optional[str] = None


class HttpProvider:
    def __init__(self) -> None:
        base_url = os.environ.get("XHS_API_BASE_URL", "").rstrip("/")
        if not base_url:
            raise ValueError("Missing env: XHS_API_BASE_URL")

        self._api_key = os.environ.get("XHS_API_KEY")
        self._search = EndpointConfig(
            url=os.environ.get("XHS_SEARCH_URL") or f"{base_url}/search",
            data_path=os.environ.get("XHS_SEARCH_DATA_PATH"),
        )
        self._note_detail = EndpointConfig(
            url=os.environ.get("XHS_NOTE_DETAIL_URL") or f"{base_url}/note",
            data_path=os.environ.get("XHS_NOTE_DETAIL_DATA_PATH"),
        )
        self._user_profile = EndpointConfig(
            url=os.environ.get("XHS_USER_PROFILE_URL") or f"{base_url}/user",
            data_path=os.environ.get("XHS_USER_PROFILE_DATA_PATH"),
        )
        self._user_notes = EndpointConfig(
            url=os.environ.get("XHS_USER_NOTES_URL") or f"{base_url}/user/notes",
            data_path=os.environ.get("XHS_USER_NOTES_DATA_PATH"),
        )
        self._hot_topics = EndpointConfig(
            url=os.environ.get("XHS_HOT_TOPICS_URL") or f"{base_url}/topics",
            data_path=os.environ.get("XHS_HOT_TOPICS_DATA_PATH"),
        )

    def _request_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(
                {k: v for k, v in params.items() if v not in (None, "")}
            )
        request_url = f"{url}{query}"
        request = urllib.request.Request(request_url)
        if self._api_key:
            request.add_header("Authorization", f"Bearer {self._api_key}")
        with urllib.request.urlopen(request, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
        return json.loads(raw)

    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
    ) -> Dict[str, Any]:
        payload = self._request_json(
            self._search.url,
            {"keyword": keyword, "limit": limit, "sort": sort},
        )
        items = _dig_list(payload, self._search.data_path)
        return {"notes": [_normalize_note(item) for item in items[:limit]]}

    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        payload = self._request_json(self._note_detail.url, {"note_id": note_id})
        data = _dig(payload, self._note_detail.data_path) or payload
        return _normalize_note_detail(data if isinstance(data, dict) else {})

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        payload = self._request_json(self._user_profile.url, {"user_id": user_id})
        data = _dig(payload, self._user_profile.data_path) or payload
        return _normalize_user_profile(data if isinstance(data, dict) else {})

    def get_user_notes(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        payload = self._request_json(
            self._user_notes.url, {"user_id": user_id, "limit": limit}
        )
        items = _dig_list(payload, self._user_notes.data_path)
        return {"notes": [_normalize_note(item) for item in items[:limit]]}

    def get_hot_topics(self, category: Optional[str] = None) -> Dict[str, Any]:
        payload = self._request_json(self._hot_topics.url, {"category": category})
        items = _dig_list(payload, self._hot_topics.data_path)
        return {"category": category, "topics": [_normalize_topic(item) for item in items]}


def create_provider_from_env():
    provider = os.environ.get("XHS_PROVIDER", "sample").strip().lower()
    if provider in ("http", "api", "remote"):
        return HttpProvider()
    return SampleProvider()
