# 快速开始指南

本指南帮助你在 5 分钟内跑通 MCP 小红书数据 Server。

## 前置条件

- Python 3.9+
- Claude Desktop / Cursor / Codex（任意 MCP 客户端）

## 第一步：运行 Server

```bash
cd mcp-xiaohongshu
python server.py
```

看到以下输出说明启动成功：

```
MCP XHS Server started (provider=SampleDataSource)
Waiting for JSON-RPC requests on stdin...
```

## 第二步：连接客户端

### Claude Desktop

编辑配置文件（macOS）：
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

添加：
```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python",
      "args": ["/你的绝对路径/mcp-xiaohongshu/server.py"]
    }
  }
}
```

重启 Claude Desktop，在对话中即可使用小红书数据工具。

### Cursor

在项目根目录创建 `.cursor/mcp.json`：
```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python",
      "args": ["/你的绝对路径/mcp-xiaohongshu/server.py"]
    }
  }
}
```

## 第三步：测试

在 Claude Desktop 中输入：

> 帮我搜索小红书上关于"护肤"的热门笔记

Claude 会自动调用 `search_notes` 工具并返回结果。

## 第四步：接入真实数据（可选）

1. 注册 [Apify](https://console.apify.com) 账号
2. 获取 API Token
3. 设置环境变量运行：

```bash
MCP_XHS_PROVIDER=apify \
APIFY_API_TOKEN=你的token \
python server.py
```

## 常见问题

### Q: 启动报错 `ModuleNotFoundError: No module named 'providers'`

确保在 `mcp-xiaohongshu` 目录下运行，或使用绝对路径。

### Q: Claude Desktop 连接不上

1. 检查配置文件路径是否正确
2. 检查 `args` 中的路径是否为绝对路径
3. 重启 Claude Desktop

### Q: 如何切换数据源？

设置环境变量 `MCP_XHS_PROVIDER`：
- `sample`（默认）：示例数据
- `apify`：Apify 真实数据
- `http`：通用 HTTP API
