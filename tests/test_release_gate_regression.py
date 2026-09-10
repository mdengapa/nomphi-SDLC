import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import nomphi_agent


class ReleaseGateRegressionTests(unittest.TestCase):

    def _transition(self, verdict_text):
        with tempfile.TemporaryDirectory() as td:
            task = Path(td)
            if verdict_text is not None:
                (task / "release-report.md").write_text(
                    f"# Release Report\n\nVerdict: {verdict_text}\n"
                )

            state = {
                "task_id": "TEST-RELEASE",
                "state": "RELEASE_GATE",
                "risk": "LOW",
            }

            with patch.object(nomphi_agent.nomphi, "td", return_value=task):
                return nomphi_agent.next_transition(state)

    def test_pass_releases(self):
        self.assertEqual(
            self._transition("PASS"),
            ("RELEASED", None),
        )

    def test_block_blocks_release(self):
        self.assertEqual(
            self._transition("BLOCK"),
            ("RELEASE_BLOCKED", None),
        )

    def test_missing_verdict_fails_closed(self):
        target, reason = self._transition(None)
        self.assertIsNone(target)
        self.assertEqual(reason, "release verdict is missing or ambiguous")


if __name__ == "__main__":
    unittest.main()
