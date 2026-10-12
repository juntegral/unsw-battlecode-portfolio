"""Scratch (diag-one1, job G): every lost game of one1..one4 in one bucket, by build and opponent group.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_buckets.py [-g]"""
import sys, json, os, glob
from collections import Counter, defaultdict
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
LIVE = '~/01. Project/개인 프로젝트/unsw-swarm/data/online/live-one1/'
BUILD = {'20850': 'one1', '20880': 'one2', '20910': 'one3', '20941': 'one4'}
ranked = {}
for p in glob.glob(LIVE + 'b*/index.json'):
    try:
        for g in json.load(open(p))['games']:
            ranked[g['gameId']] = bool(g.get('ranked'))
    except Exception:
        pass


def load(pat):
    out = {}
    for nm in ('w1', 'd1', 'o2', 'o3', 'o3d', 'o4', 'o4d', 'live'):
        p = W + pat % nm
        if os.path.exists(p):
            for l in open(p):
                g = json.loads(l)
                out.setdefault(g['gid'], g)
    return out


S = load('o1_scan-%s.jsonl')
K = load('o1_strike-%s.jsonl')
for b in sorted({g['bot'] for g in S.values()}):
    if b not in BUILD and b > '20910':
        BUILD[b] = 'one4'


def snap(g, r):
    r = min(r, g['last'])
    return g['snaps'].get(str(r), g['snaps'][str(g['last'])])


def group(g):
    if ranked.get(g['gid']):
        return 'ranked'
    if 'Quiz' in g['opp']:
        return 'WHQ'
    if 'dev test' in g['opp']:
        return 'dev1'
    return 'other'


rows = []
for gid, g in S.items():
    if g['bot'] not in BUILD:
        continue
    b, grp = BUILD[g['bot']], group(g)
    e = g['ends']
    rec = dict(gid=gid, build=b, grp=grp, map=g['map'], cells=g['cells'], result=g['result'], how=g['how'])
    if g['result'] != 'loss':
        rec['bucket'] = 'won' if g['result'] == 'win' else 'draw'
        rows.append(rec)
        continue
    u150 = [snap(g, 150)[s][0] for s in (0, 1)]
    t300 = [snap(g, 300)[s][1] for s in (0, 1)]
    qd = next((d for d in g['deaths'] if d[6] and d[1] == 0), None)
    if g['how'] == 'elim' or u150[0] * 2 < u150[1]:
        rec['bucket'] = 'a'
    elif g['how'] == 'queen' and e[0][3] == 0 and t300[0] >= 0.8 * t300[1]:
        rec['bucket'] = 'b'
        r = qd[0] if qd else -1
        rec['band'] = 'r0-50' if r <= 50 else 'r51-150' if r <= 150 else 'r151-300' if r <= 300 else 'r301+'
        rec['qcause'] = qd[4] if qd else '?'
        k = K.get(gid)
        ch = tk = 0
        if k:
            for row in k['rows']:
                if row['s'] == 0 and any(t[3] for t in row['tg']):
                    ch += 1
                    tk += int(row['ram'] and any(t[3] and t[1] == row['ramL'] for t in row['tg']))
        rec['qchance'], rec['qtaken'] = ch, tk
    elif g['how'] == 'longest':
        rec['bucket'] = 'c'
        rec['gap'] = e[1][2] - e[0][2]
        rec['total_larger'] = int(e[0][1] > e[1][1])
        rec['units'] = e[0][0]
    else:
        rec['bucket'] = 'd'
        rec['why'] = 'queen dead, swarm behind at r300 (%d v %d)' % (t300[0], t300[1]) if g['how'] == 'queen' and e[0][3] == 0 else 'queen shorter (%d v %d)' % (e[0][3], e[1][3]) if g['how'] == 'queen' else g['how']
    rows.append(rec)

if __name__ == '__main__':
    builds = sorted({r['build'] for r in rows})
    print('builds', {v: k for k, v in BUILD.items()})
    print('%-7s %-5s games won  a   b   c   d' % ('group', 'build'))
    for grp in ('WHQ', 'dev1', 'ranked', 'other'):
        for b in builds + ['all']:
            R = [r for r in rows if r['grp'] == grp and (b == 'all' or r['build'] == b)]
            if not R:
                continue
            c = Counter(r['bucket'] for r in R)
            print('%-7s %-5s %4d %4d %3d %3d %3d %3d' % (grp, b, len(R), c['won'], c['a'], c['b'], c['c'], c['d']))
    R = [r for r in rows if r['bucket'] == 'b']
    print('(b) queen death band:', dict(Counter((r['grp'], r['band']) for r in R)), '| cause', dict(Counter(r['qcause'] for r in R)))
    print('(b) games with their queen inside a short dragon reach: %d of %d; turns %d, rammed her %d' % (sum(r['qchance'] > 0 for r in R), len(R), sum(r['qchance'] for r in R), sum(r['qtaken'] for r in R)))
    R = [r for r in rows if r['bucket'] == 'c']
    if R:
        gaps = sorted(r['gap'] for r in R)
        print('(c) n %d; gap in longest median %d (range %d to %d); our total the larger in %d; our dragons at the end median %d' % (len(R), gaps[len(gaps) // 2], gaps[0], gaps[-1], sum(r['total_larger'] for r in R), sorted(r['units'] for r in R)[len(R) // 2]))
        print('    by group', dict(Counter((r['grp'], 'total larger' if r['total_larger'] else 'total smaller') for r in R)))
    print('(d)', dict(Counter(r['why'].split(' (')[0] for r in rows if r['bucket'] == 'd')))
    if '-g' in sys.argv:
        for r in sorted(rows, key=lambda r: (r['grp'], r['build'], r['cells'])):
            if r['bucket'] in 'abcd':
                print(r['grp'], r['build'], r['gid'], r['map'][:14], r['cells'], r['how'], r['bucket'], {k: v for k, v in r.items() if k in ('band', 'qcause', 'qchance', 'qtaken', 'gap', 'total_larger', 'why', 'units')})
