#!/usr/bin/env python3
"""Card #47 look: a ledger of dead-end visits, counted from the replays.
A visit starts when one of our heads steps past the gate into a shut area (at most 31 tiles, one way in) and ends when
the dragon and every child born during the stay has left or died. Net = total length that walked out - length that walked in.
usage: ledger47.py <dir with card_47_check.py> <out.json> [workers]"""
import collections, concurrent.futures as cf, glob, json, os, sys
from collections import deque, defaultdict

REPO = "~/01. Project/개인 프로젝트/battlecode"
REPLAYS = os.path.expanduser("~/meow-loop-out/card-47/attempt-1/replays")
sys.path.insert(0, REPO)
sys.path.insert(0, sys.argv[1])
import replay
import card_47_check as ck

VIEW = 3
FRESH = 25


def gap(a, b, size):
    d = abs(a - b) % size
    return min(d, size - d)


def catalogue(board, W, H):
    """Every largest shut area on the real map: {tiles: gate}."""
    found = {}
    for x in range(W):
        for y in range(H):
            gate = (x, y)
            for ch in ck.DIRS:
                if board.side(gate, ch) != 0:
                    continue
                cells = board.shut_area(board.beside(gate, ch), gate)
                if cells is None:
                    continue
                on = [board.beside(gate, c) for c in ck.DIRS if c != ch and board.side(gate, c) != 1]
                if not any(cell not in cells for cell in on):
                    continue
                found[frozenset(cells)] = gate
    kept = []
    for cells in sorted(found, key=len, reverse=True):
        if not any(cells < other for other in kept):
            kept.append(cells)
    return [(cells, found[cells]) for cells in kept]


def is_tree(board, cells):
    """No loop inside: a dragon that walks in cannot turn round, only a child born at its tail can leave."""
    edges = sum(1 for c in cells for ch in ('E', 'S') if board.side(c, ch) == 0 and board.beside(c, ch) in cells)
    return edges == len(cells) - 1


