import pathlib
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "ddia-system-design"


def skill_text() -> str:
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


class DdiaSkillBehaviorContractTest(unittest.TestCase):
    """Verify the skill instructions form a complete, self-consistent contract.

    These tests check that a compliant agent following SKILL.md would know:
    what response shape to produce, when to truncate it, what guardrails to
    enforce, when not to use the skill, and which references to load for which
    task. This is behavior-oriented regression evidence: it guards the skill's
    behavioral contract, not just file existence.
    """

    def test_response_shape_enumerates_all_seven_sections(self):
        text = skill_text()
        shape_section = text.split("## Response Shape", 1)[1].split("##", 1)[0]
        for section in [
            "Assumptions and workload shape",
            "Recommendation",
            "Key trade-offs",
            "Failure modes",
            "Consistency and correctness implications",
            "Operational checks",
            "Tests or experiments to validate the design",
        ]:
            self.assertIn(section, shape_section, f"Response shape missing section: {section}")

    def test_narrow_follow_up_exemption_is_present(self):
        text = skill_text()
        self.assertIn("narrow follow-up", text.lower())
        self.assertIn("only the relevant sections", text.lower())

    def test_guardrails_cover_core_behavioral_rules(self):
        text = skill_text()
        self.assertIn("missing workload", text.lower())
        self.assertIn("one-size-fits-all", text.lower())
        self.assertIn("derived data", text.lower())
        self.assertIn("operations", text.lower())
        self.assertIn("quotations", text.lower())

    def test_off_topic_boundaries_are_present(self):
        text = skill_text()
        self.assertIn("Out Of Scope", text)
        off_topic = text.split("## Out Of Scope", 1)[1].split("##", 1)[0]
        self.assertIn("algorithm", off_topic.lower())
        self.assertIn("frontend", off_topic.lower())

    def test_reference_loading_is_conditional_on_task_type(self):
        text = skill_text()
        load_section = text.split("## Load References Selectively", 1)[1].split("##", 1)[0]
        self.assertIn("topic-map.md", load_section)
        self.assertIn("system-design-principles.md", load_section)
        self.assertIn("architecture-review-checklists.md", load_section)
        self.assertIn("when", load_section.lower())

    def test_worked_example_demonstrates_response_shape(self):
        text = skill_text()
        example_section = text.split("## Worked Example", 1)[1].split("##", 1)[0]
        for marker in [
            "Assumptions and workload shape",
            "Recommendation",
            "Key trade-offs",
            "Failure modes",
            "Consistency and correctness implications",
            "Operational checks",
            "Tests",
        ]:
            self.assertIn(marker, example_section, f"Worked example missing: {marker}")

    def test_description_triggers_on_core_topics(self):
        text = skill_text()
        for topic in [
            "replication",
            "partitioning",
            "transactions",
            "consensus",
            "stream processing",
            "derived data",
        ]:
            self.assertIn(topic, text.lower(), f"Description missing trigger topic: {topic}")

    def test_skill_does_not_recommend_tools_categorically(self):
        text = skill_text()
        self.assertNotIn("always use kafka", text.lower())
        self.assertNotIn("always use nosql", text.lower())
        self.assertNotIn("always use microservices", text.lower())


if __name__ == "__main__":
    unittest.main()
