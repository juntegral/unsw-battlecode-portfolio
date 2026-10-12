# Scratch (diag-split): replays the games of both teams (ours = O, 500 ladder games; rank-1 = R, 597 games) and
# counts, for the focal side of each game, every dragon turn by length, every split (parent length, child size),
# every turn on which a dragon is 4 or longer by state (round band, length, dragons alive, role, room behind the
# tail, portal at the tail, enemy head near, free tile at the head), spells of 4 or longer, deaths, lifetimes and
# standings. One JSON line per game -> sl_scan-<shard>.jsonl (sl_test.jsonl with a games-per-layout limit).
# Usage: python3 data/analysis/ladder/dossier/work/sl_scan.py <shard> <shards> [games per layout per team]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LIMIT = 64
ROOM_CAP = 8
NEAR = 3
MARKS = (50, 100, 150, 200, 250, 300, 350, 400, 450, 500)
LAND = (100, 200, 300, 400)


def band(r):
    return 0 if r <= 100 else 1 if r <= 150 else 2 if r <= 200 else 3 if r <= 300 else 4 if r <= 400 else 5


def lb(n):
    return 0 if n == 2 else 1 if n == 3 else 2 if n == 4 else 3 if n <= 7 else 4


def elb(n):
    return 0 if n == 4 else 1 if n == 5 else 2 if n <= 7 else 3


def nb(n):
    return 0 if n < 32 else 1 if n < 56 else 2 if n < 60 else 3 if n < LIMIT else 4


def lifeb(n):
    return 0 if n <= 0 else 1 if n == 1 else 2 if n == 2 else 3 if n <= 5 else 4 if n <= 10 else 5 if n <= 20 else 6 if n <= 40 else 7 if n <= 80 else 8 if n <= 160 else 9


def durb(n):
    return 0 if n == 1 else 1 if n == 2 else 2 if n <= 5 else 3 if n <= 20 else 4


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nbr = []
        self.portal = []
        for y in range(h):
            for x in range(w):
                row = []
                flag = 0
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        flag = 1
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append(dest)
                self.nbr.append(row)
                self.portal.append(flag)


