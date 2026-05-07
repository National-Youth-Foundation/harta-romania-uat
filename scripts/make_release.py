#!/usr/bin/env python3
"""Creează (sau actualizează) un GitHub Release și uploadează fișierele din release-assets/.

Folosește `gh` CLI (deja disponibil în GitHub Actions și instalabil local).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Release tag, e.g. 2025.1")
    parser.add_argument("--title", default=None, help="Release title")
    parser.add_argument("--notes", default=None, help="Release notes (markdown)")
    parser.add_argument("--assets-dir", default="release-assets")
    parser.add_argument("--repo", default=None, help="owner/name; defaults to GITHUB_REPOSITORY env")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    assets_dir = repo_root / args.assets_dir
    files = sorted(assets_dir.glob("*")) if assets_dir.exists() else []
    if not files:
        print(f"No assets in {assets_dir}; nothing to release.")
        return 0

    repo = args.repo or os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("ERROR: --repo or GITHUB_REPOSITORY required")
        return 2

    title = args.title or f"Limite administrative România {args.tag}"
    notes = args.notes or (
        f"Mirror al datelor administrative din România - versiunea {args.tag}.\n\n"
        "Sursă: https://geo-spatial.org/descarcare/date/administrative-boundaries/\n"
        "Licență: CC BY-SA 4.0\n\n"
        "Acest release conține fișierele mari (>25 MB). Fișierele mici sunt în repo "
        "sub `data/`. Vezi `manifest.json` pentru indexul complet."
    )

    check = subprocess.run(
        ["gh", "release", "view", args.tag, "--repo", repo],
        capture_output=True, text=True,
    )
    if check.returncode == 0:
        print(f"Release {args.tag} already exists; uploading assets with --clobber.")
        cmd = ["gh", "release", "upload", args.tag, "--repo", repo, "--clobber"]
        cmd.extend(str(f) for f in files)
        result = run(cmd)
        return result.returncode

    cmd = ["gh", "release", "create", args.tag,
           "--repo", repo, "--title", title, "--notes", notes]
    cmd.extend(str(f) for f in files)
    result = run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
