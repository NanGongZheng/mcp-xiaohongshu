# 数据源 Provider 指南

本项目采用 **可插拔数据源** 架构，切换数据源时只需设置环境变量，无需改动 MCP Server 核心逻辑。

## 当前支持的数据源

| 数据源 | 说明 | 适合阶段 |
|---|---|---|
| `sample` | 本地示例数据，用于开发调试 | 开发/联调 |
| `apify` | 使用 Apify Actor 获取小红书真实数据 | 付费验证 |
| `http` | 通用 HTTP API / 第三方聚合网关 | MVP / 商业验证 |

## 环境变量

### 公共变量
- `MCP_XHS_PROVIDER`: `sample` / `apify` / `http`

### Apify 相关
- `APIFY_API_TOKEN`: 必填
- `APIFY_XHS_ACTOR_ID`: 可选，默认 `apify/xhs-scraper`

### HTTP 相关
- `MCP_XHS_API_BASE_URL`: 必填，API 根地址
- `MCP_XHS_API_KEY`: 可选，Bearer Token
- `MCP_XHS_SEARCH_PATH`: 可选，默认 `{base}/search`
- `MCP_XHS_NOTE_DETAIL_PATH`: 可选，默认 `{base}/note`
- `MCP_XHS_USER_PROFILE_PATH`: 可选，默认 `{base}/user`
- `MCP_XHS_USER_NOTES_PATH`: 可选，默认 `{base}/user/notes`
- `MCP_XHS_HOT_TOPICS_PATH`: 可选，默认 `{base}/topics`

## 运行示例

```bash
# 1. 使用示例数据
python server.py

# 2. 使用 Apify
MCP_XHS_PROVIDER=apify \
APIFY_API_TOKEN=xxx \
python server.py

# 3. 使用通用 HTTP API
MCP_XHS_PROVIDER=http \
MCP_XHS_API_BASE_URL=https://your-api.example.com \
python server.py
```

## 测试

```bash
python tests/test_server.py
python tests/test_http_provider.py
```

## 设计原则

1. Server 层只做 JSON-RPC 路由 + 参数校验
2. 数据获取逻辑全部放在 provider
3. 新数据源只需实现 `providers/base.py` 中的接口
4. 所有 provider 返回结构尽量保持统一，方便上层消费
