#!/usr/bin/env python3
"""Descarcă toate fișierele upstream în ./tmp/, calculează SHA256 și actualizează manifest.json.

Folosește doar stdlib (urllib + threading) ca să ruleze fără dependențe în GitHub Actions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

CHUNK = 1024 * 256


def download_one(file_meta: dict, out_dir: Path, *, force: bool) -> dict[str, Any]:
    url = file_meta["upstream_url"]
    target = out_dir / file_meta["category"] / file_meta["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not force and file_meta.get("sha256"):
        h = hashlib.sha256()
        with target.open("rb") as fh:
            for chunk in iter(lambda: fh.read(CHUNK), b""):
                h.update(chunk)
        if h.hexdigest() == file_meta["sha256"]:
            return {"status": "cached", "size": target.stat().st_size,
                    "sha256": file_meta["sha256"], "path": str(target)}

    h = hashlib.sha256()
    size = 0
    req = urllib.request.Request(url, headers={"User-Agent": "harta-romania-uat-mirror/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, target.open("wb") as out:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)
                h.update(chunk)
                size += len(chunk)
    except (urllib.error.URLError, TimeoutError) as e:
        return {"status": "error", "error": str(e)}

    return {"status": "downloaded", "size": size,
            "sha256": h.hexdigest(), "path": str(target)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="tmp", help="Output directory (default: tmp)")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--force", action="store_true", help="Re-download even if hash matches")
    parser.add_argument("--filter", help="Only files whose category or filename contains this string")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    out_dir = repo_root / args.out

    targets = manifest["files"]
    if args.filter:
        targets = [f for f in targets
                   if args.filter in f["category"] or args.filter in f["filename"]]
    print(f"Downloading {len(targets)} files into {out_dir} with {args.workers} workers")

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_one, f, out_dir, force=args.force): f for f in targets}
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            f = futures[fut]
            res = fut.result()
            results[f["upstream_url"]] = res
            done += 1
            tag = res["status"]
            if tag == "error":
                print(f"  [{done}/{total}] ERROR {f['filename']}: {res['error']}")
            else:
                kb = res["size"] / 1024
                print(f"  [{done}/{total}] {tag:>10} {kb:>10,.1f}KB  {f['category']}/{f['filename']}")

    errors = [r for r in results.values() if r["status"] == "error"]
    for f in manifest["files"]:
        res = results.get(f["upstream_url"])
        if res and res["status"] != "error":
            f["size_bytes"] = res["size"]
            f["sha256"] = res["sha256"]
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"\nDone. {len(results) - len(errors)} ok, {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
