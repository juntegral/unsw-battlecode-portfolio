"""loss15-sonnet: r100 table. Usage (via run.sh): r100.py <label> [<label> ...]   labels = smoke set names without -old (e.g. one15-c1 one14-c1)
Per game: map, result, our dragons / total length / natural pearls eaten before r100 (and the same for them), our splits < r100."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan
from pathlib import Path

for label in sys.argv[1:]:
    folder = Path('data/online/smoke') / (label + '-old')
    out = {}
    for mp in sorted(folder.glob('game-*.json')):
        j = json.load(open(mp))
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        row = o1_scan.scan(label, rp, j)
        s = row['snaps'].get('100')
        if not s:
            out[j['mapName']] = (j['id'], row['bot'], row['result'], 'ended before r100 (last r%d)' % row['last'])
            continue
        nat = [sum(1 for e in row['eats'] if e[0] < 100 and e[1] == k and e[3] == 'n') for k in (0, 1)]
        sp = sum(1 for x in row['splits'] if x[1] == 0 and x[0] < 100)
        out[j['mapName']] = (j['id'], row['bot'], row['result'], 'us n%d tot%d nat%d spl%d | them n%d tot%d nat%d' % (s[0][0], s[0][1], nat[0], sp, s[1][0], s[1][1], nat[1]))
    print('###', label)
    for m, v in sorted(out.items()):
        print('%-14s %s' % (m, ' '.join(map(str, v))))
