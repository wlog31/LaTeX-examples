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
    entries = []
    folder = resolve_folder(folder)
    if not os.path.isdir(folder):
        return entries
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".tex"):
            continue
        name = fname[:-4]
        def maybe(ext, _f=folder, _n=name):
            p = f"{_f}/{_n}.{ext}"
            return p if os.path.isfile(p) else None
        entries.append({
            "name": name,
            "tex": f"{folder}/{name}.tex",
            "pdf": maybe("pdf"),
            "svg": maybe("svg"),
        })
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
