"""示例数据源：用本地 JSON 文件模拟小红书数据，用于开发和测试。"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import XhsDataSource

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class SampleDataSource(XhsDataSource):
    def __init__(self) -> None:
        self._notes = self._load("sample_notes.json")
        self._users = self._load("sample_users.json")
        self._topics = self._load("sample_topics.json")
        # 建立 note_id -> note 索引
        self._note_index: Dict[str, Dict[str, Any]] = {
            n["note_id"]: n for n in self._notes
        }
        # 建立 user_id -> user 索引
        self._user_index: Dict[str, Dict[str, Any]] = {
            u["user_id"]: u for u in self._users
        }

    @staticmethod
    def _load(filename: str) -> List[Dict[str, Any]]:
        path = DATA_DIR / filename
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # ── B2: search_notes ──────────────────────────────────────
    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        key = keyword.lower()
        matched = [
            n for n in self._notes
            if key in json.dumps(n, ensure_ascii=False).lower()
        ]
        if sort == "popularity":
            matched.sort(key=lambda n: (n.get("likes", 0), n.get("collects", 0)), reverse=True)
        elif sort == "latest":
            matched.sort(key=lambda n: n.get("created_at", ""), reverse=True)
        return {
            "keyword": keyword,
            "sort": sort,
            "count": min(len(matched), limit),
            "notes": matched[:limit],
        }

    # ── B3: get_note_detail ───────────────────────────────────
    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        note = self._note_index.get(note_id)
        if not note:
            raise ValueError(f"Note not found: {note_id}")
        # 合并用户信息
        user = self._user_index.get(note.get("user_id", ""), {})
        return {
            **note,
            "author_followers": user.get("followers"),
            "author_total_likes": user.get("total_likes"),
            "url": f"https://www.xiaohongshu.com/explore/{note_id}",
        }

    # ── B4: get_user_profile ──────────────────────────────────
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        user = self._user_index.get(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        return user

    # ── B5: get_user_notes ────────────────────────────────────
    def get_user_notes(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        if user_id not in self._user_index:
            raise ValueError(f"User not found: {user_id}")
        user_notes = [n for n in self._notes if n.get("user_id") == user_id]
        return {
            "user_id": user_id,
            "count": min(len(user_notes), limit),
            "notes": user_notes[:limit],
        }

    # ── B6: get_hot_topics ────────────────────────────────────
    def get_hot_topics(self, category: Optional[str] = None) -> Dict[str, Any]:
        topics = self._topics
        if category:
            cat_lower = category.lower()
            topics = [t for t in topics if cat_lower in json.dumps(t, ensure_ascii=False).lower()]
        return {
            "category": category or "全部",
            "count": len(topics),
            "topics": topics,
        }
