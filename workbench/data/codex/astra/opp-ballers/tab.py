"""opp-ballers: every game vs team 1149, same script both sides. Run from ROOT: python3 data/codex/astra/opp-ballers/tab.py"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
import o1_scan
import qdeath
from pathlib import Path

OPP = 1149
VER = dict(l.split()[:2] for l in open('data/online/smoke/versions.tsv') if l.strip())
files = sorted(set(glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json')))
rows = []
for f in files:
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if OPP not in (j.get('teamAId'), j.get('teamBId')) or 1119 not in (j.get('teamAId'), j.get('teamBId')):
        continue
    mp = Path(f)
    gid = int(mp.stem.split('-')[1])
    rp = mp.parent / ('M%d.replay' % gid)
    if not rp.exists():
        print('no replay', gid)
        continue
    own = 0 if j['teamAId'] == 1119 else 1
    row = o1_scan.scan(mp.parent.name, rp, j)
    snaps = row['snaps']
    last = snaps[str(row['last'])] if str(row['last']) in snaps else snaps[sorted(snaps, key=int)[-1]]
    s100 = snaps.get('100')
    e = [sum(1 for x in row['eats'] if x[0] < 100 and x[1] == t and x[3] == 'n') for t in (0, 1)]
    qd = []
    for side in (own, 1 - own):
        try:
            q = qdeath.scan(rp, side)
            d = q['deaths'][0] if q['deaths'] else None
            qd.append((q['qalive'], q['qlen'], d))
        except Exception as ex:
            qd.append((None, None, repr(ex)[:60]))
    rows.append((j['completedAt'], gid, row, j, own, last, s100, e, qd))

rows.sort()
print('date  time  gid      ver    seat map                 res  how      rnd | Qend us/them | r100 pearls us/them | r100 dragons us/them | r100 len us/them')
for c, gid, row, j, own, last, s100, e, qd in rows:
    print('%s %s %d %-6s %s    %-19s %-4s %-8s %3d | %3s / %-3s | %3d / %-3d | %s / %s | %s / %s' % (
        c[5:10], c[11:16], gid, VER.get(str(row['bot']), row['bot']), 'AB'[own], j['mapName'][:19], row['result'].upper(), row['how'], row['last'],
        last[0][3], last[1][3], e[0], e[1],
        s100[0][0] if s100 else '-', s100[1][0] if s100 else '-', s100[0][1] if s100 else '-', s100[1][1] if s100 else '-'))
print()
keys = ['r', 'L', 'reason', 'own_turn', 'att', 'att_free', 'att_paid', 'att_portal', 'att_gap', 'seen_q', 'seen_mate', 'f0', 'f0a', 'f1', 'f1a', 'split0', 'split1', 'L0', 'closers', 'hit']
for c, gid, row, j, own, last, s100, e, qd in rows:
    for nm, q in zip(('OUR ', 'THEIR'), qd):
        d = q[2]
        if isinstance(d, dict):
            print(gid, nm, 'queen dead:', {k: d[k] for k in keys if k in d})
        elif d:
            print(gid, nm, 'err', d)
    for d in row['deaths']:
        if d[2] >= 8:
            print(gid, '  death side %s r%d L%d %s q=%d extra=%s' % ('us' if d[1] == 0 else 'them', d[0], d[2], d[4], d[6], d[18]))
n = len(rows)
w = sum(1 for r in rows if r[2]['result'] == 'win')
print('\noverall %d/%d' % (w, n))
for s in (0, 1):
    g = [r for r in rows if r[4] == s]
    print('seat', 'AB'[s], sum(1 for r in g if r[2]['result'] == 'win'), '/', len(g))
maps = {}
for r in rows:
    maps.setdefault(r[3]['mapName'], []).append(r[2]['result'] == 'win')
for m, v in sorted(maps.items()):
    print('map %-20s %d/%d' % (m, sum(v), len(v)))
