"""loss15-sonnet: one game summary. Usage (from ROOT, via run.sh): l15.py <gameid> [more ids]
Prints: header, snapshots every 25 rounds (n dragons, total length, top, queen) for us / them, r100 pearls eaten + dragons,
our deaths of dragons >=5 (round, len, kind, attacker), our queen death record (qdeath.scan), final state."""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
import o1_scan
import qdeath
from pathlib import Path


def find(gid):
    for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid) + glob.glob('data/online/smoke/*-old/game-%d.json' % gid):
        return Path(f)


def show(gid):
    mp = find(gid)
    j = json.load(open(mp))
    rp = mp.parent / ('M%d.replay' % gid)
    own = 0 if j['teamAId'] == 1119 else 1
    row = o1_scan.scan(mp.parent.name, rp, j)
    print('=== game %d  %s  map %s  seat %s  vs %s (%s)  %s  bot %s  done %s' % (
        gid, row['result'].upper(), j['mapName'], 'AB'[own], row['opp'], j['teamAElo'] if own else j['teamBElo'],
        'ranked' if j['ranked'] else mp.parent.name, row['bot'], j['completedAt'][11:16]))
    print('cells %d  last round %d  decided by %s' % (row['cells'], row['last'], row['how']))
    print(' r   | us: n  tot top  Q | them: n tot top  Q')
    for r in sorted(row['snaps'], key=int):
        s = row['snaps'][r]
        print('%4s | %2d %4d %3d %3d | %2d %4d %3d %3d' % (r, s[0][0], s[0][1], s[0][2], s[0][3], s[1][0], s[1][1], s[1][2], s[1][3]))
    e100 = sum(1 for e in row['eats'] if e[0] < 100 and e[1] == 0)
    t100 = sum(1 for e in row['eats'] if e[0] < 100 and e[1] == 1)
    n100 = sum(1 for e in row['eats'] if e[0] < 100 and e[1] == 0 and e[3] == 'n')
    m100 = sum(1 for e in row['eats'] if e[0] < 100 and e[1] == 1 and e[3] == 'n')
    sp = [x for x in row['splits'] if x[1] == 0 and x[0] < 100]
    print('r<100: eat events us %d / them %d (of which natural pearls us %d / them %d), our splits %d, our dragons at r100 %s, our total length at r100 %s' % (
        e100, t100, n100, m100, len(sp), row['snaps'].get('100', [[None]])[0][0], row['snaps'].get('100', [[0, None]])[0][1]))
    print('our deaths (L>=4):')
    for d in row['deaths']:
        if d[1] == 0 and d[2] >= 8:
            print('  r%d L%d %s q=%d free=%d extra=%s h=%s' % (d[0], d[2], d[4], d[6], d[5], d[18], d[20]))
    print('their deaths (L>=4):')
    for d in row['deaths']:
        if d[1] == 1 and d[2] >= 8:
            print('  r%d L%d %s q=%d extra=%s' % (d[0], d[2], d[4], d[6], d[18]))
    try:
        q = qdeath.scan(rp, own)
        for d in q['deaths']:
            keys = ['r', 'L', 'reason', 'own_turn', 'their_q_dead', 'att', 'att_free', 'att_paid', 'att_portal', 'att_gap', 'seen_q', 'seen_mate', 'f0', 'f0a', 'f1', 'f1a', 'split0', 'split1', 'L0', 'closers', 'hit']
            print('QUEEN DEAD:', {k: d[k] for k in keys if k in d})
        print('queen alive at end %s len %s' % (q['qalive'], q['qlen']))
    except Exception as ex:
        print('qdeath err', repr(ex)[:150])


if __name__ == '__main__':
    for g in sys.argv[1:]:
        show(int(g))
