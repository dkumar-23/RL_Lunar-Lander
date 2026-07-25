"""Static verification for the controlled Colab training notebook."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, ClassVar


class ColabNotebookTests(unittest.TestCase):
    """Ensure the notebook stays thin, clean, and provenance-aware."""

    path: ClassVar[Path]
    notebook: ClassVar[dict[str, Any]]
    source: ClassVar[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.path = Path("notebooks/train_colab.ipynb")
        cls.notebook = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.source = "\n".join(
            "".join(cell.get("source", [])) for cell in cls.notebook["cells"]
        )

    def test_notebook_has_no_committed_outputs(self) -> None:
        for cell in self.notebook["cells"]:
            if cell.get("cell_type") == "code":
                self.assertIsNone(cell.get("execution_count"))
                self.assertEqual(cell.get("outputs"), [])

    def test_notebook_requires_exact_commit(self) -> None:
        self.assertIn("GIT_COMMIT_SHA", self.source)
        self.assertIn('checkout", "--detach', self.source)
        self.assertIn("resolved_commit != GIT_COMMIT_SHA", self.source)

    def test_notebook_uses_drive_and_colab_full_context(self) -> None:
        self.assertIn("drive.mount", self.source)
        self.assertIn("/content/drive", self.source)
        self.assertIn("colab-full", self.source)

    def test_notebook_clones_approved_repository(self) -> None:
        self.assertIn("https://github.com/dkumar-23/RL_Lunar-Lander", self.source)

    def test_notebook_delegates_to_versioned_training_entrypoint(self) -> None:
        self.assertIn('"-m", "scripts.train"', self.source)
        self.assertIn('"--execution-context", "colab-full"', self.source)


if __name__ == "__main__":
    unittest.main()
