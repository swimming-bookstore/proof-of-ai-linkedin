#!/usr/bin/env python3
"""Render docs/linkedin.png (1080×1080) from docs/linkedin.html.

Block n is a story. Five words from that story seed the story in block
n+1. Each story is rated on a Goodreads-style star diagram.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "linkedin.html"
OUT = ROOT / "docs" / "linkedin.png"


def chromium() -> str:
    for name in ("chromium", "chromium-browser", "google-chrome"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("chromium is required to render docs/linkedin.html")


def main() -> None:
    if not HTML.is_file():
        raise SystemExit(f"missing {HTML}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "linkedin.png"
        subprocess.run(
            [
                chromium(),
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--hide-scrollbars",
                "--window-size=1080,1080",
                f"--screenshot={shot}",
                "--default-background-color=FFF9EF",
                HTML.resolve().as_uri(),
            ],
            check=True,
        )
        shutil.copyfile(shot, OUT)
    print(OUT)


if __name__ == "__main__":
    main()
