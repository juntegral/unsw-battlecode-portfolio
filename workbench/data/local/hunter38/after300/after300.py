#!/usr/bin/env python3
"""Our queen's deaths from round 300 on (card #38 follow-up, Zhe's question).

Run from the repo root (unsw-swarm):
    python3 data/local/hunter38/after300/after300.py list
        every death of our queen with round >= 300, straight from the replays, the denominators per arm,
        and a row-by-row comparison with verify/deaths.json
    python3 data/local/hunter38/after300/after300.py trace candidate_maze_3001_1 --back 10 [--run hunter] [--near 8]
        her last actions before the death: options per side, what she did, every other head within --near tiles,
        the killer's actions, any bot log lines of the two, and the board at the fatal action
    python3 data/local/hunter38/after300/after300.py killers
        for each head-on death: who moved, how long the killer was, how many rounds it had been within 8 tiles

Reads only. The replay reader (harness/replay.py) and the map reader (card_38_check.load_map) are the run's own;
the option codes are the ones of verify/recount.py: per side N E S W, w kelp, s herself, f free, m/M team-mate
body/head, x/X enemy body/head. Rounds are the replay's own labels, 0 to 499.
"""
import sys
sys.dont_write_bytecode = True
import argparse, glob, json, os
from collections import Counter, deque, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HUNTER = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HUNTER, 'harness'))
sys.path.insert(0, os.path.join(HUNTER, 'harness', 'work'))
sys.path.insert(0, os.path.join(HUNTER, 'verify'))
import replay                        # noqa: E402
from card_38_check import load_map   # noqa: E402

RUNS = {'hunter': os.path.join(HUNTER, 'replays'),
        'plain': '~/meow-loop-out/card-38/attempt-1/replays'}
CAUSE = ['wall', 'self', 'body', 'headon', 'none']
DIRS = 'NESW'
FROM = 300
VIEW = 3            # helper.hpp VISION_RADIUS: a dragon sees the 7x7 window around its head


def name_parts(path):
    name = os.path.basename(path)[:-len('.replay')]
    arm = name.split('_')[0]
    mp, seed, side = name.split('_', 1)[1].rsplit('_', 2)
    return name, arm, mp, seed, side


