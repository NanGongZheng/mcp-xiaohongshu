#!/usr/bin/env python3
"""
测试 MCP Database Server
"""

import json
import subprocess
import sys

def send_request(server_process, request):
    """发送请求到服务器"""
    request_json = json.dumps(request)
    server_process.stdin.write(request_json + "\n")
    server_process.stdin.flush()
    
    # 读取响应
    response_line = server_process.stdout.readline()
    if response_line:
        return json.loads(response_line)
    return None

def main():
    """测试服务器"""
    print("启动 MCP Database Server...")
    
    # 启动服务器进程
    server_process = subprocess.Popen(
        [sys.executable, "db_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 测试 1: 初始化
        print("\n1. 测试初始化...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_request(server_process, init_request)
        print(f"初始化响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试 2: 获取工具列表
        print("\n2. 测试获取工具列表...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_request(server_process, tools_request)
        print(f"工具列表响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试 3: 调用 list_tables 工具
        print("\n3. 测试调用 list_tables 工具...")
        list_tables_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_tables",
                "arguments": {}
            }
        }
        
        response = send_request(server_process, list_tables_request)
        print(f"list_tables 响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试 4: 调用 describe_table 工具
        print("\n4. 测试调用 describe_table 工具...")
        describe_table_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "describe_table",
                "arguments": {
                    "table_name": "users"
                }
            }
        }
        
        response = send_request(server_process, describe_table_request)
        print(f"describe_table 响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试 5: 调用 query 工具
        print("\n5. 测试调用 query 工具...")
        query_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {
                    "sql": "SELECT * FROM users WHERE age > 28"
                }
            }
        }
        
        response = send_request(server_process, query_request)
        print(f"query 响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试 6: 安全检查 - 尝试执行 INSERT 语句
        print("\n6. 测试安全检查 - 尝试执行 INSERT 语句...")
        unsafe_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {
                    "sql": "INSERT INTO users (name, email) VALUES ('test', 'test@example.com')"
                }
            }
        }
        
        response = send_request(server_process, unsafe_request)
        print(f"安全检查响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
    
    finally:
        # 关闭服务器
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
