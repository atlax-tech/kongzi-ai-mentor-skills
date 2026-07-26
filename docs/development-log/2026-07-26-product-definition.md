# 2026-07-26 产品定义与 Harness

## 完成内容

- 将用户需求整理为 `docs/product/PRD_v0.1.md`。
- 建立学习科学证据与适用边界文档。
- 按 Harness Armor v1 规范建立工程知识地图。
- 设计 skill-first、本地优先、证据优先的建议架构。
- 定义开发分支与稳定发布分支治理要求。

## 验证结果

- `python3 ../harness-armor/skills/harness-build/scripts/validate_harness_structure.py .`
  已运行：`valid: true`，manifest `valid: true`，结构问题 0，本地引用
  37 个、失效引用 0。
- 三个 `.harness/*.json` 已分别通过 `python3 -m json.tool` 解析。
- 已扫描合并冲突标记与常见未完成占位词：未发现命中。
- GitHub 仓库与分支保护验证将在完成外部设置后另行记录，当前不得视为
  已通过。

## 限制与未验证项

- 没有产品业务代码、安装器、依赖清单或测试运行器。
- 没有声称 cangjie、video-downloader、nuwa 或 Darwin 已完成运行时接入。
- 提醒适配器、状态 schema、首个学习主题仍待后续决策。

## 人工验收步骤

1. 阅读 PRD，抽查原始需求是否都映射为可验收条目。
2. 抽查学习科学文档中的 DOI 和产品边界。
3. 运行 Harness 结构校验并记录实际输出。
4. 检查 GitHub `main` 保护和 `dev` 默认开发分支。
