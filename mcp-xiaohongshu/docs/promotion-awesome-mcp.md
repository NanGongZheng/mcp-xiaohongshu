# awesome-mcp-servers 提交格式

提交到 https://github.com/punkpeye/awesome-mcp-servers

## PR 格式

在 README.md 的 "Social Media" 分类下添加：

```markdown
- [NanGongZheng/mcp-xiaohongshu](https://github.com/NanGongZheng/mcp-xiaohongshu) - MCP Server for querying Xiaohongshu (小红书) data: search notes, get user profiles, trending topics. Supports pluggable data sources (sample/Apify/HTTP API).
```

## PR 标题

```
Add mcp-xiaohongshu (Xiaohongshu data server)
```

## PR 描述

```
## What

MCP Server for querying Xiaohongshu (小红书) data - China's largest lifestyle social platform.

## Features

- `search_notes` - Search notes by keyword with sorting
- `get_note_detail` - Get note details
- `get_user_profile` - Get user profile info
- `get_user_notes` - Get user's note list
- `get_hot_topics` - Get trending topics by category

## Tech

- Python 3.9+
- Hand-written JSON-RPC 2.0 (no SDK dependency)
- Pluggable data sources: sample data / Apify / HTTP API
- Full type hints

## Link

https://github.com/NanGongZheng/mcp-xiaohongshu
```
