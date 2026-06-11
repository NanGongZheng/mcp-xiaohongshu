"""数据源工厂：根据环境变量选择数据源。"""

import os
from .base import XhsDataSource


def create_datasource() -> XhsDataSource:
    """根据环境变量 MCP_XHS_PROVIDER 创建对应的数据源。

    可选值：
      - sample  （默认）使用本地示例数据
      - apify   使用 Apify Actor 获取真实数据
      - http    使用通用 HTTP API / 第三方聚合网关
    """
    provider = os.environ.get("MCP_XHS_PROVIDER", "sample").lower()

    if provider == "apify":
        from .apify import ApifyDataSource
        return ApifyDataSource()

    if provider in ("http", "api", "remote"):
        from .http import HttpDataSource
        return HttpDataSource()

    # 默认使用示例数据
    from .sample import SampleDataSource
    return SampleDataSource()
