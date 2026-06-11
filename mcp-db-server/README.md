# MCP Database Query Server

基于 MCP 协议的数据库查询服务器，让 AI 能够安全地查询数据库。

## 🎯 核心功能

### 三个核心 Tool

1. **list_tables** - 列出数据库中所有表
2. **describe_table** - 查看指定表的结构（字段、类型、索引）
3. **query** - 执行只读 SQL 查询并返回结果

### 安全措施

- ✅ 仅允许 SELECT 语句，禁止增删改操作
- ✅ 查询行数上限 100 行
- ✅ 查询超时控制 10 秒
- ✅ SQL 注入防护（表名校验）
- ✅ 危险关键词检测

## 🚀 快速开始

### 1. 运行服务器

```bash
cd mcp-db-server
python3 db_server.py
```

服务器会监听 stdin 的 JSON-RPC 请求。

### 2. 测试服务器

```bash
python3 test_server.py
```

这会运行完整的测试套件，验证所有功能。

### 3. 集成到 Claude Desktop

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "database": {
      "command": "python3",
      "args": ["/path/to/mcp-db-server/db_server.py"]
    }
  }
}
```

配置文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### 4. 集成到 Cursor

在 Cursor 设置中添加 MCP Server：

```json
{
  "mcp": {
    "servers": {
      "database": {
        "command": "python3",
        "args": ["/path/to/mcp-db-server/db_server.py"]
      }
    }
  }
}
```

## 📖 使用示例

### 示例 1：列出所有表

**请求：**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_tables",
    "arguments": {}
  }
}
```

**响应：**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\"orders\", \"users\"]"
      }
    ]
  }
}
```

### 示例 2：查看表结构

**请求：**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "describe_table",
    "arguments": {
      "table_name": "users"
    }
  }
}
```

**响应：**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"cid\": 0, \"name\": \"id\", \"type\": \"INTEGER\", ...}, ...]"
      }
    ]
  }
}
```

### 示例 3：执行查询

**请求：**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "query",
    "arguments": {
      "sql": "SELECT * FROM users WHERE age > 28"
    }
  }
}
```

**响应：**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"columns\": [\"id\", \"name\", \"email\", \"age\", \"created_at\"], \"rows\": [...], \"row_count\": 3, \"truncated\": false}"
      }
    ]
  }
}
```

## 🗄️ 示例数据库

服务器自带一个示例数据库，包含两个表：

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 姓名 |
| email | TEXT | 邮箱（唯一） |
| age | INTEGER | 年龄 |
| created_at | TIMESTAMP | 创建时间 |

### orders 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID（外键） |
| product | TEXT | 产品名称 |
| amount | DECIMAL | 金额 |
| status | TEXT | 状态（pending/completed/shipped） |
| created_at | TIMESTAMP | 创建时间 |

## 🔧 连接自定义数据库

修改 `db_server.py` 中的 `DB_PATH` 变量：

```python
# 数据库路径
DB_PATH = "/path/to/your/database.db"
```

支持任何 SQLite 数据库文件。

## 🛡️ 安全说明

### 允许的操作
- ✅ SELECT 查询
- ✅ 聚合函数（COUNT, SUM, AVG 等）
- ✅ JOIN 操作
- ✅ 子查询
- ✅ LIMIT/OFFSET

### 禁止的操作
- ❌ INSERT
- ❌ UPDATE
- ❌ DELETE
- ❌ DROP
- ❌ ALTER
- ❌ CREATE
- ❌ TRUNCATE

## 📁 文件结构

```
mcp-db-server/
├── db_server.py      # MCP 服务器主程序
├── test_server.py    # 测试脚本
├── sample.db         # 示例数据库（自动生成）
└── README.md         # 本文件
```

## 🎓 学习资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)

## 📝 下一步

1. **连接真实数据库**：修改 DB_PATH 指向你的数据库
2. **添加更多 Tool**：如 count_rows、export_csv 等
3. **发布到 GitHub**：分享给社区
4. **集成到 AI 客户端**：在 Claude Desktop 或 Cursor 中使用

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
