"""Scratch (diag-wipeout): premise check. Who is eliminated in the online games (agg7-games.json rows) and in the
two ladder per-game files. Usage: python3 data/analysis/ladder/dossier/work/wo_prem.py"""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter
from pathlib import Path

DOS = Path('data/analysis/ladder/dossier')


def size(c):
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


rows = json.loads((DOS / 'online/agg7-games.json').read_text())
print('online rows', len(rows), Counter(r['label'] for r in rows))
for r in sorted(rows, key=lambda r: (r['label'], r['game'])):
    f, t = r['final'], r['their']
    tag = 'WE-OUT' if f['alive'] == 0 else 'THEY-OUT' if t['alive'] == 0 else ''
    print(r['label'], r['game'], r['opponent'][:14].ljust(14), r['map'][:16].ljust(16), r['cells'], r['result'].ljust(5),
          'us a/L/T/q', f['alive'], f['longest'], f['total'], f['queen_length'],
          'them', t['alive'], t['longest'], t['total'], t['queen_length'], r['extra']['decided'], tag)
for label in sorted(set(r['label'] for r in rows)):
    rs = [r for r in rows if r['label'] == label]
    for op in sorted(set(r['opponent'] for r in rs)):
        q = [r for r in rs if r['opponent'] == op]
        print(label, op, 'games', len(q), 'wins', sum(r['result'] == 'win' for r in q),
              'we eliminated', sum(r['final']['alive'] == 0 for r in q),
              'they eliminated', sum(r['their']['alive'] == 0 for r in q),
              'we out by size', dict(Counter(size(r['cells']) for r in q if r['final']['alive'] == 0)))

for name, path in (('ours-ladder', DOS / 'per-game.jsonl'), ('rank1', DOS / 'target/per-game-top1.jsonl')):
    allrows = [json.loads(x) for x in path.read_text().splitlines()]
    us = [r for r in allrows if r['relation'] == 'us']
    print(name, 'rows', len(allrows), 'us rows', len(us), 'keys', sorted(us[0].keys())[:60])
    print(' ended_by', Counter((r['ended_by'], r['result']) for r in us))
    out = [r for r in us if r['final_reconstructed']['alive'] == 0]
    print(' we out', len(out), 'of', len(us), 'by size', Counter(size(r['cells']) for r in out), 'games by size',
          Counter(size(r['cells']) for r in us))
