from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentLabEvidenceTests(unittest.TestCase):
    def test_agent_lab_evidence_files_exist(self) -> None:
        self.assertTrue((ROOT / "evaluation/agent-lab/README.md").is_file())
        self.assertTrue((ROOT / "evaluation/agent-lab/latest-comparison.json").is_file())
        self.assertTrue((ROOT / "evaluation/agent-lab/latest-comparison.md").is_file())

    def test_latest_comparison_json_has_required_fields(self) -> None:
        payload = json.loads((ROOT / "evaluation/agent-lab/latest-comparison.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["evidence"]["evaluator"], "seasonsolt/agent-lab")
        self.assertEqual(payload["evidence"]["treatment_repo_url"], "https://github.com/seasonsolt/ddia-skill")
        self.assertRegex(payload["evidence"]["treatment_repo_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(payload["evidence"]["treatment_skill_path"], "skills/ddia-system-design")
        self.assertIn(payload["verdict"], {"useful", "weak", "harmful", "inconclusive"})
        self.assertIn("baseline", payload)
        self.assertIn("treatment", payload)
        self.assertIn("score_lift", payload)

    def test_latest_markdown_and_root_readme_link_evidence(self) -> None:
        evidence_markdown = (ROOT / "evaluation/agent-lab/latest-comparison.md").read_text(encoding="utf-8")
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Agent Lab Skill Comparison Evidence", evidence_markdown)
        self.assertIn("not statistical proof", evidence_markdown)
        self.assertIn("evaluation/agent-lab/latest-comparison.md", root_readme)


if __name__ == "__main__":
    unittest.main()
