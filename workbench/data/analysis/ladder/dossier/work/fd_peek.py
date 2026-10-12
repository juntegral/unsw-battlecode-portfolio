# Scratch (diag-feeding): look at the row schema and how main games end. Read-only.
import json
from collections import Counter

rows = [json.loads(l) for l in open('data/analysis/ladder/rows.jsonl')]
r = rows[0]
for k, v in r.items():
    print(k, '=', v if not isinstance(v, (dict, list)) else (type(v).__name__, list(v)[:12]))
print(r['curves']['end'], r.get('queen'))
m = [r for r in rows if r['our_code'] == 'main']
print(len(m), Counter(r['ended_by'] for r in m), Counter(r['result'] for r in m))
print(Counter((r['ended_by'], r['result']) for r in m))
print('reach 201/301/401:', sum(r['last_round'] >= 201 for r in m), sum(r['last_round'] >= 301 for r in m),
      sum(r['last_round'] >= 401 for r in m))
print(Counter(r['last_round'] for r in m).most_common(5))
pg = [json.loads(l) for l in open('data/analysis/ladder/dossier/per-game.jsonl')]
print(len(pg), len(set(x['game'] for x in pg)))
