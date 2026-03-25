from __future__ import annotations

import unittest

from mcqpy_shiny.embed_cli import build_embed_qmd


class BuildEmbedQmdTests(unittest.TestCase):
    def test_hosted_wheel_embed_contains_app_and_requirements(self) -> None:
        rendered = build_embed_qmd(
            fixed_url="https://example.com/quiz.json",
            fixed_token=None,
            allow_manual_load=False,
            title="Hosted",
            card_width="840px",
            wheel_url="https://example.github.io/pkg/mcqpy_shiny-0.1.0-py3-none-any.whl",
            extra_requirements=["pyfiglet"],
        )

        self.assertIn("## file: app.py", rendered)
        self.assertIn("from mcqpy_shiny.embed_app import create_app", rendered)
        self.assertIn("## file: requirements.txt", rendered)
        self.assertIn("shiny>=1.2.1", rendered)
        self.assertIn("pyfiglet", rendered)
        self.assertIn(
            "https://example.github.io/pkg/mcqpy_shiny-0.1.0-py3-none-any.whl",
            rendered,
        )
        self.assertIn("fixed_url='https://example.com/quiz.json'", rendered)
        self.assertIn("fixed_token=None", rendered)


if __name__ == "__main__":
    unittest.main()
