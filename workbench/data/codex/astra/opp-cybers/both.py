"""opp-cybers: every game against team 1148, both sides with the same scanners. Usage (ROOT): python3 -B both.py"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
import o1_scan
import qdeath
from pathlib import Path

OPP = 1148
VERS = dict(l.split() for l in open('data/online/smoke/versions.tsv').read().splitlines() if l.strip())
files = sorted(glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json'))
rows = []
for f in files:
    j = json.load(open(f))
    if OPP not in (j.get('teamAId'), j.get('teamBId')):
        continue
    mp = Path(f)
    rp = mp.parent / ('M%d.replay' % j['id'])
    if not rp.exists():
        print('no replay', f)
        continue
    own = 0 if j['teamAId'] == 1119 else 1
    row = o1_scan.scan(mp.parent.name, rp, j)
    s100 = row['snaps'].get('100')
    last = row['snaps'][sorted(row['snaps'], key=int)[-1]]
    nat = [sum(1 for e in row['eats'] if e[0] < 100 and e[1] == s and e[3] == 'n') for s in (0, 1)]
    qd = []
    for s in (own, 1 - own):
        try:
            d = qdeath.scan(rp, s)
        except Exception as ex:
            d = 'ERR %r' % ex
        qd.append(d)
    rows.append((j, own, row, s100, last, nat, qd, mp.parent.name))
    print('%s %s bot %s(%s) seat %s %-10s %-4s how %-8s last r%d | endQ us %d them %d | end top us %d them %d | r100 nat us %d them %d dragons us %s them %s len us %s them %s' % (
        j['completedAt'][5:16], mp.parent.name, row['bot'], VERS.get(str(row['bot']), '?'), 'AB'[own], j['mapName'], row['result'], row['how'], row['last'],
        last[0][3], last[1][3], last[0][2], last[1][2], nat[0], nat[1],
        s100[0][0] if s100 else '-', s100[1][0] if s100 else '-', s100[0][1] if s100 else '-', s100[1][1] if s100 else '-'))
    KEYS = ['r', 'L', 'reason', 'h', 'own_turn', 'att', 'att_free', 'att_paid', 'att_gap', 'att_is_queen', 'opts', 'f0', 'f1', 'seen_q', 'seen_mate', 'viap', 'hit', 'n_mates']
    for nm, d in (('our Q', qd[0]), ('their Q', qd[1])):
        if isinstance(d, str) or d is None:
            print('   %s: %s' % (nm, d))
            continue
        print('   %s: alive %s len %s' % (nm, d['qalive'], d['qlen']), [{k: x[k] for k in KEYS if k in x} for x in d['deaths']])
    from collections import Counter
    for s2, nm in ((0, 'our'), (1, 'their')):
        c = Counter((d[4], 'early' if d[0] < 150 else 'late') for d in row['deaths'] if d[1] == s2)
        print('   %s dragon deaths by kind:' % nm, sorted(c.items(), key=lambda kv: -kv[1])[:8])
    tops = {r: (row['snaps'][r][0][2], row['snaps'][r][1][2]) for r in ('350', '400', '425', '450', '475') if r in row['snaps']}
    print('   longest us/them at', tops)
n = len(rows)
w = sum(1 for r in rows if r[2]['result'] == 'win')
print('TOTAL %d games, wins %d' % (n, w))
for seat in (0, 1):
    g = [r for r in rows if r[1] == seat]
    print(' seat %s: %d/%d' % ('AB'[seat], sum(1 for r in g if r[2]['result'] == 'win'), len(g)))
maps = {}
for r in rows:
    maps.setdefault(r[0]['mapName'], []).append(r[2]['result'])
for m, v in sorted(maps.items()):
    print(' map %-10s %s' % (m, ' '.join(v)))
