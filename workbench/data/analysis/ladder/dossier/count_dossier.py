#!/usr/bin/env python3
"""Offline dossier. Run python3 -B; all writes are confined to this directory."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
DATA = OUT.parent
spec = importlib.util.spec_from_file_location('dossier_previous_counts', DATA / 'losses/counts/count_replays.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
replay, Geometry = previous.replay, previous.Geometry
SIDES = ('us', 'them')
PHASES = {'0-50': (0, 50), '51-100': (51, 100), '101-200': (101, 200), '201-300': (201, 300)}
RANGES = {**PHASES, '0-100': (0, 100), '101-300': (101, 300)}
CAUSES = ('head-on mover', 'head-on hit', 'wall', 'own body', 'another body', 'no action',
          'unpaid sprint', 'illegal split', 'timeout')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ratio(n, d):
    return n / d if d else None

def stats(values):
    return dict(n=len(values), sum=sum(values), mean=ratio(sum(values), len(values)))

def fresh():
    return dict(pearls_eaten=0, splits=0, deaths={c: 0 for c in CAUSES}, turns=0,
                no_view_pearl_turns=0, no_view_pearl_moved=0, keeps_eligible=0, keeps=0, dither=0,
                adjacent_pearl_turns=0, adjacent_pearl_missed=0, hot_turns=0, portal_steps=0,
                cross_head_on_trades=0, head_on_length_lost=0, head_on_other_length_lost=0,
                same_team_head_on_trades=0)

class Geo(Geometry):
    def __init__(self, w, h, raw):
        super().__init__(w, h, raw)
        self.near_cache = {}
        self.component = [-1] * (w * h)
        cid = 0
        for src in range(w * h):
            if self.component[src] >= 0:
                continue
            self.component[src] = cid
            queue = deque([src])
            while queue:
                c = queue.popleft()
                for kind, dest in self.moves[c]:
                    if kind == 0 and self.component[dest] < 0:
                        self.component[dest] = cid
                        queue.append(dest)
            cid += 1
        self.component_count = cid

    def near6(self, src):
        if src not in self.near_cache:
            seen, front = {src}, {src}
            for _ in range(6):
                front = {z for c in front for z in self.adj[c]} - seen
                seen |= front
            self.near_cache[src] = seen
        return self.near_cache[src]


def scan(row, g=None):
    path = ROOT / 'data/online/ladder' / str(row['battle']) / ('M%d.replay' % row['game'])
    meta_path = path.parent / ('game-%d.json' % row['game'])
    metadata = json.loads(meta_path.read_text())
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2*k])*w + int(q[3 + 2*k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    if g is None:
        g = Geo(w, h, raw)
    else:
        assert (w, h, previous.canonical_edges(w, h, raw)) == (g.w, g.h, g.edges)
    ours = row['our_side']
    assert metadata['team' + ours + 'Id'] == 1119
    side = lambda i: 'us' if teams[i] == ours else 'them'
    starts = {s: [dict(id=i, length=len(b), head=[b[0] % w, b[0] // w])
                  for i, b in bodies.items() if side(i) == s] for s in SIDES}
    queens = {s: min(z['id'] for z in starts[s]) for s in SIDES}
    assert set(queens.values()) == {0, 1}
    start_cells = {s: [z['head'][1]*w + z['head'][0] for z in starts[s]] for s in SIDES}
    start_components = {s: {g.component[c] for c in start_cells[s]} for s in SIDES}
    reachable = {s: g.bfs(start_cells[s]) for s in SIDES}
    portal_only = {s: {c for c in range(w*h) if reachable[s][c] != previous.INF
                      and g.component[c] not in start_components[s]} for s in SIDES}
    room_cells = {c for c in range(w*h) if g.component[c] not in start_components['us'] | start_components['them']
                  and any(reachable[s][c] != previous.INF for s in SIDES)}
    # Voronoi halves use start-head path distance, leaving equal-distance tiles neutral.
    enemy_half = {s: {c for c in range(w*h) if reachable[s][c] > reachable[SIDES[1-SIDES.index(s)]][c]}
                  for s in SIDES}
    count = {s: {name: fresh() for name in RANGES} for s in SIDES}
    seen = {s: set() for s in SIDES}
    seen_snaps, state_snaps, half_snaps = {}, {}, {}
    queen_death = {s: None for s in SIDES}
    first_contact = {s: None for s in SIDES}
    portal_total = Counter()
    trail = {i: deque([b[0]], maxlen=12) for i, b in bodies.items()}
    lastdir = {}
    births_by_tile = Counter()
    pearls, present = [], {}
    visit = {}
    turn_deaths = []
    rnd, actor, used = 0, None, 0
    dirs, action_cause, current = [], None, None
    started = False
    pending = None
    active_ranges = []
    all_eats = Counter()
    all_splits, all_deaths = Counter(), Counter()

    def standings():
        return {s: dict(alive=sum(side(i) == s for i in bodies),
                        total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                        longest=max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                        queen_length=len(bodies.get(queens[s], ()))) for s in SIDES}

    def snapshot(n):
        if n in (50, 100, 200, 300):
            state_snaps[str(n)] = standings()
            seen_snaps[str(n)] = {s: len(seen[s]) for s in SIDES}
            half_snaps[str(n)] = {s: dict(n=sum(b[0] in enemy_half[s] for i, b in bodies.items() if side(i) == s),
                                         d=sum(side(i) == s for i in bodies)) for s in SIDES}

    def finish_turn():
        nonlocal current
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if hs:
            assert len(hs) == 2 and sum(d['id'] == actor for d in hs) == 1
            mover = next(d for d in hs if d['id'] == actor)
            hit = next(d for d in hs if d['id'] != actor)
            assert mover['destination'] == hit['head']
            if mover['side'] != hit['side']:
                for own, other in ((mover, hit), (hit, mover)):
                    for name in active_ranges:
                        c = count[own['side']][name]
                        c['cross_head_on_trades'] += 1
                        c['head_on_length_lost'] += own['length']
                        c['head_on_other_length_lost'] += other['length']
            else:
                for name in active_ranges:
                    count[mover['side']][name]['same_team_head_on_trades'] += 1
            for d in hs:
                if d['queen']:
                    queen_death[d['side']].update(other_id=hit['id'] if d is mover else mover['id'],
                        other_length=hit['length'] if d is mover else mover['length'],
                        cross_team=mover['side'] != hit['side'])
        turn_deaths.clear()
        if current is None:
            return
        t = current
        s, i = t['side'], t['id']
        for name in active_ranges:
            c = count[s][name]
            if t['adjacent']:
                c['adjacent_pearl_missed'] += int(not t['adjacent_eaten'])
            if t['no_pearl'] and t['first'] is not None:
                c['no_view_pearl_moved'] += 1
                c['dither'] += int(t['first'] in t['trail'])
                if t['previous'] is not None:
                    c['keeps_eligible'] += 1
                    c['keeps'] += int(t['first_dir'] == t['previous'])
        lastdir[i] = t['first_dir']
        current = None

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            assert pending is None
            finish_turn()
        if k == 0:
            if started:
                snapshot(rnd)
            started = True
            rnd, actor = p.i32(0), None
            active_ranges = [name for name, (lo, hi) in RANGES.items() if lo <= rnd <= hi]
        elif k == 1:
            actor = p.i32(0)
            assert actor in bodies
            dirs, used, action_cause = [], 0, None
            s = side(actor)
            head = bodies[actor][0]
            if first_contact[s] is None and any(side(i) != s and g.visible(head, b[0]) for i, b in bodies.items()):
                first_contact[s] = rnd
            if not active_ranges:
                continue
            win = g.window(head)
            seen[s] |= win
            no_pearl = not any(c in present for c in win)
            adjacent = {dest for kind, dest in g.moves[head] if kind != 1 and dest in present}
            hot = any(births_by_tile[c] >= 2 for c in {head} | set(g.adj[head]))
            current = dict(id=actor, side=s, head=head, no_pearl=no_pearl, adjacent=adjacent,
                           adjacent_eaten=set(), previous=lastdir.get(actor), trail=set(trail[actor]),
                           first=None, first_dir=None, visit=[])
            for name in active_ranges:
                c = count[s][name]
                c['turns'] += 1
                c['no_view_pearl_turns'] += int(no_pearl)
                c['adjacent_pearl_turns'] += int(bool(adjacent))
                c['hot_turns'] += int(hot)
                lo, hi = RANGES[name]
                bucket = (rnd - lo) // 20
                key = (s, name, actor, bucket)
                v = visit.setdefault(key, dict(tiles=set(), no_pearl_tiles=set(), rounds=set(), no_pearl_rounds=set()))
                v['tiles'].add(head)
                v['rounds'].add(rnd)
                if no_pearl:
                    v['no_pearl_tiles'].add(head)
                    v['no_pearl_rounds'].add(rnd)
                current['visit'].append(v)
        elif k == 4:
            assert actor == p.i32(0)
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            fuel = p.pointer(1)
            action_cause = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)] if a and a.u16(0) < 3 else 'no action')
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                assert c not in present
                origin = 'natural' if actor is None else 'death_drop'
                pr = dict(tile=c, birth_round=rnd, birth_event=idx, origin=origin,
                          near6={s: False for s in SIDES}, eater=None, eat_round=None,
                          portal_room=c in room_cells, portal_required={s: c in portal_only[s] for s in SIDES})
                if rnd <= 300:
                    near = g.near6(c)
                    for s in SIDES:
                        pr['near6'][s] = any(side(i) == s and b[0] in near for i, b in bodies.items())
                pearls.append(pr)
                present[c] = pr
                births_by_tile[c] += 1
            else:
                assert c in present and actor in bodies and pending is None
                pr = present.pop(c)
                s = side(actor)
                pr.update(eater=s, eater_id=actor, eat_round=rnd, wait=rnd-pr['birth_round'])
                pending = (actor, c)
                all_eats[s] += 1
                for name in active_ranges:
                    count[s][name]['pearls_eaten'] += 1
                if current is not None and c in current['adjacent']:
                    current['adjacent_eaten'].add(c)
        elif k == 9:
            i = p.i32(0)
            head, tail = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            moved = old != head
            if moved:
                b.appendleft(head)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
            if pending is not None:
                assert pending == (i, head) and moved
                pending = None
            if i == actor and moved:
                assert used < len(dirs)
                direction = dirs[used]
                kind, dest = g.moves[old][direction]
                assert kind != 1 and dest == head
                used += 1
                if kind == 2:
                    portal_total[side(i)] += 1
                    for name in active_ranges:
                        count[side(i)][name]['portal_steps'] += 1
                if current is not None:
                    if current['first'] is None:
                        current['first'], current['first_dir'] = head, direction
                    for v in current['visit']:
                        v['tiles'].add(head)
                        if current['no_pearl']:
                            v['no_pearl_tiles'].add(head)
                trail[i].append(head)
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            assert parent == actor and child not in teams
            length = len(bodies[parent])
            s = side(parent)
            all_splits[s] += 1
            for name in active_ranges:
                count[s][name]['splits'] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            assert len(bodies[parent]) + len(bodies[child]) == length
            trail[child] = deque([bodies[child][0]], maxlen=12)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            dest = g.moves[bodies[i][0]][dirs[used]][1] if i == actor and used < len(dirs) else None
            cause = ('wall', 'own body', 'another body',
                     'head-on mover' if i == actor else 'head-on hit', action_cause or 'no action')[reason]
            d = dict(id=i, side=s, round=rnd, event=idx, reason=reason, cause=cause,
                     length=len(bodies[i]), head=bodies[i][0], destination=dest, queen=i == queens[s])
            if d['queen']:
                assert queen_death[s] is None
                queen_death[s] = {k: v for k, v in d.items() if k not in ('head', 'destination')}
            turn_deaths.append(d)
            all_deaths[s] += 1
            for name in active_ranges:
                count[s][name]['deaths'][cause] += 1
            bodies.pop(i)
    finish_turn()
    assert pending is None
    snapshot(rnd)
    final = standings()
    assert final == row['final'], (row['game'], final, row['final'])
    assert rnd == row['last_round']
    result = root.pointer(4)
    for z, s in enumerate(SIDES if ours == 'A' else ('them', 'us')):
        st = result.pointer(z)
        assert [final[s][k] for k in ('alive', 'longest', 'total', 'queen_length')] == [st.i32(o) for o in (0, 4, 8, 12)]
    winner = 'AB'[result.u16(6)] if result.u16(4) == 1 else None
    assert ('draw' if winner is None else 'win' if winner == ours else 'loss') == row['result']
    for n in (50, 100, 200, 300):
        old = row['curves'].get(str(n))
        if old is not None:
            assert state_snaps[str(n)] == {s: {k: old[s][k] for k in final[s]} for s in SIDES}
            for s in SIDES:
                names = [name for name in PHASES if RANGES[name][1] <= n]
                assert sum(count[s][name]['pearls_eaten'] for name in names) == old[s]['pearls']
    for s in SIDES:
        assert len(starts[s]) + all_splits[s] - all_deaths[s] == final[s]['alive']
        assert all_eats[s] == row['curves']['end'][s]['pearls']
        assert (queen_death[s] or {}).get('round') == row['queen'][s]['death_round']
        assert (queens[s] in bodies) == row['queen'][s]['alive_end']
    outputs = []
    for s in SIDES:
        ranges = {}
        for name, (lo, hi) in RANGES.items():
            c = count[s][name]
            cohort = [pr for pr in pearls if lo <= pr['birth_round'] <= hi]
            waits = [pr['wait'] for pr in cohort if pr['eater'] == s]
            natural = [pr for pr in cohort if pr['origin'] == 'natural']
            rooms = [pr for pr in cohort if pr['portal_room']]
            required = [pr for pr in cohort if pr['portal_required'][s]]
            vrows = []
            for (vs, vn, i, block), v in visit.items():
                if vs == s and vn == name:
                    start, end = lo + block*20, lo + block*20 + 19
                    vrows.append(dict(dragon=i, start=start, end=min(end, hi, rnd), full_20=end <= min(hi, rnd),
                                      active_rounds=len(v['rounds']), no_pearl_rounds=len(v['no_pearl_rounds']),
                                      distinct=len(v['tiles']), no_pearl_distinct=len(v['no_pearl_tiles'])))
            full = [v for v in vrows if v['full_20']]
            c.update(start=lo, end=hi, observed_rounds=max(0, min(rnd, hi)-lo+1),
                     end_state=state_snaps.get(str(hi), {}).get(s),
                     seen_tiles_end=seen_snaps.get(str(hi), {}).get(s),
                     seen_share_end=ratio(seen_snaps.get(str(hi), {}).get(s, 0), w*h) if str(hi) in seen_snaps else None,
                     dither_share=ratio(c['dither'], c['no_view_pearl_moved']),
                     keeps_direction_share=ratio(c['keeps'], c['keeps_eligible']),
                     adjacent_pearl_missed_share=ratio(c['adjacent_pearl_missed'], c['adjacent_pearl_turns']),
                     hot_tile_share=ratio(c['hot_turns'], c['turns']),
                     distinct_per_dragon_20=stats([v['distinct'] for v in full]),
                     no_view_pearl_distinct_per_dragon_20=stats([v['no_pearl_distinct'] for v in full if v['no_pearl_rounds']]),
                     visit_windows=sorted(vrows, key=lambda v: (v['start'], v['dragon'])),
                     births=len(cohort), near6_births=sum(pr['near6'][s] for pr in cohort),
                     near6_birth_share=ratio(sum(pr['near6'][s] for pr in cohort), len(cohort)),
                     cohort_eaten={ss: sum(pr['eater'] == ss for pr in cohort) for ss in SIDES},
                     cohort_eaten_share={ss: ratio(sum(pr['eater'] == ss for pr in cohort), len(cohort)) for ss in SIDES},
                     cohort_wait=stats(waits), cohort_not_eaten=sum(pr['eater'] is None for pr in cohort),
                     natural_births=len(natural), natural_near6=sum(pr['near6'][s] for pr in natural),
                     natural_eaten={ss: sum(pr['eater'] == ss for pr in natural) for ss in SIDES},
                     portal_room_births=len(rooms), portal_room_eaten={ss: sum(pr['eater'] == ss for pr in rooms) for ss in SIDES},
                     portal_required_births=len(required), portal_required_eaten={ss: sum(pr['eater'] == ss for pr in required) for ss in SIDES},
                     head_on_net_length_lost=c['head_on_length_lost']-c['head_on_other_length_lost'])
            ranges[name] = c
        outputs.append(dict(game=row['game'], battle=row['battle'], layout_key=row['map_key'],
                            map_name=row['map'], map_version=row['map_version'], cells=w*h, width=w, height=h,
                            starting_dragons=starts[s], all_starting_dragons=starts, opponent_rating=row['opponent_rating'],
                            our_side=ours, side=ours if s == 'us' else ('B' if ours == 'A' else 'A'), relation=s,
                            team='meow' if s == 'us' else row['opponent'], result=row['result'] if s == 'us' else
                            ('draw' if row['result'] == 'draw' else 'loss' if row['result'] == 'win' else 'win'),
                            our_result=row['result'], ended_by=row['ended_by'], last_round=rnd,
                            replay=str(path.relative_to(ROOT)), ranges=ranges,
                            portal_steps_game=portal_total[s],
                            portal_births_game=dict(
                                rooms=sum(pr['portal_room'] for pr in pearls),
                                room_eaten={ss: sum(pr['portal_room'] and pr['eater'] == ss for pr in pearls) for ss in SIDES},
                                required=sum(pr['portal_required'][s] for pr in pearls),
                                required_eaten={ss: sum(pr['portal_required'][s] and pr['eater'] == ss for pr in pearls) for ss in SIDES}),
                            portal_room_cells=len(room_cells),
                            portal_required_cells=len(portal_only[s]), components_without_portals=g.component_count,
                            first_enemy_head_in_view=first_contact[s], first_contact_observed_through=rnd,
                            heads_enemy_half={str(n): dict(**half_snaps[str(n)][s],
                                share=ratio(half_snaps[str(n)][s]['n'], half_snaps[str(n)][s]['d']))
                                if str(n) in half_snaps else None for n in (50, 100)},
                            queen=dict(id=queens[s], death=queen_death[s],
                                       length={str(n): state_snaps.get(str(n), {}).get(s, {}).get('queen_length')
                                               for n in (50, 100, 200, 300)}, alive_end=queens[s] in bodies),
                            final_reconstructed=final[s], final_matches_rows=True, winner_matches_rows=True,
                            game_counts=dict(pearls_eaten=all_eats[s], splits=all_splits[s], deaths=all_deaths[s])))
    validation = dict(game=row['game'], final_reconstructed=final, final_matches_rows=True, winner_matches_rows=True,
                      replay_sha256=sha(path), metadata_sha256=sha(meta_path), replay=str(path.relative_to(ROOT)))
    return outputs, validation, g


def worker(rows):
    records, checks, geo = [], [], None
    for n, r in enumerate(rows, 1):
        out, check, geo = scan(r, geo)
        records.extend(out)
        checks.append(check)
        if n % 10 == 0:
            print(f'{r["map_key"]}: {n}/{len(rows)}', flush=True)
    return records, checks


def main():
    source = (DATA / 'rows.jsonl').read_bytes()
    rows = [r for r in map(json.loads, source.decode().splitlines()) if r['our_code'] == 'main']
    assert len({r['game'] for r in rows}) == len(rows)
    maps = json.loads((DATA / 'maps.json').read_text())
    assert len({r['map_key'] for r in rows}) == 19
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in [DATA / 'rows.jsonl', DATA / 'maps.json',
               DATA / 'losses/counts/count_replays.py', ROOT / 'tools/ladder_replay.py']}
    snapshot = dict(time=datetime.now().astimezone().isoformat(timespec='seconds'), rows_sha256=inputs[str((DATA/'rows.jsonl').relative_to(ROOT))],
                    inputs_sha256=inputs, games=len(rows), rows=rows, maps=maps)
    (OUT / 'input-snapshot.json').write_text(json.dumps(snapshot, ensure_ascii=False) + '\n')
    layouts = defaultdict(list)
    for r in rows:
        layouts[r['map_key']].append(r)
    records, checks = [], []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(worker, sorted(rs, key=lambda r: r['game'])) for rs in layouts.values()]
        for fut in as_completed(futures):
            out, validation = fut.result()
            records.extend(out)
            checks.extend(validation)
            print(f'Validated {len(checks)}/{len(rows)} games', flush=True)
    records.sort(key=lambda r: (r['game'], r['relation']))
    checks.sort(key=lambda r: r['game'])
    assert {r['game'] for r in checks} == {r['game'] for r in rows}
    assert len(records) == 2*len(rows)
    assert all(len([r for r in records if r['game'] == i]) == 2 for i in {r['game'] for r in rows})
    for name, expected in inputs.items():
        assert sha(ROOT/name) == expected, ('Input changed during run', name)
    (OUT / 'per-game.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in records))
    (OUT / 'validation.json').write_text(json.dumps(dict(games_verified=len(checks), sides=len(records),
                final_standings_matches=len(checks), winner_matches=len(checks), checks=checks), ensure_ascii=False, indent=2)+'\n')
    print(f'RECONSTRUCTION COMPLETE {len(checks)} games / {len(records)} sides', flush=True)

if __name__ == '__main__':
    main()
