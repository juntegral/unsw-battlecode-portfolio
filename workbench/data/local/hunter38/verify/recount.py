#!/usr/bin/env python3
"""Independent recount of how our queen dies (card #38 follow-up).

Run from the repo root:
    python3 data/local/hunter38/verify/recount.py            # both runs, writes verify/deaths.json, games.json
    python3 data/local/hunter38/verify/recount.py --board base_autarky_v0_3000_0 --back 4   # draw boards before a death

Reused from the run's tools (read first, agreed with): replay.load / replay.point / EVENT_NAMES (the Cap'n Proto
reader) and card_38_check.load_map (kelp and portal edges). Everything else (who is our queen, death rows,
"forced", room, lengths, pearls) is rebuilt here from the replay events.

Definitions used here
  round         = the number the replay's roundStart event carries (checked in the output: first and last value).
  our queen     = dragon 0 or 1, whichever is on our team (side 0 = team A, side 1 = team B; checked against the
                  bot names stored in the replay).
  death row     = one per dragonDeath event of our queen. `mover` is the dragon whose action was running.
  her last action = her own dragonAction event before the death (for a death during an enemy action this is an
                  earlier turn; the row says so with own_action=False).
  first-step options at the start of HER OWN last action, per direction (codes used in the tables in brackets):
        wall [w]      = kelp or an unpaired portal on that edge
        self [s]      = the destination holds one of her own segments (tail included, as the engine checks)
        mate body [m] / mate head [M] = a dragon of her own team is on the destination
        foe body [x] / foe head [X]   = a dragon of the other team is on the destination
        free [f]      = none of the above (a paired portal counts by the tile it leads to)
     forced       = no direction is free
     forced_hard  = no direction is free or a head (a head-on kills her too, so `forced` is the one reported)
  way out       = a run of DEPTH one-tile steps exists that keeps her alive with every other dragon frozen where it
                  is (no pearls, no splits). `ways` lists the first steps that start one.
  trapped_from  = the round of the first of her actions from which, up to her last, no way out existed.
  trap_kind     = 'trapped at spawn' (never had a way out), 'her own step' (the step before had a way out in
                  another direction but not in the one she took), 'board changed after her step' (the direction
                  she took had a way out when she took it; other dragons moved before her next action),
                  'after a split', 'after a multi-step move', 'had a way out at her last action'.
  The same rows are written for the enemy queen (who='foe') so the two can be set side by side.
  Companion scripts: tables.py (the tables in report.md), compare.py (row by row against deaths/rows.json),
  none_check.py (the no-action deaths on tower_defense).
  room          = tiles reachable from her head by walking over free tiles (kelp and portals respected, all dragon
                  segments block, her own tail blocks), capped at ROOM_CAP. Taken at the start of each of her
                  actions; `room_hist` is the last ROOM_BACK of them, oldest first.
"""
import sys
sys.dont_write_bytecode = True
import argparse, glob, json, os
from collections import Counter, deque, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HUNTER = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HUNTER, 'harness'))
sys.path.insert(0, os.path.join(HUNTER, 'harness', 'work'))
import replay                      # noqa: E402
from card_38_check import load_map  # noqa: E402

RUNS = {'hunter': os.path.join(HUNTER, 'replays'),
        'plain': '~/meow-loop-out/card-38/attempt-1/replays'}
CAUSE = ['wall', 'self', 'body', 'headon', 'none']
DIRS = 'NESW'
ROOM_CAP = 60
ROOM_BACK = 12
DEPTH = 16          # one-tile steps she must be able to survive on a frozen board to count as "has a way out"
MARKS = (50, 100, 200, 300)


def room_of(head, step, blocked, cap=ROOM_CAP):
    seen = {head}
    todo = [head]
    while todo and len(seen) - 1 < cap:
        cell = todo.pop()
        for d in DIRS:
            hop = step(cell, d)
            if hop is None:
                continue
            to = hop[0]
            if to in seen or to in blocked:
                continue
            seen.add(to)
            todo.append(to)
    return min(len(seen) - 1, cap)


