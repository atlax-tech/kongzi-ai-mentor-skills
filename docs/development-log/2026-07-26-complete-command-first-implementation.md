# 2026-07-26：完成 Kongzi 命令式学习闭环

## 本次完成

- 建立 `/Kongzi` 根路由与 8 个子 Skill：
  - start/profile；
  - sources；
  - roadmap；
  - study；
  - review；
  - progress/report；
  - mentor；
  - integrations。
- 落地 Python 3 标准库状态引擎：
  - Obsidian 初始化与现有 vault 入口；
  - 渐进式画像，自述与行为证据分离；
  - 多旅程隔离；
  - 本地 Markdown/TXT/HTML/EPUB/DOCX/PDF 和公开网页/PDF；
  - source → claim → locator 证据链；
  - 知识节点、前置依赖、Mermaid 知识图和周期计划；
  - 用户原始作答、rubric 评分、纠错、迁移证据；
  - 分知识类型掌握条件与间隔复习；
  - launchd/cron 提醒、自动日报和周日报；
  - 状态恢复、schema 检查、带逐文件哈希的学习包导出/导入。
- 完整 peer-skill 安装与发现：
  - Cangjie；
  - Nuwa；
  - Darwin；
  - video-downloader。
- 上游安装写入 `UPSTREAM.json`，记录仓库、子目录、commit 和安装时间。
- 制作 MIT License、Nuwa 风格 README、imagegen Hero 动图和真实 CLI Demo 动图。
- 建立 GitHub Actions `test` job 和公开发布 allowlist，确保 `main` 不携带内部 Harness/架构文档。

## 实际验证

### 自动测试

```text
python3 -m unittest discover -s tests -v
Ran 9 tests
OK
```

覆盖：

- 用户未输出时禁止结束会话；
- 节点必须关联 source-backed claim；
- procedure 节点需要两次延迟通过和应用证据才到 mastered；
- 计划会话完成状态写回；
- 日报重复生成不覆盖；
- mentor on/off 不修改事实和评分证据；
- 损坏 state/profile/queue 从事件日志恢复并保留 pre-repair 文件；
- 学习包跨 vault 导出/导入、哈希校验和路径重写；
- 发布包排除 `.harness/`、`AGENTS.md` 和 `docs/`。

### Skill 与安装

```text
quick_validate.py .
Skill is valid!

npx skills add . --list --full-depth
Found 9 skills
```

在临时项目中用 `npx skills add ... --skill kongzi --agent claude-code
--copy -y` 成功安装根 Skill，完整相对资源同时存在。

四个上游 Skill 在临时 Skills 目录完成真实安装。验证 commit：

| 上游 | commit |
|---|---|
| kangarooking/cangjie-skill | `355dd47a97eeb87d249bf7d32aab561405b6de76` |
| alchaincyf/nuwa-skill | `72857dc720f4d1dd3e68a40a544341dfc65ea33e` |
| alchaincyf/darwin-skill | `7c7b7909b630dc3b5cbb91bd4bcb1b10bfb1f894` |
| kangarooking/kangarooking-skills | `fb327e91bf4f1887a63c3143cb2223b6b09e5185` |

### 权威网页抓取

通过 Kongzi 抓取 PubMed 论文页面：

```text
URL: https://pubmed.ncbi.nlm.nih.gov/16719566/
HTTP: 200
characters: 6577
sha256: 06778233da85e4042d0dbb265e2e81698c50a4fee0eed1557769d0d22883c36f
doctor: healthy
```

第一次 Python TLS 连接被提前断开后，补充三次重试与 `curl` 自动回退；同一页面随后成功。

### 视频上游

通过 Kongzi 调用真实 video-downloader，对 YouTube
`jNQXAC9IVRw` 完成 metadata-only 路径：

```text
returncode: 0
artifacts:
  youtube-jNQXAC9IVRw/metadata.json
  youtube-jNQXAC9IVRw/post_caption.txt
registered_source: true
```

并根据上游真实 CLI 将参数从错误的 `--asr-backend` 修正为 `--asr`。

### Dogfood

在临时 Obsidian vault 完成：

```text
init → profile → source → claim → node → map → plan →
session start → learner answer → grade → finish →
daily report → weekly report → reminder definition → doctor
```

结果包含 Dashboard、Journey、Knowledge Map、Learning Plan、来源正文、
日报、周报和 append-only 事件。

## 尚需人工/外部证据

- Cangjie 五阶段、Nuwa 六维调研、Darwin 独立评委流程由 Agent 执行，
  当前已完成完整安装、prepare/import 契约与测试提示；首次真实学习内容触发时
  必须遵循各自完整 `SKILL.md`，不能用缩减流程替代。
- 视频 metadata-only 已实测；完整视频下载 + 本地 Whisper 和
  SiliconFlow 两条 ASR 路径仍需在用户提供实际视频时验证。
- 稳定发布还需从公开 allowlist 创建 PR、让 `test` 成为 `main` 必需检查，
  再确认 `main` 无内部 Harness/架构文档。

## 手工验收

1. 在新 Obsidian vault 运行 `/Kongzi`，逐题完成最小画像。
2. 添加一份本地资料和一份公开权威网页，抽查 source/claim/locator。
3. 完成一次学习会话，确认 Agent 等待真实作答才评分。
4. 在 disposable vault 将复习卡 due_at 调到过去，完成两次延迟复习和迁移题。
5. 运行 `report daily`、`report weekly`、`doctor`。
6. 导出学习包，导入另一个空 vault，确认来源路径已重写。
7. 打开 README Hero 和 Demo GIF。
8. 检查 release tree 不含 `.harness/`、`AGENTS.md`、`docs/`。

## 稳定发布结果

- 发布 PR：<https://github.com/atlax-tech/kongzi-ai-mentor-skills/pull/1>
- 合并 commit：`97e7d65f734281881d1c086a8de850d498bde480`
- Release：<https://github.com/atlax-tech/kongzi-ai-mentor-skills/releases/tag/v0.1.0>
- GitHub Actions `test`：PASS（16 秒）
- 远端默认分支：`main`
- `main` 必需检查：strict `test`
- `main` 保护：PR required、enforce admins、linear history、conversation
  resolution、force push disabled、deletion disabled
- 公开根目录仅包含 `.github`、`.gitignore`、LICENSE、README、SKILL、
  agents、assets、references、scripts、skills、tests。
- 公开检查：`AGENTS.md`、`.harness/`、`docs/ARCHITECTURE.md`、
  `docs/product/PRD_v0.1.md` 全部不存在。
