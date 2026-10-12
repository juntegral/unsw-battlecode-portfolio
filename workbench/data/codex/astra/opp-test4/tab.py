"""opp-test4: every game vs team 19. Run from ROOT: python3 data/codex/astra/opp-test4/tab.py"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
import o1_scan
import qdeath
from pathlib import Path
from collections import defaultdict

OPP = 19
MINID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
ver = {}
try:
    for ln in open('data/online/smoke/versions.tsv'):
        p = ln.rstrip('\n').split('\t')
        if len(p) >= 2:
            ver[p[0]] = p[1]
            ver[p[1]] = p[0]
except Exception as ex:
    print('versions err', ex)

files = glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json')
games = {}
for f in files:
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if OPP in (j.get('teamAId'), j.get('teamBId')) and 1119 in (j.get('teamAId'), j.get('teamBId')):
        games[j['id']] = (Path(f), j)

rows = []
for gid in sorted(g for g in games if g >= MINID):
    mp, j = games[gid]
    rp = mp.parent / ('M%d.replay' % gid)
    if not rp.exists():
        print('no replay', gid, mp.parent.name, j.get('winner'), j.get('mapName'))
        continue
    own = 0 if j['teamAId'] == 1119 else 1
    try:
        row = o1_scan.scan(mp.parent.name, rp, j)
    except Exception as ex:
        print('scan err', gid, repr(ex)[:100])
        continue
    e = [sum(1 for x in row['eats'] if x[0] < 100 and x[1] == s and x[3] == 'n') for s in (0, 1)]
    s100 = row['snaps'].get('100')
    last = row['snaps'][sorted(row['snaps'], key=int)[-1]]
    qd = ''
    try:
        q = qdeath.scan(rp, own)
        for d in q['deaths']:
            qd += 'r%s L%s %s att=%s paid=%s gap=%s ownturn=%s; ' % (d.get('r'), d.get('L'), d.get('reason'), d.get('att'), d.get('att_paid'), d.get('att_gap'), d.get('own_turn'))
    except Exception as ex:
        qd = 'qerr'
    tq = ''
    try:
        q2 = qdeath.scan(rp, 1 - own)
        for d in q2['deaths']:
            tq += 'r%s L%s %s att=%s paid=%s; ' % (d.get('r'), d.get('L'), d.get('reason'), d.get('att'), d.get('att_paid'))
    except Exception as ex:
        tq = 'qerr'
    r = dict(gid=gid, date=j['completedAt'][5:16], set=mp.parent.name, bot=row['bot'], v=ver.get(str(row['bot']), '?'), seat='AB'[own],
             map=j['mapName'], res=row['result'], how=row['how'], last=row['last'], cells=row['cells'],
             qus=last[0][3], qth=last[1][3], nus=last[0][0], nth=last[1][0], tus=last[0][1], tth=last[1][1],
             p_us=e[0], p_th=e[1], d_us=s100[0][0] if s100 else None, d_th=s100[1][0] if s100 else None, qd=qd, tq=tq,
             ranked=j['ranked'], elo=(j['teamAElo'], j['teamBElo']), ch=j.get('eloChangeA'))
    rows.append(r)
    print('%d %s %-18s bot%s(%s) seat%s %-12s c%-4s %s how=%s last=%s | Qend us %s them %s | n %s/%s tot %s/%s | r100 pearls %s/%s dragons %s/%s' % (
        gid, r['date'], r['set'][:18], r['bot'], r['v'], r['seat'], r['map'][:12], r['cells'], r['res'].upper(), r['how'], r['last'],
        r['qus'], r['qth'], r['nus'], r['nth'], r['tus'], r['tth'], r['p_us'], r['p_th'], r['d_us'], r['d_th']))
    if qd:
        print('      OUR Q DEAD:', qd)
    if tq:
        print('      THEIR Q DEAD:', tq)

json.dump(rows, open('data/codex/astra/opp-test4/rows.json', 'w'), default=str)


def wr(sel, name):
    w = sum(1 for r in sel if r['res'] == 'w')
    print('%-28s %d/%d' % (name, w, len(sel)))


print()
for scope, sel in (('ALL', rows), ('ranked', [r for r in rows if r['ranked']]), ('since one1 (bot>=21000)', [r for r in rows if str(r['bot']).isdigit() and int(r['bot']) >= 21000])):
    wr(sel, scope)
    for s in 'AB':
        wr([r for r in sel if r['seat'] == s], scope + ' seat ' + s)
bm = defaultdict(list)
for r in rows:
    bm[r['map']].append(r)
for m in sorted(bm):
    if len(bm[m]) >= 2:
        wr(bm[m], 'map ' + m)
bs = defaultdict(list)
for r in rows:
    bs[r['set']].append(r)
for m in sorted(bs):
    wr(bs[m], 'set ' + m)
