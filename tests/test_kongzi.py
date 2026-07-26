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

        self.run_cli("report", "daily", "--vault", str(self.vault))
        self.run_cli("report", "daily", "--vault", str(self.vault))
        reports = list((self.vault / "Kongzi" / "Reports" / "Daily").glob("*.md"))
        self.assertEqual(len(reports), 2)
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


if __name__ == "__main__":
    unittest.main()
