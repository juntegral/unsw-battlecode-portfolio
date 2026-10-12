#!/usr/bin/env python3
"""Offline counts. Run with python3 -B; every output stays in this directory."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
from array import array
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
DATA = ROOT / 'data/analysis/ladder'
sys.path.insert(0, str(ROOT / 'tools'))
from ladder_replay import replay, canonical_edges, edge_id

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
INF = 65535


def load_inputs():
    rows = [json.loads(s) for s in (DATA / 'rows.jsonl').read_text().splitlines() if s.strip()]
    losses = json.loads((DATA / 'losses/losses.json').read_text())
    maps = json.loads((DATA / 'maps.json').read_text())
    main = [r for r in rows if r['our_code'] == 'main']
    assert len({r['game'] for r in main}) == len(main)
    q1 = {r['game'] for r in losses if r['our_code'] == 'main' and r['bucket'] == 'Q1'}
    never = {r['game'] for r in main if (r['curves']['100']['us']['alive'] <= 6
             if r['curves']['100'] else r['final']['us']['alive'] == 0)}
    layouts = {r['map_key'] for r in main if r['game'] in never}
    growth = {r['game']: ('never_grew' if r['game'] in never else 'grew') for r in main
              if r['game'] in never or (r['map_key'] in layouts and r['curves']['100']
                                       and r['curves']['100']['us']['alive'] > 6)}
    return main, q1, growth, maps


class Geometry:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, (kind, pid) in self.edges.items():
            if kind == 2:
                portals[pid].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d, (dx, dy) in enumerate(STEP):
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        assert len(portals[pid]) == 2
                        partner = next(z for z in portals[pid] if z != e)
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
        self.adj = [list({dest for kind, dest in row if kind != 1}) for row in self.moves]
        assert all(i in self.adj[j] for i, ns in enumerate(self.adj) for j in ns)
        self.cache = {}
        self.windows = {}
        centres = {y * w + x for x in {(w - 1) // 2, w // 2} for y in {(h - 1) // 2, h // 2}}
        self.centre = self.bfs(centres)

    def bfs(self, sources):
        dist = array('H', [INF]) * len(self.adj)
        queue = deque(sources)
        for s in sources:
            dist[s] = 0
        while queue:
            c = queue.popleft()
            nd = dist[c] + 1
            for t in self.adj[c]:
                if dist[t] == INF:
                    dist[t] = nd
                    queue.append(t)
        return dist

    def distances(self, source):
        if source not in self.cache:
            self.cache[source] = self.bfs([source])
        return self.cache[source]

    def window(self, source):
        if source not in self.windows:
            y, x = divmod(source, self.w)
            self.windows[source] = {((y + dy) % self.h) * self.w + (x + dx) % self.w
                                    for dy in range(-3, 4) for dx in range(-3, 4)}
        return self.windows[source]

    def visible(self, a, b):
        ay, ax = divmod(a, self.w)
        by, bx = divmod(b, self.w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, self.w - dx) <= 3 and min(dy, self.h - dy) <= 3


def study(r, q1, growth_group, geometry=None):
    folder = ROOT / 'data/online/ladder' / str(r['battle'])
    path = folder / ('M%d.replay' % r['game'])
    metadata = json.loads((folder / ('game-%d.json' % r['game'])).read_text())
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    if geometry is None:
        geometry = Geometry(w, h, raw)
    else:
        assert (w, h, canonical_edges(w, h, raw)) == (geometry.w, geometry.h, geometry.edges)
    g = geometry
    ours = r['our_side']
    assert metadata['team' + ours + 'Id'] == 1119
    side = lambda i: 'us' if teams[i] == ours else 'them'
    queens = {s: min(i for i in bodies if side(i) == s) for s in ('us', 'them')}
    qu, qt = queens['us'], queens['them']
    initial = {s: sum(side(i) == s for i in bodies) for s in ('us', 'them')}
    first_meal = None
    first_split = None
    pearls50 = Counter()
    pearls100 = Counter()
    present = {}
    memories = defaultdict(dict)
    fresh = None
    hunt_turns = []
    closest = INF
    closest_whole = INF
    adjacency = 0
    adjacency_short = 0
    adjacency_whole = 0
    adjacency_short_whole = 0
    no_meal = Counter()
    joint = Counter()
    deaths = {}
    turn_deaths = []
    rnd, actor, turnseq, step_used = 0, None, 0, 0
    dirs, action_cause = [], None
    current = None
    pending_eat = None
    snap100 = None
    rounds_seen = set()
    candidate_hunt = q1 or (r['queen']['us']['death_round'] is not None
                            and r['queen']['them']['death_round'] is not None
                            and r['queen']['us']['death_round'] <= r['queen']['them']['death_round'])

    def window_active():
        return candidate_hunt and rnd > 100 and qu not in bodies and qt in bodies

    def update_closest():
        nonlocal closest, closest_whole
        if candidate_hunt and qt in bodies:
            d = g.distances(bodies[qt][0])
            nearest = min((d[b[0]] for i, b in bodies.items() if side(i) == 'us' and len(b) <= 4), default=INF)
            closest_whole = min(closest_whole, nearest)
            if window_active():
                closest = min(closest, nearest)

    def finish_turn():
        nonlocal current
        if current is not None and not current['eaten']:
            known = current['known']
            if known:
                d = g.distances(current['head'])
                near = min(d[c] for c in known)
                klass = 'le6' if near <= 6 else '7_15' if near <= 15 else 'gt15' if near != INF else 'unreachable'
            else:
                klass = 'none'
            first = current['first_step']
            net = current['last_step']
            startd = g.centre[current['head']]
            reduced = first is not None and g.centre[first] < startd
            net_reduced = net is not None and g.centre[net] < startd
            no_meal['turns'] += 1
            no_meal['known_' + klass] += 1
            no_meal['centre_reduce'] += int(reduced)
            no_meal['net_centre_reduce'] += int(net_reduced)
            no_meal['no_successful_step'] += int(first is None)
            no_meal['multi_step_turns'] += int(current['steps'] > 1)
            no_meal['centre_unreachable_start'] += int(startd == INF)
            no_meal['enemy_in_view'] += int(current['enemy'])
            joint[klass, int(reduced), int(current['enemy']), int(first is None)] += 1
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if hs:
            assert len(hs) == 2
            for d in hs:
                other = next(z for z in hs if z is not d)
                d['other_id'] = other['id']
                d['other_side'] = other['side']
                d['other_length'] = other['length']
                d['simultaneous_with'] = other['id']
        turn_deaths.clear()
        current = None

    def snapshot():
        return {s: dict(alive=sum(side(i) == s for i in bodies),
                        total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                        longest=max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                        queen_length=len(bodies.get(queens[s], ()))) for s in ('us', 'them')}

    for idx, ev in enumerate(root.pointer(3)):
        kind = ev.u16(0)
        if kind not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kind in (0, 1):
            assert pending_eat is None
            finish_turn()
        if kind == 0:
            if rnd == 100 and 100 in rounds_seen:
                snap100 = snapshot()
            rnd = p.i32(0)
            rounds_seen.add(rnd)
            actor = None
            update_closest()
        elif kind == 1:
            actor = p.i32(0)
            assert actor in bodies
            turnseq += 1
            dirs, step_used, action_cause = [], 0, None
            head = bodies[actor][0]
            if side(actor) == 'us':
                if qt in bodies and g.visible(head, bodies[qt][0]):
                    fresh = rnd
                if growth_group is not None and rnd <= 100:
                    mem = memories[actor]
                    for c in g.window(head):
                        if c in present:
                            mem[c] = (rnd, present[c])
                    known = [c for c, (seen, birth) in mem.items()
                             if rnd - seen <= 25 and present.get(c) == birth]
                    enemy = any(side(i) == 'them' and g.visible(head, b[0]) for i, b in bodies.items())
                    current = dict(head=head, known=known, enemy=enemy, eaten=0,
                                   first_step=None, last_step=None, steps=0)
            if actor == qt and window_active():
                d = g.distances(head)
                heads = [b for i, b in bodies.items() if side(i) == 'us']
                short = [b for b in heads if len(b) <= 4]
                nearest = min((d[b[0]] for b in short), default=INF)
                hunt_turns.append([rnd, len(bodies[qt]), sum(d[b[0]] <= 12 for b in heads),
                                   sum(d[b[0]] <= 12 for b in short),
                                   None if nearest == INF else nearest, None if fresh is None else rnd - fresh,
                                   len(short)])
            update_closest()
        elif kind == 4:
            assert actor == p.i32(0)
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used_up = p.pointer(1)
            action_cause = ('timeout' if p.bit(32) or (used_up is not None and used_up.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)] if a and a.u16(0) < 3 else 'no action')
        elif kind == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                assert c not in present
                present[c] = idx
            else:
                assert c in present and actor in bodies and pending_eat is None
                present.pop(c)
                pending_eat = (actor, c)
                s = side(actor)
                if s == 'us' and first_meal is None:
                    first_meal = rnd
                if rnd <= 50:
                    pearls50[s] += 1
                if rnd <= 100:
                    pearls100[s] += 1
                if current is not None:
                    current['eaten'] += 1
        elif kind == 9:
            i = p.i32(0)
            head, tail = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != head
            active = window_active()
            short_before = len(b) <= 4
            if moved:
                b.appendleft(head)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
            if pending_eat is not None:
                assert pending_eat == (i, head) and moved
                pending_eat = None
            if moved and i == actor:
                step_used += 1
                if current is not None:
                    if current['first_step'] is None:
                        current['first_step'] = head
                    current['last_step'] = head
                    current['steps'] += 1
                if active and side(i) == 'us' and head in g.adj[bodies[qt][0]]:
                    adjacency += 1
                    adjacency_short += int(short_before)
                if candidate_hunt and qt in bodies and side(i) == 'us' and head in g.adj[bodies[qt][0]]:
                    adjacency_whole += 1
                    adjacency_short_whole += int(short_before)
            update_closest()
        elif kind == 10:
            if side(p.i32(0)) == 'us' and first_split is None:
                first_split = rnd
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            update_closest()
        elif kind == 11:
            i, reason = p.i32(0), p.u16(4)
            dest = g.moves[bodies[i][0]][dirs[step_used]][1] if i == actor and step_used < len(dirs) else None
            other = next((z for z, b in bodies.items() if z != i and dest in b), None) if reason == 2 else None
            d = dict(id=i, side=side(i), round=rnd, event=idx, turn=turnseq, actor=actor,
                     length=len(bodies[i]), reason=reason,
                     cause=('wall', 'own body', 'other dragon body', 'head-on', action_cause or 'no action')[reason],
                     other_id=other, other_side=None if other is None else side(other),
                     other_length=None if other is None else len(bodies[other]),
                     queen_lengths_before={s: len(bodies.get(queens[s], ())) for s in ('us', 'them')})
            deaths[i] = d
            turn_deaths.append(d)
            bodies.pop(i)
            update_closest()
    finish_turn()
    assert pending_eat is None
    if rnd == 100:
        snap100 = snapshot()
    final = snapshot()
    assert final == r['final'], (r['game'], final, r['final'])
    assert rnd == r['last_round']
    for z, s in enumerate(('us', 'them') if ours == 'A' else ('them', 'us')):
        st = root.pointer(4).pointer(z)
        assert [final[s][k] for k in ('alive', 'longest', 'total', 'queen_length')] == [st.i32(o) for o in (0, 4, 8, 12)]
    result = root.pointer(4)
    winner = 'AB'[result.u16(6)] if result.u16(4) == 1 else None
    outcome = 'draw' if winner is None else 'win' if winner == ours else 'loss'
    assert outcome == r['result'], (r['game'], outcome, r['result'])
    if r['curves']['100'] is not None:
        assert snap100 is not None
        assert all(snap100[s][k] == r['curves']['100'][s][k] for s in ('us', 'them') for k in final[s])
        assert all(pearls100[s] == r['curves']['100'][s]['pearls'] for s in ('us', 'them'))
    for s in ('us', 'them'):
        assert (deaths.get(queens[s], {}).get('round')) == r['queen'][s]['death_round']
    du, dt = deaths.get(qu), deaths.get(qt)
    reference = bool(du and dt and du['event'] < dt['event'] and du.get('simultaneous_with') != qt)
    base = dict(game=r['game'], battle=r['battle'], map_key=r['map_key'], result=r['result'],
                replay=str(path.relative_to(ROOT)), initial_dragons=initial,
                final_reconstructed=final, final_matches_rows=True, winner_matches_rows=True)
    hunt = None
    if q1 or reference:
        hunt = dict(base, group='Q1' if q1 else 'reference', turns=hunt_turns,
                    closest_short=None if closest_whole == INF else closest_whole,
                    closest_short_window=None if closest == INF else closest,
                    adjacent_steps=adjacency_whole, adjacent_short_steps=adjacency_short_whole,
                    adjacent_steps_window=adjacency, adjacent_short_steps_window=adjacency_short,
                    queen_death=dt, our_queen_death=du)
        if q1:
            assert outcome == 'loss' and qu not in bodies and qt in bodies
            assert final['us']['longest'] > final['them']['longest']
    growth = None
    if growth_group is not None:
        alive100 = snap100['us']['alive'] if snap100 is not None else 0
        assert (alive100 <= 6) == (growth_group == 'never_grew')
        if snap100 is None:
            assert final['us']['alive'] == 0 and rnd < 100
        growth = dict(base, group=growth_group, two_a_side=initial == {'us': 2, 'them': 2},
                      alive_end_round100=alive100, gone_before100=snap100 is None,
                      first_meal_round=first_meal, first_split_round=first_split,
                      pearls_through50={s: pearls50[s] for s in ('us', 'them')},
                      no_meal=dict(no_meal),
                      joint=[list(k) + [n] for k, n in sorted(joint.items())])
    return hunt, growth, base, g


def study_layout(args):
    rows, q1, groups = args
    geometry = None
    hunts, growths, checks = [], [], []
    for r in rows:
        hunt, growth, check, geometry = study(r, r['game'] in q1, groups.get(r['game']), geometry)
        if hunt is not None:
            hunts.append(hunt)
        if growth is not None:
            growths.append(growth)
        checks.append(check)
    return hunts, growths, checks


def main():
    rows, q1, groups, maps = load_inputs()
    refresh_hunt = '--refresh-hunt' in sys.argv
    if refresh_hunt:
        wanted = {r['game'] for r in json.loads((OUT / 'hunt.json').read_text())}
        rows = [r for r in rows if r['game'] in wanted]
        groups = {}
    bymap = defaultdict(list)
    for r in rows:
        bymap[r['map_key']].append(r)
    hunts, growths, checks = [], [], []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(study_layout, (rs, q1, groups)): key for key, rs in bymap.items()}
        for future in as_completed(futures):
            hh, gg, cc = future.result()
            hunts.extend(hh)
            growths.extend(gg)
            checks.extend(cc)
            print(f'{futures[future]}: {len(cc)} checked; total {len(checks)}/{len(rows)}', flush=True)
    hunts.sort(key=lambda r: r['game'])
    growths.sort(key=lambda r: r['game'])
    checks.sort(key=lambda r: r['game'])
    assert sum(r['group'] == 'Q1' for r in hunts) == len(q1)
    assert {r['game'] for r in hunts if r['group'] == 'Q1'} == q1
    assert {r['game'] for r in growths} == set(groups)
    assert len(checks) == len(rows)
    for r in checks:
        assert r['initial_dragons']['us'] == maps[r['map_key']]['dragons_at_spawn']
    outputs = [('hunt.json', hunts)] if refresh_hunt else [('hunt.json', hunts), ('growth.json', growths), ('validation.json', checks)]
    if refresh_hunt:
        assert {r['game'] for r in hunts} == wanted
    for name, value in outputs:
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (DATA / 'rows.jsonl', DATA / 'maps.json', DATA / 'losses/losses.json')}
    if refresh_hunt:
        assert inputs == json.loads((OUT / 'inputs.json').read_text())
    else:
        (OUT / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    print('FINAL', len(hunts), 'hunt;', len(growths), 'growth;', len(checks), 'checked', flush=True)


if __name__ == '__main__':
    main()
