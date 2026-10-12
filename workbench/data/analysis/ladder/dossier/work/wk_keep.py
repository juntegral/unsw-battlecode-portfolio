# Scratch (diag-walk): wk_scan.py with one more field at the end of each step key: 1 the step keeps the direction of the
# dragon's previous turn, 0 it turns, 9 no previous step. Written by a text edit of wk_scan.py; outputs wk_keep-*.jsonl.
# Scratch (diag-walk): one pass over every game of ours (who=O, team 1119, 500 main ladder games) or of rank-1
# (who=R, team 306, 597 games), rounds 0-300, the followed side only. One output line per game.
# Blind turn  = the turn starts with no pearl in the 7 by 7 view (dossier definition).
# Re-tread    = the first step of a blind turn lands on one of the dragon's own last 12 head tiles (dossier definition).
# What scores (first that holds; a replay cannot show the bot's sums, so this says which terms CAN be non-zero):
#   T an enemy head is in view; S a pearl will be born inside the view within 8 rounds (the countdown is visible);
#   R a pearl this dragon saw earlier lies within 7 tiles (straight distance); H a tile with 2+ births so far is in view;
#   C fewer than 3L+8 free tiles can be reached from the head (the bot's own "room wanted");
#   Nc none of these and the centre rule is on (L<=4, small layout, first 30/60 rounds);
#   N4/N6/Nf none of these and the nearest tile this dragon has never seen is 1-4 / 5-6 / 7+ path steps away.
# Around (first that holds): M a team mate's head within 3 tiles; K 20 or fewer tiles within 4 path steps (pocket);
#   P a portal within 3 path steps; W 21-32 tiles within 4 steps (walls near); O open ground.
# Usage: python3 data/analysis/ladder/dossier/work/wk_scan.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
HORIZON = 8
LAST = 300
STOP = 341
CAP = 40


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves, self.adj, self.ptile = [], [], []
        for y in range(h):
            for x in range(w):
                row, has = [], False
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                        has = True
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
                self.adj.append(sorted({dest for kind, dest in row if kind != 1}))
                self.ptile.append(has)
        self.wins, self.dias, self.balls, self.nearp = {}, {}, {}, {}
        long_map = w >= 2 * h
        cells = w * h
        self.centre_on = cells <= 1000 and (long_map or cells <= 700)
        self.centre_rounds = 60 if long_map else 30

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            t = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            s = (t, frozenset(t))
            self.wins[c] = s
        return s

    def diamond(self, c):
        s = self.dias.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4)
                              for dx in range(-3, 4) if 0 < abs(dx) + abs(dy) <= 3} - {c}))
            self.dias[c] = s
        return s

    def ball(self, c):
        n = self.balls.get(c)
        if n is None:
            d = {c: 0}
            q = deque([c])
            near = self.ptile[c]
            while q:
                z = q.popleft()
                if d[z] >= 4:
                    continue
                for t in self.adj[z]:
                    if t not in d:
                        d[t] = d[z] + 1
                        q.append(t)
                        if d[t] <= 3 and self.ptile[t]:
                            near = True
            n = len(d)
            self.balls[c] = n
            self.nearp[c] = near
        return n

    def cdist(self, c):
        y, x = divmod(c, self.w)
        dx, dy = abs(x - self.w // 2), abs(y - self.h // 2)
        return min(dx, self.w - dx) + min(dy, self.h - dy)

    def mdist(self, a, c):
        ay, ax = divmod(a, self.w)
        cy, cx = divmod(c, self.w)
        dx, dy = abs(ax - cx), abs(ay - cy)
        return min(dx, self.w - dx) + min(dy, self.h - dy)


def lbucket(L):
    return '2' if L <= 2 else '3' if L == 3 else '4' if L == 4 else '5' if L <= 7 else '8'


def abucket(a):
    return 'a' if a <= 5 else 'b' if a <= 15 else 'c' if a <= 40 else 'd'


def scan(row, geos):
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
    key = (row['layout'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    moves, adj = g.moves, g.adj
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    queen = min(i for i in bodies if side(i) == 'u')
    events = list(root.pointer(3))

    nat = defaultdict(list)
    rnd, inturn = 0, False
    for ev in events:
        k = ev.u16(0)
        if k == 0:
            rnd, inturn = ev.pointer(0).i32(0), False
            if rnd > STOP + HORIZON + 1:
                break
        elif k == 1:
            inturn = True
        elif k == 3 and not inturn:
            p = ev.pointer(0)
            if p.u32(0):
                nat[rnd].append(tile(replay.point(p.pointer(0))))

    occ = [0] * N
    hg = dict(u=[0] * N, t=[0] * N)
    for i, b in bodies.items():
        for c in b:
            occ[c] += 1
        hg[side(i)][b[0]] += 1
    present = set()
    pv, sv, hv = [0] * N, [0] * N, [0] * N
    births_tile = Counter()
    added_upto = -1
    birth = {i: 0 for i in bodies}
    trail = {i: deque([b[0]], maxlen=12) for i, b in bodies.items()}
    lastdir, seenb, mem, streak, pend, spend = {}, {}, {}, {}, {}, {}
    logs = defaultdict(list)
    slogs = defaultdict(list)
    eats = defaultdict(list)
    kids = {}
    steps = defaultdict(lambda: [0] * 12)
    queenc = defaultdict(lambda: [0] * 4)
    blindc = defaultdict(lambda: [0, 0])
    streakc = defaultdict(lambda: [0] * 5)
    retc, nc, born = Counter(), Counter(), Counter()
    episodes = [0, 0]
    chk = [dict(turns=0, blind=0, moved=0, dither=0, keeps=0, keeps_eligible=0, pearls=0, splits=0) for _ in range(2)]
    side_seen = set()
    snaps = {}
    first_contact = None
    rnd, actor, used, dirs, cur = 0, None, 0, [], None
    started = False

    def close_kid(i, code):
        k = kids.pop(i, None)
        if k is not None:
            born[k + '|' + code] += 1

    def finish_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        i = t['id']
        if t['blind'] and t['first'] is not None:
            wi = t['wi']
            t['key'] = t['key'] + '|' + ('9' if t['previous'] is None else str(int(t['first_dir'] == t['previous'])))
            c = chk[wi]
            re = int(t['first'] in t['trail'])
            c['moved'] += 1
            c['dither'] += re
            v = steps[t['key']]
            v[0] += 1
            v[1] += re
            qv = queenc['%d|%d|%s' % (wi, int(i == queen), t['sc'])]
            qv[0] += 1
            qv[1] += re
            if t['previous'] is not None:
                kept = int(t['first_dir'] == t['previous'])
                c['keeps_eligible'] += 1
                c['keeps'] += kept
                v[2] += 1
                v[3] += kept
                qv[2] += 1
                qv[3] += kept
            if i in bodies:
                pend[i] = (t['key'], re)
            logs[i].append((t['rnd'], t['key'], re))
            free = t['free']
            alt = 'forced' if len(free) <= 1 else 'boxed' if all(d[1] in t['trail'] for d in free) else 'choice'
            if re:
                tl = t['tlist']
                ago = len(tl) - 1 - max(n for n, z in enumerate(tl) if z == t['first'])
                agob = str(ago) if ago in (3, 5, 7) else '9' if ago in (9, 11) else 'x'
                retc['%d|%s|%s|%s|%s' % (wi, t['lb'], t['sc'], agob, alt)] += 1
            if t['sc'][0] == 'N':
                du, mask = t['probe']
                tu = 2 if du == 0 else (mask >> t['first_dir']) % 2
                tc = int(g.cdist(t['first']) < g.cdist(t['head']))
                nc['%d|%s|%d|%d|%d|%s' % (wi, t['sc'], re, tu, tc, alt)] += 1
        lastdir[i] = t['first_dir']

    def probe(head, free, sb):
        lab, frontier = {}, []
        for d, dest in free:
            if dest in lab:
                lab[dest] |= 1 << d
            else:
                lab[dest] = 1 << d
                frontier.append(dest)
        done = set(lab)
        done.add(head)
        depth = 1
        while frontier and depth <= 8:
            mask = 0
            for c in frontier:
                if not sb[c]:
                    mask |= lab[c]
            if mask:
                return depth, mask
            nxt = {}
            for c in frontier:
                m = lab[c]
                for t in adj[c]:
                    if t not in done:
                        nxt[t] = nxt.get(t, 0) | m
            done.update(nxt)
            lab = nxt
            frontier = list(nxt)
            depth += 1
        return 0, 0

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

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish_turn()
        if k == 0:
            if started and rnd in (50, 100):
                snaps[rnd] = len(side_seen)
            started = True
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
            for rr in range(added_upto + 1, rnd + HORIZON + 1):
                for c in nat.get(rr, ()):
                    for z in g.window(c)[0]:
                        sv[z] += 1
            added_upto = max(added_upto, rnd + HORIZON)
        elif k == 1:
            actor = p.i32(0)
            dirs, used = [], 0
            if side(actor) != 'u':
                continue
            b = bodies[actor]
            head, L = b[0], len(b)
            win, winset = g.window(head)
            enemy = False
            eg = hg['t']
            for c in win:
                if eg[c]:
                    enemy = True
                    break
            if first_contact is None and enemy:
                first_contact = rnd
            if rnd > LAST:
                continue
            wi = 0 if rnd <= 100 else 1
            blind = pv[head] == 0
            sb = seenb.get(actor)
            if sb is None:
                sb = bytearray(N)
                seenb[actor] = sb
                mem[actor] = set()
                streak[actor] = 0
                if actor in kids:
                    kids[actor] = kids[actor] + '|' + str(int(blind))
            for c in win:
                sb[c] = 1
            if rnd <= 100:
                side_seen.update(winset)
            mm = mem[actor]
            if mm:
                for c in tuple(mm):
                    if c not in present and c in winset:
                        mm.discard(c)
            if not blind:
                for c in win:
                    if c in present:
                        mm.add(c)
            ug = hg['u']
            mates = -1
            for c in win:
                mates += ug[c]
            hotp = hv[head] > 0
            dens = len(present) * 1000 // N
            db = 0 if dens < 4 else 1 if dens < 8 else 2 if dens < 16 else 3 if dens < 32 else 4
            bc = blindc['%d|%d|%d|%d' % (wi, db, min(mates, 2), int(hotp))]
            bc[0] += 1
            bc[1] += int(blind)
            c0 = chk[wi]
            c0['turns'] += 1
            c0['blind'] += int(blind)
            pr = pend.pop(actor, None)
            if pr is not None:
                v = steps[pr[0]]
                if pr[1]:
                    v[6] += 1
                    v[7] += int(not blind)
                else:
                    v[4] += 1
                    v[5] += int(not blind)
            sp = spend.pop(actor, None)
            if sp is not None:
                sc_ = streakc[sp]
                sc_[1] += 1
                sc_[2] += int(not blind)
            if blind:
                streak[actor] += 1
                n = streak[actor]
                if n == 1:
                    episodes[wi] += 1
                skey = '%d|%d' % (wi, 0 if n == 1 else 1 if n <= 4 else 2 if n <= 9 else 3)
                streakc[skey][0] += 1
                spend[actor] = skey
                slogs[actor].append((rnd, skey))
            else:
                streak[actor] = 0
            cur = dict(id=actor, rnd=rnd, wi=wi, head=head, blind=blind, previous=lastdir.get(actor), first=None, first_dir=None)
            if blind:
                free = [(d, moves[head][d][1]) for d in range(4) if moves[head][d][0] != 1 and occ[moves[head][d][1]] == 0]
                pb = None
                if enemy:
                    sc = 'T'
                elif sv[head] > 0:
                    sc = 'S'
                elif mm and min(g.mdist(head, c) for c in mm) <= 7:
                    sc = 'R'
                elif hotp:
                    sc = 'H'
                elif not roomy(head, 3 * L + 8):
                    sc = 'C'
                else:
                    pb = probe(head, free, sb)
                    if g.centre_on and L <= 4 and rnd < g.centre_rounds:
                        sc = 'Nc'
                    else:
                        sc = 'N4' if 1 <= pb[0] <= 4 else 'N6' if 5 <= pb[0] <= 6 else 'Nf'
                near = False
                for c in g.diamond(head):
                    if ug[c]:
                        near = True
                        break
                ball = g.ball(head)
                ar = 'M' if near else 'K' if ball <= 20 else 'P' if g.nearp[head] else 'W' if ball <= 32 else 'O'
                lb = lbucket(L)
                cur.update(trail=set(trail[actor]), tlist=list(trail[actor]), free=free, sc=sc, probe=pb, lb=lb,
                           key='%d|%s|%s|%s|%s|%d' % (wi, lb, abucket(rnd - birth[actor]), sc, ar, int(streak[actor] >= 5)))
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present.add(c)
                for z in g.window(c)[0]:
                    pv[z] += 1
                if actor is None and c in nat.get(rnd, ()):
                    for z in g.window(c)[0]:
                        sv[z] -= 1
                births_tile[c] += 1
                if births_tile[c] == 2:
                    for z in g.window(c)[0]:
                        hv[z] += 1
            else:
                present.discard(c)
                for z in g.window(c)[0]:
                    pv[z] -= 1
                if side(actor) == 'u':
                    eats[actor].append(rnd)
                    if rnd <= LAST:
                        chk[0 if rnd <= 100 else 1]['pearls'] += 1
                    if actor in kids:
                        close_kid(actor, 'f%d' % min(rnd - birth[actor], CAP + 1))
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                b.appendleft(hd)
                occ[hd] += 1
                s = side(i)
                hg[s][old] -= 1
                hg[s][hd] += 1
                if i == actor:
                    if cur is not None and cur['first'] is None and used < len(dirs):
                        cur['first'], cur['first_dir'] = hd, dirs[used]
                    used += 1
                    trail[i].append(hd)
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s0 = side(parent)
            for c in bodies[parent]:
                occ[c] -= 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                for c in bodies[i]:
                    occ[c] += 1
            hg[s0][bodies[child][0]] += 1
            trail[child] = deque([bodies[child][0]], maxlen=12)
            birth[child] = rnd
            if s0 == 'u' and rnd <= LAST:
                chk[0 if rnd <= 100 else 1]['splits'] += 1
                kids[child] = '%d' % (0 if rnd <= 100 else 1)
        elif k == 11:
            i = p.i32(0)
            b = bodies.pop(i)
            for c in b:
                occ[c] -= 1
            s = side(i)
            hg[s][b[0]] -= 1
            if s == 'u':
                pend.pop(i, None)
                spend.pop(i, None)
                if i in kids:
                    if '|' not in kids[i]:
                        kids[i] = kids[i] + '|9'
                    close_kid(i, 'd%d' % min(rnd - birth[i], CAP + 1))
    finish_turn()
    if rnd in (50, 100) and rnd not in snaps:
        snaps[rnd] = len(side_seen)
    endr = min(rnd, row['last_round'])
    for i in list(kids):
        if '|' not in kids[i]:
            kids[i] = kids[i] + '|9'
        close_kid(i, 'c%d' % min(endr - birth[i], CAP + 1))
    for i, entries in logs.items():
        es = eats.get(i, ())
        for r0, key, re in entries:
            if r0 + 10 <= row['last_round']:
                n = sum(1 for e in es if r0 <= e <= r0 + 10)
                v = steps[key]
                if re:
                    v[10] += 1
                    v[11] += n
                else:
                    v[8] += 1
                    v[9] += n
    for i, entries in slogs.items():
        es = eats.get(i, ())
        for r0, skey in entries:
            if r0 + 10 <= row['last_round']:
                v = streakc[skey]
                v[3] += 1
                v[4] += sum(1 for e in es if r0 <= e <= r0 + 10)
    return dict(who=row['who'], game=row['game'], layout=row['layout'], result=row['result'], rating=row['rating'],
                last_round=row['last_round'], cells=N, chk=chk, seen50=snaps.get(50), seen100=snaps.get(100),
                first_contact=first_contact, episodes=episodes, steps=dict(steps), queenc=dict(queenc),
                blindc=dict(blindc), streakc=dict(streakc), retc=dict(retc), nc=dict(nc), born=dict(born))


def save(who, shard, body):
    tag = who + str(shard)
    if tag == 'O0':
        Path(OUT + 'wk_keep-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'wk_keep-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'wk_keep-O2.jsonl').write_text(body)
    elif tag == 'O3':
        Path(OUT + 'wk_keep-O3.jsonl').write_text(body)
    elif tag == 'O4':
        Path(OUT + 'wk_keep-O4.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'wk_keep-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'wk_keep-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'wk_keep-R2.jsonl').write_text(body)
    elif tag == 'R3':
        Path(OUT + 'wk_keep-R3.jsonl').write_text(body)
    elif tag == 'R4':
        Path(OUT + 'wk_keep-R4.jsonl').write_text(body)
    else:
        Path(OUT + 'wk_keep-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, out, bad, off = {}, [], [], 0
    for n, r in enumerate(rows):
        try:
            rec = scan(r, geos)
            for wi, name in enumerate(('0-100', '101-300')):
                for f, val in rec['chk'][wi].items():
                    if r[name][f] != val:
                        off += 1
                        if off <= 12:
                            print('MISMATCH', r['game'], name, f, r[name][f], val, flush=True)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 10 == 9:
            print(n + 1, len(rows), 'bad', len(bad), 'off', off, flush=True)
    save(who, shard if not limit else 9, '\n'.join(out) + '\n')
    print('done', who, shard, len(out), 'bad', bad, 'mismatches', off)


main()
