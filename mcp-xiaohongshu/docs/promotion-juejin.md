# 推广文章：掘金

# 从零开始写一个 MCP Server：小红书数据查询实战

## 前言

MCP（Model Context Protocol）是 Anthropic 提出的标准协议，让大模型能调用外部工具。你可以把它理解为 AI 时代的 USB 接口——你做的 MCP Server 就是一个插件，让 AI 能调用你提供的能力。

本文分享我从零开始开发一个小红书数据 MCP Server 的完整过程，包括技术选型、架构设计、踩坑经验。

## 你能得到什么

- 理解 MCP 协议的核心概念（Client/Server/Tool/Resource）
- 学会手写 JSON-RPC 2.0 实现 MCP Server（不依赖 SDK）
- 了解可插拔数据源架构设计
- 直接跑通一个完整项目

## 项目效果

接入 Claude Desktop 后，直接用自然语言查询小红书数据：

```
用户：帮我搜一下小红书上关于"日本旅游"的热门笔记
Claude：[调用 search_notes tool，返回结构化数据]
```

## 技术架构

```
Claude Desktop / Cursor / Codex
        ↓ JSON-RPC 2.0 (stdio)
    MCP Server (server.py)
        ↓
    数据源抽象层 (providers/base.py)
        ↓           ↓           ↓
    SampleData   ApifyData   HttpData
    (本地测试)    (真实数据)   (第三方API)
```

### 核心设计决策

**1. 手写 JSON-RPC，不依赖 MCP SDK**

原因：MCP SDK 需要安装依赖，而手写实现只需要 Python 标准库，200 行代码即可。

```python
# 核心路由逻辑
def handle_request(self, request):
    method = request.get("method")
    if method == "initialize":
        return self._initialize(request_id)
    if method == "tools/list":
        return self._tools_list(request_id)
    if method == "tools/call":
        return self._tools_call(request_id, params)
```

**2. 可插拔数据源**

所有数据获取逻辑抽象为 `XhsDataSource` 接口，不同数据源只需实现同一套方法：

```python
class XhsDataSource(ABC):
    @abstractmethod
    def search_notes(self, keyword, limit, sort): ...
    @abstractmethod
    def get_note_detail(self, note_id): ...
    @abstractmethod
    def get_user_profile(self, user_id): ...
```

切换数据源只需一行环境变量：
```bash
MCP_XHS_PROVIDER=apify python server.py
```

**3. 5 个 Tool 覆盖核心场景**

| Tool | 用途 |
|------|------|
| search_notes | 关键词搜索笔记 |
| get_note_detail | 获取笔记详情 |
| get_user_profile | 获取用户主页信息 |
| get_user_notes | 获取用户笔记列表 |
| get_hot_topics | 获取热门话题 |

## 快速体验

```bash
git clone https://github.com/NanGongZheng/mcp-xiaohongshu.git
cd mcp-xiaohongshu
python server.py
```

接入 Claude Desktop 的配置：
```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

## 踩坑记录

1. **MCP SDK 网络问题**：pip install 超时，最终决定手写 JSON-RPC，反而更轻量
2. **数据源抽象**：一开始把数据获取逻辑写死在 server.py 里，后来重构为 provider 模式，扩展性好很多
3. **参数校验**：JSON Schema 验证是必须的，否则 AI 传过来的参数经常缺字段

## 后续计划

- 接入 Apify 真实数据源
- 支持评论分析、笔记全文提取
- 批量查询 + 数据导出
- 性能优化（缓存、并发）

## 总结

MCP Server 的开发门槛不高，核心就是实现 JSON-RPC 2.0 协议 + 定义 Tool Schema。关键是选好方向——做小而精的垂直场景，而不是大而全的通用工具。

项目开源地址：https://github.com/NanGongZheng/mcp-xiaohongshu

欢迎 Star / Issue / PR 🙏

---

**标签**：MCP、大模型、Python、开源、AI工具
