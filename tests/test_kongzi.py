from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "kongzi.py"
INSTALLER = ROOT / "scripts" / "install_integrations.py"
PACKAGER = ROOT / "scripts" / "package_release.py"


class KongziCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="kongzi-test-")
        self.vault = Path(self.temp.name) / "vault"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        merged = os.environ.copy()
        if env:
            merged.update(env)
        completed = subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
            env=merged,
        )
        if check and completed.returncode:
            self.fail(f"CLI failed: {completed.args}\nstdout={completed.stdout}\nstderr={completed.stderr}")
        return completed

    def data(self, completed: subprocess.CompletedProcess[str]) -> dict:
        return json.loads(completed.stdout)

    def initialize(self) -> dict:
        result = self.run_cli(
            "init",
            "--vault",
            str(self.vault),
            "--name",
            "Ada",
            "--goal",
            "Learn retrieval practice",
            "--outcome",
            "Design a one-week evidence-based study plan",
        )
        return self.data(result)

    def test_first_status_and_dashboard_offer_one_localized_next_action(self) -> None:
        before = self.data(self.run_cli("status", "--vault", str(self.vault)))
        self.assertFalse(before["initialized"])
        self.assertIn("init --vault", before["next_action"])
        self.run_cli(
            "init",
            "--vault",
            str(self.vault),
            "--name",
            "新手",
            "--timezone",
            "Asia/Shanghai",
        )
        dashboard = (self.vault / "Kongzi" / "Dashboard.md").read_text(encoding="utf-8")
        self.assertIn("+08:00（Asia/Shanghai）", dashboard)
        self.assertIn("完成第一项画像问题", dashboard)
        self.assertNotIn("2. 创建学习旅程", dashboard)
        status = self.data(self.run_cli("status", "--vault", str(self.vault)))
        self.assertEqual(status["missing_profile_fields"][0], "goal")
        self.assertIn("下一项：goal", status["next_action"])

    def test_unconfirmed_schedule_defaults_are_labeled_inferred(self) -> None:
        initialized = self.initialize()
        journey = initialized["journey"]["journey"]
        self.assertFalse(journey["availability"]["confirmed"])
        self.assertEqual(journey["availability"]["daily_minutes_source"], "inferred-default")
        journey_note = next((self.vault / "Kongzi" / "Journeys").rglob("Journey.md"))
        journey_text = journey_note.read_text(encoding="utf-8")
        self.assertIn("暂定默认，待画像确认", journey_text)
        self.assertIn("限制：未提供，待确认", journey_text)
        self.assertNotIn("限制：无", journey_text)

    def add_profile(self) -> None:
        for index, field in enumerate(
            ("goal", "baseline", "constraints", "materials", "experience", "diagnostic")
        ):
            self.run_cli(
                "profile",
                "set",
                "--vault",
                str(self.vault),
                "--field",
                field,
                "--value",
                f"value-{index}",
            )

    def prepare_node(self) -> tuple[str, str]:
        material = Path(self.temp.name) / "paper.md"
        material.write_text(
            "# Retrieval practice\n\nRetrieval after a delay supports durable access.\n",
            encoding="utf-8",
        )
        source = self.data(
            self.run_cli(
                "source",
                "add",
                "--vault",
                str(self.vault),
                str(material),
                "--authority",
                "primary",
            )
        )["source"]["id"]
        claim = self.data(
            self.run_cli(
                "claim",
                "add",
                "--vault",
                str(self.vault),
                "--statement",
                "Delayed retrieval can strengthen durable access.",
                "--source-id",
                source,
                "--locator",
                "Retrieval practice, paragraph 1",
            )
        )["claim"]["id"]
        node = self.data(
            self.run_cli(
                "node",
                "add",
                "--vault",
                str(self.vault),
                "--title",
                "Retrieval practice",
                "--knowledge-type",
                "procedure",
                "--claim",
                claim,
                "--outcome",
                "Create three retrieval prompts",
            )
        )["node"]["id"]
        return node, claim

    def test_full_cycle_requires_output_and_delayed_mastery(self) -> None:
        self.initialize()
        self.add_profile()
        node, claim = self.prepare_node()
        self.run_cli("map", "render", "--vault", str(self.vault))
        self.run_cli(
            "plan",
            "build",
            "--vault",
            str(self.vault),
            "--weeks",
            "1",
            "--sessions-per-week",
            "3",
        )
        session = self.data(
            self.run_cli("session", "start", "--vault", str(self.vault), "--node-id", node)
        )["session"]["id"]
        answer = self.data(
            self.run_cli(
                "session",
                "answer",
                "--vault",
                str(self.vault),
                "--session-id",
                session,
                "--kind",
                "application",
                "--question",
                "How would you study tree traversal?",
                "--answer",
                "Recall it from a blank page, check, and repeat later.",
            )
        )["answer"]["id"]
        graded = self.data(
            self.run_cli(
                "session",
                "grade",
                "--vault",
                str(self.vault),
                "--answer-id",
                answer,
                "--score",
                "0.9",
                "--feedback",
                "Uses retrieval and spacing.",
                "--correction",
                "Add a transfer example.",
                "--claim",
                claim,
                "--retrieval",
                "0.9",
                "--accuracy",
                "0.9",
                "--transfer",
                "0.8",
            )
        )
        card = graded["review_card"]["id"]
        early = self.run_cli(
            "review",
            "answer",
            "--vault",
            str(self.vault),
            "--card-id",
            card,
            "--answer",
            "early",
            "--score",
            "1",
            "--feedback",
            "early",
            check=False,
        )
        self.assertEqual(early.returncode, 2)
        self.assertIn("尚未到期", early.stderr)

        self.run_cli(
            "session",
            "finish",
            "--vault",
            str(self.vault),
            "--session-id",
            session,
            "--minutes",
            "25",
            "--reflection",
            "Recall before rereading.",
            "--confidence",
            "0.7",
        )
        state_after_finish = json.loads(
            (self.vault / ".kongzi" / "state.json").read_text(encoding="utf-8")
        )
        plan_id = state_after_finish["journeys"][
            next(iter(state_after_finish["journeys"]))
        ]["active_plan_id"]
        self.assertEqual(state_after_finish["plans"][plan_id]["sessions"][0]["status"], "completed")
        queue_path = self.vault / ".kongzi" / "review-queue.json"
        for _ in range(2):
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            queue["cards"][card]["due_at"] = (
                dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            ).replace(microsecond=0).isoformat()
            queue_path.write_text(json.dumps(queue), encoding="utf-8")
            self.run_cli(
                "review",
                "answer",
                "--vault",
                str(self.vault),
                "--card-id",
                card,
                "--answer",
                "Recall, check, correct, and retry after a delay.",
                "--score",
                "0.9",
                "--feedback",
                "Correct delayed retrieval.",
            )
        state = json.loads((self.vault / ".kongzi" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["nodes"][node]["status"], "mastered")
        self.assertEqual(state["nodes"][node]["mastery"]["level"], 4)
        self.assertEqual(
            state["journeys"][next(iter(state["journeys"]))]["status"], "learning"
        )
        map_note = next((self.vault / "Kongzi" / "Journeys").rglob("Knowledge Map.md"))
        self.assertIn("mastered · L4", map_note.read_text(encoding="utf-8"))

        self.run_cli("report", "daily", "--vault", str(self.vault))
        self.run_cli("report", "daily", "--vault", str(self.vault))
        reports = list((self.vault / "Kongzi" / "Reports" / "Daily").glob("*.md"))
        self.assertEqual(len(reports), 2)
        self.assertTrue(all(path.read_text(encoding="utf-8").startswith("# Kongzi") for path in reports))
        doctor = self.data(self.run_cli("doctor", "--vault", str(self.vault)))
        self.assertTrue(doctor["healthy"])

    def test_session_cannot_finish_without_learner_output(self) -> None:
        self.initialize()
        node, _ = self.prepare_node()
        session = self.data(
            self.run_cli("session", "start", "--vault", str(self.vault), "--node-id", node)
        )["session"]["id"]
        result = self.run_cli(
            "session",
            "finish",
            "--vault",
            str(self.vault),
            "--session-id",
            session,
            "--minutes",
            "10",
            "--reflection",
            "none",
            "--confidence",
            "0.2",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("用户输出", result.stderr)

    def test_learner_question_requires_grounded_explanation_and_restatement(self) -> None:
        self.initialize()
        node, claim = self.prepare_node()
        session = self.data(
            self.run_cli("session", "start", "--vault", str(self.vault), "--node-id", node)
        )["session"]["id"]
        question = self.data(
            self.run_cli(
                "session",
                "question",
                "--vault",
                str(self.vault),
                "--session-id",
                session,
                "--question",
                "为什么先回忆再重读，而不是直接重读？",
            )
        )["question"]["id"]
        unsupported = self.run_cli(
            "session",
            "explain",
            "--vault",
            str(self.vault),
            "--question-id",
            question,
            "--response",
            "先回忆能暴露提取失败。",
            "--check-question",
            "请用自己的话解释先回忆的作用。",
            check=False,
        )
        self.assertEqual(unsupported.returncode, 2)
        self.assertIn("claim", unsupported.stderr)
        explanation = self.data(
            self.run_cli(
                "session",
                "explain",
                "--vault",
                str(self.vault),
                "--question-id",
                question,
                "--response",
                "先闭卷回忆会暴露提取缺口，随后核对才能把反馈用在真正的错误上。",
                "--claim",
                claim,
                "--check-question",
                "请用自己的话解释先回忆的作用。",
            )
        )["explanation"]
        premature = self.run_cli(
            "session",
            "finish",
            "--vault",
            str(self.vault),
            "--session-id",
            session,
            "--minutes",
            "10",
            "--reflection",
            "仍需复述。",
            "--confidence",
            "0.5",
            check=False,
        )
        self.assertEqual(premature.returncode, 2)
        self.assertIn("用户输出", premature.stderr)
        answer = self.data(
            self.run_cli(
                "session",
                "answer",
                "--vault",
                str(self.vault),
                "--session-id",
                session,
                "--explanation-id",
                explanation["id"],
                "--kind",
                "explain",
                "--question",
                explanation["check_question"],
                "--answer",
                "先尝试提取，才知道自己具体忘在哪里，核对时也更有针对性。",
            )
        )["answer"]["id"]
        self.run_cli(
            "session",
            "grade",
            "--vault",
            str(self.vault),
            "--answer-id",
            answer,
            "--score",
            "0.88",
            "--feedback",
            "准确说明了提取与反馈的关系。",
            "--correction",
            "下一次再补一个延迟条件。",
            "--claim",
            claim,
            "--retrieval",
            "0.9",
            "--accuracy",
            "0.9",
            "--transfer",
            "0.7",
        )
        self.run_cli(
            "session",
            "finish",
            "--vault",
            str(self.vault),
            "--session-id",
            session,
            "--minutes",
            "18",
            "--reflection",
            "先提取暴露缺口，再用材料纠错。",
            "--confidence",
            "0.75",
        )
        report = self.data(
            self.run_cli("report", "daily", "--vault", str(self.vault))
        )["report"]
        self.assertEqual(report["learner_questions_answered"], 1)
        state = json.loads((self.vault / ".kongzi" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(
            state["learner_questions"][question]["explanation_id"], explanation["id"]
        )
        self.assertEqual(state["explanations"][explanation["id"]]["check_answer_id"], answer)
        self.assertTrue(self.data(self.run_cli("doctor", "--vault", str(self.vault)))["healthy"])

    def test_node_requires_grounded_claim(self) -> None:
        self.initialize()
        result = self.run_cli(
            "node",
            "add",
            "--vault",
            str(self.vault),
            "--title",
            "Unsupported",
            "--outcome",
            "Say something",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("claim", result.stderr)

    def test_plan_records_personalization_methods_and_replan_history(self) -> None:
        self.initialize()
        self.add_profile()
        self.prepare_node()
        first = self.data(
            self.run_cli(
                "plan",
                "build",
                "--vault",
                str(self.vault),
                "--weeks",
                "1",
                "--sessions-per-week",
                "3",
                "--minutes",
                "30",
                "--reason",
                "初始诊断显示需要先练提取",
            )
        )["plan"]
        self.assertEqual(
            [item["mode"] for item in first["sessions"]],
            ["learn", "practice", "integrate"],
        )
        self.assertTrue(all(item["method"] for item in first["sessions"]))
        self.assertEqual(first["sessions"][0]["minimum_viable_minutes"], 10)
        self.assertEqual(first["basis"]["profile_fields"]["constraints"], "value-2")
        second = self.data(
            self.run_cli(
                "plan",
                "build",
                "--vault",
                str(self.vault),
                "--weeks",
                "1",
                "--sessions-per-week",
                "2",
                "--minutes",
                "20",
                "--reason",
                "观察到连续两次会话超时，缩短单次时长",
            )
        )["plan"]
        state = json.loads((self.vault / ".kongzi" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(second["supersedes_plan_id"], first["id"])
        self.assertEqual(state["plans"][first["id"]]["status"], "superseded")
        self.assertEqual(state["plans"][first["id"]]["superseded_by"], second["id"])
        plan_files = list((self.vault / "Kongzi" / "Journeys").rglob("Learning Plan--*.md"))
        self.assertEqual(len(plan_files), 2)

    def test_reminder_definitions_support_vault_paths_with_spaces(self) -> None:
        self.vault = Path(self.temp.name) / "My Obsidian Vault"
        self.initialize()
        cron = self.data(
            self.run_cli(
                "reminder",
                "generate",
                "--vault",
                str(self.vault),
                "--method",
                "cron",
                "--time",
                "20:15",
            )
        )
        cron_text = Path(cron["definition_path"]).read_text(encoding="utf-8")
        self.assertIn(f"--vault '{self.vault.resolve()}'", cron_text)
        launchd = self.data(
            self.run_cli(
                "reminder",
                "generate",
                "--vault",
                str(self.vault),
                "--method",
                "launchd",
                "--time",
                "20:15",
            )
        )
        plist = Path(launchd["definition_path"])
        self.assertIn(str(self.vault.resolve()), plist.read_text(encoding="utf-8"))
        self.assertRegex(plist.name, r"dev\.kongzi\.review-reminder\.[0-9a-f]{8}\.plist")

    def test_overdue_report_and_finished_plan_routing_are_truthful(self) -> None:
        self.initialize()
        self.add_profile()
        node, claim = self.prepare_node()
        session = self.data(
            self.run_cli("session", "start", "--vault", str(self.vault), "--node-id", node)
        )["session"]["id"]
        answer = self.data(
            self.run_cli(
                "session",
                "answer",
                "--vault",
                str(self.vault),
                "--session-id",
                session,
                "--kind",
                "application",
                "--question",
                "Apply the supported method.",
                "--answer",
                "Attempt, check, and correct after retrieval.",
            )
        )["answer"]["id"]
        graded = self.data(
            self.run_cli(
                "session",
                "grade",
                "--vault",
                str(self.vault),
                "--answer-id",
                answer,
                "--score",
                "0.9",
                "--feedback",
                "Grounded.",
                "--correction",
                "Retest after a delay.",
                "--claim",
                claim,
                "--retrieval",
                "0.9",
                "--accuracy",
                "0.9",
                "--transfer",
                "0.9",
            )
        )
        self.run_cli(
            "session",
            "finish",
            "--vault",
            str(self.vault),
            "--session-id",
            session,
            "--minutes",
            "12",
            "--reflection",
            "Retrieval before review.",
            "--confidence",
            "0.8",
        )
        status = self.data(self.run_cli("status", "--vault", str(self.vault)))
        self.assertEqual(status["planned_sessions_remaining"], 0)
        self.assertIn("下一次延迟复习", status["next_action"])
        self.assertNotIn("下一次学习会话", status["next_action"])

        queue_path = self.vault / ".kongzi" / "review-queue.json"
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        card_id = graded["review_card"]["id"]
        queue["cards"][card_id]["due_at"] = (
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)
        ).replace(microsecond=0).isoformat()
        queue_path.write_text(json.dumps(queue), encoding="utf-8")
        report_result = self.data(
            self.run_cli("report", "weekly", "--vault", str(self.vault))
        )
        report = report_result["report"]
        self.assertEqual(report["due_reviews"], 1)
        self.assertGreaterEqual(report["max_overdue_hours"], 4.9)
        markdown = Path(report_result["path"]).read_text(encoding="utf-8")
        self.assertTrue(markdown.startswith("# Kongzi Weekly Report"))
        self.assertIn("- 最早到期：", markdown)
        self.assertIn("- 最大逾期：", markdown)
        self.assertNotIn("\n            ##", markdown)

    def test_integration_discovery_uses_configured_roots(self) -> None:
        self.initialize()
        skills = Path(self.temp.name) / "skills"
        for name in ("cangjie-skill", "nuwa-skill", "darwin-skill", "video-downloader"):
            directory = skills / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")
        result = self.data(
            self.run_cli(
                "integration",
                "status",
                "--vault",
                str(self.vault),
                env={"KONGZI_SKILLS_DIRS": str(skills)},
            )
        )
        self.assertTrue(all(item["installed"] for item in result["integrations"].values()))

    def test_mentor_lens_does_not_mutate_learning_evidence(self) -> None:
        self.initialize()
        self.prepare_node()
        state_path = self.vault / ".kongzi" / "state.json"
        before = json.loads(state_path.read_text(encoding="utf-8"))
        evidence_before = {
            key: before[key]
            for key in ("journeys", "sources", "claims", "nodes", "plans", "sessions", "answers", "grades")
        }
        persona = Path(self.temp.name) / "mentor.md"
        persona.write_text(
            "# Mentor\n\nUse questions and first-principles explanations.\n",
            encoding="utf-8",
        )
        self.run_cli(
            "mentor",
            "set",
            "--vault",
            str(self.vault),
            "--name",
            "Feynman lens",
            "--persona-path",
            str(persona),
        )
        after = json.loads(state_path.read_text(encoding="utf-8"))
        evidence_after = {key: after[key] for key in evidence_before}
        self.assertEqual(evidence_before, evidence_after)
        self.assertTrue(after["mentor"]["enabled"])

    def test_repair_rebuilds_corrupt_indexes_from_events(self) -> None:
        self.initialize()
        self.add_profile()
        node, claim = self.prepare_node()
        session = self.data(
            self.run_cli("session", "start", "--vault", str(self.vault), "--node-id", node)
        )["session"]["id"]
        answer = self.data(
            self.run_cli(
                "session",
                "answer",
                "--vault",
                str(self.vault),
                "--session-id",
                session,
                "--kind",
                "application",
                "--question",
                "Apply retrieval.",
                "--answer",
                "Attempt without cues, then correct.",
            )
        )["answer"]["id"]
        self.run_cli(
            "session",
            "grade",
            "--vault",
            str(self.vault),
            "--answer-id",
            answer,
            "--score",
            "0.8",
            "--feedback",
            "Grounded.",
            "--correction",
            "Repeat later.",
            "--claim",
            claim,
            "--retrieval",
            "0.8",
            "--accuracy",
            "0.8",
            "--transfer",
            "0.8",
        )
        for name in ("state.json", "profile.json", "review-queue.json"):
            (self.vault / ".kongzi" / name).write_text("{broken", encoding="utf-8")
        repaired = self.data(
            self.run_cli("repair", "--vault", str(self.vault), "--component", "all")
        )
        self.assertEqual(set(repaired["repaired"]), {"state", "profile", "queue"})
        for backup in repaired["pre_repair_backups"].values():
            self.assertTrue(Path(backup).exists())
        state = json.loads((self.vault / ".kongzi" / "state.json").read_text(encoding="utf-8"))
        queue = json.loads(
            (self.vault / ".kongzi" / "review-queue.json").read_text(encoding="utf-8")
        )
        self.assertIn(node, state["nodes"])
        self.assertTrue(queue["cards"])
        self.assertTrue(self.data(self.run_cli("doctor", "--vault", str(self.vault)))["healthy"])

    def test_installer_dry_run_is_non_mutating(self) -> None:
        target = Path(self.temp.name) / "skills"
        completed = subprocess.run(
            [sys.executable, str(INSTALLER), "--target", str(target), "--dry-run"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertFalse(target.exists())
        self.assertEqual(len(json.loads(completed.stdout)["plan"]), 4)

    def test_bundle_round_trip_preserves_and_rebases_learning_state(self) -> None:
        initialized = self.initialize()
        node, _ = self.prepare_node()
        bundle = Path(self.temp.name) / "learning.kongzi.zip"
        exported = self.data(
            self.run_cli(
                "bundle",
                "export",
                "--vault",
                str(self.vault),
                "--output",
                str(bundle),
            )
        )
        self.assertTrue(bundle.exists())
        self.assertGreater(exported["files"], 0)
        imported_vault = Path(self.temp.name) / "imported"
        imported = self.data(
            self.run_cli(
                "bundle",
                "import",
                "--vault",
                str(imported_vault),
                "--bundle",
                str(bundle),
            )
        )
        self.assertEqual(
            imported["active_journey_id"],
            initialized["journey"]["journey"]["id"],
        )
        state = json.loads(
            (imported_vault / ".kongzi" / "state.json").read_text(encoding="utf-8")
        )
        self.assertIn(node, state["nodes"])
        for source in state["sources"].values():
            self.assertTrue(source["content_path"].startswith(str(imported_vault.resolve())))
        self.assertTrue(
            self.data(self.run_cli("doctor", "--vault", str(imported_vault)))["healthy"]
        )
        self.assertTrue(
            self.data(self.run_cli("migrate", "--vault", str(imported_vault)))["up_to_date"]
        )

    def test_release_package_excludes_internal_harness_docs(self) -> None:
        output = Path(self.temp.name) / "release"
        completed = subprocess.run(
            [sys.executable, str(PACKAGER), "--source", str(ROOT), "--output", str(output)],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((output / "SKILL.md").exists())
        self.assertFalse((output / "AGENTS.md").exists())
        self.assertFalse((output / ".harness").exists())
        self.assertFalse((output / "docs").exists())

    def test_readme_structure_and_upstream_acknowledgement_boundary(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        headings = [
            line
            for line in readme.splitlines()
            if line.startswith("#") and not line.startswith("# Kongzi Daily")
        ]
        self.assertEqual(
            headings,
            [
                "# Kongzi.skill",
                "## 效果示例",
                "## 安装",
                "### 方式一：一行命令（推荐，跨 runtime）",
                "### 方式二：手动安装",
                "### 方式三：作为参考资料使用",
                "### 使用",
                "## Kongzi 覆盖什么",
                "### 诚实边界",
                "## 已集成能力",
                "### 完整运行时集成",
                "### 构建参考",
                "## 贡献与社区",
                "## Darwin.skill：让 Kongzi 持续进化",
                "## 学习方法如何选择",
                "## 仓库结构",
                "## 背后的故事",
                "## 许可证",
                "## English",
            ],
        )
        self.assertNotIn("scripts/install_integrations.py", readme)
        self.assertNotIn("/Kongzi integration", readme)
        self.assertNotIn("在 Kongzi 中的用途", readme)
        self.assertIn("只作致谢与来源声明", readme)


if __name__ == "__main__":
    unittest.main()
