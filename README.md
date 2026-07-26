<div align="center">

# Kongzi.skill

<p align="center">
  <img src="assets/hero.gif" alt="Kongzi AI Mentor Hero Animation" />
  <br/>
  <sub>从一本资料，到一条真正学得会、记得住、用得出的个人学习路线</sub>
</p>

> *「学而时习之，不亦说乎」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green)](https://agentskills.io)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-blue)](https://skills.sh)
[![CI](https://github.com/atlax-tech/kongzi-ai-mentor-skills/actions/workflows/test.yml/badge.svg)](https://github.com/atlax-tech/kongzi-ai-mentor-skills/actions/workflows/test.yml)
[![Multi-Runtime](https://img.shields.io/badge/Runtime-Claude%20Code%20·%20Codex%20·%20Cursor%20·%20OpenClaw-blueviolet)](#安装)

<br>

**Kongzi 帮你把任意知识方向变成一套适合自己的学习路线：先录入资料，再构建知识地图；AI 像老师一样提问、等待你作答、纠错、安排复习，并把全过程保存在 Obsidian。**

<sub>基于开放的 [Agent Skills 协议](https://agentskills.io)，可在 Claude Code、Codex、Cursor、OpenClaw、Hermes Agent、Gemini CLI、OpenCode 等兼容 runtime 中运行。</sub>

<br>

不是再给你一份看起来很完整的课程表。<br>
Kongzi 先知道你要做到什么、现在会什么、每天有多少时间。<br>
然后让资料有出处、路线有依赖、学习有输出、掌握有延迟证据。

[看效果](#效果示例) · [安装](#安装) · [使用](#使用) · [它覆盖什么](#kongzi-覆盖什么) · [学习方法](#学习方法如何选择)

<br>

[English summary](#english)

</div>

---

## 效果示例

<p align="center">
  <img src="assets/demo.gif" alt="Kongzi real command flow demo" />
  <br/>
  <sub>动图由真实临时 Obsidian vault 和 Kongzi CLI 全流程生成</sub>
</p>

```
用户      ❯ /Kongzi 我想用 4 周学会 SQL，每天 30 分钟，完全没基础

Kongzi    ❯ 先不急着给课程表。我会为你保留学习状态，并先确定“学会”的标准。

            第一个问题：
            4 周后，你最希望能独立完成哪件事？
            A. 看懂并修改查询
            B. 从零分析一份业务数据
            C. 应付面试/考试
            D. 其他具体产出
```

```
用户      ❯ /Kongzi study

Kongzi    ❯ 今天的目标：不用提示，判断何时应该用 GROUP BY。

            先闭卷回答：
            有一张 orders 表，如何求每个客户的订单总额？
            请写出 SQL，并解释为什么需要 GROUP BY。

用户      ❯ SELECT customer_id, SUM(amount)
            FROM orders GROUP BY customer_id;
            因为要按客户分别聚合。

Kongzi    ❯ 已记录你的原始作答。

            准确度 0.92 · 提取 0.90 · 迁移 0.78
            核心正确。下一步只补一个缺口：当 SELECT 中加入非聚合列时，
            它必须进入 GROUP BY，或由数据库明确支持函数依赖。

            迁移题：如果要按客户和月份分别聚合，你会改哪两处？
```

```
用户      ❯ /Kongzi

Kongzi    ❯ 已恢复「SQL 业务分析」旅程。
            今天有 3 张复习卡到期，上次薄弱点是窗口函数与聚合的边界。

            唯一下一步：先完成 8 分钟延迟复习，再进入新节点。
```

Kongzi 不把“看懂了”当成“掌握了”。用户必须输出；即时作答、延迟复习和迁移应用分别保存。

---

## 安装

Kongzi 基于开放的 [Agent Skills](https://agentskills.io) 协议，可在任何 skills-compatible 的 AI agent runtime 中运行。

### 方式一：一行命令（推荐，跨 runtime）

打开你正在使用的 Agent（Claude Code、Codex、Cursor、OpenClaw、Hermes、Gemini CLI、OpenCode 等），告诉它：

```
帮我安装这个 skill：https://github.com/atlax-tech/kongzi-ai-mentor-skills
```

或者使用通用 CLI 安装器：

```bash
npx skills add atlax-tech/kongzi-ai-mentor-skills
```

它会自动识别当前 runtime 并把 Skill 放到正确目录。需要指定时加 `-a claude-code`、`-a codex`、`-a cursor` 或其他 runtime 参数。

安装 Kongzi 后，在 Agent 中输入：

```
/Kongzi integration 安装完整依赖
```

Kongzi 会安装 Cangjie、Nuwa、Darwin 和 video-downloader 四个完整上游 Skill。

### 方式二：手动安装

<details>
<summary>展开查看各 runtime 的 skills 目录</summary>

| Runtime | 安装路径 |
|---|---|
| Claude Code | `~/.claude/skills/kongzi/` |
| Codex CLI | `~/.codex/skills/kongzi/` |
| Cursor | `~/.cursor/skills/kongzi/` |
| OpenClaw | `~/.openclaw/workspace/skills/kongzi/` |
| 其他 runtime | clone 到对应 runtime 的 `skills/` 目录 |

```bash
git clone https://github.com/atlax-tech/kongzi-ai-mentor-skills <上面对应的路径>
cd <上面对应的路径>
python3 scripts/install_integrations.py --target <runtime的skills目录>
```

</details>

如果你主要在 Claude Code + Obsidian 中使用：

```bash
git clone https://github.com/atlax-tech/kongzi-ai-mentor-skills ~/.claude/skills/kongzi
python3 ~/.claude/skills/kongzi/scripts/install_integrations.py \
  --target ~/.claude/skills
```

### 方式三：作为参考资料使用

即使 runtime 不支持 Agent Skills 自动加载，也可以把 `SKILL.md` 内容交给 Agent，并直接运行：

```bash
python3 scripts/kongzi.py --help
```

核心状态引擎只依赖 Python 标准库。PDF 会自动使用 `pypdf` 或系统 `pdftotext`；视频转录由 video-downloader 调用 ffmpeg、Whisper 或 SiliconFlow。

---

### 使用

装好后，在你的 Obsidian vault 中打开 Claude Code、Codex 或其他 Agent，输入：

```
> /Kongzi
> /Kongzi 我想在 6 周内学会统计学，每天 40 分钟
> /Kongzi resume
```

录入资料：

```
> /Kongzi source 把这本 PDF 作为主资料
> /Kongzi source 抓取这篇官方文档
> /Kongzi source 把这个 Bilibili 视频下载、转录并用 Cangjie 蒸馏
```

学习与复习：

```
> /Kongzi roadmap
> /Kongzi study
> /Kongzi quiz
> /Kongzi review
> /Kongzi reminder 每天晚上 8 点提醒我
```

进度与导师：

```
> /Kongzi status
> /Kongzi report daily
> /Kongzi report weekly
> /Kongzi mentor 让 Richard Feynman 作为我的物理导师
> /Kongzi bundle 导出我的完整学习记录
```

输入 `/Kongzi` 永远会先读取本地状态：有未完成会话就继续，有到期复习就优先复习，否则给出唯一下一步。

---

## Kongzi 覆盖什么

| 能力 | Kongzi 会做什么 |
|---|---|
| **学习者画像** | 逐题访谈目标、基础、时间、限制、材料和过往阻力；把自述与真实表现分开 |
| **权威资料** | 接收本地文件，抓取公开网页，保存哈希、访问时间、来源等级和定位符 |
| **知识蒸馏** | 用 Cangjie 完整蒸馏书籍、长文和视频转录，保留候选、驳回、验证与测试记录 |
| **知识地图** | 按概念、事实、程序、心智模型、元认知拆节点，显式标注前置依赖 |
| **定制路线** | 根据目标、截止日期、每天时长和诊断结果制定周期与每次必须产出 |
| **老师式提问** | 先让用户闭卷输出，再记录、评分、纠错和追问迁移题 |
| **间隔复习** | 生成 1/3/7/14/30 天等自适应复习卡；低分缩短间隔并保留失败历史 |
| **掌握判断** | 即时高分只算“会做过”；延迟提取与应用都通过才标记掌握 |
| **Obsidian** | 保存来源、旅程、知识地图、计划、笔记、日报、周报与导师人格 |
| **迁移与恢复** | 导出带逐文件哈希的学习包；导入时校验并重写 vault 路径；损坏索引可从事件日志重建 |
| **系统提醒** | 生成 macOS launchd 或 cron 提醒；每次 `/Kongzi` 也会检查到期复习 |
| **导师人格** | 用 Nuwa 蒸馏公开人物的思维模型；人格决定风格，证据决定事实 |
| **持续进化** | 用 Darwin 的九维评分、基线与 ratchet 改进 Skill，不牺牲证据约束 |

### 诚实边界

- Kongzi 不是专业课程或教师资质的替代品，它负责降低搜索、组织、练习和复习成本。
- 没有录入或抓取到的资料，不会被伪装成权威知识。
- 搜索摘要、模型记忆和导师口吻都不能代替来源正文。
- “费曼学习法”适合暴露解释缺口，但不替代程序练习、反馈、延迟复习和真实项目。
- 学习偏好只作为便利与可访问性假设，不会把用户固定成某种“学习风格”。
- 视频平台访问失败时会保留真实错误并改用本地媒体入口，不会补写不存在的转录。

**一个不保存用户原始输出、不区分即时流畅与延迟掌握的学习 Skill，不值得信任。**

---

## 已集成能力

### 完整运行时集成

| Skill | 在 Kongzi 中的用途 | 项目 |
|---|---|---|
| **Cangjie.skill** | 书籍、论文、长文与转录的五阶段蒸馏、三重验证、原子知识与测试提示 | [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) |
| **Nuwa.skill** | 研究并蒸馏行业人物的 3–7 个思维模型、决策启发式和诚实边界 | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) |
| **Darwin.skill** | 九维评测、独立判断、基线、checkpoint 与只进不退的 ratchet | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) |
| **video-downloader** | 下载/提取 Douyin、Bilibili、YouTube、Xiaohongshu 视频，保存元数据、字幕与 ASR 转录 | [kangarooking/kangarooking-skills/video-downloader](https://github.com/kangarooking/kangarooking-skills/tree/main/video-downloader) |

### 构建参考

| 项目 | Kongzi 借鉴的公开模式 |
|---|---|
| [atlax-tech/harness-armor](https://github.com/atlax-tech/harness-armor) | 仓库 Harness、验收与分支治理 |
| [iamzifei/show-me-the-money](https://github.com/iamzifei/show-me-the-money) | 隔离状态、追加快照、日报/周报和可追溯学习记录 |
| [XBuilderLAB/cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) | 根路由 + 子 Skill、逐题画像、不可变证据与周期复盘 |

这些项目不会被压缩成“类似功能”。四个运行时上游通过完整 Skill 目录安装，Agent 执行时必须读取其完整 `SKILL.md` 并遵循原流程。

---

## 贡献与社区

Kongzi 是 MIT 开源项目。欢迎提交：

- 一个真实学习旅程中卡住的场景
- 新领域的权威来源选择规则
- 更好的诊断题、迁移题和评分 rubric
- 不同 runtime、视频平台和 Obsidian 工作流的兼容性修复
- Darwin 评测结果与能通过 ratchet 的改进

提交前请运行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/kongzi.py doctor --vault <测试vault>
```

---

## Darwin.skill：让 Kongzi 持续进化

<div align="center">

[![Darwin.skill](https://img.shields.io/badge/Darwin.skill-Self--Evolving-7c3aed)](https://github.com/alchaincyf/darwin-skill)

</div>

Kongzi 内置代表性测试提示，覆盖首次使用、恢复、权威网页、主动输出、Cangjie、视频、Nuwa、日报周报和 Darwin 自评。

```
/Kongzi integration 用 Darwin 改进 Kongzi
```

Agent 会保留当前基线，按 Darwin 九维 rubric 使用独立判断，等待规定 checkpoint，再只合并通过 ratchet 的变化。证据来源、用户必须输出、延迟掌握、追加日志这四条约束不能被“优化”掉。

---

## 学习方法如何选择

Kongzi 不押注单一学习法，而是按知识类型选择组合：

**1. 事实与术语**——提取练习 + 间隔复习 + 相似概念辨析。

**2. 概念与心智模型**——例子/反例 + 自我解释 + 闭卷提取 + 新情境迁移。

**3. 操作与解题程序**——完整示例 → 补全步骤 → 独立练习 → 变式应用 → 反馈纠错。

**4. 感知与分类判断**——对比案例 + 交错练习 + 快速反馈。

**5. 创作与职业能力**——拆分子技能 + 刻意练习 + 真实项目 + 评审 + 反思。

**6. 隐性经验**——专家示范 + 教练提示 + 脚手架逐步撤除 + 真实任务。

Kongzi 会组合提取练习、间隔效应、交错练习、worked examples、自我解释、精细加工、双重编码、刻意练习、掌握学习、认知学徒制、项目式学习和元认知校准。

费曼式解释适合检查“能否用自己的话说清楚”，但并不适合独自承担所有学习：会解释游泳原理不等于会游泳，会复述 API 不等于能调试程序。

---

## 仓库结构

```text
kongzi-ai-mentor-skills/
├── SKILL.md                 # /Kongzi 根路由
├── skills/                  # 画像、来源、路线、学习、复习、报告、导师、集成
├── scripts/
│   ├── kongzi.py            # 本地状态、证据、计划、复习与报告命令
│   └── install_integrations.py
├── references/              # Agent 按需读取的公开协议与学习方法选择表
├── assets/                  # Hero 与真实命令 Demo 动图
├── tests/                   # 状态不变量与 Darwin 测试提示
├── agents/openai.yaml
├── README.md
└── LICENSE
```

学习内容写在你自己的 Obsidian vault：机器状态位于 `.kongzi/`，可阅读笔记位于 `Kongzi/`。

---

## 背后的故事

很多“AI 学习助手”擅长一次性讲解，却不知道用户昨天学了什么、是否真的回答过、三天后是否还记得，也无法说明答案来自哪里。

Kongzi 的出发点很朴素：少报一门不需要的课，少在零散内容里兜圈子，把时间花在真正的输出、纠错和复习上。

**Kongzi（孔子）**代表的不是复古课堂，而是“因材施教”和“学而时习”：路线因人而异，资料可以回查，学习必须经过用户自己的嘴、手和脑。

---

## 许可证

[MIT](LICENSE)

---

<div align="center">

**Cangjie** 把资料蒸馏成可验证知识。<br>
**Nuwa** 把公开人物蒸馏成导师视角。<br>
**Kongzi** 把知识、导师与学习者连接成持续学习闭环。<br><br>

如果它帮你少踩了一次学习的坑，欢迎给个 Star。

</div>

---

## English

**Kongzi is a local-first, source-grounded AI learning mentor for any subject.** It builds a learner profile, registers authoritative materials, creates a prerequisite-aware knowledge map, schedules a personalized study cycle, asks the learner to produce answers, grades and corrects them, schedules spaced reviews, and writes durable progress plus daily/weekly reports into Obsidian.

**Install:** `npx skills add atlax-tech/kongzi-ai-mentor-skills`

**Start or resume:** `/Kongzi`

**Full integrations:** Cangjie for source distillation, video-downloader for supported video platforms and ASR, Nuwa for expert-style mentor models, and Darwin for ratcheted skill improvement.

Kongzi never treats chat fluency as mastery: claims require inspectable source locators, learner answers are stored before feedback, and mastery requires delayed retrieval plus application evidence.
