#!/usr/bin/env python3
"""Read-only replay audit; run python3 -B verify/check.py from the workspace.

Round tables are end-of-round (as tools/show.py). Turn metrics are sampled
before kind-1 turnStart events, with the closing round included literally.
Only check.md is written. No bots, models, or network are invoked.
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict, deque

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'tools'))
from replay_format import load, point
from show import snapshot


def audit(name, start=None):
    path = BASE / f'runs/eval-final/sqheld_{name}/seed-1-A-side-0/game.replay'
    root = load(path).root()
    dragons, edges, portals = {}, {}, defaultdict(list)
    for line in root.text(0).splitlines():
        f = line.split('#', 1)[0].split()
        if not f:
            continue
        if f[0] == 'MAP':
            w, h = map(int, f[1:3])
        elif f[0] == 'EDGE':
            i, kind, partner = map(int, f[1:4])
            edges[i] = kind
            if kind == 2:
                portals[partner].append(i)
        elif f[0] == 'DRAGON':
            c = list(map(int, f[3:]))
            dragons[len(dragons)] = dict(team=int(f[1]), body=deque(zip(c[::2], c[1::2])))
    partners = {a: b for pair in portals.values() for a, b in (pair, pair[::-1])}
    graph = {}
    for y in range(h):
        for x in range(w):
            moves = []
            for d, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
                edge = (2*y + (0 if d == 0 else 2 if d == 2 else 1))*(w+1) + x + (d == 1)
                if edges.get(edge, 0) == 1:
                    continue
                dest = ((x+dx) % w, (y+dy) % h)
                if edge in partners:
                    row, col = divmod(partners[edge], w+1)
                    assert (row % 2 == 0) == (d in (0, 2)), 'portal orientations differ'
                    dest = ((col - (d == 3)) % w, (row//2 - (d == 0)) % h)
                moves.append(dest)
            graph[x, y] = moves
    reverse = defaultdict(list)
    for cell, targets in graph.items():
        for target in targets:
            reverse[target].append(cell)
    occupied = Counter(cell for d in dragons.values() for cell in d['body'])
    round_no, active, active_team = 0, None, None
    rounds, death_codes, head_roles = {}, Counter(), Counter()
    free_hist, dist_hist, queen_dist_hist, queen_lengths = Counter(), Counter(), Counter(), Counter()
    reachable_queen = []
    near_cache = {}
    queen_close_ids, queen_close_observations = set(), 0
    queen_enemy_counts = []
    close_ids, close_observations, close_rounds = set(), 0, set()
    adjacent_ids, adjacent_observations, adjacent_turns = set(), 0, 0
    queen_adjacent = 0
    all_enemy_counts = []
    stops = []
    update_checks = 0

    def save_round():
        enemies = [d for d in dragons.values() if d['team'] == 1]
        q = dragons.get(0)
        rounds[round_no] = (len(enemies), max((len(d['body']) for d in enemies), default=0),
                            len(q['body']) if q else 0)

    def turn_metrics(dragon_id):
        nonlocal close_observations, adjacent_observations, adjacent_turns, queen_adjacent, queen_close_observations
        if start is None or round_no < start:
            return
        q = dragons.get(0)
        assert q and q['team'] == 0, 'queen absent during requested interval'
        head = q['body'][0]
        enemies = [(i, d['body'][0]) for i, d in dragons.items() if d['team'] == 1]
        all_enemy_counts.append(len(enemies))
        # Geometric cell proximity: wrapped Manhattan distance, ignoring walls/bodies.
        body_key = tuple(q['body'])
        if body_key not in near_cache:
            near_cells = set()
            for x, y in body_key:
                for dx in range(-3, 4):
                    for dy in range(-3+abs(dx), 4-abs(dx)):
                        near_cells.add(((x+dx) % w, (y+dy) % h))
            near_cache[body_key] = near_cells
        near_cells = near_cache[body_key]
        nearby = {i for i, cell in enemies if cell in near_cells}
        close_ids.update(nearby)
        close_observations += len(nearby)
        if nearby:
            close_rounds.add(round_no)
        adjacent = {i for i, cell in enemies if cell in graph[head]}
        adjacent_ids.update(adjacent)
        adjacent_observations += len(adjacent)
        adjacent_turns += bool(adjacent)
        # Reverse BFS lets source enemy heads and destination queen head be occupied;
        # every intermediate cell must be unoccupied. Other heads also block.
        distances = {head: 0}
        todo = deque([head])
        while todo:
            cell = todo.popleft()
            for prev in reverse[cell]:
                if prev in distances:
                    continue
                distances[prev] = distances[cell] + 1
                if not occupied[prev]:
                    todo.append(prev)
        best = min((distances[cell] for _, cell in enemies if cell in distances), default=None)
        dist_hist[best] += 1
        if dragon_id != 0:
            return
        queen_adjacent += len(adjacent)
        queen_lengths[len(q['body'])] += 1
        queen_enemy_counts.append(len(enemies))
        queen_close_ids.update(nearby)
        queen_close_observations += len(nearby)
        free_hist[sum(not occupied[cell] for cell in graph[head])] += 1
        stops.append((round_no, head, body_key))
        queen_dist_hist[best] += 1
        if best is not None:
            reachable_queen.append((round_no, best))

    def remove_body(d):
        occupied.subtract(d['body'])

    for event in root.pointer(3):
        kind, p = event.u16(0), event.pointer(0)
        if kind == 0:
            save_round()
            round_no = p.i32(0) + 1
        elif kind == 1:
            active = p.i32(0)
            assert active in dragons
            active_team = dragons[active]['team']
            turn_metrics(active)
        elif kind == 9:
            d = dragons[p.i32(0)]
            old_head = d['body'][0]
            new_head = point(p.pointer(0))
            assert new_head == old_head or new_head in graph[old_head], (old_head, new_head, round_no)
            update_checks += 1
            remove_body(d)
            d['body'].appendleft(new_head)
            tail = point(p.pointer(1))
            while len(d['body']) > 1 and d['body'][-1] != tail:
                d['body'].pop()
            occupied.update(d['body'])
        elif kind == 10:
            parent, child, team = p.i32(0), p.i32(4), p.u16(8)
            remove_body(dragons[parent])
            for i, index in ((parent, 0), (child, 1)):
                dragons[i] = dict(team=team, body=deque(point(c) for c in p.pointer(index)))
                occupied.update(dragons[i]['body'])
        elif kind == 11:
            i, code = p.i32(0), p.u16(4)
            d = dragons.pop(i)
            remove_body(d)
            if d['team'] == 1 and round_no >= 320:
                death_codes[code] += 1
                if code == 3:
                    assert i == active or active_team == 0
                    head_roles['initiated' if i == active else 'hit by active enemy'] += 1
    save_round()
    final = snapshot(path)
    assert final['round'] == round_no
    assert final['dragons'] == dragons or all(
        final['dragons'][i]['team'] == d['team'] and final['dragons'][i]['body'] == d['body']
        for i, d in dragons.items()) and len(final['dragons']) == len(dragons)
    for r in ((start, 186, 200, 300, 400, 500) if start else (320, 360, 400, 440, 480, 489)):
        s = snapshot(path, r)
        enemies = [d for d in s['dragons'].values() if d['team'] == 1]
        assert rounds[r][:2] == (len(enemies), max((len(d['body']) for d in enemies), default=0))
        assert rounds[r][2] == (len(s['dragons'][0]['body']) if 0 in s['dragons'] else 0)
    return dict(name=name, start=start, rounds=rounds, final=final, free=dict(free_hist),
                distance=dict(dist_hist), queen_distance=dict(queen_dist_hist), reachable_queen=reachable_queen,
                queen_enemy_range=(min(queen_enemy_counts), max(queen_enemy_counts)) if queen_enemy_counts else None,
                end_round_enemy_range=(min(v[0] for n, v in rounds.items() if n >= start), max(v[0] for n, v in rounds.items() if n >= start)) if start else None,
                queen_nearby=len(queen_close_ids), queen_nearby_observations=queen_close_observations,
                lengths=dict(queen_lengths), nearby=len(close_ids),
                nearby_observations=close_observations, nearby_rounds=len(close_rounds),
                adjacent=len(adjacent_ids), adjacent_observations=adjacent_observations,
                adjacent_turns=adjacent_turns, queen_adjacent=queen_adjacent,
                enemy_range=(min(all_enemy_counts), max(all_enemy_counts)) if all_enemy_counts else None,
                deaths=dict(death_codes), head_roles=dict(head_roles), updates=update_checks,
                stops=stops)


def main():
    results = [audit('blobs_large_90030', 186), audit('portalrooms_large_90006', 56),
               audit('portals_medium_90020')]
    for r in results:
        print({k: v for k, v in r.items() if k not in ('rounds', 'final', 'stops')})
        print('rounds', {n: r['rounds'][n] for n in (56, 186, 200, 300, 320, 360, 400, 440, 480, 489, 500) if n in r['rounds']})
        print('end', r['final']['winner'], r['final']['end_reason'], r['final']['standings'])
        if r['stops']:
            print('first turn starts', [(n, cell, len(body)) for n, cell, body in r['stops'][:5]])
    lines = [
        '# Replay verification',
        'Reproduce: `python3 -B verify/check.py`. Uses `tools/replay_format.py`; round tables cross-checked against `tools/show.py`.',
        'Rounds below mean end-of-round. Intervals include every dragon turn start in the stated closing round through r500; free-neighbour distributions use queen turn starts only.',
        'Movement graph respects wall edges, wrapping and portals (every replay update checked). BFS blocks all occupied intermediate cells; source enemy head and destination queen head are allowed endpoints; unreachable = ∞.',
        '“Within 3 cells” means wrapped Manhattan distance ≤3 to any queen segment, ignoring obstacles; counts are distinct enemy IDs, with repeated head observations stated separately.',
        '',
        '## W1 — confirmed: NO as stated; survival, length and queen-rule wins: YES.',
    ]
    for r in results[:2]:
        lines.append(f"**{r['name']}**, from r{r['start']}: dragon 0 alive at end; end-round lengths r{r['start']}/r186/r300/r400/r500 = " + '/'.join(str(r['rounds'][n][2]) for n in (r['start'], 186, 300, 400, 500)) + '.')
        lines.append(f"Free-neighbour distribution: {r['free']} (free neighbours: queen turns). Reachable queen-start distances (round, distance): {r['reachable_queen']}; other {r['queen_distance'].get(None, 0)} queen starts unreachable.")
        finite = [d for d in r['distance'] if d is not None]
        lines.append(f"Across all {sum(r['distance'].values())} turn starts: minimum enemy-head path = {min(finite)}; unreachable at {r['distance'].get(None, 0)} starts. Enemy heads next to queen head: {r['adjacent_observations']} observations ({r['adjacent']} IDs); also zero at queen starts.")
        lines.append('Enemy dragons at r200/r300/r400/r500 = ' + '/'.join(str(r['rounds'][n][0]) for n in (200, 300, 400, 500)) + f"; range at all turn starts {r['enemy_range']}, queen starts {r['queen_enemy_range']}, round ends {r['end_round_enemy_range']}.")
        lines.append(f"Enemy heads within 3 of queen body: {r['nearby']} distinct IDs; {r['nearby_observations']} observations across all turn starts, in {r['nearby_rounds']} rounds. Queen starts alone: {r['queen_nearby']} IDs, {r['queen_nearby_observations']} observations.")
        a, b = r['final']['standings']
        lines.append(f"End: r500 round limit, side 0 wins longer queen {a['queen']}–{b['queen']}; side 0/1 dragons {a['dragons']}/{b['dragons']}, longest {a['longest']}/{b['longest']}, total length {a['total']}/{b['total']}.")
    lines.extend([
        'Differences: blobs has two free neighbours at the r186 queen start; head remains reachable at queen starts r186–188. The reported 47–64 enemies is 45–64 during turns, 46–64 at queen starts/round ends. Portalrooms has two free neighbours at the r56 queen start and reachable head at r56–57. Later sampled queen starts have one free neighbour and no free-cell enemy path.',
        '',
        '## W2 — reported dragon counts confirmed: YES; deliberate self-thinning/feed-one-long-dragon interpretation: NOT established.',
    ])
    r = results[2]
    lines.append('**portals_medium_90020**, side 1: counts r320/r360/r440/r480/r489 = ' + '/'.join(str(r['rounds'][n][0]) for n in (320, 360, 440, 480, 489)) + '; no count differs. Longest lengths r320/r400/r440/r480 = ' + '/'.join(str(r['rounds'][n][1]) for n in (320, 400, 440, 480)) + '.')
    c, roles = r['deaths'], r['head_roles']
    lines.append(f"Deaths r320–489 inclusive: {sum(c.values())} total; head hit by active enemy {roles['hit by active enemy']}; own turn initiating head-to-head {roles['initiated']} (head-to-head combined {c[3]}); wall {c.get(0, 0)}; body {c.get(1, 0)+c.get(2, 0)} (self {c.get(1, 0)}, another dragon {c.get(2, 0)}); no valid action {c.get(4, 0)}.")
    lines.append('Replay death codes: 0 wall, 1 self-body, 2 other-body, 3 head-to-head, 4 no valid action; last category does not prove no output was sent. Most deaths are combat; longest length falls to 8 then 3, so these measurements do not establish intentional feeding of one banker.')
    a, b = r['final']['standings']
    lines.append(f"End: r489 elimination, side 0 wins; side 0/1 dragons {a['dragons']}/{b['dragons']}, longest {a['longest']}/{b['longest']}, total length {a['total']}/{b['total']}, queens {a['queen']}/{b['queen']}.")
    assert len(lines) <= 30
    (BASE / 'verify/check.md').write_text('\n'.join(lines) + '\n')
    return results


if __name__ == '__main__':
    main()
