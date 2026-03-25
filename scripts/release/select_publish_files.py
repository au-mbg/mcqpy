"""Select built distributions that still need to be uploaded to PyPI."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


@dataclass(frozen=True)
class DistributionArtifact:
    path: Path
    project_name: str
    version: str


_SDIST_RE = re.compile(r"^(?P<name>.+)-(?P<version>\d[^/]*)\.tar\.gz$")


def canonicalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_wheel_filename(filename: str) -> tuple[str, str]:
    parts = filename.split("-")
    if len(parts) < 5 or not filename.endswith(".whl"):
        raise ValueError(f"Unsupported wheel filename: {filename}")
    return parts[0], parts[1]


def parse_sdist_filename(filename: str) -> tuple[str, str]:
    match = _SDIST_RE.match(filename)
    if match is None:
        raise ValueError(f"Unsupported source distribution filename: {filename}")
    return match.group("name"), match.group("version")


def discover_artifacts(dist_dir: Path) -> list[DistributionArtifact]:
    artifacts: list[DistributionArtifact] = []
    for path in sorted(dist_dir.iterdir()):
        if path.suffix == ".whl":
            name, version = parse_wheel_filename(path.name)
            artifacts.append(
                DistributionArtifact(
                    path=path,
                    project_name=canonicalize_name(name),
                    version=version,
                )
            )
        elif path.suffixes[-2:] == [".tar", ".gz"]:
            name, version = parse_sdist_filename(path.name)
            artifacts.append(
                DistributionArtifact(
                    path=path,
                    project_name=canonicalize_name(name),
                    version=version,
                )
            )
    return artifacts


def package_version_exists(project_name: str, version: str) -> bool:
    url = f"https://pypi.org/pypi/{project_name}/{version}/json"
    try:
        with urlopen(url, timeout=20) as response:  # noqa: S310
            payload = json.load(response)
    except HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    return payload.get("info", {}).get("version") == version


def select_publishable_artifacts(artifacts: list[DistributionArtifact]) -> list[Path]:
    grouped: dict[tuple[str, str], list[DistributionArtifact]] = defaultdict(list)
    for artifact in artifacts:
        grouped[(artifact.project_name, artifact.version)].append(artifact)

    selected: list[Path] = []
    for (project_name, version), group in sorted(grouped.items()):
        if package_version_exists(project_name, version):
            continue
        selected.extend(artifact.path for artifact in sorted(group, key=lambda item: item.path.name))
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List built distribution files whose package version is not yet on PyPI."
    )
    parser.add_argument(
        "--dist-dir",
        default="dist",
        help="Directory containing built wheels and source distributions.",
    )
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    artifacts = discover_artifacts(dist_dir)
    selected = select_publishable_artifacts(artifacts)
    for path in selected:
        print(path)


if __name__ == "__main__":
    main()