def game(path):
    name = os.path.basename(path)[:-len('.replay')]
    variant, rest = name.split('_', 1)
    mp, seed, side = rest.rsplit('_', 2)
    ours = 'B' if side == '1' else 'A'
    root = replay.load(path).root()
    W, H, bodies, team_of, kinds = ck.read_map(root.text(0))
    board = ck.Board(W, H, kinds)
    regs = catalogue(board, W, H)
    cell2reg = {c: i for i, (cells, _) in enumerate(regs) for c in cells}
    full = [all(gap(c[0], g[0], W) <= VIEW and gap(c[1], g[1], H) <= VIEW for c in cells) for cells, g in regs]
    tree = [is_tree(board, cells) for cells, _ in regs]
    gate2regs = defaultdict(list)
    for i, (_, g) in enumerate(regs):
        gate2regs[g].append(i)
    last_in, pending, opp = {}, {}, collections.Counter()
    tag = ck.team_tag(ours)
    key, streams, opened = ck.make_key(W, H, tag), {}, {}
    inreg, visit_of, visits, knows, born, been = {}, {}, [], defaultdict(dict), {}, defaultdict(set)
    for did, body in bodies.items():
        if team_of[did] == ours:
            inreg[did] = cell2reg.get(body[0])
    rnd = 0
    split_loss, odd = collections.Counter(), collections.Counter()
    sample = None

    def close(v):
        if not v['active']:
            v['close'] = rnd
            v['open'] = False

    def start(did, length, grew, born_in):
        reg = inreg[did]
        k = knows.get(did, {}).get(reg)
        v = {'reg': reg, 'gate': regs[reg][1], 'size': len(regs[reg][0]), 'full_view': full[reg], 'round': rnd,
             'entrant': did, 'age': rnd - born[did] if did in born else None, 'L0': length, 'eaten': int(grew),
             'splits': 0, 'members': [did], 'active': {did}, 'exit_len': 0, 'exits': 0, 'born_out': 0, 'died': 0,
             'died_len': 0, 'reasons': collections.Counter(), 'knew': dict(k) if k else None, 'born_in': born_in,
             'reentry': reg in been[did], 'open': True, 'close': None,
             'tree': tree[reg], 'entrant_out': False}
        been[did].add(reg)
        visits.append(v)
        visit_of[did] = v

    def leave(did, length):
        v = visit_of.pop(did, None)
        if v is not None:
            v['exit_len'] += length
            v['exits'] += 1
            v['entrant_out'] = v['entrant_out'] or did == v['entrant']
            v['active'].discard(did)
            close(v)

    for ev in root.pointer(3):
        which = ev.u16(0)
        kind = replay.EVENT_NAMES[which] if which < len(replay.EVENT_NAMES) else '?'
        pl = ev.pointer(0)
        if kind == 'roundStart':
            rnd = pl.i32(0)
        elif kind == 'dragonUpdate':
            did = pl.i32(0)
            head, tail = replay.point(pl.pointer(0)), replay.point(pl.pointer(1))
            body = bodies.setdefault(did, deque())
            before = len(body)
            moved = not body or body[0] != head
            if moved:
                body.appendleft(head)
            while len(body) > 1 and body[-1] != tail:
                body.pop()
            if team_of.get(did) != ours or not moved:
                continue
            grew = len(body) > before
            new, old = cell2reg.get(head), inreg.get(did)
            for reg, told, recent, was_in, size, age in pending.pop(did, ()):
                opp[(tree[reg], told, recent, was_in, new == reg, size, age)] += 1
            if new is None and head in gate2regs:
                prev = cell2reg.get(body[1]) if len(body) > 1 else None
                todo = []
                for reg in gate2regs[head]:
                    if prev == reg:
                        continue
                    k = knows.get(did, {}).get(reg)
                    age = rnd - last_in[reg] if reg in last_in else 999
                    todo.append((reg, bool(k), age <= FRESH, reg in been[did], min(len(body), 5),
                                 0 if age <= 8 else 1 if age <= FRESH else 2))
                if todo:
                    pending[did] = todo
            if new is not None:
                last_in[new] = rnd
            if new == old:
                v = visit_of.get(did)
                if v is not None and grew:
                    v['eaten'] += 1
                continue
            if old is not None:
                leave(did, len(body))
            inreg[did] = new
            if new is not None:
                start(did, before, grew, False)
        elif kind == 'dragonSplit':
            parent, child = pl.i32(0), pl.i32(4)
            team = ('A', 'B')[pl.u16(8)]
            old = bodies.get(parent, deque())
            pb = deque(replay.point(p) for p in pl.pointer(0))
            cb = deque(replay.point(p) for p in pl.pointer(1))
            bodies[parent], bodies[child] = pb, cb
            team_of[parent] = team_of[child] = team
            if team != ours:
                continue
            split_loss[len(old) - len(pb) - len(cb)] += 1
            if old and pb and old[0] != pb[0]:
                odd['parent_head_moved_at_split'] += 1
            born[child] = rnd
            inreg[child] = cell2reg.get(cb[0])
            v = visit_of.get(parent)
            if v is not None:
                v['splits'] += 1
                if inreg[child] == v['reg']:
                    visit_of[child] = v
                    v['active'].add(child)
                    v['members'].append(child)
                    been[child].add(v['reg'])
                else:
                    v['exit_len'] += len(cb)
                    v['exits'] += 1
                    v['born_out'] += 1
            elif inreg[child] is not None:
                start(child, len(cb), False, True)
        elif kind == 'dragonDeath':
            did, reason = pl.i32(0), pl.u16(4)
            if team_of.get(did) == ours:
                v = visit_of.pop(did, None)
                if v is not None:
                    v['died'] += 1
                    v['died_len'] += len(bodies.get(did, ()))
                    v['reasons'][reason] += 1
                    v['active'].discard(did)
                    close(v)
                inreg.pop(did, None)
            bodies.pop(did, None)
        elif kind == 'sonarPing':
            if team_of.get(pl.i32(0)) != ours:
                continue
            wire = pl.u64(16)
            if ((wire & ck.TAG_MASK) >> 53) != tag:
                continue
            if wire not in opened:
                plain = ck.unseal(key, wire, streams)
                opened[wire] = ck.parse(plain, W, H) if plain is not None else {'kind': 'unreadable'}
            msg = opened[wire]
            if msg.get('kind') != 'split' or msg.get('end') is None:
                continue
            if sample is None:
                sample = json.loads(json.dumps(msg, default=str))
            hit = pl.i32(12) if pl.u16(6) else None
            if hit is None or team_of.get(hit) != ours:
                continue
            end = msg['end']
            if not board.told_true(end):
                odd['told_end_not_true'] += 1
                continue
            reg = cell2reg.get(board.beside(end['gate'], end['dir']))
            if reg is None:
                odd['told_end_not_in_catalogue'] += 1
                continue
            rec = knows[hit].setdefault(reg, {'first': rnd, 'n': 0, 'pearls_max': 0, 'last_with_pearls': None})
            rec['last'] = rnd
            rec['n'] += 1
            pearls = end.get('pearls') or 0
            rec['pearls_last'] = pearls
            rec['pearls_max'] = max(rec['pearls_max'], pearls)
            if pearls > 0:
                rec['last_with_pearls'] = rnd
                rec['pearls_at_last_with'] = pearls
    rows = []
    for v in visits:
        v['active'] = sorted(v['active'])
        v['reasons'] = dict(v['reasons'])
        rows.append(v)
    return {'name': name, 'variant': variant, 'map': mp, 'seed': seed, 'side': side, 'rounds': rnd, 'W': W, 'H': H,
            'regions': [[list(g), len(c), full[i]] for i, (c, g) in enumerate(regs)],
            'region_cells': [sorted(c) for c, _ in regs],
            'opp': [list(k) + [n] for k, n in opp.items()], 'split_loss': dict(split_loss), 'odd': dict(odd), 'sample': sample, 'visits': rows}