def survive(body, step, frozen, depth, budget=4000):
    """Is there a run of `depth` one-tile steps that keeps her alive, with every other dragon frozen where it is,
    no pearls eaten and no splits? Her own body moves with her (the tail tile is blocked for the step, as in the
    engine). Returns the first directions that start such a run. A search that runs out of budget counts as alive."""
    good = set()
    for d0 in DIRS:
        hop = step(body[0], d0)
        if hop is None or hop[0] in body or hop[0] in frozen:
            continue
        seen = set()
        left = [budget]

        def go(b, n):
            if n == 0 or left[0] <= 0:
                return True
            if (b, n) in seen:
                return False
            seen.add((b, n))
            left[0] -= 1
            for d in DIRS:
                h = step(b[0], d)
                if h is None or h[0] in b or h[0] in frozen:
                    continue
                if go((h[0],) + b[:-1], n - 1):
                    return True
            return False

        if go((hop[0],) + tuple(body[:-1]), depth - 1):
            good.add(d0)
    return good


CODE = {'wall': 'w', 'self': 's', 'free': 'f', 'mate head': 'M', 'mate body': 'm', 'foe head': 'X', 'foe body': 'x'}


def options(head, own, bodies, queen, step, team_of):
    """What each first step would hit. `mate` = another dragon of her own team, `foe` = the other team."""
    where = {}
    for did, b in bodies.items():
        if did == queen or not b:
            continue
        side = 'mate' if team_of.get(did) == team_of.get(queen) else 'foe'
        for k, cell in enumerate(b):
            where[cell] = side + (' head' if k == 0 else ' body')
    out = {}
    for d in DIRS:
        hop = step(head, d)
        if hop is None:
            out[d] = 'wall'
        elif hop[0] in own:
            out[d] = 'self'
        else:
            out[d] = where.get(hop[0], 'free')
    return out


