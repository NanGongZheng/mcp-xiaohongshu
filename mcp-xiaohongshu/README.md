# MCP 小红书数据 Server

[![MCP](https://img.shields.io/badge/MCP-2025--11--25-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

让 AI 能够搜索和分析小红书内容的 MCP Server。接入 Claude Desktop、Cursor、Codex 等任意 MCP 客户端即可使用。

## 快速开始

### 1. 克隆并运行

```bash
git clone https://github.com/yourname/mcp-xiaohongshu.git
cd mcp-xiaohongshu

# 直接运行（使用内置示例数据，无需额外配置）
python server.py
```

### 2. 连接到 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-xiaohongshu/server.py"]
    }
  }
}
```

### 3. 连接到 Cursor

在项目根目录创建 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-xiaohongshu/server.py"]
    }
  }
}
```

### 4. 使用真实数据（可选）

```bash
# 方式一：Apify（推荐，稳定可靠）
MCP_XHS_PROVIDER=apify \
APIFY_API_TOKEN=your_token \
python server.py

# 方式二：通用 HTTP API
MCP_XHS_PROVIDER=http \
MCP_XHS_API_BASE_URL=https://your-api.example.com \
python server.py
```

## Tools（工具）

| 工具 | 说明 | 参数 |
|------|------|------|
| `search_notes` | 搜索小红书笔记 | `keyword`（必填）、`limit`、`sort` |
| `get_note_detail` | 获取笔记详情 | `note_id`（必填） |
| `get_user_profile` | 获取用户主页信息 | `user_id`（必填） |
| `get_user_notes` | 获取用户笔记列表 | `user_id`（必填）、`limit` |
| `get_hot_topics` | 获取热门话题 | `category`（可选） |

### search_notes

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_notes",
    "arguments": {
      "keyword": "日本旅游攻略",
      "limit": 10,
      "sort": "popularity"
    }
  }
}
```

**参数说明：**
- `keyword`（string，必填）：搜索关键词
- `limit`（int，可选）：返回数量上限，默认 10
- `sort`（string，可选）：排序方式，`relevance` | `popularity` | `latest`

**返回示例：**
```json
{
  "keyword": "日本旅游攻略",
  "sort": "popularity",
  "count": 2,
  "notes": [
    {
      "note_id": "6650a1c6000000001d00abcd",
      "title": "日本旅游攻略：东京7天路线推荐",
      "author": "旅行小鹿",
      "likes": 12893,
      "collects": 8754,
      "comments": 542,
      "tags": ["日本旅游", "东京", "旅行攻略"],
      "created_at": "2026-05-20"
    }
  ]
}
```

### get_note_detail

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_note_detail",
    "arguments": {
      "note_id": "6650a1c6000000001d00abcd"
    }
  }
}
```

### get_user_profile

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_user_profile",
    "arguments": {
      "user_id": "u_skin_wei"
    }
  }
}
```

### get_user_notes

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_user_notes",
    "arguments": {
      "user_id": "u_travel_deer",
      "limit": 5
    }
  }
}
```

### get_hot_topics

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_hot_topics",
    "arguments": {
      "category": "护肤"
    }
  }
}
```

## 项目结构

```
mcp-xiaohongshu/
├── server.py                  # MCP Server 主程序
├── providers/
│   ├── __init__.py            # 数据源工厂
│   ├── base.py                # 数据源抽象接口（XhsDataSource）
│   ├── sample.py              # 示例数据源（开发/测试用）
│   ├── apify.py               # Apify 数据源（真实数据）
│   └── http.py                # 通用 HTTP API 数据源
├── data/
│   ├── sample_notes.json      # 示例笔记数据
│   ├── sample_users.json      # 示例用户数据
│   └── sample_topics.json     # 示例热门话题
├── tests/
│   ├── test_server.py         # B1-B6 全量测试
│   └── test_http_provider.py  # HTTP Provider 测试
├── docs/
│   └── data-providers.md      # 数据源 Provider 详细指南
└── README.md                  # 本文件
```

## 数据源 Provider

| Provider | 说明 | 适合阶段 |
|----------|------|----------|
| `sample` | 本地示例数据 | 开发/测试 |
| `apify` | Apify Actor 获取真实数据 | 付费验证 |
| `http` | 通用 HTTP API / 第三方网关 | MVP / 商业验证 |

详细配置见 [`docs/data-providers.md`](docs/data-providers.md)。

**添加自定义数据源：**

1. 在 `providers/` 下新建文件，继承 `XhsDataSource`（`providers/base.py`）
2. 实现 5 个抽象方法：`search_notes`、`get_note_detail`、`get_user_profile`、`get_user_notes`、`get_hot_topics`
3. 在 `providers/__init__.py` 的 `create_datasource()` 中注册

## 开发

```bash
# 运行测试
python tests/test_server.py

# 手动测试 MCP 协议
printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | python server.py
```

## 安全设计

- 所有数据获取均通过 Provider 抽象层，Server 不直接访问网络
- 支持只读模式（仅查询，不写入）
- 参数校验：所有 Tool 参数均通过 JSON Schema 验证
- 无状态设计：不存储用户数据，不保留会话

## 变现路径

1. **开源基础版** — 吸引用户，建立社区
2. **高级功能付费** — 批量查询、数据分析、导出报告
3. **SaaS 月费** — 托管版，按月收费
4. **定制开发** — 为企业定制功能

## 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [小红书开放平台](https://open.xiaohongshu.com/)
- [Apify 小红书爬虫](https://apify.com/)

## 许可证

MIT License
