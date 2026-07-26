# 2026-07-26 产品定义与 Harness

## 完成内容

- 将用户需求整理为 `docs/product/PRD_v0.1.md`。
- 建立学习科学证据与适用边界文档。
- 按 Harness Armor v1 规范建立工程知识地图。
- 设计 skill-first、本地优先、证据优先的建议架构。
- 定义开发分支与稳定发布分支治理要求。

## 验证结果

- `python3 ../harness-armor/skills/harness-build/scripts/validate_harness_structure.py .`
  已运行并在治理决策写入后复验：`valid: true`，manifest `valid: true`，
  结构问题 0，本地引用 41 个、失效引用 0。
- 三个 `.harness/*.json` 已分别通过 `python3 -m json.tool` 解析。
- 已扫描合并冲突标记与常见未完成占位词：未发现命中。
- 已创建 `atlax-tech/kongzi-ai-mentor-skills`，默认分支为 `dev`。
- GitHub Free 不支持 private 仓库保护；凭证模式扫描无命中后，仓库已公开，
  决策见 `docs/decisions/0001-public-repository-for-protected-main.md`。
- `main` 保护 API 读回：PR 必须、管理员受限、线性历史与评论解决开启、
  force push 和删除关闭。
- 直推探针被 GitHub 以 `GH006` 与
  `Changes must be made through a pull request` 拒绝；远端 `main` 未改变。

## 限制与未验证项

- 没有产品业务代码、安装器、依赖清单或测试运行器。
- 没有声称 cangjie、video-downloader、nuwa 或 Darwin 已完成运行时接入。
- 提醒适配器、状态 schema、首个学习主题仍待后续决策。

## 人工验收步骤

1. 阅读 PRD，抽查原始需求是否都映射为可验收条目。
2. 抽查学习科学文档中的 DOI 和产品边界。
3. 运行 Harness 结构校验并记录实际输出。
4. 检查 GitHub `main` 保护和 `dev` 默认开发分支。
5. 尝试通过普通 push 更新 `main`，确认 GitHub 返回 protected-branch 拒绝。
