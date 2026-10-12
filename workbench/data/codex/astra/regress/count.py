#!/usr/bin/env python3
"""Single-process replay census; all output stays in this directory."""
import sys
sys.dont_write_bytecode = True
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SM = ROOT / 'data/online/smoke'
sys.path.insert(0, str(ROOT / 'tools'))
from ladder_replay import replay, edge_id, canonical_edges

VERSIONS = [f'one{i}' for i in range(5, 15)]
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSES = ['wall', 'own_body', 'mate', 'enemy_body', 'rammed_head_on',
          'initiated_head_on', 'mate_head_on', 'other']
METRICS = ['pearls50', 'pearls100', 'pearls200', 'alive100', 'alive200',
           'total100', 'total200', 'queen100', 'queen200', 'queen_death_share',
           'queen_death_median', 'portals100', 'splits100'] + [
           'deaths_' + c for c in CAUSES] + ['far_share']

def inputs():
    jobs, seen, excluded = [], set(), []
    for folder in sorted(SM.glob('one*-old')):
        if not re.fullmatch(r'one(?:[5-9]|1[0-4])-.+-old', folder.name):
            continue
        for p in sorted(folder.glob('game-*.json')):
            j = json.loads(p.read_text())
            rp = folder / f'M{j["id"]}.replay'
            if j['id'] in seen:
                excluded.append([str(p.relative_to(ROOT)), 'duplicate']); continue
            if not rp.exists() or j.get('status') != 'completed':
                excluded.append([str(p.relative_to(ROOT)), 'missing replay/incomplete']); continue
            if 1119 not in (j['teamAId'], j['teamBId']) or j.get('ranked'):
                excluded.append([str(p.relative_to(ROOT)), 'not our unranked game']); continue
            seen.add(j['id']); jobs.append((rp, j, folder.name))
    return jobs, excluded

