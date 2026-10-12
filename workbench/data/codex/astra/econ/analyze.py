"""Offline spread census; imports the existing replay state reader."""
import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['data/codex/astra/approach']
from scan import Board, replay
from collections import deque, Counter
from pathlib import Path
import json, hashlib, datetime

OUT = Path(__file__).resolve().parent
LABELS = ('one5-w1', 'one5-c1', 'one7-w1', 'one7-c1')

def flood(graph, starts):
    dist = {c: 0 for c in starts}; queue = deque(dist)
    while queue:
        c = queue.popleft()
        for n in graph[c]:
            if n is not None and n not in dist:
                dist[n] = dist[c] + 1; queue.append(n)
    return dist

def run(label, path, meta):
    B = Board(path); own = int(meta['teamAId'] != 1119)
    assert B.root.pointer(4).bit(0)
    assert B.root.text(1+own) == ('20980' if label.startswith('one5') else '21086')
    side = lambda i: int(B.teams[i] != own)
    bearing, natural, present, snaps = set(), set(), {}, {}
    pending = 0; nat = [0,0]; eats = [0,0]; splits = [0,0]; deaths = [0,0]; turns = [0,0]
    checks = Counter(); last = -1
    def snap():
        return dict(heads=[[(i, *b[0], len(b)) for i,b in B.bodies.items() if side(i)==s] for s in (0,1)],
                    nat=nat.copy(), eats=eats.copy(), splits=splits.copy(), deaths=deaths.copy(), turns=turns.copy())
    initial = snap()
    for ev in B.root.pointer(3):
        k = ev.u16(0); p = ev.pointer(0)
        if k == 0:
            if B.rnd >= 0 and B.rnd <= 150 and B.rnd % 10 == 0: snaps[B.rnd] = snap()
        if k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                assert c not in present
                bearing.add(c); present[c] = pending == 0
                if pending: pending -= 1
                else: natural.add(c)
            else:
                origin = present.pop(c)
                eats[side(B.actor)] += 1
                nat[side(B.actor)] += origin
        elif k == 10: splits[side(p.i32(0))] += 1
        elif k == 11:
            assert pending == 0
            pending = (len(B.bodies[p.i32(0)])+1)//2
            deaths[side(p.i32(0))] += 1
        B.update(k,p)
        if k == 1: turns[side(B.actor)] += 1
        if k == 9:
            assert B.bodies[p.i32(0)][-1] == replay.point(p.pointer(1))
            checks['moves'] += 1
        last = B.rnd
    if last <= 150 and last % 10 == 0: snaps[last] = snap()
    final = snap()
    for r in range(0,151,10):
        if r not in snaps:
            assert r > last
            snaps[r] = final
    rev = {c:[] for c in B.adj}
    for c, ns in B.adj.items():
        for n in ns:
            if n is not None: rev[n].append(c)
    view = {c:{((c[0]+dx)%B.W,(c[1]+dy)%B.H) for dx in range(-3,4) for dy in range(-3,4)} for c in B.adj}
    # Forward head->tile ownership; reverse multi-source finds head->bearing distance.
    dist_to = {name:flood(rev,tiles) for name,tiles in [('all',bearing),('natural',natural)]}
    rows=[]
    for r,snap0 in sorted(snaps.items()):
        hs = [[(h[1],h[2]) for h in ss] for ss in snap0['heads']]
        ds = [flood(B.adj,h) for h in hs]
        for name,tiles in [('all',bearing),('natural',natural)]:
            counts = Counter()
            for c in tiles:
                a,b = ds[0].get(c,float('inf')),ds[1].get(c,float('inf'))
                counts['none' if a==b==float('inf') else 'tie' if a==b else 'ours' if a<b else 'theirs'] += 1
            for s in (0,1):
                reach = [ds[s][c] for c in tiles if c in ds[s]]
                seen = set().union(*(view[h] for h in hs[s])) if hs[s] else set()
                local = [len(view[h] & tiles) for h in hs[s]]
                mate = 0
                for i,h in enumerate(hs[s]):
                    near = B.flood(h,2)
                    mate += any(j!=i and m in near for j,m in enumerate(hs[s]))
                n = len(hs[s]); visible = len(seen & tiles)
                row=dict(label=label,gid=meta['id'],map=meta['mapName'],cells=B.W*B.H,r=r,side=s,kind=name,
                    ended=r>last,bearing=len(tiles),heads=n,owned=counts['ours' if s==0 else 'theirs'],
                    tie=counts['tie'],unclaimed=counts['none'],reachable=len(reach),distance_sum=sum(reach),
                    distance_mean=sum(reach)/len(reach) if reach else None,
                    visible_bearing=visible,heads_per_visible=n/visible if visible else None,
                    local_head_tile_pairs=sum(local),no_bearing4=sum(dist_to[name].get(h,10**9)>4 for h in hs[s]),
                    crowded2=mate,natural_eaten=snap0['nat'][s],all_eaten=snap0['eats'][s],
                    splits=snap0['splits'][s],deaths=snap0['deaths'][s],turns=snap0['turns'][s])
                assert n == len(initial['heads'][s]) + row['splits'] - row['deaths']
                assert sum(counts.values()) == len(tiles)
                rows.append(row)
    return dict(label=label,gid=meta['id'],map=meta['mapName'],path=str(path),bot=B.root.text(1+own),
                opponent_bot=B.root.text(2-own),last=last,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                checks=dict(checks),snaps=snaps,rows=rows,bearing=sorted(bearing),natural_bearing=sorted(natural))

if __name__ == '__main__':
    inventory=[]
    for label in LABELS:
        for mp in sorted((Path('data/online/smoke')/(label+'-old')).glob('game-*.json')):
            meta=json.loads(mp.read_text()); path=mp.with_name('M%d.replay'%meta['id'])
            target=OUT/('game-%d.json'%meta['id'])
            if not target.exists():
                data=run(label,path,meta)
                target.write_text(json.dumps(data,separators=(',',':')))
                print(label,meta['id'],data['last'],flush=True)
            inventory.append(dict(label=label,gid=meta['id'],path=str(path)))
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.datetime.now().astimezone().isoformat(),games=inventory),indent=2))
