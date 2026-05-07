#!/usr/bin/env python3
"""Generează manifest.json cu lista completă a fișierelor upstream."""

from __future__ import annotations

import json
import sys
from pathlib import Path

UPSTREAM_BASE = "https://services.geo-spatial.org/data/administrative_boundaries"
FORMATS = ["gpkg", "zip", "parquet", "fgb", "geojson", "topojson", "kml"]

CATEGORIES: dict[str, list[str]] = {
    "country": [
        "polygon", "simplified_polygon", "line", "simplified_line",
    ],
    "macroregion": [
        "polygon", "line", "simplified_polygon", "simplified_line",
    ],
    "region": [
        "polygon", "line", "simplified_polygon", "simplified_line",
    ],
    "county": [
        "polygon", "line", "simplified_polygon", "simplified_line",
    ],
    "lau": [
        "polygon", "line",
        "simplified_polygon", "simplified_line",
        "bucharest_merged_polygon", "bucharest_merged_line",
        "simplified_bucharest_merged_polygon", "simplified_bucharest_merged_line",
    ],
}


def build_files() -> list[dict]:
    files: list[dict] = []
    for category, variants in CATEGORIES.items():
        for variant in variants:
            for fmt in FORMATS:
                stem = f"ro_admin_{category}_{variant}" if category != "country" \
                    else f"ro_admin_country_{variant}"
                filename = f"{stem}.{fmt}"
                files.append({
                    "category": category,
                    "variant": variant,
                    "format": fmt,
                    "filename": filename,
                    "upstream_url": f"{UPSTREAM_BASE}/{category}/{filename}",
                    "size_bytes": None,
                    "sha256": None,
                    "storage": None,
                    "local_path": None,
                    "release_url": None,
                })
    return files


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "manifest.json"

    files = build_files()
    manifest = {
        "schema_version": 1,
        "upstream_source": "https://geo-spatial.org/descarcare/date/administrative-boundaries/",
        "upstream_base": UPSTREAM_BASE,
        "license": "CC-BY-SA-4.0",
        "attribution": (
            "Date prelucrate de comunitatea geo-spatial.org pe baza datelor publice "
            "puse la dispoziție de Agenția Națională de Cadastru și Publicitate Imobiliară "
            "(ANCPI) și Institutul Național de Statistică (INS)."
        ),
        "size_threshold_bytes": 25 * 1024 * 1024,
        "categories": list(CATEGORIES.keys()),
        "formats": FORMATS,
        "file_count": len(files),
        "files": files,
    }

    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        existing_by_url = {f["upstream_url"]: f for f in existing.get("files", [])}
        for f in manifest["files"]:
            old = existing_by_url.get(f["upstream_url"])
            if old:
                for key in ("size_bytes", "sha256", "storage", "local_path", "release_url"):
                    if old.get(key) is not None:
                        f[key] = old[key]

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {manifest_path} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
