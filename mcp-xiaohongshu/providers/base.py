from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class XhsDataSource(ABC):
    """小红书数据源抽象接口

    所有数据源（示例数据、Apify、自建爬虫）都实现此接口。
    替换数据源时只需替换 provider 实例，无需改动 server 逻辑。
    """

    @abstractmethod
    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort: str = "relevance",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """搜索笔记
        Returns: {"keyword": str, "sort": str, "count": int, "notes": list}
        """
        ...

    @abstractmethod
    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        """获取笔记详情
        Returns: 完整笔记信息 dict
        """
        ...

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户主页信息
        Returns: 用户信息 dict
        """
        ...

    @abstractmethod
    def get_user_notes(
        self, user_id: str, limit: int = 10
    ) -> Dict[str, Any]:
        """获取用户笔记列表
        Returns: {"user_id": str, "count": int, "notes": list}
        """
        ...

    @abstractmethod
    def get_hot_topics(
        self, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取热门话题
        Returns: {"category": str, "topics": list}
        """
        ...