def play(path, side, want_round=None, back=0):
    """Replays one game. Returns (game row, death rows, board snapshots if want_round is given)."""
    ours = 'A' if side == '0' else 'B'
    root = replay.load(path).root()
    text = root.text(0)
    W, H, step, gate = load_map(text)
    result = root.pointer(4)
    winner = ('A', 'B')[result.u16(6)] if result.u16(4) == 1 else None
    end_reason = result.u16(2)
    bodies, team_of = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            did = len(bodies)
            bodies[did] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            team_of[did] = 'A' if int(q[1]) == 0 else 'B'
    queen = next(i for i in (0, 1) if team_of[i] == ours)
    foe_queen = 1 - queen
    spawn = {i: list(bodies[i]) for i in (0, 1)}
    name = os.path.basename(path)[:-len('.replay')]
    g = dict(file=name, side=side, ours=ours, W=W, H=H, winner=winner, win=int(winner == ours), end_reason=end_reason,
             botA=root.text(1), botB=root.text(2), queen=queen)
    pearls = set()
    rnd = None
    rounds_seen = []
    mover = None
    act = {}              # last action per queen id
    hist = {queen: [], foe_queen: []}   # every action start of each queen
    eats = {queen: [], foe_queen: []}       # rounds a queen ate
    splits = {queen: [], foe_queen: []}
    length_at = {queen: {}, foe_queen: {}}
    alive = {queen: True, foe_queen: True}
    deaths = []
    snaps = []
    tle = Counter()
    hop_bad = 0

    def snapshot(tag):
        snaps.append(dict(tag=tag, rnd=rnd, bodies={d: list(b) for d, b in bodies.items() if b},
                          team=dict(team_of), pearls=set(pearls)))

    for ev in root.pointer(3):
        which = ev.u16(0)
        kind = replay.EVENT_NAMES[which] if which < len(replay.EVENT_NAMES) else ''
        pl = ev.pointer(0)
        if kind == 'roundStart':
            rnd = pl.i32(0)
            rounds_seen.append(rnd)
            mover = None
            for m in MARKS:
                if rnd == m:
                    for qid in (queen, foe_queen):
                        length_at[qid][m] = len(bodies[qid]) if alive[qid] and bodies.get(qid) else 0
        elif kind == 'tileChange':
            at = replay.point(pl.pointer(0))
            if pl.u32(0) == 1:
                pearls.add(at)
            else:
                pearls.discard(at)
        elif kind == 'dragonAction':
            mover = pl.i32(0)
            a = pl.pointer(0)
            if pl.bit(32):
                tle[team_of.get(mover, '?')] += 1
            if mover in (queen, foe_queen):
                what = a.u16(0) if a is not None else -1
                steps = ''
                if what == 0:
                    try:
                        steps = ''.join(DIRS[v] if v < 4 else '?' for v in a.pointer(0))
                    except Exception:
                        steps = '?'
                rec = dict(rnd=rnd, what={0: 'move', 1: 'split', 2: 'suicide'}.get(what, f'other{what}'), steps=steps,
                           child=a.i32(4) if what == 1 else None, tle=bool(pl.bit(32)), done=0,
                           start_len=len(bodies.get(mover) or ()), start_head=(bodies[mover][0] if bodies.get(mover) else None))
                act[mover] = rec
                if bodies.get(mover):
                    body = bodies[mover]
                    head = body[0]
                    own = set(body)
                    blocked = set()
                    for b in bodies.values():
                        blocked.update(b)
                    opt = options(head, own, bodies, mover, step, team_of)
                    rec['opt'] = opt
                    rec['room'] = room_of(head, step, blocked)
                    rec['body'] = list(body)
                    rec['ways'] = ''.join(sorted(survive(tuple(body), step, blocked - own, DEPTH)))
                    hist[mover].append(dict(rnd=rnd, head=head, len=len(body), room=rec['room'],
                                            opt=''.join(CODE[opt[d]] for d in DIRS), what=rec['what'], steps=steps,
                                            ways=rec['ways']))
                    if mover == queen and want_round is not None and want_round - back <= rnd <= want_round:
                        snapshot(f'r{rnd} before her action {rec["what"]} {steps} '
                                 f'(first steps with a {DEPTH}-step way out: {rec["ways"] or "none"})')
        elif kind == 'dragonUpdate':
            did = pl.i32(0)
            h = replay.point(pl.pointer(0))
            tp = replay.point(pl.pointer(1))
            b = bodies.setdefault(did, deque())
            before = len(b)
            hopped = bool(b) and b[0] != h
            if not b or b[0] != h:
                if b and all((step(b[0], d) or (None,))[0] != h for d in DIRS):
                    hop_bad += 1
                b.appendleft(h)
                if did in act and mover == did:
                    act[did]['done'] += 1
            while len(b) > 1 and b[-1] != tp:
                b.pop()
            if hopped and len(b) > before and did in eats:
                eats[did].append(rnd)
        elif kind == 'dragonSplit':
            pa, ch = pl.i32(0), pl.i32(4)
            bodies[pa] = deque(replay.point(x) for x in pl.pointer(0))
            bodies[ch] = deque(replay.point(x) for x in pl.pointer(1))
            team_of[pa] = team_of[ch] = ('A', 'B')[pl.u16(8)]
            if pa in splits:
                splits[pa].append(rnd)
        elif kind == 'dragonDeath':
            did = pl.i32(0)
            r = pl.u16(4)
            cause = CAUSE[r] if r < 5 else f'other{r}'
            if did in (queen, foe_queen):
                qid = did
                last = act.get(qid, {})
                own_action = mover == qid
                hs = hist[qid]
                row = dict(file=name, run=None, who='our' if qid == queen else 'foe', arm=name.split('_')[0], side=side,
                           rnd=rnd, cause=cause, mover=mover,
                           mover_team=team_of.get(mover), mover_is_queen=mover in (0, 1), own_action=own_action,
                           len=len(bodies.get(qid) or ()), head=bodies[qid][0] if bodies.get(qid) else None,
                           spawn_head=spawn[qid][0],
                           last=dict(rnd=last.get('rnd'), what=last.get('what'), steps=last.get('steps'),
                                     done=last.get('done'), start_len=last.get('start_len'), tle=last.get('tle'),
                                     opt=last.get('opt'), room=last.get('room'), start_head=last.get('start_head'),
                                     ways=last.get('ways')),
                           room_hist=[(h['rnd'], h['room'], h['len'], h['opt'], h['what'] + ':' + h['steps'], h['head'], h['ways'])
                                      for h in hs[-ROOM_BACK:]])
                # When did she become trapped: the first of her actions from which, up to her last, no way out existed.
                k = len(hs)
                while k > 0 and not hs[k - 1]['ways']:
                    k -= 1
                row['trapped_from'] = hs[k]['rnd'] if k < len(hs) else None
                row['trapped_actions'] = len(hs) - k
                row['n_actions'] = len(hs)
                if k == len(hs):
                    row['trap_kind'] = 'had a way out at her last action'
                elif k == 0:
                    row['trap_kind'] = 'trapped at spawn'
                else:
                    pre = hs[k - 1]
                    row['pre'] = dict(rnd=pre['rnd'], what=pre['what'], steps=pre['steps'], ways=pre['ways'],
                                      opt=pre['opt'], len=pre['len'], room=pre['room'], head=pre['head'])
                    if pre['what'] != 'move':
                        row['trap_kind'] = 'after a ' + pre['what']
                    elif len(pre['steps']) != 1:
                        row['trap_kind'] = 'after a multi-step move'
                    elif pre['steps'] in pre['ways']:
                        row['trap_kind'] = 'board changed after her step'
                    else:
                        row['trap_kind'] = 'her own step'
                opt = last.get('opt') or {}
                row['n_free'] = sum(v == 'free' for v in opt.values())
                row['forced'] = bool(opt) and row['n_free'] == 0
                row['forced_hard'] = bool(opt) and all(v != 'free' and not v.endswith('head') for v in opt.values())
                row['opt_code'] = ''.join(CODE[opt[d]] for d in DIRS) if opt else ''
                row['step_index'] = (last.get('done', 0) + 1) if own_action and last.get('what') == 'move' else None
                row['n_steps'] = len(last.get('steps') or '')
                if own_action and last.get('what') == 'move' and last.get('steps'):
                    k = last.get('done', 0)
                    row['fatal_dir'] = last['steps'][k] if k < len(last['steps']) else None
                    free_steps = (last['start_len'] + 3) // 4
                    row['fatal_step_paid'] = k >= free_steps
                    row['fatal_first_opt'] = opt.get(last['steps'][0]) if k == 0 else None
                # team mates next to her head at death: who fills the neighbours
                nb = Counter()
                if bodies.get(qid):
                    head = bodies[qid][0]
                    ownset = set(bodies[qid])
                    where = {}
                    for d2, b in bodies.items():
                        if d2 == qid:
                            continue
                        for cell in b:
                            where[cell] = d2
                    for d in DIRS:
                        hop = step(head, d)
                        if hop is None:
                            nb['wall'] += 1
                        elif hop[0] in ownset:
                            nb['self'] += 1
                        elif hop[0] in where:
                            nb['mate' if team_of[where[hop[0]]] == team_of[qid] else 'foe'] += 1
                        else:
                            nb['free'] += 1
                row['neigh_at_death'] = dict(nb)
                sx, sy = spawn[qid][0]
                row['dist_from_spawn'] = (min(abs(row['head'][0] - sx), W - abs(row['head'][0] - sx))
                                          + min(abs(row['head'][1] - sy), H - abs(row['head'][1] - sy))) if row['head'] else None
                deaths.append(row)
                if want_round is not None and qid == queen:
                    snapshot(f'r{rnd} at her death ({cause}), before removal')
            if did in alive:
                alive[did] = False
            bodies.pop(did, None)
    for qid, tag in ((queen, 'our'), (foe_queen, 'foe')):
        g[f'{tag}_queen_alive'] = int(alive[qid])
        g[f'{tag}_queen_final'] = len(bodies.get(qid) or ()) if alive[qid] else 0
        for m in MARKS:
            g[f'{tag}_queen_len_r{m}'] = length_at[qid].get(m)
        g[f'{tag}_queen_eats_before300'] = sum(r < 300 for r in eats[qid])
        g[f'{tag}_queen_eats_from300'] = sum(r >= 300 for r in eats[qid])
        g[f'{tag}_queen_splits'] = len(splits[qid])
    g['first_round'], g['last_round'], g['n_rounds'] = rounds_seen[0], rounds_seen[-1], len(rounds_seen)
    g['tle_ours'] = tle[ours]
    g['hop_bad'] = hop_bad
    g['longest'] = {t: max((len(b) for d, b in bodies.items() if team_of.get(d) == t), default=0) for t in 'AB'}
    g['alive_n'] = {t: sum(1 for d, b in bodies.items() if team_of.get(d) == t and b) for t in 'AB'}
    # how the game ended, by the stated rule
    if g['alive_n']['A'] == 0 or g['alive_n']['B'] == 0:
        g['how'] = 'elim'
    elif g['our_queen_final'] != g['foe_queen_final']:
        g['how'] = 'queen'
    else:
        g['how'] = 'longest'
    g['map'], g['seed'] = name.split('_', 1)[1].rsplit('_', 2)[0], name.rsplit('_', 2)[1]
    g['arm'] = name.split('_')[0]
    g['spawn_len'] = len(spawn[queen])
    return g, deaths, (snaps, W, H, step, queen, ours)


