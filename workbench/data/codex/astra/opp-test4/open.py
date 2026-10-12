"""opp-test4: opening and queen table for ranked games. Run from ROOT."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan
from pathlib import Path

for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json')):
    j = json.load(open(f))
    if 19 not in (j.get('teamAId'), j.get('teamBId')):
        continue
    mp = Path(f)
    row = o1_scan.scan(mp.parent.name, mp.parent / ('M%d.replay' % j['id']), j)
    sp = row['splits']
    fs = [min([x[0] for x in sp if x[1] == s] or [-1]) for s in (0, 1)]
    n50 = [sum(1 for x in sp if x[1] == s and x[0] < 50) for s in (0, 1)]
    n100 = [sum(1 for x in sp if x[1] == s and x[0] < 100) for s in (0, 1)]
    qs = [sum(1 for x in sp if x[1] == s and x[5] and x[0] < 100) for s in (0, 1)]
    sn = row['snaps']
    line = ' '.join('r%s n%d/%d Q%d/%d top%d/%d' % (r, sn[r][0][0], sn[r][1][0], sn[r][0][3], sn[r][1][3], sn[r][0][2], sn[r][1][2]) for r in ('25', '50', '100', '150', '200', '300') if r in sn)
    print(j['id'], j['mapName'][:10], row['result'], 'first split us r%d them r%d | splits<50 %d/%d <100 %d/%d | queen splits<100 %d/%d' % (fs[0], fs[1], n50[0], n50[1], n100[0], n100[1], qs[0], qs[1]))
    print('    ', line)
    rams = [d for d in row['deaths'] if d[4] == 'rammed' and d[0] < 200]
    for s in (0, 1):
        v = [d for d in rams if d[1] == s]
        paid = sum(1 for d in v if d[18] and d[18][2] > 0)
        print('     %s dragons rammed before r200: %d (attacker paid in %d), of them len>=4: %d' % (('our', 'their')[s], len(v), paid, sum(1 for d in v if d[2] >= 4)))
    pd = row['paids']
    print('     paids sample', pd[:2] if pd else None, 'n', len(pd))
