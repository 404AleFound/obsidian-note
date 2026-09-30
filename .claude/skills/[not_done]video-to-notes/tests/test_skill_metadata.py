from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = SKILL_ROOT / "SKILL.md"
README_PATH = SKILL_ROOT / "README.md"


class SkillMetadataTests(unittest.TestCase):
    def test_bare_url_trigger_is_at_start_of_description(self) -> None:
        lines = SKILL_PATH.read_text(encoding="utf-8").splitlines()
        description = next(
            line.removeprefix("description: ")
            for line in lines
            if line.startswith("description: ")
        )

        discovery_prefix = description[:200].lower()
        self.assertIn("youtube", discovery_prefix)
        self.assertIn("bilibili", discovery_prefix)
        self.assertIn("不要问", description)  # 裸链接立即处理，不要问用户

    def test_skill_is_concise_and_points_to_readme(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertLessEqual(len(text.splitlines()), 150)
        self.assertIn("[README.md](README.md)", text)
        self.assertTrue(README_PATH.is_file())

    def test_processing_is_local_until_report_is_complete(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn('run.py process "VIDEO_URL" --environment local', text)
        self.assertIn("不要停在 `process`", text)
        self.assertIn("绝不拿网页搜索片段", text)

    def test_readme_documents_model_weights(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")

        self.assertIn("large-v3-turbo", text)
        self.assertIn("uv sync --extra whisper", text)


if __name__ == "__main__":
    unittest.main()
