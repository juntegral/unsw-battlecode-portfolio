"""Scratch (meow-main07): o1_mid on any smoke folder. Usage (repo root): o1_midrun.py <name> <folder under data/online/smoke>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
import o1_mid
name, folder = sys.argv[1], Path('data/online/smoke') / sys.argv[2]
n = 0
with open(o1_mid.OUT + 'o1_mid-%s.jsonl' % name, 'w') as f:
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        f.write(json.dumps(o1_mid.scan(name, rp, j), separators=(',', ':')) + '\n')
        n += 1
print('done', name, n)
