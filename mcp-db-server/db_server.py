#!/usr/bin/env python3
"""
MCP Database Query Server
基于 MCP 协议的数据库查询服务器

核心功能：
1. list_tables - 列出数据库中所有表
2. describe_table - 查看指定表的结构
3. query - 执行只读 SQL 查询

安全措施：
- 仅允许 SELECT 语句
- 查询行数上限 100 行
- 查询超时控制 10 秒
"""

import json
import sys
import sqlite3
import re
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from contextlib import contextmanager

# MCP 协议版本
MCP_PROTOCOL_VERSION = "2025-11-25"
JSONRPC_VERSION = "2.0"

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "sample.db")

@dataclass
class MCPTool:
    """MCP Tool 定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_sample_db()
    
    def _init_sample_db(self):
        """初始化示例数据库"""
        # 如果数据库文件已存在，检查是否有数据
        if os.path.exists(self.db_path):
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] > 0:
                    return  # 数据库已有数据，跳过初始化
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建示例表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    product TEXT NOT NULL,
                    amount DECIMAL(10,2),
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 插入示例数据
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    (1, '张三', 'zhangsan@example.com', 28),
                    (2, '李四', 'lisi@example.com', 32),
                    (3, '王五', 'wangwu@example.com', 25),
                    (4, '赵六', 'zhaoliu@example.com', 35),
                    (5, '钱七', 'qianqi@example.com', 29),
                ]
                cursor.executemany(
                    "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
                    sample_users
                )
                
                sample_orders = [
                    (1, 1, 'iPhone 15', 7999.00, 'completed'),
                    (2, 1, 'MacBook Pro', 14999.00, 'pending'),
                    (3, 2, 'iPad Air', 4799.00, 'completed'),
                    (4, 3, 'AirPods Pro', 1899.00, 'shipped'),
                    (5, 4, 'Apple Watch', 2999.00, 'pending'),
                    (6, 5, 'iPhone 15', 7999.00, 'completed'),
                    (7, 2, 'MacBook Air', 9999.00, 'pending'),
                    (8, 3, 'iPad Pro', 8999.00, 'shipped'),
                ]
                cursor.executemany(
                    "INSERT INTO orders (id, user_id, product, amount, status) VALUES (?, ?, ?, ?, ?)",
                    sample_orders
                )
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def list_tables(self) -> List[str]:
        """列出所有表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row['name'] for row in cursor.fetchall()]
    
    def describe_table(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        # 防止 SQL 注入
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not cursor.fetchone():
                raise ValueError(f"Table '{table_name}' does not exist")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "cid": row['cid'],
                    "name": row['name'],
                    "type": row['type'],
                    "notnull": bool(row['notnull']),
                    "default_value": row['dflt_value'],
                    "primary_key": bool(row['pk'])
                })
            
            return columns
    
    def execute_query(self, sql: str, params: Optional[List] = None) -> Dict[str, Any]:
        """执行只读 SQL 查询"""
        # 安全检查：只允许 SELECT 语句
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Only SELECT statements are allowed")
        
        # 禁止危险操作
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Dangerous keyword '{keyword}' detected")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 设置查询超时（10秒）
            cursor.execute("PRAGMA busy_timeout = 10000")
            
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # 限制返回行数
                rows = cursor.fetchmany(100)
                
                # 获取列名
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # 转换为字典列表
                result = []
                for row in rows:
                    result.append(dict(row))
                
                return {
                    "columns": columns,
                    "rows": result,
                    "row_count": len(result),
                    "truncated": len(result) == 100
                }
            
            except sqlite3.Error as e:
                raise ValueError(f"SQL Error: {str(e)}")

class MCPServer:
    """MCP 服务器"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[MCPTool]:
        """注册 MCP 工具"""
        return [
            MCPTool(
                name="list_tables",
                description="列出数据库中所有表",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="describe_table",
                description="查看指定表的结构（字段、类型、索引）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "表名"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            MCPTool(
                name="query",
                description="执行只读 SQL 查询并返回结果（仅允许 SELECT 语句）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL 查询语句（仅 SELECT）"
                        },
                        "params": {
                            "type": "array",
                            "description": "查询参数（可选）",
                            "items": {
                                "type": ["string", "number", "null"]
                            }
                        }
                    },
                    "required": ["sql"]
                }
            )
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理 JSON-RPC 请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return self._handle_initialize(params, request_id)
            elif method == "tools/list":
                return self._handle_tools_list(params, request_id)
            elif method == "tools/call":
                return self._handle_tools_call(params, request_id)
            elif method == "notifications/initialized":
                return None  # 通知不需要响应
            else:
                return self._create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
        
        except Exception as e:
            return self._create_error_response(
                request_id,
                -32603,
                str(e)
            )
    
    def _handle_initialize(self, params: Dict, request_id: Any) -> Dict:
        """处理初始化请求"""
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mcp-db-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, params: Dict, request_id: Any) -> Dict:
        """处理工具列表请求"""
        tools = []
        for tool in self.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    def _handle_tools_call(self, params: Dict, request_id: Any) -> Dict:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "list_tables":
                result = self.db_manager.list_tables()
                return self._create_tool_result(request_id, result)
            
            elif tool_name == "describe_table":
                table_name = arguments.get("table_name")
                if not table_name:
                    raise ValueError("Missing required parameter: table_name")
                result = self.db_manager.describe_table(table_name)
                return self._create_tool_result(request_id, result)
            
            elif tool_name == "query":
                sql = arguments.get("sql")
                if not sql:
                    raise ValueError("Missing required parameter: sql")
                query_params = arguments.get("params")
                result = self.db_manager.execute_query(sql, query_params)
                return self._create_tool_result(request_id, result)
            
            else:
                return self._create_error_response(
                    request_id,
                    -32602,
                    f"Unknown tool: {tool_name}"
                )
        
        except ValueError as e:
            return self._create_error_response(
                request_id,
                -32602,
                str(e)
            )
    
    def _create_tool_result(self, request_id: Any, result: Any) -> Dict:
        """创建工具执行结果"""
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> Dict:
        """创建错误响应"""
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

def main():
    """主函数：从 stdin 读取 JSON-RPC 请求"""
    server = MCPServer()
    
    # 输出到 stderr 用于调试
    print("MCP Database Server started", file=sys.stderr)
    print(f"Database path: {server.db_manager.db_path}", file=sys.stderr)
    print("Waiting for requests on stdin...", file=sys.stderr)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            
            if response is not None:
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
