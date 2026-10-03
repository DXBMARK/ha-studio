#!/usr/bin/env python3
"""Print the CHANGELOG section for a version: release_notes.py 1.0.0 (c) 2026 DXBMARK LLC - Apache-2.0"""
import pathlib, re, sys
ver = sys.argv[1]
text = (pathlib.Path(__file__).resolve().parent.parent / 'CHANGELOG.md').read_text(encoding='utf-8')
m = re.search(rf'^## {re.escape(ver)}\b.*?$(.*?)(?=^## |\Z)', text, re.S | re.M)
if not m:
    sys.exit(f'no CHANGELOG section for {ver}')
print(m.group(1).strip())