def cls(e):
    return '0' if e == 0 else '1-2' if e < 3 else '3+'


def line(label, rows):
    n = len(rows)
    if not n:
        print(f"{label:38s} n=   0")
        return
    by = defaultdict(list)
    for v in rows:
        by[cls(v['eaten'])].append(v)
    net = [v['exit_len'] - v['L0'] for v in rows]
    low = by['0'] + by['1-2']
    print(f"{label:38s} n={n:4d} L0 {sum(v['L0'] for v in rows) / n:4.1f} | ate 0/1-2/3+ {len(by['0']):3d}/{len(by['1-2']):3d}/{len(by['3+']):3d}"
          f" | net +/0/- {sum(x > 0 for x in net):3d}/{sum(x == 0 for x in net):3d}/{sum(x < 0 for x in net):3d}"
          f" | net sum {sum(net):+5d} (ate<3 {sum(v['exit_len'] - v['L0'] for v in low):+5d}, ate3+ {sum(v['exit_len'] - v['L0'] for v in by['3+']):+5d})"
          f" | none out {sum(v['exits'] == 0 for v in rows):3d} | entrant out {sum(v['entrant_out'] for v in rows):3d} | rounds {sum(v['close'] - v['round'] for v in rows) / n:4.1f}")


def main():
    out = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    paths = sorted(glob.glob(os.path.join(REPLAYS, '*.replay')))
    with cf.ProcessPoolExecutor(workers) as pool:
        games = list(pool.map(game, paths))
    json.dump(games, open(out, 'w'))
    print('games', len(games), '| split loss (old - parent - child):',
          dict(sum((collections.Counter(g['split_loss']) for g in games), collections.Counter())),
          '| odd:', dict(sum((collections.Counter(g['odd']) for g in games), collections.Counter())))
    print('sample told end:', json.dumps(next((g['sample'] for g in games if g['sample']), None))[:300])
    seen = {}
    for g in games:
        seen.setdefault(g['map'], g)
    for mp, g in seen.items():
        sizes = sorted(r[1] for r in g['regions'])
        print(f"map {mp} {g['W']}x{g['H']}: {len(sizes)} shut areas, sizes {sizes[:40]}, fully in view from the gate {sum(r[2] for r in g['regions'])}")
    for variant in ('base', 'candidate'):
        every = [dict(v, map=g['map'], game=g['name']) for g in games if g['variant'] == variant for v in g['visits']]
        walked = [v for v in every if not v['open'] and not v['born_in']]
        line('ROOMY areas (a loop inside)', [v for v in walked if not v['tree']])
        done = [v for v in walked if v['tree']]
        for scope in ('all maps', 'prisoners_dilemma_v0'):
            tally = collections.Counter()
            for g in games:
                if g['variant'] == variant and (scope == 'all maps' or g['map'] == scope):
                    for is_tree_, told, recent, was_in, entered, _size, _age, n in g['opp']:
                        if is_tree_ and not was_in:
                            tally[(told, recent, entered)] += n
            print(f"  at the gate of a true dead end, arriving from outside, never inside before ({scope}):",
                  ' ; '.join(f"{'told' if t else 'not told'}, {'we were in there in the last 25 rounds' if r else 'not visited lately'}: stepped in {tally[(t, r, True)]} of {tally[(t, r, True)] + tally[(t, r, False)]}"
                             for t in (False, True) for r in (False, True)))
        print(f"--- {variant}: visits {len(every)}, still open at game end {sum(v['open'] for v in every)}, started by a birth inside {sum(v['born_in'] for v in every)}")
        line('all walked-in visits', done)
        line('  area fully in view from the gate', [v for v in done if v['full_view']])
        line('  area NOT fully in view', [v for v in done if not v['full_view']])
        line('  area of 8 tiles or fewer', [v for v in done if v['size'] <= 8])
        line('  area of 9 to 31 tiles', [v for v in done if v['size'] > 8])
        line('  same dragon had been in before', [v for v in done if v['reentry']])
        line('  entered at length 2 or 3', [v for v in done if v['L0'] <= 3])
        line('  entered at length 4 or more', [v for v in done if v['L0'] >= 4])
        for mp in seen:
            line(f'  map {mp}', [v for v in done if v['map'] == mp])
        if variant == 'candidate':
            told = [v for v in done if v['knew']]
            line('  entrant had been TOLD this area', told)
            line('    told within 25 rounds', [v for v in told if v['round'] - v['knew']['last'] <= FRESH])
            line('    told longer ago', [v for v in told if v['round'] - v['knew']['last'] > FRESH])
            print('    told entrants: highest pearl count ever told', dict(collections.Counter(v['knew']['pearls_max'] for v in told)),
                  '| times told', dict(collections.Counter(v['knew']['n'] for v in told)))
            line('    last told count was 0 pearls', [v for v in told if v['knew']['pearls_last'] == 0])
            line('    last told count 1-2 pearls', [v for v in told if 1 <= v['knew']['pearls_last'] <= 2])
            line('    last told count 3+ pearls', [v for v in told if v['knew']['pearls_last'] >= 3])
            line('  entrant NOT told', [v for v in done if not v['knew']])

    pairs = defaultdict(dict)
    for g in games:
        rows = [v for v in g['visits'] if v['tree'] and not v['open'] and not v['born_in']]
        pairs[(g['map'], g['seed'], g['side'])][g['variant']] = (sum(v['eaten'] < 3 for v in rows), sum(v['exit_len'] - v['L0'] for v in rows), len(rows))
    low = [(p['candidate'][0] - p['base'][0]) for p in pairs.values()]
    net = [(p['candidate'][1] - p['base'][1]) for p in pairs.values()]
    print(f"--- 16 pairs, true dead ends: walk-ins that ate under 3, candidate minus base: fewer in {sum(x < 0 for x in low)}, same {sum(x == 0 for x in low)}, more in {sum(x > 0 for x in low)} (diffs {sorted(low)});"
          f" net length, candidate better in {sum(x > 0 for x in net)}, worse in {sum(x < 0 for x in net)} (diffs {sorted(net)})")

    def area(game_name, cell):
        g = next(g for g in games if g['name'] == game_name)
        reg = next((i for i, cells in enumerate(g['region_cells']) if any(tuple(c) == tuple(cell) for c in cells)), None)
        rows = [v for v in g['visits'] if v['reg'] == reg and not v['born_in']]
        return g, reg, rows

    def show(v):
        k = v['knew']
        return (f"r{v['round']} id {v['entrant']} in at {v['L0']}, ate {v['eaten']}, splits {v['splits']}, out {v['exit_len']} in {v['exits']} bodies, "
                f"died inside {v['died']} (len {v['died_len']}), closed r{v['close']}, "
                + (f"told r{k['last']} pearls {k['pearls_last']} x{k['n']}" if k else "not told"))

    print('--- replay 1: prisoners_dilemma_v0 14700 side 1, pocket holding (17,2)')
    for name in ('candidate_prisoners_dilemma_v0_14700_1', 'base_prisoners_dilemma_v0_14700_1'):
        g, reg, rows = area(name, (17, 2))
        print(name, 'area', None if reg is None else (g['regions'][reg], g['region_cells'][reg]))
        line('  visits here', [v for v in rows if not v['open']])
        print('  told entrants', sum(bool(v['knew']) for v in rows), '| entry lengths', dict(collections.Counter(v['L0'] for v in rows)),
              '| eaten', dict(collections.Counter(v['eaten'] for v in rows)))
        for v in rows[:4]:
            print('   ', show(v))
        allrows = [v for v in g['visits'] if not v['born_in'] and not v['open']]
        line('  all areas, this game', allrows)
    print('--- replay 2: portals_v0 14700 side 1, dragon 1263')
    g = next(g for g in games if g['name'] == 'candidate_portals_v0_14700_1')
    for v in g['visits']:
        if 1263 in v['members']:
            print('   ', 'area', g['regions'][v['reg']], 'born_in' if v['born_in'] else '', show(v), 'members', v['members'])
            line('  visits to that area, whole game', [w for w in g['visits'] if w['reg'] == v['reg'] and not w['born_in'] and not w['open']])
            line('    of those, told', [w for w in g['visits'] if w['reg'] == v['reg'] and not w['born_in'] and not w['open'] and w['knew']])
    print('--- replay 3: trauma 14701 side 1, corridor holding (36,12)')
    for name in ('candidate_trauma_14701_1', 'base_trauma_14701_1'):
        g, reg, rows = area(name, (36, 12))
        print(name, 'area', None if reg is None else g['regions'][reg])
        line('  visits here', [v for v in rows if not v['open']])
        line('    told', [v for v in rows if not v['open'] and v['knew']])
        for v in [v for v in rows if 340 <= v['round'] <= 362][:4]:
            print('   ', show(v))


if __name__ == '__main__':
    main()
