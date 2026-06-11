# MCP 小红书数据 Server

基于 MCP 协议的小红书数据查询服务器，让 AI 能够搜索和分析小红书内容。

## 🎯 核心功能

### Tools（工具）

1. **search_notes** - 搜索小红书笔记
   - 参数：keyword（关键词）、limit（数量）、sort（排序方式）
   - 返回：笔记列表（标题、作者、点赞数、收藏数等）

2. **get_note_detail** - 获取笔记详情
   - 参数：note_id（笔记ID）
   - 返回：笔记完整内容、图片、评论等

3. **get_user_profile** - 获取用户主页信息
   - 参数：user_id（用户ID）
   - 返回：用户信息、粉丝数、笔记数等

4. **get_user_notes** - 获取用户的笔记列表
   - 参数：user_id（用户ID）、limit（数量）
   - 返回：用户发布的笔记列表

5. **get_hot_topics** - 获取热门话题
   - 参数：category（分类，可选）
   - 返回：当前热门话题和标签

### Resources（资源）

- `xhs://trending` - 小红书热门内容
- `xhs://categories` - 内容分类列表

## 🏗️ 技术方案

### 数据获取方式

**方案 A：第三方数据服务 / 聚合 API（当前推荐）**
- 优先接入第三方数据接口，快速验证产品价值
- 优点：落地快、维护成本低、适合 MVP
- 缺点：需评估供应商稳定性、成本与字段完整度

**方案 B：自建爬虫**
- 使用 Playwright/Selenium 模拟浏览器
- 优点：完全免费、可定制
- 缺点：需要处理反爬、维护成本高

**方案 C：第三方 API**
- 使用数据市场/聚合平台的小红书 API
- 优点：简单易用
- 缺点：可能不稳定、需要付费

### 技术栈

- Python 3.9+
- MCP Python SDK（或手写 JSON-RPC）
- Playwright（仅作为未来扩展备选）
- SQLite（数据缓存）

## 🔌 数据源 Provider

- `MCP_XHS_PROVIDER=sample`：本地示例数据，开发调试用
- `MCP_XHS_PROVIDER=apify`：Apify Actor，适合付费验证真实数据
- `MCP_XHS_PROVIDER=http`：通用 HTTP API / 第三方聚合网关，适合 MVP 快速接入

详细文档见：`docs/data-providers.md`


> 任务A已完成，最终结论：MVP 阶段优先采用「第三方数据服务 + 官方平台补充调研」策略，不建议首发就以自建爬虫为主链路。
>
> 详见：`mcp-xiaohongshu/数据获取方案调研报告.md`

## ✅ 当前进展（Task B 执行记录）

- **B1 框架搭建**：已完成（JSON-RPC 2.0 MCP 框架 + stdio 启动 + `initialize/tools/list/tools/call` 链路）
- **B2 search_notes**：已完成，支持关键词/排序/数量参数
- **B3 get_note_detail**：已完成，返回笔记详情+作者信息+URL
- **B4 get_user_profile**：已完成，返回粉丝数/获赞数/笔记数等
- **B5 get_user_notes**：已完成，返回用户笔记列表
- **B6 get_hot_topics**：已完成，支持按分类筛选热门话题
- **数据源抽象**：已创建 `providers/` 接口层，支持 sample（默认）和 apify 两种数据源，切换只需设置 `MCP_XHS_PROVIDER` 环境变量
- **测试**：`tests/test_server.py` 覆盖 B1-B6 全部工具，全部通过 ✅

> 框架 + 全部 5 个 Tool 已就绪。下一步是接入真实小红书数据源（Apify / 自建爬虫）。

## 📋 开发计划

### Phase 1：基础框架（1-2天）
- [ ] 设计数据模型
- [ ] 实现 MCP Server 框架
- [ ] 实现 search_notes 功能

### Phase 2：核心功能（3-5天）
- [ ] 实现 get_note_detail
- [ ] 实现 get_user_profile
- [ ] 实现 get_user_notes
- [ ] 数据缓存机制

### Phase 3：高级功能（6-7天）
- [ ] 实现 get_hot_topics
- [ ] 数据分析和统计
- [ ] 批量查询支持

### Phase 4：优化和发布（8-14天）
- [ ] 性能优化
- [ ] 错误处理
- [ ] 文档完善
- [ ] 发布到 GitHub

## 🔧 使用示例

### 搜索笔记

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

### 获取笔记详情

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_note_detail",
    "arguments": {
      "note_id": "6572f123000000001d02xxxx"
    }
  }
}
```

## 💰 变现路径

1. **开源基础版** - 吸引用户
2. **高级功能付费** - 批量查询、数据分析、导出报告
3. **SaaS 月费** - 托管版，按月收费
4. **定制开发** - 为企业定制功能

## 📚 参考资源

- [小红书开放平台](https://open.xiaohongshu.com/)
- [Apify 小红书爬虫](https://apify.com/)
- [MCP 官方文档](https://modelcontextprotocol.io)

## 📄 许可证

MIT License
