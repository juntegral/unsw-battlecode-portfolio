# Scratch (sweep brief): fields of dossier/per-game.jsonl, first row only.
import json

path = 'data/analysis/ladder/dossier/per-game.jsonl'
with open(path) as f:
    row = json.loads(f.readline())
for k, v in row.items():
    if k == 'ranges':
        continue
    print('TOP', k, json.dumps(v, ensure_ascii=True)[:200])
print('ranges:', list(row['ranges'].keys()))
r = row['ranges']['0-100']
for k, v in r.items():
    if k == 'visit_windows':
        print(k, 'list', len(v))
    else:
        print(k, json.dumps(v)[:170])
