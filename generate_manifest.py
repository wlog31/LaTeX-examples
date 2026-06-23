#!/usr/bin/env python3
"""generate_manifest.py"""

import json
import os
from datetime import datetime, timezone

FOLDERS = ["tikz", "documents", "preambles"]


def resolve_folder(name):
    """Return the actual filesystem name for folder `name` (case-insensitive)."""
    for entry in os.listdir("."):
        if entry.lower() == name.lower() and os.path.isdir(entry):
            return entry
    return name


def scan(folder):
    """Recursively scan `folder` for .tex files, any depth of subfolders included.

    entry["name"] is the path relative to `folder` (no extension, '/' separated),
    e.g. "circle.tex" -> "circle", "geometry/circle.tex" -> "geometry/circle".
    """
    entries = []
    folder = resolve_folder(folder)
    if not os.path.isdir(folder):
        return entries
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames.sort()
        rel_dir = os.path.relpath(dirpath, folder)
        for fname in sorted(filenames):
            if not fname.endswith(".tex"):
                continue
            name_only = fname[:-4]
            rel_name = name_only if rel_dir == "." else f"{rel_dir}/{name_only}".replace(os.sep, "/")

            def maybe(ext, _d=dirpath, _n=name_only):
                p = os.path.join(_d, f"{_n}.{ext}")
                return p.replace(os.sep, "/") if os.path.isfile(p) else None

            entries.append({
                "name": rel_name,
                "tex": os.path.join(dirpath, fname).replace(os.sep, "/"),
                "pdf": maybe("pdf"),
                "svg": maybe("svg"),
            })
    entries.sort(key=lambda e: e["name"])
    return entries


manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "folders": {f: scan(f) for f in FOLDERS},
}

with open("files.json", "w", encoding="utf-8") as fp:
    json.dump(manifest, fp, ensure_ascii=False, indent=2)

total = sum(len(v) for v in manifest["folders"].values())
print(f"Done: {total} files")
for folder, files in manifest["folders"].items():
    for f in files:
        flags = [x for x in ("pdf", "svg") if f[x]]
        flag_str = "  [" + ", ".join(flags) + "]" if flags else ""
        print(f"  {folder}/{f['name']}.tex{flag_str}")
