# Scratch (diag-walk): does the bot's tie-break decide the step when nothing scores?
# main.cpp:5361 adds 0.25 * ((id*31 + round*17 + k*7) % 5) to direction k (0 N, 1 E, 2 S, 3 W). Past 7 steps from any target
# the only terms that differ between directions are the distance to the nearest tile this dragon has never seen
# (8 + 2 a step inside 6 steps, 2 a step beyond; main.cpp:5028, 5037-5046), so the step should be: smallest distance to a
# never-seen tile, ties broken by that formula. This script takes blind turns of a dragon that is alone (no other head of
# either side in its view, no pearl due in view within 8 rounds, no remembered pearl within 7, no tile with 2+ births in
# view, room for 3L+8, centre rule off) and checks the step against that prediction. Rank-1's games are the placebo.
# Usage: python3 data/analysis/ladder/dossier/work/wk_tie.py <O|R> <per layout> <part> <parts>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
HORIZON = 8
LAST = 200


def tie(i, rnd, k):
    return (i * 31 + rnd * 17 + k * 7) % 5


def scan(row, tally):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    N = w * h
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
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    moves, adj = [], []
    for y in range(h):
        for x in range(w):
            rw = []
            for d in range(4):
                dx, dy = STEP[d]
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                rw.append((kind, dest))
            moves.append(rw)
            adj.append(sorted({dest for kind, dest in rw if kind != 1}))
    wins = {}

    def window(c):
        s = wins.get(c)
        if s is None:
            y, x = divmod(c, w)
            s = tuple(sorted({((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4)}))
            wins[c] = s
        return s

    def mdist(a, c):
        ay, ax = divmod(a, w)
        cy, cx = divmod(c, w)
        dx, dy = abs(ax - cx), abs(ay - cy)
        return min(dx, w - dx) + min(dy, h - dy)

    long_map = w >= 2 * h
    centre_on = N <= 1000 and (long_map or N <= 700)
    centre_rounds = 60 if long_map else 30
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    events = list(root.pointer(3))
    nat = defaultdict(list)
    rnd, inturn = 0, False
    for ev in events:
        k = ev.u16(0)
        if k == 0:
            rnd, inturn = ev.pointer(0).i32(0), False
            if rnd > LAST + HORIZON + 1:
                break
        elif k == 1:
            inturn = True
        elif k == 3 and not inturn:
            p = ev.pointer(0)
            if p.u32(0):
                nat[rnd].append(tile(replay.point(p.pointer(0))))
    occ = [0] * N
    heads = [0] * N
    for i, b in bodies.items():
        for c in b:
            occ[c] += 1
        heads[b[0]] += 1
    present = set()
    pv, sv, hv = [0] * N, [0] * N, [0] * N
    births_tile = Counter()
    added_upto = -1
    trail = {i: deque([b[0]], maxlen=12) for i, b in bodies.items()}
    lastdir, seenb, mem = {}, {}, {}
    rnd, actor, used, dirs, cur = 0, None, 0, [], None

    def unseen_from(dest, sb, head):
        if not sb[dest]:
            return 1
        d = {dest: 1, head: 0}
        q = deque([dest])
        while q:
            z = q.popleft()
            if d[z] >= 12:
                return 99
            for t in adj[z]:
                if t not in d and occ[t] == 0:
                    if not sb[t]:
                        return d[z] + 1
                    d[t] = d[z] + 1
                    q.append(t)
        return 99

    def roomy(head, need):
        got = {head}
        q = deque([head])
        while q:
            z = q.popleft()
            for t in adj[z]:
                if t not in got and occ[t] == 0:
                    got.add(t)
                    if len(got) > need:
                        return True
                    q.append(t)
        return False

    def finish_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        i = t['id']
        if t.get('cand') and t['first'] is not None:
            cand = t['cand']
            best = min(v for v in cand.values())
            argmin = sorted(d for d, v in cand.items() if v == best)
            fd = t['first_dir']
            grp = 'near' if best <= 6 else 'far' if best < 99 else 'none'
            tally[grp, 'steps'] += 1
            tally[grp, 'retread'] += int(t['first'] in t['trail'])
            if t['previous'] is not None:
                tally[grp, 'keep_elig'] += 1
                tally[grp, 'kept'] += int(fd == t['previous'])
            tally[grp, 'in_argmin'] += int(fd in argmin)
            tally[grp, 'argmin_size_%d' % len(argmin)] += 1
            if fd in argmin and len(argmin) >= 2:
                tally[grp, 'tied'] += 1
                for off in (-1, 0, 1):
                    pred = max(argmin, key=lambda k: tie(i, t['rnd'] + off, k))
                    tally[grp, 'tie_match_%+d' % off] += int(pred == fd)
                tally[grp, 'chance'] += 1.0 / len(argmin)
            pred = max(argmin, key=lambda k: tie(i, t['rnd'], k))
            tally[grp, 'full_match'] += int(pred == fd)
            tally[grp, 'pred_retread'] += int(moves[t['head']][pred][1] in t['trail'])
            if t['previous'] is not None:
                tally[grp, 'pred_kept'] += int(pred == t['previous'])
        lastdir[i] = t['first_dir']

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish_turn()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > LAST:
                break
            for rr in range(added_upto + 1, rnd + HORIZON + 1):
                for c in nat.get(rr, ()):
                    for z in window(c):
                        sv[z] += 1
            added_upto = max(added_upto, rnd + HORIZON)
        elif k == 1:
            actor = p.i32(0)
            dirs, used = [], 0
            if side(actor) != 'u':
                continue
            b = bodies[actor]
            head, L = b[0], len(b)
            win = window(head)
            blind = pv[head] == 0
            sb = seenb.get(actor)
            if sb is None:
                sb = bytearray(N)
                seenb[actor] = sb
                mem[actor] = set()
            for c in win:
                sb[c] = 1
            mm = mem[actor]
            winset = set(win)
            for c in tuple(mm):
                if c not in present and c in winset:
                    mm.discard(c)
            if not blind:
                for c in win:
                    if c in present:
                        mm.add(c)
            cur = dict(id=actor, rnd=rnd, head=head, previous=lastdir.get(actor), first=None, first_dir=None)
            if not blind:
                continue
            others = -1
            for c in win:
                others += heads[c]
            if others > 0 or sv[head] > 0 or hv[head] > 0:
                continue
            if mm and min(mdist(head, c) for c in mm) <= 7:
                continue
            if centre_on and L <= 4 and rnd < centre_rounds:
                continue
            if not roomy(head, 3 * L + 8):
                continue
            cand = {}
            for d in range(4):
                kind, dest = moves[head][d]
                if kind == 0 and occ[dest] == 0:
                    cand[d] = unseen_from(dest, sb, head)
                elif kind == 2:
                    cand = None
                    break
            if cand and len(cand) >= 2:
                cur.update(cand=cand, trail=set(trail[actor]))
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present.add(c)
                for z in window(c):
                    pv[z] += 1
                if actor is None and c in nat.get(rnd, ()):
                    for z in window(c):
                        sv[z] -= 1
                births_tile[c] += 1
                if births_tile[c] == 2:
                    for z in window(c):
                        hv[z] += 1
            else:
                present.discard(c)
                for z in window(c):
                    pv[z] -= 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                b.appendleft(hd)
                occ[hd] += 1
                heads[old] -= 1
                heads[hd] += 1
                if i == actor:
                    if cur is not None and cur['first'] is None and used < len(dirs):
                        cur['first'], cur['first_dir'] = hd, dirs[used]
                    used += 1
                    trail[i].append(hd)
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for c in bodies[parent]:
                occ[c] -= 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                for c in bodies[i]:
                    occ[c] += 1
            heads[bodies[child][0]] += 1
            trail[child] = deque([bodies[child][0]], maxlen=12)
        elif k == 11:
            i = p.i32(0)
            b = bodies.pop(i)
            for c in b:
                occ[c] -= 1
            heads[b[0]] -= 1
    finish_turn()


def main():
    who, per, part, parts = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    by = defaultdict(list)
    for r in sorted(rows, key=lambda r: r['game']):
        if r['who'] == who:
            by[r['layout']].append(r)
    pick = []
    for l in sorted(by):
        gs = by[l]
        pick += gs[::max(1, len(gs) // per)][:per]
    pick = [r for n, r in enumerate(pick) if n % parts == part]
    tally = Counter()
    for n, r in enumerate(pick):
        scan(r, tally)
        if n % 10 == 9:
            print(n + 1, len(pick), flush=True)
    print('RESULT', who, part, parts, len(pick), json.dumps({'%s|%s' % k: v for k, v in sorted(tally.items())}))
    for grp in ('near', 'far', 'none'):
        n = tally[grp, 'steps']
        if not n:
            continue
        print(who, grp, 'steps', n, 're-tread %.1f%%' % (100 * tally[grp, 'retread'] / n),
              'kept %.1f%%' % (100 * tally[grp, 'kept'] / max(1, tally[grp, 'keep_elig'])),
              '| step has the smallest never-seen distance %.1f%%' % (100 * tally[grp, 'in_argmin'] / n),
              '| of those with a tie (%d): tie-break formula right, round-1 / round / round+1: %.1f%% / %.1f%% / %.1f%%; chance %.1f%%' % (
                  tally[grp, 'tied'], 100 * tally[grp, 'tie_match_-1'] / max(1, tally[grp, 'tied']),
                  100 * tally[grp, 'tie_match_+0'] / max(1, tally[grp, 'tied']), 100 * tally[grp, 'tie_match_+1'] / max(1, tally[grp, 'tied']),
                  100 * tally[grp, 'chance'] / max(1, tally[grp, 'tied'])),
              '| whole rule right %.1f%%' % (100 * tally[grp, 'full_match'] / n),
              '| the rule itself would re-tread %.1f%%, keep %.1f%%' % (100 * tally[grp, 'pred_retread'] / n, 100 * tally[grp, 'pred_kept'] / max(1, tally[grp, 'keep_elig'])))


main()