def draw(snap, W, H, step, queen, ours, radius=5):
    """Text board around our queen's head. Q/q our queen head/body, M/m our other dragons, X/x enemy, o pearl,
    . free; walls are drawn between tiles as | and -, a portal edge as :."""
    b = snap['bodies']
    if queen not in b:
        return '(queen gone)'
    hx, hy = b[queen][0]
    cell = {}
    for did, body in b.items():
        mine = snap['team'][did] == ours
        for k, c in enumerate(body):
            ch = ('Q' if k == 0 else 'q') if did == queen else (('M' if k == 0 else 'm') if mine else ('X' if k == 0 else 'x'))
            cell[c] = ch
    out = [f"{snap['tag']}  head=({hx},{hy}) len={len(b[queen])}"]
    for dy in range(-radius, radius + 1):
        y = (hy + dy) % H
        top, mid = '', ''
        for dx in range(-radius, radius + 1):
            x = (hx + dx) % W
            c = (x, y)
            n = step(c, 'N')
            w = step(c, 'W')
            top += '+' + ('-' if n is None else (':' if n[1] else ' '))
            mid += ('|' if w is None else (':' if w[1] else ' ')) + cell.get(c, 'o' if c in snap['pearls'] else '.')
        out.append(top)
        out.append(mid)
    return '\n'.join(out)


