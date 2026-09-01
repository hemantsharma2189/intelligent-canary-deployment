import json
import unittest
from pathlib import Path

from scripts.rollout_explainer import (
    build_ai_prompt,
    create_evidence_summary,
)


class TestRolloutExplainer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        result_path = Path(
            "examples/failed-rollout.json"
        )

        with result_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            cls.data = json.load(file)

    def test_failed_rollout_recommends_rollback(self):
        summary = create_evidence_summary(
            self.data
        )

        self.assertIn(
            "rolled back to the stable version",
            summary,
        )

    def test_summary_contains_observed_metrics(self):
        summary = create_evidence_summary(
            self.data
        )

        self.assertIn("88.4%", summary)
        self.assertIn("0.92 seconds", summary)

    def test_ai_prompt_contains_rollout_evidence(self):
        prompt = build_ai_prompt(
            self.data
        )

        self.assertIn("v2.0.0", prompt)
        self.assertIn("rollback", prompt)
        self.assertIn("success_rate_percent", prompt)

    def test_ai_prompt_prevents_invented_evidence(self):
        prompt = build_ai_prompt(
            self.data
        )

        self.assertIn(
            "Do not invent evidence",
            prompt,
        )


if __name__ == "__main__":
    unittest.main()
