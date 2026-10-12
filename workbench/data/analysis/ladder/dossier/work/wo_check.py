"""Scratch (diag-wipeout): independent recount of the window tables with the shared reader (tools/ladder_replay.scan),
not my state machine. For every wipe-out game of a source: deaths by side and cause in the 60 rounds up to the half
round, cross head-ons by mover side, pearls dropped and eaten within 5 rounds by side; compared with wo_scan rows.
Usage: python3 data/analysis/ladder/dossier/work/wo_check.py <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import scan
from collections import Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1')


def paths(src):
    out = {}
    if src == 'O':
        for label in LABELS:
            folder = Path('data/online/smoke') / (label + '-new')
            if folder.is_dir():
                for mp in sorted(folder.glob('game-*.json')):
                    j = json.loads(mp.read_text())
                    out[j['id']] = (folder / ('M%d.replay' % j['id']), j, 1119)
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] == 'us':
                rp = Path(r['replay'])
                out[r['game']] = (rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team)
    return out


def main():
    src = sys.argv[1]
    where = paths(src)
    mine, theirs = Counter(), Counter()
    games = 0
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['final'][0] != 0:
                continue
            games += 1
            al = [x[0] for x in g['snap']]
            peak = max(al)
            pr = max(r for r, a in enumerate(al) if a == peak)
            hr = next(r for r in range(pr, len(al)) if al[r] * 2 < peak)
            lo = max(0, hr - 60)
            for d in g['deaths']:
                if lo < d['r'] <= hr:
                    s = 'us' if d['s'] == 0 else 'them'
                    c = d['c']
                    if c == 'head-on':
                        c = 'head-on mover' if d['role'] == 'mover' else 'head-on hit'
                        if d['cross'] and d['role'] == 'mover':
                            mine[(s, 'cross head-ons started')] += 1
                    mine[(s, c)] += 1
                    mine[(s, 'length')] += d['L']
                    mine[(s, 'drops')] += d['drop']
                    mine[(s, 'drops eaten in 5 by us')] += d['eat5'][0]
                    mine[(s, 'drops eaten in 5 by them')] += d['eat5'][1]
            rp, j, team = where[g['gid']]
            jj = dict(j)
            if team != 1119:
                for z in 'AB':
                    jj['team' + z + 'Id'] = 1119 if j['team' + z + 'Id'] == team else -1
            ref = scan(rp, jj, str(rp.parent), set())
            assert max(ref['snapshots']) == g['last']
            for r in (pr, hr):
                sn = ref['snapshots'][r]
                assert (sn['us']['alive'], sn['us']['total'], sn['them']['alive'], sn['them']['total']) == (g['snap'][r][0], g['snap'][r][1], g['snap'][r][4], g['snap'][r][5]), (g['gid'], r)
            pearls = dict((p['pearl'], p) for p in ref['pearls'])
            for d in ref['deaths']:
                if lo < d['round'] <= hr:
                    s = d['side']
                    c = d['cause']
                    if c == 'head-on':
                        c = 'head-on mover' if d['id'] == d['actor'] else 'head-on hit'
                    elif c == 'other dragon body':
                        c = 'other body'
                    elif c == 'other':
                        c = d['other']
                    theirs[(s, c)] += 1
                    theirs[(s, 'length')] += d['length']
                    theirs[(s, 'drops')] += d['dropped']
                    for pid in d['pearls']:
                        pr2 = pearls[pid]
                        if pr2['eater'] != 'nobody' and pr2['wait'] <= 5:
                            theirs[(s, 'drops eaten in 5 by ' + pr2['eater'])] += 1
            dd = dict((d['death'], d) for d in ref['deaths'])
            for c in ref['collisions']:
                if c['cross_team'] and lo < c['round'] <= hr:
                    a, b = [dd[x] for x in c['deaths']]
                    mover = a if a['id'] == a['actor'] else b
                    theirs[(mover['side'], 'cross head-ons started')] += 1
    keys = sorted(set(mine) | set(theirs))
    bad = 0
    for k in keys:
        flag = '' if mine[k] == theirs[k] else '   <-- DIFFERS'
        bad += mine[k] != theirs[k]
        print('%-5s %-28s mine %6d   shared reader %6d%s' % (k[0], k[1], mine[k], theirs[k], flag))
    print(src, 'wipe-out games', games, 'cells compared', len(keys), 'different', bad)


main()
