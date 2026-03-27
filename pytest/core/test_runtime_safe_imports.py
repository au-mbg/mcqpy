from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_shiny_used_core_subset_imports_without_optional_dependencies() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    core_src = repo_root / "packages" / "mcqpy-core" / "src"
    code = """
import builtins
import sys

real_import = builtins.__import__
blocked = {"numpy", "pandas", "matplotlib", "scipy", "yaml", "rich", "rich_click"}

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in blocked:
        raise ModuleNotFoundError(name)
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import

import mcqpy_core
from mcqpy_core.web import WebQuizBundle, decode_quiz_token, grade_web_quiz
from mcqpy_core.manifest import ManifestItem
from mcqpy_core.question import Question

assert mcqpy_core.Question is Question
assert WebQuizBundle is not None
assert decode_quiz_token is not None
assert grade_web_quiz is not None
assert ManifestItem is not None
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={"PYTHONPATH": str(core_src)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
