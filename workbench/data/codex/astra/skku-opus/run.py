"""Every game meow (1119) v Team SKKU (249): per-game rows. Run from ROOT: python3 -B data/codex/astra/skku-opus/run.py"""
import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/codex/astra/stuck-opus', 'data/codex/astra/skku']
import json, glob, os
from pathlib import Path
from statistics import median
import ladder_replay as lr
import o1_scan
import analyze

OUT = Path('data/codex/astra/skku-opus')
vers = dict(l.split() for l in open('data/online/smoke/versions.tsv') if l.strip())
seen = {}
for mp in sorted(glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json') + glob.glob('data/online/smoke/*/game-*.json')):
    try: j = json.loads(open(mp).read())
    except Exception: continue
    if {j.get('teamAId'), j.get('teamBId')} != {1119, 249}: continue
    if j.get('status') != 'completed' and not j.get('winner'): continue
    gid = j['id']
    rp = os.path.join(os.path.dirname(mp), f'M{gid}.replay')
    if gid in seen or not os.path.exists(rp): continue
    seen[gid] = (mp, rp, j)
rows = []
for gid in sorted(seen):
    mp, rp, j = seen[gid]
    folder = os.path.basename(os.path.dirname(mp))
    try:
        sc = o1_scan.scan(folder, rp, j)
        d = analyze.details(rp, j)
    except Exception as e:
        print('FAIL', gid, repr(e), flush=True); continue
    seat = 'A' if j['teamAId'] == 1119 else 'B'
    q = d['queens']
    def cnt(r, s): return len({t['id'] for t in d['turns'] if t['r'] == r and t['s'] == s})
    def eats(r, s): return sum(t['eat'] for t in d['turns'] if t['r'] <= r and t['s'] == s)
    def first(lst): return lst[0] if lst else None
    qd = [None, None]; atk = [None, None]
    for x in d['deaths']:
        if x['id'] in q and qd[x['s']] is None:
            qd[x['s']] = x['r']
            a = x.get('attack') or {}
            atk[x['s']] = dict(r=x['r'], qL=x['L'], reason=x['reason'], actor=a.get('id'), actor_side=a.get('s'), aL=a.get('L'), dist=a.get('distance'),
                               steps=a.get('steps'), paid=a.get('paid'), seen=a.get('seen_last'), foe_q_alive=x.get('enemy_queen_alive'),
                               self=(a.get('id') == x['id']), units=(x.get('last') or [{}])[-1].get('units'), portal=any(a.get('portal') or []))
    fe = [first([t['r'] for t in d['turns'] if t['s'] == s and t['eat']]) for s in (0, 1)]
    fs = [first([x['r'] for x in d['splits'] if x['s'] == s]) for s in (0, 1)]
    qfs = [first([x['r'] for x in d['splits'] if x['s'] == s and x['queen']]) for s in (0, 1)]
    home = [median([x['home'] for x in d['qturn'][s]]) if d['qturn'][s] else None for s in (0, 1)]
    home100 = [median([x['home'] for x in d['qturn'][s] if x['r'] <= 100]) if d['qturn'][s] else None for s in (0, 1)]
    qL50 = [first([x['L'] for x in d['qturn'][s] if x['r'] >= 50]) for s in (0, 1)]
    # head-to-head rams on any dragon: deaths with actor from the other side
    rams = [sum(1 for x in d['deaths'] if x['s'] == s and x['actor'] != x['id'] ) for s in (0, 1)]
    row = dict(gid=gid, folder=folder, when=j.get('completedAt'), ranked=j.get('ranked'), bot=sc['bot'], ver=vers.get(str(sc['bot']), str(sc['bot'])), seat=seat,
               ourq_id=q[0], theirq_id=q[1], map=j['mapName'], cells=d['W'] * d['H'], result=sc['result'], how=sc['how'], last=sc['last'], ends=[list(x[:4]) for x in sc['ends']],
               qd=qd, atk=atk, first_eat=fe, first_split=fs, q_first_split=qfs, home=home, home100=home100, qL50=qL50,
               n50=[cnt(50, 0), cnt(50, 1)], n100=[cnt(100, 0), cnt(100, 1)], p100=[eats(100, 0), eats(100, 1)], p50=[eats(50, 0), eats(50, 1)], killed=rams)
    rows.append(row)
    print(gid, folder, row['ver'], seat, row['map'], row['result'], row['how'], row['last'], row['ends'], 'qd', qd, flush=True)
(OUT / 'rows.json').write_text(json.dumps(rows, indent=1, default=str))
print('games', len(rows))
