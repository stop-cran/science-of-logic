import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import review


class RepoBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.root = self.base / "repo"
        (self.root / "synopsis").mkdir(parents=True)
        (self.root / ".github").mkdir()
        (self.root / ".git").mkdir()
        (self.root / "README.md").write_text("index marker", encoding="utf-8")
        (self.root / "REVIEW.md").write_text("rubric", encoding="utf-8")
        (self.root / ".github" / "copilot-instructions.md").write_text(
            "instructions",
            encoding="utf-8",
        )
        (self.root / "synopsis" / "25-test.md").write_text(
            "essence marker",
            encoding="utf-8",
        )
        (self.root / "synopsis" / ".gitkeep").write_text("", encoding="utf-8")
        (self.root / ".git" / "config").write_text(
            "forbidden git marker",
            encoding="utf-8",
        )
        (self.base / "outside.md").write_text(
            "forbidden outside marker",
            encoding="utf-8",
        )
        self.repo = review.Repo(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_allowed_corpus_reads_and_searches(self):
        self.assertIn("essence marker", self.repo.read_file("synopsis/25-test.md"))
        self.assertIn(
            "synopsis/25-test.md:1",
            self.repo.grep("essence", "synopsis/*.md"),
        )
        self.assertEqual(
            self.repo.match_files("synopsis/25-*.md"),
            ["synopsis/25-test.md"],
        )
        self.assertEqual(
            self.repo.match_files("synopsis/*"),
            ["synopsis/25-test.md"],
        )

    def test_parent_escape_is_rejected_across_tools(self):
        read_result = review.dispatch(
            self.repo,
            "read_file",
            {"path": "../outside.md"},
        )
        grep_result = review.dispatch(
            self.repo,
            "grep",
            {"pattern": "forbidden", "glob": "../*.md"},
        )
        list_result = review.dispatch(
            self.repo,
            "list_dir",
            {"path": ".."},
        )
        self.assertTrue(read_result.startswith("ERROR"))
        self.assertTrue(grep_result.startswith("ERROR"))
        self.assertTrue(list_result.startswith("ERROR"))
        self.assertNotIn("forbidden outside marker", read_result + grep_result)

    def test_unrelated_repo_files_are_rejected_and_hidden(self):
        read_result = review.dispatch(
            self.repo,
            "read_file",
            {"path": ".git/config"},
        )
        grep_result = review.dispatch(
            self.repo,
            "grep",
            {"pattern": "forbidden", "glob": ".git/config"},
        )
        root_listing = self.repo.list_dir(".")
        self.assertTrue(read_result.startswith("ERROR"))
        self.assertTrue(grep_result.startswith("ERROR"))
        self.assertNotIn("d .git\n", root_listing + "\n")
        self.assertNotIn("forbidden git marker", read_result + grep_result)

    def test_missing_required_pattern_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "matched no files"):
            review.expand_required_files(
                self.repo,
                ["synopsis/99-nope-*.md"],
                "--target",
            )

    def test_target_must_be_a_synopsis_markdown_file(self):
        with self.assertRaisesRegex(ValueError, "synopsis Markdown"):
            review.validate_synopsis_files(["README.md"], "--target")


