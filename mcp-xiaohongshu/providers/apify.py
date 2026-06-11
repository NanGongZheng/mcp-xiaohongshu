"""Apify 数据源：通过 Apify Actor 获取小红书真实数据。

使用前需设置环境变量：
  export APIFY_API_TOKEN=your_token_here

可选配置：
  export APIFY_XHS_ACTOR_ID=apify/xhs-scraper  # 默认 Actor ID
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

from .base import XhsDataSource

APIFY_BASE_URL = "https://api.apify.com/v2"
DEFAULT_ACTOR_ID = "apify/xhs-scraper"


class ApifyDataSource(XhsDataSource):
    def __init__(self) -> None:
        self.token = os.environ.get("APIFY_API_TOKEN")
        self.actor_id = os.environ.get("APIFY_XHS_ACTOR_ID", DEFAULT_ACTOR_ID)
        if not self.token:
            raise ValueError(
                "APIFY_API_TOKEN environment variable is required. "
                "Get your token at https://console.apify.com/account/integrations"
            )

    def _run_actor(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """运行 Apify Actor 并返回结果"""
        url = f"{APIFY_BASE_URL}/acts/{self.actor_id}/runs?token={self.token}"
        data = json.dumps(input_data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                run_info = json.loads(resp.read().decode("utf-8"))
            # 获取结果
            dataset_id = run_info.get("data", {}).get("defaultDatasetId")
            if not dataset_id:
                return []
            items_url = f"{APIFY_BASE_URL}/datasets/{dataset_id}/items?token={self.token}&format=json"
            with urllib.request.urlopen(items_url, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(f"Apify API error: {e}")

    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        raw = self._run_actor({"searchKeyword": keyword, "maxItems": limit, "sort": sort})
        notes = []
        for item in raw:
            notes.append({
                "note_id": item.get("noteId") or item.get("id", ""),
                "title": item.get("title", ""),
                "author": item.get("authorName") or item.get("nickname", ""),
                "user_id": item.get("authorId") or item.get("userId", ""),
                "likes": item.get("likedCount") or item.get("likes", 0),
                "collects": item.get("collectedCount") or item.get("collects", 0),
                "comments": item.get("commentCount") or item.get("comments", 0),
                "tags": item.get("tags", []),
                "created_at": item.get("time") or item.get("createdAt", ""),
                "raw": item,
            })
        return {"keyword": keyword, "sort": sort, "count": len(notes), "notes": notes[:limit]}

    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        raw = self._run_actor({"noteIds": [note_id], "maxItems": 1})
        if not raw:
            raise ValueError(f"Note not found: {note_id}")
        item = raw[0]
        return {
            "note_id": item.get("noteId") or item.get("id", note_id),
            "title": item.get("title", ""),
            "author": item.get("authorName") or item.get("nickname", ""),
            "user_id": item.get("authorId") or item.get("userId", ""),
            "content": item.get("desc") or item.get("content", ""),
            "likes": item.get("likedCount") or item.get("likes", 0),
            "collects": item.get("collectedCount") or item.get("collects", 0),
            "comments": item.get("commentCount") or item.get("comments", 0),
            "images": item.get("images", []),
            "tags": item.get("tags", []),
            "created_at": item.get("time") or item.get("createdAt", ""),
            "url": item.get("url") or f"https://www.xiaohongshu.com/explore/{note_id}",
            "raw": item,
        }

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        raw = self._run_actor({"userIds": [user_id], "maxItems": 1})
        if not raw:
            raise ValueError(f"User not found: {user_id}")
        item = raw[0]
        return {
            "user_id": item.get("userId") or item.get("id", user_id),
            "nickname": item.get("nickname") or item.get("name", ""),
            "desc": item.get("desc") or item.get("description", ""),
            "followers": item.get("fansCount") or item.get("followers", 0),
            "following": item.get("followingCount") or item.get("following", 0),
            "total_likes": item.get("likedCount") or item.get("totalLikes", 0),
            "note_count": item.get("noteCount") or item.get("notes", 0),
            "avatar": item.get("avatar") or item.get("image", ""),
            "url": item.get("url") or f"https://www.xiaohongshu.com/user/profile/{user_id}",
            "raw": item,
        }

    def get_user_notes(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        raw = self._run_actor({"userIds": [user_id], "maxItems": limit})
        notes = []
        for item in raw:
            notes.append({
                "note_id": item.get("noteId") or item.get("id", ""),
                "title": item.get("title", ""),
                "likes": item.get("likedCount") or item.get("likes", 0),
                "collects": item.get("collectedCount") or item.get("collects", 0),
                "comments": item.get("commentCount") or item.get("comments", 0),
                "created_at": item.get("time") or item.get("createdAt", ""),
            })
        return {"user_id": user_id, "count": len(notes), "notes": notes[:limit]}

    def get_hot_topics(self, category: Optional[str] = None) -> Dict[str, Any]:
        input_data = {"maxItems": 50}
        if category:
            input_data["searchKeyword"] = category
        raw = self._run_actor(input_data)
        topics = []
        for item in raw:
            topics.append({
                "title": item.get("title") or item.get("keyword", ""),
                "heat": item.get("heat") or item.get("count", 0),
                "category": item.get("category", ""),
            })
        return {"category": category or "全部", "count": len(topics), "topics": topics}
