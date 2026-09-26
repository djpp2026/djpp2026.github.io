#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "videos.json"
URL = ""  # Isi URL videos.json lama jika memang ingin melakukan migrasi.

if json.loads(DATA.read_text(encoding="utf-8") or "[]"):
    print("videos.json sudah berisi data; migrasi dilewati.")
    raise SystemExit

if not URL:
    print("URL legacy belum dikonfigurasi; migrasi dilewati.")
    raise SystemExit

with urllib.request.urlopen(URL, timeout=20) as r:
    old = json.load(r)

new = []
for v in old:
    x = dict(v)
    x.setdefault("jam", "00:00")
    new.append(x)

DATA.write_text(
    json.dumps(new, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)
print(f"Imported {len(new)} legacy records.")