class ReviewContractTests(unittest.TestCase):
    VALID_REVIEW = """\
## 1. Verdict
Publishable.
## 2. Verified
Gate passed.
## 3. Findings
None.
## 4. Questions
None.
## 5. Handoff
Settled.
"""

    def test_contract_requires_gate_and_all_sections(self):
        self.assertEqual(
            review.review_contract_errors(self.VALID_REVIEW, True, 0, None),
            [],
        )
        self.assertIn(
            "run_gate was not called",
            review.review_contract_errors(self.VALID_REVIEW, False, None, None),
        )
        errors = review.review_contract_errors(
            self.VALID_REVIEW.replace("## 3. Findings\nNone.\n", ""),
            True,
            0,
            None,
        )
        self.assertIn("missing or out-of-order section 3. Findings", errors)

    def test_contract_accepts_unnumbered_headings_and_trims_preamble(self):
        unnumbered = self.VALID_REVIEW.replace("## 1. ", "## ").replace(
            "## 2. ",
            "## ",
        ).replace("## 3. ", "## ").replace("## 4. ", "## ").replace(
            "## 5. ",
            "## ",
        )
        self.assertEqual(
            review.review_contract_errors(unnumbered, True, 0, None),
            [],
        )
        self.assertEqual(
            review.clean_final("reasoning preamble\n\n" + unnumbered),
            unnumbered,
        )

    def test_failed_gate_must_be_reported_as_blocker(self):
        errors = review.review_contract_errors(self.VALID_REVIEW, True, 1, None)
        self.assertIn(
            "run_gate exited 1; the final review must report this as a Blocker",
            errors,
        )
        blocker_review = self.VALID_REVIEW.replace(
            "Publishable.",
            "Not publishable. Blocker: the mechanical gate failed.",
        )
        self.assertEqual(
            review.review_contract_errors(blocker_review, True, 1, None),
            [],
        )

    def test_run_gate_records_exit_code(self):
        repo = unittest.mock.Mock(spec=review.Repo)
        repo.reset_gate_status = review.Repo.reset_gate_status.__get__(
            repo,
            review.Repo,
        )
        repo.run_gate = review.Repo.run_gate.__get__(repo, review.Repo)
        repo.root = Path("C:/repo")
        repo.reset_gate_status()
        completed = unittest.mock.Mock(returncode=3, stdout="gate output", stderr="")
        with patch("review.subprocess.run", return_value=completed):
            result = repo.run_gate()
        self.assertTrue(repo.gate_attempted)
        self.assertEqual(repo.gate_exit_code, 3)
        self.assertIsNone(repo.gate_error)
        self.assertEqual(result, "gate output\n(exit 3)")

    def test_contract_retries_are_bounded_and_preserve_last_draft(self):
        class FakeRepo:
            def reset_gate_status(self):
                self.gate_attempted = False
                self.gate_exit_code = None
                self.gate_error = None

        responses = [
            {"choices": [{"message": {"content": "first draft"}, "finish_reason": "stop"}]},
            {"choices": [{"message": {"content": "last draft"}, "finish_reason": "stop"}]},
        ]
        with patch("review._post_with_retry", side_effect=responses):
            with self.assertRaises(review.ReviewFailure) as raised:
                review.review_one(
                    "model",
                    "https://example",
                    "api-version",
                    "token",
                    "system",
                    "user",
                    FakeRepo(),
                    0.2,
                    10,
                    10,
                    1,
                    False,
                )
        self.assertEqual(raised.exception.rejected_review, "last draft")
        self.assertIn(
            "missing or out-of-order section 1. Verdict",
            raised.exception.contract_errors,
        )

    def test_retry_handles_read_timeout(self):
        response = unittest.mock.Mock()
        response.status_code = 200
        response.json.return_value = {"ok": True}
        with (
            patch(
                "review.requests.post",
                side_effect=[review.requests.exceptions.ReadTimeout("slow"), response],
            ) as post,
            patch("review.time.sleep"),
        ):
            result = review._post_with_retry(
                "https://example",
                {},
                {},
                read_timeout=12,
                attempts=2,
            )
        self.assertEqual(result, {"ok": True})
        self.assertEqual([call.kwargs["timeout"] for call in post.call_args_list], [12, 12])

    def test_failure_output_uses_diagnostic_suffix(self):
        path = review._review_output_path(
            Path("C:/repo"),
            "out",
            "synopsis/25-test.md",
            "DeepSeek/V4 Pro",
            failed=True,
        )
        self.assertEqual(path.name, "25-test--DeepSeek-V4-Pro.failed.txt")


if __name__ == "__main__":
    unittest.main()
