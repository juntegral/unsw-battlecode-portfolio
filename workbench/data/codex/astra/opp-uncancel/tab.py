"""opp-uncancel: table of all games vs team 899, same scan both sides."""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
import o1_scan
import qdeath
from pathlib import Path
from collections import Counter

OPP = 899
VERS = dict(l.split() for l in open('data/online/smoke/versions.tsv').read().splitlines() if l.strip())
games = {}
for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*/game-*.json'):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if OPP in (j.get('teamAId'), j.get('teamBId')) and 1119 in (j.get('teamAId'), j.get('teamBId')):
        rp = Path(f).parent / ('M%d.replay' % j['id'])
        if rp.exists():
            games[j['id']] = (j, rp)
verbose = len(sys.argv) > 1
tot = Counter()
print('gid      date-time   ver   seat map                 res how     last | endQ us/them | r100 us n/tot/nat  them n/tot/nat | splits<100 us/them | first split us/them')
for gid in sorted(games):
    j, rp = games[gid]
    own = 0 if j['teamAId'] == 1119 else 1
    row = o1_scan.scan('x', rp, j)
    ver = VERS.get(str(row['bot']), str(row['bot']))
    s = row['snaps'].get('100')
    nat = [sum(1 for e in row['eats'] if e[0] < 100 and e[1] == k and e[3] == 'n') for k in (0, 1)]
    sp = [[x for x in row['splits'] if x[1] == k] for k in (0, 1)]
    spn = [sum(1 for x in sp[k] if x[0] < 100) for k in (0, 1)]
    fs = [sp[k][0][0] if sp[k] else -1 for k in (0, 1)]
    e = row['ends']
    r100 = 'us %d/%d/%d them %d/%d/%d' % (s[0][0], s[0][1], nat[0], s[1][0], s[1][1], nat[1]) if s else 'ended r%d' % row['last']
    print('%d %s %-6s %s   %-19s %-4s %-7s %4d | Q %3d/%3d top %d/%d n %d/%d | %s | %d/%d | %d/%d' % (
        gid, j['completedAt'][5:16], ver, 'AB'[own], j['mapName'], row['result'], row['how'], row['last'],
        e[0][3], e[1][3], e[0][2], e[1][2], e[0][0], e[1][0], r100, spn[0], spn[1], fs[0], fs[1]))
    tot['all', row['result']] += 1
    tot['seat ' + 'AB'[own], row['result']] += 1
    tot['map ' + j['mapName'], row['result']] += 1
    tot['ver ' + ver, row['result']] += 1
    if verbose:
        keys = ['r', 'L', 'reason', 'own_turn', 'their_q_dead', 'att', 'att_free', 'att_paid', 'att_portal', 'att_gap', 'seen_q', 'seen_mate', 'f0', 'f0a', 'f1', 'f1a', 'split0', 'split1', 'L0', 'closers', 'hit']
        for side, nm in ((own, 'OUR'), (1 - own, 'THEIR')):
            try:
                q = qdeath.scan(rp, side)
                for d in q['deaths']:
                    print('   %s QUEEN DEAD:' % nm, {k: d[k] for k in keys if k in d})
            except Exception as ex:
                print('   qdeath err', nm, repr(ex)[:120])
        print('   snaps r: us n tot top Q | them n tot top Q')
        for r in sorted(row['snaps'], key=int):
            x = row['snaps'][r]
            print('   %4s | %2d %4d %3d %3d | %2d %4d %3d %3d' % (r, x[0][0], x[0][1], x[0][2], x[0][3], x[1][0], x[1][1], x[1][2], x[1][3]))
        for d in row['deaths']:
            if d[2] >= 8:
                print('   death r%d side %s L%d %s q=%d extra=%s' % (d[0], 'us' if d[1] == 0 else 'THEM', d[2], d[4], d[6], d[18]))
        print('   queen splits us:', [(x[0], x[2], x[3], x[4]) for x in sp[0] if x[5]][:8], ' them:', [(x[0], x[2], x[3], x[4]) for x in sp[1] if x[5]][:8])
print()
for k in sorted(set(a for a, _ in tot)):
    w, l, d = tot[k, 'win'], tot[k, 'loss'], tot[k, 'draw']
    if w + l + d >= 2 or k == 'all':
        print('%-24s W%d L%d D%d' % (k, w, l, d))