def scan(path, j, folder, version_ids):
    root = replay.load(path).root()
    own = 0 if j['teamAId'] == 1119 else 1
    bot_id = root.text(own + 1)
    if bot_id not in version_ids:
        return {'excluded': 'unknown bot id', 'gid': j['id'], 'bot_id': bot_id}
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (kind, pid) in edges.items():
        if kind == 2: portals[pid].append(e)
    assert all(len(es) == 2 for es in portals.values())
    queens = {s: min(i for i in bodies if teams[i] == s) for s in (0, 1)}
    start = bodies[queens[own]][0]
    starts = [b[0] for i, b in bodies.items() if teams[i] == own]

    def dest(h, d):
        x, y = h
        kind, pid = edges.get(edge_id(W, H, x, y, d), (0, -1))
        if kind == 2:
            e = edge_id(W, H, x, y, d)
            partner = next(z for z in portals[pid] if z != e)
            row, px = divmod(partner, W+1)
            return ((px-(d == 3)) % W, (row//2-(d == 0)) % H)
        dx, dy = STEP[d]
        return ((x+dx) % W, (y+dy) % H)

    # Distance is shortest directed legal terrain route, ignoring dragons.
    dist, queue = {start: 0}, deque([start])
    while queue:
        xy = queue.popleft()
        for d in range(4):
            if edges.get(edge_id(W, H, *xy, d), (0, -1))[0] == 1: continue
            nxt = dest(xy, d)
            if nxt not in dist:
                dist[nxt] = dist[xy]+1; queue.append(nxt)
    rnd, actor, dirs, used = -1, None, [], 0
    eats = Counter(); splits = portals_n = turns = far = 0
    far_torus = 0
    snapshots, deaths, moments = {}, [], []
    pending = None
    queen_death = None
    head_victim = None
    present = set()
    audit = Counter()

    def snapshot():
        return dict(alive=sum(teams[i] == own for i in bodies),
                    total=sum(len(b) for i, b in bodies.items() if teams[i] == own),
                    queen=len(bodies.get(queens[own], ())))

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11): continue
        p = ev.pointer(0)
        if k == 0:
            assert pending is None
            rnd, actor = p.i32(0), None
            if rnd in (100, 200): snapshots[rnd] = snapshot()
        elif k == 1:
            assert pending is None
            actor, dirs, used, head_victim = p.i32(0), [], 0, None
            if rnd < 200 and teams[actor] == own:
                h = bodies[actor][0]
                turns += 1; far += dist.get(h, W*H+1) > 12
                dx, dy = abs(h[0]-start[0]), abs(h[1]-start[1])
                far_torus += min(dx, W-dx)+min(dy, H-dy) > 12
        elif k == 4:
            assert actor == p.i32(0)
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used = 0
        elif k == 3:
            xy = replay.point(p.pointer(0))
            if p.u32(0):
                assert xy not in present
                present.add(xy)
            else:
                assert xy in present and pending is None and actor in bodies
                present.remove(xy); pending = (actor, xy)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]; old = b[0]
            moved = old != hd
            if moved:
                assert i == actor and used < len(dirs), (j['id'], rnd, i, actor, used, dirs)
                d = dirs[used]
                assert dest(old, d) == hd, (j['id'], rnd, old, d, hd, dest(old, d))
                if rnd < 100 and teams[i] == own and edges.get(edge_id(W, H, *old, d), (0, -1))[0] == 2:
                    portals_n += 1
                    moments.append(dict(kind='portal', r=rnd, event=idx, id=i, before=list(old), after=list(hd)))
                used += 1; b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl: b.pop()
            assert b[-1] == tl
            if pending:
                assert pending == (i, hd) and moved
                if teams[i] == own: eats[rnd] += 1
                pending = None
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            if rnd < 100 and teams[parent] == own:
                splits += 1
                moments.append(dict(kind='split', r=rnd, event=idx, id=parent,
                                    queen=parent == queens[own], before=len(bodies[parent]),
                                    lengths=[len(p.pointer(z)) for z in (0, 1)]))
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z)); teams[i] = p.u16(8)
        elif k == 11:
            assert pending is None
            i, reason = p.i32(0), p.u16(4)
            cause, hit = 'other', None
            if reason == 0: cause = 'wall'
            elif reason == 1: cause = 'own_body'
            elif reason == 2:
                assert i == actor and used < len(dirs)
                xy = dest(bodies[i][0], dirs[used])
                owners = [z for z, b in bodies.items() if z != i and xy in b]
                assert len(owners) == 1, (j['id'], rnd, xy, owners)
                hit = owners[0]; cause = 'mate' if teams[hit] == teams[i] else 'enemy_body'
            elif reason == 3:
                if i != actor:
                    assert actor in bodies
                    head_victim = i
                    cause = 'mate_head_on' if teams[actor] == teams[i] else 'rammed_head_on'
                    hit = actor
                else:
                    assert head_victim is not None
                    hit = head_victim
                    cause = 'mate_head_on' if teams[hit] == teams[i] else 'initiated_head_on'
            if teams[i] == own:
                d = dict(r=rnd, event=idx, id=i, cause=cause, length=len(bodies[i]),
                         queen=i == queens[own], head=list(bodies[i][0]), actor=actor, hit=hit)
                deaths.append(d)
                if i == queens[own]: queen_death = rnd
            bodies.pop(i)
    assert pending is None
    final = snapshot()
    for s in (0, 1):
        ls = [len(b) for i, b in bodies.items() if teams[i] == s]
        st = root.pointer(4).pointer(s)
        assert (len(ls), max(ls, default=0), sum(ls)) == (st.i32(0), st.i32(4), st.i32(8))
        if root.u32(0) >= 2:
            assert len(bodies.get(queens[s], ())) == st.i32(12)
    values = {f'pearls{r}': sum(n for rr, n in eats.items() if rr < r) for r in (50, 100, 200)}
    for r in (100, 200):
        ss = snapshots.get(r, final)
        values.update({f'{k}{r}': ss[k] for k in ('alive', 'total', 'queen')})
    dc = Counter(d['cause'] for d in deaths if d['r'] < 200)
    values.update({'deaths_'+c: dc[c] for c in CAUSES})
    values.update(queen_death_share=int(queen_death is not None), queen_death_median=queen_death,
                  portals100=portals_n, splits100=splits, far_share=far/turns if turns else None)
    return dict(gid=j['id'], version=version_ids[bot_id], bot_id=bot_id, map=j['mapName'],
                map_id=j['mapId'], side='AB'[own], folder=folder, replay=str(path.relative_to(ROOT)),
                opponent=j['teamBName'] if own == 0 else j['teamAName'],
                opponent_id=j['teamBId'] if own == 0 else j['teamAId'],
                opponent_bot=root.text(2-own), completed=j.get('completedAt'), last_round=rnd,
                start=list(start), starter_heads=[list(h) for h in starts], values=values,
                turns200=turns, far_turns200=far, far_torus_turns200=far_torus,
                checkpoints=snapshots, deaths=deaths, moments=moments, audit=dict(audit),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    version_ids = dict(line.split() for line in (SM/'versions.tsv').read_text().splitlines())
    jobs, excluded = inputs()
    stamp = datetime.now().astimezone().isoformat()
    (HERE/'manifest.json').write_text(json.dumps(dict(frozen_at=stamp,
        jobs=[dict(replay=str(p.relative_to(ROOT)), gid=j['id'], folder=f) for p,j,f in jobs],
        excluded=excluded), ensure_ascii=False, indent=2))
    cache = {}
    if (HERE/'games.jsonl').exists():
        cache = {x['gid']: x for x in map(json.loads, (HERE/'games.jsonl').read_text().splitlines())}
    rows = []
    for n, (p, j, f) in enumerate(jobs, 1):
        row = cache.get(j['id'])
        if row is None: row = scan(p, j, f, version_ids)
        rows.append(row)
        if n % 15 == 0:
            print(f'{n}/{len(jobs)} {f}', flush=True)
            (HERE/'games.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in rows))
    (HERE/'games.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in rows))
    print('DONE', len(rows), Counter(x.get('version', 'excluded') for x in rows), flush=True)

if __name__ == '__main__': main()
