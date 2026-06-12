# MCP 创业项目进度快照

> 最后更新：2026-06-12
> GitHub：https://github.com/NanGongZheng/mcp-xiaohongshu

## 总体进度

| 任务组 | 状态 | 说明 |
|--------|------|------|
| A 数据获取调研 | ✅ 完成 | Apify/自建爬虫/第三方API 方案评估，结论：MVP优先用第三方API |
| B 核心功能 | ✅ 完成 | B1框架 + B2-B6 全部5个Tool + 数据源抽象层 + 测试 |
| C 文档测试 | ✅ 完成 | README + QUICKSTART + CONTRIBUTING + 单元测试 |
| D1 GitHub发布 | ✅ 完成 | 仓库已上线，已推送4个commit |
| D2 社区推广 | 🟡 文案就绪 | 4份推广文案已备好，待实际发帖 |
| D3 用户反馈 | 📋 待做 | Issue模板/Discussion 待创建 |

## 已完成的代码

```
mcp-xiaohongshu/
├── server.py              # MCP Server 主程序（JSON-RPC 2.0 / stdio）
├── providers/
│   ├── base.py            # 数据源抽象接口（XhsDataSource ABC）
│   ├── sample.py          # 示例数据源（开发测试用）
│   ├── apify.py           # Apify 数据源（真实数据）
│   └── http.py            # 通用 HTTP API 数据源
├── data/                  # 示例数据（notes/users/topics）
├── tests/test_server.py   # B1-B6 全量测试（7用例全绿）
├── docs/                  # 文档 + 推广文案
├── README.md              # 生产级文档
├── QUICKSTART.md          # 快速开始教程
└── CONTRIBUTING.md        # 贡献指南
```

## 5 个 MCP Tool

| Tool | 说明 | 数据源支持 |
|------|------|-----------|
| search_notes | 搜索笔记 | sample ✅ / apify ✅ / http ✅ |
| get_note_detail | 笔记详情 | sample ✅ / apify ✅ / http ✅ |
| get_user_profile | 用户主页 | sample ✅ / apify ✅ / http ✅ |
| get_user_notes | 用户笔记列表 | sample ✅ / apify ✅ / http ✅ |
| get_hot_topics | 热门话题 | sample ✅ / apify ✅ / http ✅ |

## 下一步行动（按优先级）

### 1. D2 社区推广（立即可做）
- [ ] 发 awesome-mcp-servers PR（文案：`docs/promotion-awesome-mcp.md`）
- [ ] 发 V2EX 帖子（文案：`docs/promotion-v2ex.md`）
- [ ] 发掘金文章（文案：`docs/promotion-juejin.md`）
- [ ] 发即刻动态（文案：`docs/promotion-jike.md`）

### 2. D3 用户反馈（D2 发帖后）
- [ ] 创建 GitHub Issue 模板
- [ ] 创建 Discussion 讨论区
- [ ] 收集用户反馈并整理需求

### 3. 真实数据源接入（D2/D3 后）
- [ ] 获取 Apify API Token，用真实数据跑通 search_notes → get_note_detail 链路
- [ ] 补齐 B3 图片和评论提取
- [ ] 补齐 B4 缓存机制
- [ ] 补齐 B5 分页/排序
- [ ] 补齐 B6 更新频率控制

### 4. 后续拓展
- [ ] 支持抖音数据（扩展为小红书+抖音双平台）
- [ ] 高级功能：批量查询、数据导出、趋势分析
- [ ] SaaS 托管版探索

## Git 提交记录

```
d2b067e D2准备: 推广文案(V2EX/即刻/掘金/awesome-mcp-servers)
e331fe9 D1完成: GitHub仓库已发布
95802ec 添加 .gitignore 和 MIT LICENSE
508e1c7 Task C完成: 重写README + QUICKSTART教程 + CONTRIBUTING指南
78c4373 更新TODO: 标记B1-B6已完成
750299e 完成 Task B: 框架(B1) + 全部5个Tool(B2-B6) + 数据源抽象层 + 测试
```

## 关键决策记录

1. **技术方案**：手写 JSON-RPC 2.0（不依赖 MCP SDK），零外部依赖
2. **数据源架构**：可插拔 Provider 模式，一行环境变量切换数据源
3. **MVP 策略**：先用示例数据验证框架，再接入真实数据
4. **主攻方向**：小红书数据 MCP Server（市场空白 + 高价值 + 可变现）
