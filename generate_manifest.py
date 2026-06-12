#!/usr/bin/env python3
"""
generate_manifest.py
────────────────────
graphics/, documents/, preambles/ 를 스캔하여 index.html이 읽는
files.json 매니페스트를 생성합니다.

GitHub Actions 워크플로에서 TeX 컴파일 후 실행:
    python3 generate_manifest.py
"""

import json
import os
from datetime import datetime, timezone

FOLDERS = ["graphics", "documents", "preambles"]


def scan(folder: str) -> list:
    """Return a list of file entries for .tex files found in `folder`."""
    entries = []
    if not os.path.isdir(folder):
        return entries

    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".tex"):
            continue
        name = fname[:-4]  # strip .tex

        def maybe(ext):
            p = f"{folder}/{name}.{ext}"
            return p if os.path.isfile(p) else None

        entries.append({
            "name": name,
            "tex":  f"{folder}/{name}.tex",
            "pdf":  maybe("pdf"),
            "svg":  maybe("svg"),
        })

    return entries


manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "folders": {f: scan(f) for f in FOLDERS},
}

with open("files.json", "w", encoding="utf-8") as fp:
    json.dump(manifest, fp, ensure_ascii=False, indent=2)

total = sum(len(v) for v in manifest["folders"].values())
print(f"✓ files.json 생성 완료 — 총 {total}개 파일")
for folder, files in manifest["folders"].items():
    for f in files:
        flags = []
        if f["pdf"]: flags.append("pdf")
        if f["svg"]: flags.append("svg")
        flag_str = f"  [{', '.join(flags)}]" if flags else ""
        print(f"  {folder}/{f['name']}.tex{flag_str}")