def all_games(run):
    rows, deaths = [], []
    for p in sorted(glob.glob(os.path.join(RUNS[run], '*.replay'))):
        side = os.path.basename(p)[:-len('.replay')].rsplit('_', 1)[1]
        g, d, _ = play(p, side)
        g['run'] = run
        for x in d:
            x['run'], x['map'], x['seed'] = run, g['map'], g['seed']
        rows.append(g)
        deaths.extend(d)
    return rows, deaths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board')
    ap.add_argument('--run', default='hunter')
    ap.add_argument('--back', type=int, default=3)
    ap.add_argument('--at', type=int, help='draw the rounds up to this one instead of up to the death')
    ap.add_argument('--radius', type=int, default=5)
    a = ap.parse_args()
    if a.board:
        p = os.path.join(RUNS[a.run], a.board + '.replay')
        side = a.board.rsplit('_', 1)[1]
        g, d, _ = play(p, side)
        for row in [x for x in d if x['who'] == 'our']:
            at = a.at if a.at is not None else row['rnd']
            _, _, (snaps, W, H, step, queen, ours) = play(p, side, want_round=at, back=a.back)
            print(json.dumps({k: row.get(k) for k in ('file', 'rnd', 'cause', 'mover', 'own_action', 'len', 'last', 'forced',
                                                      'n_free', 'trapped_from', 'trap_kind', 'pre')}, default=str))
            for s in snaps:
                print(draw(s, W, H, step, queen, ours, a.radius))
                print()
        return
    out_g, out_d = [], []
    for run in RUNS:
        g, d = all_games(run)
        out_g += g
        out_d += d
    with open(os.path.join(HERE, 'games.json'), 'w') as f:
        json.dump(out_g, f, indent=1, default=str)
    with open(os.path.join(HERE, 'deaths.json'), 'w') as f:
        json.dump(out_d, f, indent=1, default=str)
    for run in RUNS:
        gs = [g for g in out_g if g['run'] == run]
        ds = [d for d in out_d if d['run'] == run and d['who'] == 'our']
        print(f'== {run}: {len(gs)} games, {len(ds)} queen deaths; rounds {min(g["first_round"] for g in gs)}..{max(g["last_round"] for g in gs)}; '
              f'bad hops {sum(g["hop_bad"] for g in gs)}; our TLE {sum(g["tle_ours"] for g in gs)}')
        for arm in ('base', 'candidate'):
            c = Counter(d['cause'] for d in ds if d['arm'] == arm)
            print(f'   {arm}: games {sum(g["arm"] == arm for g in gs)} wins {sum(g["win"] for g in gs if g["arm"] == arm)} deaths {dict(c)}')


if __name__ == '__main__':
    main()