def walk(path, watch=None):
    """One pass over a game. Yields nothing; returns a dict with the queen's death (if any), lengths at r300 and at
    the end, and, when `watch` = (first round, last round, near), the lines of the trace."""
    name, arm, mp, seed, side = name_parts(path)
    ours = 'A' if side == '0' else 'B'
    root = replay.load(path).root()
    text = root.text(0)
    W, H, step, gate = load_map(text)
    result = root.pointer(4)
    winner = ('A', 'B')[result.u16(6)] if result.u16(4) == 1 else None
    bodies, team_of = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            did = len(bodies)
            bodies[did] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            team_of[did] = 'A' if int(q[1]) == 0 else 'B'
    queen = next(i for i in (0, 1) if team_of[i] == ours)
    foe_queen = 1 - queen
    g = dict(file=name, arm=arm, map=mp, seed=seed, side=side, ours=ours, queen=queen, W=W, H=H, cells=W * H,
             win=int(winner == ours), winner=winner, death=None, foe_death=None, len300=None, foe_len300=None)
    pearls = set()
    rnd = None
    last_round = None
    mover = None
    mover_start = None          # (head, length, steps) of the running action
    near_log = defaultdict(list)    # enemy id -> rounds its head was within 8 of her head at its own action
    lines = []
    snaps = []
    eats_from = 0
    queen_last = None

    def dist(a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def in_view(centre, cell, radius=VIEW):
        dx, dy = abs(centre[0] - cell[0]), abs(centre[1] - cell[1])
        return min(dx, W - dx) <= radius and min(dy, H - dy) <= radius

    def options(did):
        head = bodies[did][0]
        own = set(bodies[did])
        where = {}
        for d2, b in bodies.items():
            if d2 == did or not b:
                continue
            tag = ('m', 'M') if team_of.get(d2) == team_of.get(did) else ('x', 'X')
            for k, cell in enumerate(b):
                where[cell] = tag[1] if k == 0 else tag[0]
        out = ''
        for d in DIRS:
            hop = step(head, d)
            out += 'w' if hop is None else 's' if hop[0] in own else where.get(hop[0], 'f')
        return out

    def snapshot(tag):
        snaps.append(dict(tag=tag, rnd=rnd, bodies={d: list(b) for d, b in bodies.items() if b},
                          team=dict(team_of), pearls=set(pearls)))

    lo, hi, near = watch if watch else (None, None, 0)
    for ev in root.pointer(3):
        which = ev.u16(0)
        kind = replay.EVENT_NAMES[which] if which < len(replay.EVENT_NAMES) else ''
        pl = ev.pointer(0)
        if kind == 'roundStart':
            rnd = pl.i32(0)
            last_round = rnd
            mover = None
            if rnd == FROM:
                g['len300'] = len(bodies[queen]) if bodies.get(queen) else 0
                g['foe_len300'] = len(bodies[foe_queen]) if bodies.get(foe_queen) else 0
        elif kind == 'tileChange':
            at = replay.point(pl.pointer(0))
            if pl.u32(0) == 1:
                pearls.add(at)
            else:
                pearls.discard(at)
        elif kind == 'dragonAction':
            mover = pl.i32(0)
            a = pl.pointer(0)
            what = a.u16(0) if a is not None else -1
            steps = ''
            if what == 0:
                steps = ''.join(DIRS[v] if v < 4 else '?' for v in a.pointer(0))
            wname = {0: 'move', 1: 'split', 2: 'no action'}.get(what, f'other{what}')
            if what == 1:
                wname += f' child {a.i32(4)}'
            b = bodies.get(mover)
            mover_start = (b[0] if b else None, len(b or ()), wname + (' ' + steps if steps else ''))
            qb = bodies.get(queen)
            if qb and b and mover != queen and team_of.get(mover) != ours and dist(b[0], qb[0]) <= 8:
                near_log[mover].append(rnd)
            if mover == queen and qb:
                seen_at = {}
                for d2, b2 in bodies.items():
                    if not b2 or team_of.get(d2) == ours:
                        continue
                    seen_at[d2] = (b2[0], len(b2), sum(1 for c in b2 if in_view(qb[0], c)), in_view(qb[0], b2[0]),
                                   any(in_view(qb[0], c) and not in_view(qb[0], c, VIEW - 1) for c in b2))
                queen_last = dict(rnd=rnd, head=qb[0], len=len(qb), act=mover_start[2], seen=seen_at)
            if watch and lo <= rnd <= hi and qb and b:
                if mover == queen:
                    heads = []
                    for d2, b2 in bodies.items():
                        if d2 == queen or not b2:
                            continue
                        dd = dist(b2[0], qb[0])
                        if dd <= near:
                            heads.append((dd, ('mate' if team_of[d2] == ours else 'FOE'), d2, b2[0], len(b2)))
                    heads.sort()
                    npearl = sum(1 for p in pearls if dist(p, qb[0]) <= 4)
                    lines.append(f"r{rnd} QUEEN #{queen} head {qb[0]} len {len(qb)} sides NESW={options(queen)} -> {mover_start[2]}"
                                 f" | pearls within 4: {npearl} | heads within {near}: "
                                 + ('; '.join(f"{t} #{i} at {h} len {n} dist {dd}" for dd, t, i, h, n in heads) or 'none'))
                    snapshot(f"r{rnd} before her action ({mover_start[2]})")
                elif team_of.get(mover) != ours and dist(b[0], qb[0]) <= near:
                    lines.append(f"r{rnd}   foe #{mover} head {b[0]} len {len(b)} dist {dist(b[0], qb[0])} "
                                 f"sides NESW={options(mover)} -> {mover_start[2]}")
        elif kind == 'dragonLog':
            if watch and lo <= rnd <= hi:
                did = pl.i32(0)
                qb = bodies.get(queen)
                b = bodies.get(did)
                if did == queen or (qb and b and dist(b[0], qb[0]) <= near):
                    lines.append(f"r{rnd}   log #{did} ({'ours' if team_of.get(did) == ours else 'foe'}): {pl.text(0)}")
        elif kind == 'dragonUpdate':
            did = pl.i32(0)
            h = replay.point(pl.pointer(0))
            tp = replay.point(pl.pointer(1))
            b = bodies.setdefault(did, deque())
            before = len(b)
            hopped = bool(b) and b[0] != h
            if not b or b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tp:
                b.pop()
            if did == queen and hopped and len(b) > before and rnd >= FROM:
                eats_from += 1
        elif kind == 'dragonSplit':
            pa, ch = pl.i32(0), pl.i32(4)
            bodies[pa] = deque(replay.point(x) for x in pl.pointer(0))
            bodies[ch] = deque(replay.point(x) for x in pl.pointer(1))
            team_of[pa] = team_of[ch] = ('A', 'B')[pl.u16(8)]
        elif kind == 'dragonDeath':
            did = pl.i32(0)
            r = pl.u16(4)
            cause = CAUSE[r] if r < 5 else f'other{r}'
            if did in (queen, foe_queen):
                row = dict(rnd=rnd, cause=cause, len=len(bodies.get(did) or ()), head=bodies[did][0] if bodies.get(did) else None,
                           mover=mover, mover_team=team_of.get(mover), mover_len=len(bodies.get(mover) or ()),
                           mover_start=mover_start, mover_near_rounds=list(near_log.get(mover, [])) if did == queen else None)
                if did == queen and queen_last:
                    k = queen_last['seen'].get(mover)
                    hit = 0
                    if mover != queen and mover_start[0] is not None and ' ' in mover_start[2] and mover_start[2].startswith('move'):
                        cell = mover_start[0]
                        for ch in mover_start[2].split()[1]:
                            hop = step(cell, ch)
                            if hop is None:
                                break
                            cell = hop[0]
                            hit += 1
                            if cell == row['head']:
                                break
                    row['queen_last'] = dict(rnd=queen_last['rnd'], head=queen_last['head'], len=queen_last['len'], act=queen_last['act'],
                                             killer=k, hit_step=hit)
                g['death' if did == queen else 'foe_death'] = row
                if did == queen and watch and lo <= rnd <= hi:
                    lines.append(f"r{rnd} DEATH of our queen: {cause}, length {row['len']}, head {row['head']}; action running: "
                                 f"#{mover} ({'ours' if team_of.get(mover) == ours else 'foe'}) from {mover_start[0]} len {mover_start[1]} {mover_start[2]}")
                    snapshot(f"r{rnd} at her death ({cause}), before removal")
            elif watch and lo <= rnd <= hi and bodies.get(queen) and bodies.get(did) and dist(bodies[did][0], bodies[queen][0]) <= near:
                lines.append(f"r{rnd}   death #{did} ({'ours' if team_of.get(did) == ours else 'foe'}) {cause} len {len(bodies[did])} at {bodies[did][0]}")
            bodies.pop(did, None)
    g['last_round'] = last_round
    g['final'] = len(bodies.get(queen) or ())
    g['foe_final'] = len(bodies.get(foe_queen) or ())
    g['eats_from300'] = eats_from
    g['alive_n'] = {t: sum(1 for d, b in bodies.items() if team_of.get(d) == t and b) for t in 'AB'}
    g['longest'] = {t: max((len(b) for d, b in bodies.items() if team_of.get(d) == t), default=0) for t in 'AB'}
    return g, lines, (snaps, W, H, step, queen, ours)


def med(v):
    v = sorted(v)
    return '-' if not v else v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2


def cmd_list():
    out = []
    for run, folder in RUNS.items():
        for p in sorted(glob.glob(os.path.join(folder, '*.replay'))):
            g, _, _ = walk(p)
            g['run'] = run
            out.append(g)
    for run in RUNS:
        for arm in ('base', 'candidate'):
            gs = [g for g in out if g['run'] == run and g['arm'] == arm]
            dead_before = [g for g in gs if g['death'] and g['death']['rnd'] < FROM]
            dead_from = [g for g in gs if g['death'] and g['death']['rnd'] >= FROM]
            at300 = [g for g in gs if g['last_round'] >= FROM and not (g['death'] and g['death']['rnd'] < FROM)]
            short = [g for g in gs if g['last_round'] < FROM and not g['death']]
            alive_end = [g for g in gs if not g['death']]
            print(f"== {run} / {arm}: games {len(gs)}; queen dead before r{FROM}: {len(dead_before)}; game over before r{FROM} with her alive: "
                  f"{len(short)}; alive at r{FROM}: {len(at300)}; died r{FROM}+: {len(dead_from)}; alive at the end: {len(alive_end)} "
                  f"(of those, games that reached r{FROM}: {len([g for g in alive_end if g['last_round'] >= FROM])})")
            print(f"   exactly r{FROM}: {sum(g['death']['rnd'] == FROM for g in dead_from)}; "
                  f"causes r{FROM}+: {dict(Counter(g['death']['cause'] for g in dead_from))}")
            for c in CAUSE:
                ls = [g['death']['len'] for g in dead_from if g['death']['cause'] == c]
                if ls:
                    print(f"   {c:6} n={len(ls)} lengths {sorted(ls)} min/median/max {min(ls)}/{med(ls)}/{max(ls)}")
            for g in sorted(dead_from, key=lambda g: g['file']):
                d = g['death']
                fd = g['foe_death']
                print(f"   {g['file']:34} {g['map']:14} {g['cells']:5} cells side {g['side']} r{d['rnd']} {d['cause']:6} len {d['len']:3} "
                      f"(len at r300 {g['len300']}, pearls r300+ {g['eats_from300']}) by #{d['mover']} team {d['mover_team']}"
                      f"{' (herself)' if d['mover'] == g['queen'] else ''} from {d['mover_start'][0]} len {d['mover_start'][1]} [{d['mover_start'][2]}]"
                      f" | enemy queen: {'dead r' + str(fd['rnd']) if fd else 'alive, final ' + str(g['foe_final'])}"
                      f" | game: {'win' if g['win'] else 'loss'}, longest A {g['longest']['A']} B {g['longest']['B']}")
            surv = [g for g in gs if not g['death'] and g['last_round'] >= FROM]
            print(f"   queens alive at the end (games that reached r{FROM}): {len(surv)}; final lengths {sorted(g['final'] for g in surv)}; "
                  f"wins {sum(g['win'] for g in surv)}")
            for g in sorted(surv, key=lambda g: g['file']):
                print(f"      {g['file']:34} len r300 {g['len300']} final {g['final']} enemy queen r300 {g['foe_len300']} final {g['foe_final']} "
                      f"{'win' if g['win'] else 'loss'}")
    # row by row against the verified recount
    D = json.load(open(os.path.join(HUNTER, 'verify', 'deaths.json')))
    theirs = {(d['run'], d['file']): (d['rnd'], d['cause'], d['len']) for d in D if d['who'] == 'our'}
    mine = {(g['run'], g['file']): (g['death']['rnd'], g['death']['cause'], g['death']['len']) for g in out if g['death']}
    print(f"\ncompare with verify/deaths.json (our queen, all rounds): theirs {len(theirs)} rows, mine {len(mine)} rows, "
          f"equal on round, cause and length: {sum(theirs.get(k) == v for k, v in mine.items())}, "
          f"only theirs {len(set(theirs) - set(mine))}, only mine {len(set(mine) - set(theirs))}")


def cmd_trace(a):
    from recount import draw
    p = os.path.join(RUNS[a.run], a.file + '.replay')
    g, _, _ = walk(p)
    if a.at is None and not g['death']:
        print('our queen does not die in this game; give --at')
        return
    at = a.at if a.at is not None else g['death']['rnd']
    g, lines, (snaps, W, H, step, queen, ours) = walk(p, watch=(at - a.back, at, a.near))
    print(f"# {a.file} ({a.run} run): map {g['map']} {W}x{H}, our side {g['side']} = team {ours}, our queen #{queen}, "
          f"len at r300 {g['len300']}, {'win' if g['win'] else 'loss'}")
    for l in lines:
        print(l)
    print()
    for s in snaps[-a.boards:]:
        print(draw(s, W, H, step, queen, ours, a.radius))
        print()


def cmd_killers():
    for run, folder in RUNS.items():
        for p in sorted(glob.glob(os.path.join(folder, '*.replay'))):
            g, _, _ = walk(p)
            d = g['death']
            if not d or d['rnd'] < FROM or d['cause'] != 'headon':
                continue
            nr = d['mover_near_rounds']
            streak = 0
            r = d['rnd']
            while r in nr:
                streak += 1
                r -= 1
            ql = d['queen_last']
            k = ql['killer']
            L = d['mover_start'][1]
            print(f"{run:6} {g['file']:34} r{d['rnd']} queen len {d['len']:3}; mover #{d['mover']} team {d['mover_team']} "
                  f"({'enemy' if d['mover_team'] != g['ours'] else 'OURS'}) len {L} from {d['mover_start'][0]} "
                  f"[{d['mover_start'][2]}]; rounds in a row its head started within 8 of hers, the last included: {streak}")
            if not k:
                print('       killer not on the board at her last action')
                continue
            head, real, seen, head_seen, cut = k
            free_real = (real + 3) // 4
            # map_hits() in main.cpp, with what the window shows and no memory of earlier sightings
            if head_seen:
                free_m = max(1, (seen + 3) // 4)
                size = max(seen, seen + 1, 3) if cut else seen
                reach_m = max(free_m, min((size + 3) // 4 + size - 2, 3))
                model = f"reach by the map_hits formula on what the window shows: {reach_m} (free {free_m})"
            else:
                reach_m = None
                model = 'head outside her window: no reach to compute'
            print(f"       her own last action r{ql['rnd']}: head {ql['head']} len {ql['len']} {ql['act']}; the killer then: "
                  f"head {head}, real length {real} (free steps {free_real}, with paid steps up to {free_real + real - 2}), "
                  f"head inside her 7x7 window: {head_seen}, segments inside the window: {seen}, body cut by the window edge: {cut}; "
                  f"{model}; it reached her head on step {ql['hit_step']} of its action "
                  f"({max(0, ql['hit_step'] - free_real)} paid)"
                  + ('' if reach_m is None else f"; beyond that reach: {ql['hit_step'] > reach_m}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['list', 'trace', 'killers'])
    ap.add_argument('file', nargs='?')
    ap.add_argument('--run', default='hunter')
    ap.add_argument('--back', type=int, default=10)
    ap.add_argument('--at', type=int)
    ap.add_argument('--near', type=int, default=8)
    ap.add_argument('--radius', type=int, default=5)
    ap.add_argument('--boards', type=int, default=2)
    a = ap.parse_args()
    if a.cmd == 'list':
        cmd_list()
    elif a.cmd == 'trace':
        cmd_trace(a)
    else:
        cmd_killers()


if __name__ == '__main__':
    main()
