#!/usr/bin/env python3
"""Distribuie fișierele descărcate: cele mici → data/ (git), cele mari → release-assets/ (Releases).

Fișierele sub size_threshold_bytes sunt copiate în data/{category}/ și committed direct.
Fișierele peste threshold sunt copiate în release-assets/ și uplodate ca release assets.
Manifest-ul e actualizat cu storage și local_path / release_url.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="tmp", help="Directory with downloaded files")
    parser.add_argument("--release-tag", default=None,
                        help="Release tag for URL generation (e.g. 2025.1)")
    parser.add_argument("--repo", default=None,
                        help="GitHub repo as owner/name for release URL generation")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    threshold = manifest["size_threshold_bytes"]

    src_dir = repo_root / args.src
    data_dir = repo_root / "data"
    release_dir = repo_root / "release-assets"
    release_dir.mkdir(exist_ok=True)

    repo_slug = args.repo or os.environ.get("GITHUB_REPOSITORY")
    release_tag = args.release_tag or os.environ.get("RELEASE_TAG")

    counts = {"git": 0, "release": 0, "missing": 0}
    git_size = 0
    release_size = 0

    for f in manifest["files"]:
        src = src_dir / f["category"] / f["filename"]
        if not src.exists():
            counts["missing"] += 1
            continue

        size = f["size_bytes"] or src.stat().st_size

        if size <= threshold:
            dst = data_dir / f["category"] / f["filename"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            f["storage"] = "git"
            f["local_path"] = str(dst.relative_to(repo_root))
            f["release_url"] = None
            counts["git"] += 1
            git_size += size
        else:
            dst = release_dir / f["filename"]
            shutil.copy2(src, dst)
            f["storage"] = "release"
            f["local_path"] = None
            if repo_slug and release_tag:
                f["release_url"] = (
                    f"https://github.com/{repo_slug}/releases/download/"
                    f"{release_tag}/{f['filename']}"
                )
            counts["release"] += 1
            release_size += size

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"Git:     {counts['git']:3d} files, {git_size / 1024 / 1024:8.1f} MB")
    print(f"Release: {counts['release']:3d} files, {release_size / 1024 / 1024:8.1f} MB")
    if counts["missing"]:
        print(f"Missing: {counts['missing']:3d} files (run download_all.py first)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
