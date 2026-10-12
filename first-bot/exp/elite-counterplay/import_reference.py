#!/usr/bin/env python3
"""Reuse every matching checked existing mass ledger; do not alter its cache.

New missing reference games are then reconstructed by extract.js reference.
Streaming, one process; full frozen population, never sampling.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
cache = ROOT / '.cache/elite-counterplay'
m = json.loads((cache / 'manifest.json').read_text())
tasks = {t['key']: t for t in m['tasks'] if t['src'] == 'top'}
out = cache / 'reference.jsonl'
if out.exists():
    raise SystemExit('Import output exists; never overwrite or duplicate it.')
n = 0
with (ROOT / '.cache/mass-ledger/top-sample.jsonl').open() as src, out.open('x') as dst:
    for line in src:
        if not line.strip():
            continue
        g = json.loads(line)
        task = tasks.pop(g['key'], None)
        if not task:
            continue
        if any(g['chk'].values()):
            raise ValueError(f"Invalid existing ledger {g['key']}")
        task = {k: v for k, v in task.items() if k != 'file'}
        dst.write(json.dumps({**g, **task, 'reusedLedger': True}, ensure_ascii=False, separators=(',', ':')) + '\n')
        n += 1
print(json.dumps({'imported': n, 'missing': len(tasks)}))
