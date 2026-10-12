#!/usr/bin/env python3
"""Compare online batches: per opponent/map results. usage: batchcmp.py DIR1 [DIR2 ...]"""
import json, gzip, os, sys, collections
MP = {4: 'default', 7: 'queen', 9: 'school', 11: 'trophy', 13: 'devil', 15: 'trauma', 17: 'prisoners', 19: 'autarky', 20: 'portals', 21: 'slithery'}
def load(d):
    idx = json.load(open(os.path.join(d, 'index.json')))
    names = {}
    try:
        req = json.load(open(os.path.join(d, 'requests.json')))
        names = {s['teamId']: s['name'] for s in req.get('sent', [])}
    except Exception:
        pass
    out = []
    for g in idx['games']:
        p = os.path.join(d, f"events-{g['gameId']}.jsonl.gz")
        if not os.path.exists(p):
            continue
        meta = json.loads(gzip.open(p, 'rt').readline())['meta']
        us = meta['ourSide']; them = 'B' if us == 'A' else 'A'; res = meta['result']
        w = res.get('winner')
        out.append(dict(opp=g.get('opponentTeam'), name=names.get(g.get('opponentTeam'), str(g.get('opponentTeam'))), map=MP.get(g['map'], g['map']),
                        res='W' if w == us else ('D' if w is None else 'L'), end=res['endReason'],
                        long=(res['team' + us]['longestDragon'], res['team' + them]['longestDragon']),
                        tot=(res['team' + us]['totalLength'], res['team' + them]['totalLength']),
                        n=(res['team' + us]['dragonCount'], res['team' + them]['dragonCount'])))
    return out
for d in sys.argv[1:]:
    rows = load(d)
    c = collections.Counter(r['res'] for r in rows)
    el = sum(1 for r in rows if r['res'] == 'L' and r['end'] == 'teamEliminated')
    print(f"== {os.path.basename(d)}: {c['W']}W {c['L']}L {c['D']}D  (lost by elimination {el})")
    bym = collections.defaultdict(list)
    for r in rows: bym[r['map']].append(r['res'])
    print('   by map:', {k: ''.join(v) for k, v in sorted(bym.items())})
    byo = collections.defaultdict(list)
    for r in rows: byo[r['name']].append(f"{r['map']}:{r['res']}{'e' if r['end']=='teamEliminated' else ''}({r['long'][0]}-{r['long'][1]})")
    for k, v in sorted(byo.items()): print(f"   {k[:22]:22s} {' '.join(v)}")
