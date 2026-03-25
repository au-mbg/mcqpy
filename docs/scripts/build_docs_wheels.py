"""Copy built wheels into the docs site and generate a small wheel index."""

from __future__ import annotations

from pathlib import Path
from shutil import copy2


def _collect_wheels(root: Path) -> list[Path]:
    candidates = [
        root / "dist",
        root / "packages" / "mcqpy-core" / "dist",
        root / "packages" / "mcqpy-pdf" / "dist",
        root / "packages" / "mcqpy-shiny" / "dist",
    ]
    wheels: dict[str, Path] = {}
    for dist_dir in candidates:
        if not dist_dir.exists():
            continue
        for wheel in sorted(dist_dir.glob("*.whl")):
            wheels[wheel.name] = wheel
    return [wheels[name] for name in sorted(wheels)]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    docs_site_dir = root / "docs" / "site"
    wheels_dir = docs_site_dir / "wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)

    for existing in wheels_dir.glob("*.whl"):
        existing.unlink()

    wheels = _collect_wheels(root)
    if not wheels:
        raise SystemExit(
            "No wheels found in workspace dist directories. Build the packages first."
        )

    copied: list[Path] = []
    for wheel in wheels:
        target = wheels_dir / wheel.name
        copy2(wheel, target)
        copied.append(target)

    links = "\n".join(
        f'<li><a href="{wheel.name}">{wheel.name}</a></li>' for wheel in copied
    )
    index_html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>mcqpy wheel index</title>
  </head>
  <body>
    <h1>mcqpy wheel index</h1>
    <p>Temporary wheel index for browser-based Shinylive testing and branch preview deployments.</p>
    <ul>
{links}
    </ul>
  </body>
</html>
"""
    (wheels_dir / "index.html").write_text(index_html, encoding="utf-8")


if __name__ == "__main__":
    main()
