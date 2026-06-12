# [开源] mcp-xiaohongshu：让 AI 直接搜索和分析小红书数据的 MCP Server

## 项目地址
https://github.com/NanGongZheng/mcp-xiaohongshu

## 一句话介绍
一个基于 MCP 协议的小红书数据查询服务器，接入 Claude / Cursor 后，你可以直接用自然语言搜索小红书笔记、查看用户主页、获取热门话题。

## 能做什么

用 Claude Desktop 直接对话：

> "帮我搜一下小红书上关于'日本旅游'的热门笔记"
> "看看用户 u_skin_wei 的主页信息"
> "现在小红书上护肤类有什么热门话题"

AI 会自动调用对应的 MCP Tool 并返回结构化数据。

## 核心功能

| Tool | 说明 |
|------|------|
| `search_notes` | 搜索笔记（支持按热度/时间排序） |
| `get_note_detail` | 获取笔记详情 |
| `get_user_profile` | 获取用户主页信息 |
| `get_user_notes` | 获取用户笔记列表 |
| `get_hot_topics` | 获取热门话题（支持分类筛选） |

## 技术亮点

- **可插拔数据源架构**：内置 sample（开发测试）、Apify（真实数据）、HTTP（第三方API）三种 provider，一行环境变量切换
- **MCP 标准协议**：兼容所有 MCP 客户端（Claude Desktop、Cursor、Codex）
- **手写 JSON-RPC 2.0**：不依赖 MCP SDK，纯 Python 标准库实现，零依赖
- **Type hints 全覆盖**

## 5 分钟跑通

```bash
git clone https://github.com/NanGongZheng/mcp-xiaohongshu.git
cd mcp-xiaohongshu
python server.py  # 示例数据，无需配置
```

接入真实数据：
```bash
MCP_XHS_PROVIDER=apify APIFY_API_TOKEN=xxx python server.py
```

## 适合谁

- 想用 AI 分析小红书内容的运营/营销同学
- 想了解 MCP 协议怎么写 Server 的开发者
- 想在 AI 时代占流量入口位的创业者

## 后续计划

- 接入真实数据源（Apify / 第三方API）
- 支持评论分析、笔记内容全文提取
- 批量查询 + 数据导出

欢迎 Star / Issue / PR 🙏
