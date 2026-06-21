import pathlib
import re
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "ddia-system-design"


class DdiaSkillContentTest(unittest.TestCase):
    def test_skill_frontmatter_and_reference_links(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: ddia-system-design", text)
        self.assertIn("description:", text)
        self.assertIn("references/topic-map.md", text)
        self.assertIn("references/system-design-principles.md", text)
        self.assertIn("references/architecture-review-checklists.md", text)

    def test_references_cover_core_backend_topics(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL / "references" / "topic-map.md",
                SKILL / "references" / "system-design-principles.md",
                SKILL / "references" / "architecture-review-checklists.md",
            ]
        ).lower()
        required_terms = [
            "reliability",
            "scalability",
            "maintainability",
            "replication",
            "partitioning",
            "transactions",
            "isolation",
            "linearizability",
            "consensus",
            "stream processing",
            "batch processing",
            "derived data",
        ]
        for term in required_terms:
            self.assertIn(term, combined)

    def test_skill_has_no_empty_bullets(self):
        for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"(?m)^-\s*$", text), f"Empty bullet in {path}")


if __name__ == "__main__":
    unittest.main()
