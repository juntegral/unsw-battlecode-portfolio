import sys, json
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan

OUT = Path(__file__).resolve().parent
for label in ('one5-w1', 'one5-c1', 'one3-w1'):
    path = OUT / (label + '-ledger.jsonl')
    if path.exists():
        continue
    with path.open('w') as out:
        for mp in sorted((Path('data/online/smoke') / (label+'-old')).glob('game-*.json')):
            j = json.loads(mp.read_text())
            row = o1_scan.scan(label, mp.with_name('M%d.replay' % j['id']), j)
            for side in (0, 1):
                a = row['snaps'].get('100', row['ends'])[side]
                b = row['snaps'].get('300', row['ends'])[side]
                eats = sum(101 <= e[0] <= 300 and e[1] == side for e in row['eats'])
                dead = sum(d[2] for d in row['deaths'] if 101 <= d[0] <= 300 and d[1] == side)
                paid = sum(d[3] for d in row['paids'] if 101 <= d[0] <= 300 and d[1] == side)
                splits = sum(101 <= d[0] <= 300 and d[1] == side for d in row['splits'])
                deaths = sum(101 <= d[0] <= 300 and d[1] == side for d in row['deaths'])
                assert b[1] - a[1] == eats-dead-paid, (j['id'], side, 'length')
                assert b[0] - a[0] == splits-deaths, (j['id'], side, 'heads')
            out.write(json.dumps(row, separators=(',', ':'))+'\n')
            out.flush()
            print(label, j['id'], flush=True)
