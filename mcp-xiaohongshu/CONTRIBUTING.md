# 贡献指南

感谢你对 MCP 小红书数据 Server 的关注！

## 开发环境

```bash
git clone https://github.com/yourname/mcp-xiaohongshu.git
cd mcp-xiaohongshu
python -m venv venv
source venv/bin/activate
```

## 运行测试

```bash
python tests/test_server.py
```

## 添加新 Tool

1. 在 `providers/base.py` 的 `XhsDataSource` 中添加抽象方法
2. 在 `providers/sample.py` 中实现示例版本
3. 在 `providers/apify.py` 和 `providers/http.py` 中实现真实版本
4. 在 `server.py` 的 `ALL_TOOLS` 中注册 Tool 定义
5. 在 `server.py` 的 `_dispatch()` 中添加路由
6. 在 `tests/test_server.py` 中添加测试用例

## 添加新数据源

1. 在 `providers/` 下新建文件，继承 `XhsDataSource`
2. 实现所有抽象方法
3. 在 `providers/__init__.py` 的 `create_datasource()` 中注册
4. 添加对应测试

## 代码风格

- Python 3.9+ 兼容
- 使用 type hints
- 函数和变量用 snake_case
- 类名用 PascalCase
- 提交前确保测试通过

## 提交规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
test: 测试相关
refactor: 重构
chore: 其他
```

## Issue 和 PR

- Bug 报告请提供复现步骤和错误日志
- Feature Request 请说明使用场景
- PR 请确保测试通过并更新相关文档
