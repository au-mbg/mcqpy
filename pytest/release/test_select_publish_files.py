from pathlib import Path

from scripts.release.select_publish_files import (
    discover_artifacts,
    select_publishable_artifacts,
)


def test_discover_artifacts_parses_wheels_and_sdists(tmp_path: Path) -> None:
    wheel = tmp_path / "mcqpy_core-0.1.1-py3-none-any.whl"
    sdist = tmp_path / "mcqpy-core-0.1.1.tar.gz"
    wheel.write_text("", encoding="utf-8")
    sdist.write_text("", encoding="utf-8")

    artifacts = discover_artifacts(tmp_path)

    assert [(item.project_name, item.version, item.path.name) for item in artifacts] == [
        ("mcqpy-core", "0.1.1", "mcqpy-core-0.1.1.tar.gz"),
        ("mcqpy-core", "0.1.1", "mcqpy_core-0.1.1-py3-none-any.whl"),
    ]


def test_select_publishable_artifacts_skips_existing_versions(monkeypatch, tmp_path: Path) -> None:
    wheel_core = tmp_path / "mcqpy_core-0.1.1-py3-none-any.whl"
    sdist_core = tmp_path / "mcqpy-core-0.1.1.tar.gz"
    wheel_shiny = tmp_path / "mcqpy_shiny-0.1.2-py3-none-any.whl"
    wheel_core.write_text("", encoding="utf-8")
    sdist_core.write_text("", encoding="utf-8")
    wheel_shiny.write_text("", encoding="utf-8")

    artifacts = discover_artifacts(tmp_path)

    def fake_exists(project_name: str, version: str) -> bool:
        return (project_name, version) == ("mcqpy-core", "0.1.1")

    monkeypatch.setattr(
        "scripts.release.select_publish_files.package_version_exists",
        fake_exists,
    )

    selected = select_publishable_artifacts(artifacts)

    assert selected == [wheel_shiny]