def scan(row, geos):
    root = replay.load(row['replay']).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    cells = w * h
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = row['layout_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    assert (g.w, g.h) == (w, h)
    nbr = g.nbr
    focal = row['our_side']
    sd = {i: (0 if teams[i] == focal else 1) for i in bodies}
    queen = [min(i for i in bodies if sd[i] == s) for s in (0, 1)]
    cnt = [0] * cells
    for b in bodies.values():
        for c in b:
            cnt[c] += 1
    alive = [sum(1 for i in bodies if sd[i] == s) for s in (0, 1)]
    maxalive = list(alive)
    born = {i: 0 for i in bodies}
    fresh = {}
    spell = {}
    present = {}
    expected = deque()

    turns = [[0] * 6 for s in range(2)]
    eats = [[[0, 0] for z in range(6)] for s in range(2)]
    splits = [[0] * 6 for s in range(2)]
    deathsn = [[0] * 6 for s in range(2)]
    lenlost = [[0] * 6 for s in range(2)]
    lhist = [[0] * 17 for z in range(6)]
    eatl = [[0] * 5 for z in range(6)]
    nbt = [[0] * 5 for z in range(6)]
    rounds_nb = [[0] * 5 for z in range(6)]
    alive_sum = [[0] * 6 for s in range(2)]
    rounds = [0] * 6
    attempts = [0] * 6
    spare_lost = [0] * 6
    natborn = [0] * 6
    splen, elig, spells, deaths, life = Counter(), {}, Counter(), Counter(), Counter()
    snaps, alive25, land = {}, {}, {}

    def near_enemy(hd, tl):
        hx, hy = hd % w, hd // w
        tx, ty = tl % w, tl // w
        mx = 0
        hit = 0
        for j, x in bodies.items():
            if sd[j] == 0:
                if len(x) > mx:
                    mx = len(x)
            elif not hit:
                e = x[0]
                ex, ey = e % w, e // w
                dx = abs(ex - hx)
                dy = abs(ey - hy)
                if min(dx, w - dx) + min(dy, h - dy) <= NEAR:
                    hit = 1
                else:
                    dx = abs(ex - tx)
                    dy = abs(ey - ty)
                    if min(dx, w - dx) + min(dy, h - dy) <= NEAR:
                        hit = 1
        return mx, hit

    def room_from(tl):
        seen = {tl}
        frontier = [tl]
        n = 0
        while frontier and n < ROOM_CAP:
            nxt = []
            for u in frontier:
                for v in nbr[u]:
                    if v not in seen and cnt[v] == 0:
                        seen.add(v)
                        nxt.append(v)
                        n += 1
            frontier = nxt
        return n

    def feat(i, bd):
        b = bodies[i]
        n = len(b)
        hd, tl = b[0], b[-1]
        mx, hit = near_enemy(hd, tl)
        role = 0 if i == queen[0] else 1 if n >= mx else 2
        rm = room_from(tl)
        rb = 0 if rm == 0 else 1 if rm < 4 else 2 if rm < ROOM_CAP else 3
        free = 0
        for v in nbr[hd]:
            if cnt[v] == 0:
                free = 1
                break
        return (bd, elb(n), nb(alive[0]), role, rb, g.portal[tl], hit, free)

    def snapshot(bd):
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if sd[i] == s]
            hist = [0] * 5
            for n in ls:
                hist[lb(n)] += 1
            out.append(dict(alive=len(ls), total=sum(ls), longest=max(ls, default=0),
                            queen=len(bodies.get(queen[s], ())), spare=sum(max(0, n // 2 - 1) for n in ls), hist=hist))
        held = {}
        for i, b in bodies.items():
            if sd[i] == 0 and len(b) >= 4:
                k = ','.join(map(str, feat(i, bd)))
                v = held.get(k)
                if v is None:
                    v = held[k] = [0, 0]
                v[0] += 1
                v[1] += len(b) // 2 - 1
        return dict(sides=out, held=held)

    def territory():
        dist = []
        for s in (0, 1):
            d = [-1] * cells
            frontier = []
            for i, b in bodies.items():
                if sd[i] == s and d[b[0]] < 0:
                    d[b[0]] = 0
                    frontier.append(b[0])
            k = 0
            while frontier:
                k += 1
                nxt = []
                for u in frontier:
                    for v in nbr[u]:
                        if d[v] < 0:
                            d[v] = k
                            nxt.append(v)
                frontier = nxt
            dist.append(d)
        f = e = t = 0
        for c in range(cells):
            a, b2 = dist[0][c], dist[1][c]
            if a < 0 and b2 < 0:
                continue
            if b2 < 0 or (a >= 0 and a < b2):
                f += 1
            elif a < 0 or b2 < a:
                e += 1
            else:
                t += 1
        return [f, e, t]

    def close_spell(i, how, n):
        sp = spell.pop(i, None)
        if sp is not None:
            spells[','.join(map(str, sp[0])) + ',' + how + ',' + str(durb(sp[1])) + ',' + str(elb(n))] += 1

    rnd, actor, bd = 0, None, 0
    cur_key = None
    act_kind, act_timeout = 2, False
    victim_side = -1
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            new = p.i32(0)
            if rnd in MARKS and new == rnd + 1:
                snaps[rnd] = snapshot(bd)
                if rnd in LAND:
                    land[rnd] = territory()
            if rnd % 25 == 0 and new == rnd + 1:
                alive25[rnd] = list(alive)
            rnd, actor = new, None
            bd = band(rnd)
            rounds[bd] += 1
            rounds_nb[bd][nb(alive[0])] += 1
            alive_sum[0][bd] += alive[0]
            alive_sum[1][bd] += alive[1]
        elif k == 1:
            actor = p.i32(0)
            cur_key = None
            act_kind, act_timeout = 2, False
            victim_side = -1
            b = bodies.get(actor)
            if b is None:
                continue
            s = sd[actor]
            turns[s][bd] += 1
            if s == 0:
                n = len(b)
                lhist[bd][min(n, 16)] += 1
                nbt[bd][nb(alive[0])] += 1
                if n >= 4:
                    f = feat(actor, bd)
                    sp = spell.get(actor)
                    if sp is None:
                        sp = spell[actor] = [f, 0]
                    sp[1] += 1
                    cur_key = ','.join(map(str, f)) + ',' + str(0 if sp[1] == 1 else 1 if sp[1] <= 5 else 2)
                    v = elig.get(cur_key)
                    if v is None:
                        v = elig[cur_key] = [0, 0, 0]
                    v[0] += 1
                    v[2] += n // 2 - 1
        elif k == 4:
            a = p.pointer(0)
            used = p.pointer(1)
            act_kind = a.u16(0) if a else 2
            act_timeout = bool(p.bit(32) or (used is not None and used.bit(64)))
            if actor in bodies and sd[actor] == 0 and act_kind == 1:
                attempts[bd] += 1
        elif k == 3:
            t = replay.point(p.pointer(0))
            t = t[1] * w + t[0]
            if p.u32(0):
                if expected:
                    xy = expected.popleft()
                    assert xy == t
                    present[t] = 1
                else:
                    present[t] = 0
                    natborn[bd] += 1
            else:
                origin = present.pop(t)
                s = sd[actor]
                eats[s][bd][origin] += 1
                if s == 0:
                    eatl[bd][lb(len(bodies[actor]))] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                cnt[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                cnt[b.pop()] -= 1
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            s = sd[a]
            before = len(bodies[a])
            for cell in bodies[a]:
                cnt[cell] -= 1
            sd[c] = s
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for cell in bodies[i]:
                    cnt[cell] += 1
            splits[s][bd] += 1
            alive[s] += 1
            if alive[s] > maxalive[s]:
                maxalive[s] = alive[s]
            born[c] = rnd
            fresh[a] = rnd
            fresh[c] = rnd
            if s == 0:
                splen[str(bd) + ',' + str(min(before, 16)) + ',' + str(min(len(bodies[c]), 12))] += 1
                if cur_key is not None and a == actor:
                    elig[cur_key][1] += 1
                    cur_key = None
                close_spell(a, 's', before)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            s = sd[i]
            n = len(b)
            if reason == 3:
                if i == actor:
                    cause = 'hmx' if victim_side != s else 'hms'
                else:
                    victim_side = s
                    cause = 'hvx' if sd[actor] != s else 'hvs'
            elif reason == 4:
                if i == actor:
                    cause = 'timeout' if act_timeout else ('sprint', 'isplit', 'noact')[act_kind] if act_kind < 3 else 'noact'
                else:
                    cause = 'noact'
            else:
                cause = ('wall', 'own', 'body')[reason] if reason < 3 else '?'
            deathsn[s][bd] += 1
            lenlost[s][bd] += n
            if s == 0:
                free = 0
                for v in nbr[b[0]]:
                    if cnt[v] == 0:
                        free = 1
                        break
                mx, hit = near_enemy(b[0], b[-1])
                age = rnd - born[i]
                ageb = 0 if age <= 1 else 1 if age <= 5 else 2 if age <= 20 else 3
                fr = 1 if rnd - fresh.get(i, -9) <= 1 else 0
                deaths[','.join(map(str, (bd, cause, lb(n), nb(alive[0]), 1 - free, ageb, fr, hit)))] += 1
                spare_lost[bd] += max(0, n // 2 - 1)
                life[str(band(born[i])) + ',' + str(lifeb(age)) + ',1'] += 1
                close_spell(i, 'd', n)
            alive[s] -= 1
            for seg, cell in enumerate(b):
                cnt[cell] -= 1
                if seg % 2 == 0:
                    expected.append(cell)
            bodies.pop(i)
    for i, b in bodies.items():
        if sd[i] == 0:
            life[str(band(born[i])) + ',' + str(lifeb(rnd - born[i])) + ',0'] += 1
    for i in list(spell):
        close_spell(i, 'e', len(bodies[i]))
    final = snapshot(bd)
    return dict(game=row['game'], tm=row['tm'], layout=key, cells=cells, w=w, h=h, focal=focal, result=row['result'],
                last=rnd, rating=row.get('opponent_rating'), turns=turns, eats=eats, splits=splits, deathsn=deathsn,
                lenlost=lenlost, lhist=lhist, eatl=eatl, nbt=nbt, rounds_nb=rounds_nb, alive_sum=alive_sum,
                rounds=rounds, attempts=attempts, spare_lost=spare_lost, natborn=natborn, splen=dict(splen), elig=elig,
                spells=dict(spells), deaths=dict(deaths), life=dict(life), snaps=snaps, alive25=alive25, land=land,
                final=final, maxalive=maxalive)


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = []
    for tm, f in (('O', 'data/analysis/ladder/dossier/per-game.jsonl'),
                  ('R', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl')):
        seen = Counter()
        for line in open(f):
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            seen[r['layout_key']] += 1
            if limit and seen[r['layout_key']] > limit:
                continue
            rows.append(dict(game=r['game'], tm=tm, layout_key=r['layout_key'], replay=r['replay'],
                             our_side=r['our_side'], result=r['result'], opponent_rating=r.get('opponent_rating')))
    rows.sort(key=lambda r: (r['layout_key'], r['tm'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    text = '\n'.join(out) + '\n'
    if limit:
        Path(OUT + 'sl_test.jsonl').write_text(text)
    elif shard == 0:
        Path(OUT + 'sl_scan-0.jsonl').write_text(text)
    elif shard == 1:
        Path(OUT + 'sl_scan-1.jsonl').write_text(text)
    elif shard == 2:
        Path(OUT + 'sl_scan-2.jsonl').write_text(text)
    elif shard == 3:
        Path(OUT + 'sl_scan-3.jsonl').write_text(text)
    elif shard == 4:
        Path(OUT + 'sl_scan-4.jsonl').write_text(text)
    else:
        Path(OUT + 'sl_scan-5.jsonl').write_text(text)
    print('done', shard, len(out), 'bad', bad)


main()
