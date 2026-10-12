# Scratch (diag-hungry): an offline rebuild of score_step for every hungry turn of the local m3b7 games (the traced
# build could not be compiled or played under this session's tool guard). For each dragon of ours the script keeps
# what the bot keeps (main.cpp 1443-1454, 1597-1619): for every tile it has had in its 7 by 7 view the round, the pearl
# and the countdown it saw, and the hot mark. On a hungry turn (length 2 or 3, rounds 0-300, 26+ rounds since the last
# meal or birth) it rebuilds, for each step on offer, the survey of 2922-3077 over the tiles within 16 steps:
#   room, territory (2956-2967, weights 3234-3247), dist_pearl (2977-2985, remembered pearls included),
#   dist_soon (2989-2996), dist_hot (2997-3001), dist_unseen (3002-3005), and the flat terms of 5039-5144
#   (tight / trapped / no tail, eat bonus, spawn clear, a mate's head beside the step) and a one-tile look-ahead.
# Not rebuilt: enemy threat terms, the leader zone (approximated: longest own dragon, radius 9), route targets,
# harvest, pockets, the full 8-step look-ahead, tiles beyond 16 steps (never-seen tiles are searched to 80 steps).
# Usage: python3 data/analysis/ladder/dossier/work/hg_scan3.py <arm dir under solo/runs> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque
from pathlib import Path

RUNS = '~/meow-redteam/solo/runs/'
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
RAD = 16
INF = 1 << 28


def edge_id(w, h, x, y, d):
    return (2 * y * (w + 1) + x if d == 0 else (2 * y + 1) * (w + 1) + (x + 1) % w if d == 1
            else 2 * ((y + 1) % h) * (w + 1) + x if d == 2 else (2 * y + 1) * (w + 1) + x)


def build_moves(w, h, raw):
    edges = {}
    for e, k, p in raw:
        row, x = divmod(e, w + 1)
        if row % 2 == 0 and x == w:
            continue
        e = 2 * ((row // 2) % h) * (w + 1) + x if row % 2 == 0 else row * (w + 1) + x % w
        if e not in edges or k > edges[e][0]:
            edges[e] = (k, p)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    moves = []
    for y in range(h):
        for x in range(w):
            row = []
            for d, (dx, dy) in enumerate(STEP):
                e = edge_id(w, h, x, y, d)
                k, pid = edges.get(e, (0, -1))
                if k == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                row.append((k, dest))
            moves.append(row)
    return moves


def scan(path, our, gi, rows_out):
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w = h = 0
    bodies, teams, raw, barren = {}, {}, [], None
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = int(q[1]), int(q[2])
            barren = bytearray(w * h)
        elif q[0] == 'TILE':
            if int(q[4]) == 0:
                barren[int(q[2]) * w + int(q[1])] = 1
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    N = w * h
    grow = 300 if N <= 1200 else 150
    moves = build_moves(w, h, raw)
    adj = [[t for k, t in row if k != 1] for row in moves]
    wins = {}

    def win(c):
        v = wins.get(c)
        if v is None:
            y, x = divmod(c, w)
            v = tuple(((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4))
            wins[c] = v
        return v

    def gap(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    sd = {i: 0 if teams[i] == our else 1 for i in bodies}
    fed = {i: 0 for i in bodies}

    def blank():
        return dict(sr=[-1] * N, tm=[-2] * N, pe=bytearray(N), hot=bytearray(N), low=[-1000] * N, un=set(range(N)))

    mem = {i: blank() for i in bodies if sd[i] == 0}
    present = set()
    spawn_at = [0] * N
    cur = None
    rnd, actor = 0, None
    alive = [0, 0]
    for i in bodies:
        alive[sd[i]] += 1

    def analyse(i, b):
        head = b[0]
        L = len(b)
        m = mem[i]
        sr, tm, pe, hot = m['sr'], m['tm'], m['pe'], m['hot']
        wn = set(win(head))
        other = set()
        mates, foes = [], []
        lead, leadlen = -1, L
        for j, bb in bodies.items():
            if j == i:
                continue
            for t in bb:
                if t in wn:
                    other.add(t)
            if bb[0] in wn:
                (mates if sd[j] == 0 else foes).append(bb[0])
            if sd[j] == 0 and len(bb) > leadlen:
                lead, leadlen = bb[0], len(bb)
        zone_on = rnd > grow and lead >= 0

        def zone(x):
            if not zone_on:
                return False
            tl = gap(x, lead)
            return tl <= 9 and not gap(x, head) < tl

        own = {t: L - off + 1 for off, t in enumerate(b)}
        tail = b[-1]
        S = {head: 0}
        q = [head]
        for t in q:
            s = S[t]
            if s >= RAD:
                continue
            for nb in adj[t]:
                if nb not in S and nb not in other and nb not in own:
                    S[nb] = s + 1
                    q.append(nb)

        def flood(srcs):
            dist = {x: 0 for x in srcs}
            qq = list(srcs)
            for t in qq:
                s = dist[t]
                for nb in adj[t]:
                    if nb in S and nb not in dist and nb != head:
                        dist[nb] = s + 1
                        qq.append(nb)
            return dist

        ally = flood(mates) if mates else {}
        rival = flood(foes) if foes else {}
        mate_adj = set()
        for mh in mates:
            for nb in adj[mh]:
                mate_adj.add(nb)
        dests = []
        for d in range(4):
            k, dest = moves[head][d]
            dests.append(None if k == 1 or dest in other or dest in own else (k, dest))
        out = []
        for d in range(4):
            if dests[d] is None:
                out.append(None)
                continue
            k, dest = dests[d]
            st = {dest: 1}
            qq = [dest]
            a_seen = a_un = 0
            o_seen = o_un = 0.0
            dp = ds = dh = du = -1
            tp = ts = -1
            look = 0.0
            tailhit = 0
            for t in qq:
                s = st[t]
                th = rival.get(t, INF)
                al = ally.get(t, INF)
                share = 1.0 if s < th else 0.5 if s == th else 0.0
                if al < s:
                    share = 0.0
                if t == tail:
                    tailhit = 1
                seen_t = sr[t] >= 0
                zn = zone(t) if zone_on else False
                if not seen_t:
                    a_un += 1
                    o_un += share
                    if du < 0:
                        du = s
                else:
                    a_seen += 1
                    if pe[t]:
                        o_seen += share
                    elif tm[t] < 0:
                        o_seen += share * 0.3
                    else:
                        o_seen += share * 80.0 / (80.0 + max(0, tm[t] - (rnd - sr[t])))
                    if pe[t] and not zn:
                        if dp < 0 and (share >= 1.0 or (s <= th + 1 and al >= s)):
                            dp = s
                            tp = t
                        if s <= 8 and th > s and al >= s:
                            look = max(look, 80.0 * (1.0 if th > s else 0.5) * 0.85 ** (s - 1))
                    if tm[t] >= 0 and not zn:
                        sp = tm[t] - (rnd - sr[t])
                        if ds < 0 and share >= 1.0 and sp <= s + 6:
                            ds = s + max(0, sp - s)
                            ts = t
                        if not pe[t] and s <= 8 and 1 <= sp <= s and th > s and al >= s:
                            look = max(look, 40.0 * 0.85 ** (s - 1))
                    if hot[t] and dh < 0 and al >= s and s <= th + 1 and not zn:
                        sp = 0 if pe[t] else tm[t] - (rnd - sr[t])
                        dh = s + max(0, sp - s)
                for nb in adj[t]:
                    if nb in st or nb in other:
                        continue
                    if nb in own:
                        if s + 1 < own[nb]:
                            continue
                    elif nb not in S:
                        continue
                    st[nb] = s + 1
                    qq.append(nb)
            room = a_seen + 0.5 * a_un
            terr = o_seen + 0.5 * o_un
            cr = 0.0
            if room < 3.0 * L + 8.0:
                cr += 400.0 * (3.0 * L + 8.0 - room)
            if room < L + 2.0:
                cr += 5000.0 * (L + 2.0 - room)
            if not tailhit:
                cr += 600.0
            eat = 1 if dest in present and not zone(dest) else 0
            sc = 0
            if dest not in present and tm[dest] >= 0 and sr[dest] >= 0:
                sp = tm[dest] - (rnd - sr[dest])
                if 0 <= sp <= min(L, 4):
                    sc = 1
            out.append([round(room, 1), round(terr, 2), dp, ds, dh, du, eat, 1 if dest in mate_adj else 0, sc, round(cr), round(look, 1),
                        1 if k == 2 else 0, tp, ts, dest])
        un = m['un']
        need = {dests[d][1] for d in range(4) if dests[d] is not None and out[d][5] < 0}
        if un and need:
            dist = {}
            qq = []
            for t in un:
                if t not in other:
                    dist[t] = 0
                    qq.append(t)
            left = len(need)
            for t in qq:
                if left <= 0:
                    break
                s = dist[t]
                if s >= 80:
                    break
                for nb in adj[t]:
                    if nb not in dist and nb not in other:
                        dist[nb] = s + 1
                        qq.append(nb)
                        if nb in need:
                            left -= 1
            for d in range(4):
                if dests[d] is not None and out[d][5] < 0 and dests[d][1] in dist:
                    out[d][5] = dist[dests[d][1]] + 1
        # truth of the targets named by each step: is the pearl there now, is the tile in view
        for d in range(4):
            if out[d] is None:
                continue
            tp, ts = out[d][12], out[d][13]
            out[d][12] = -1 if tp < 0 else (2 if tp in wn else 1 if tp in present else 0)
            out[d][13] = -1 if ts < 0 else (2 if ts in present else 1 if spawn_at[ts] - rnd <= 6 else 0)
        npv = sum(1 for t in wn if t in present)
        return dict(g=gi, i=i, r=rnd, L=L, idle=rnd - fed[i], h=head, np=npv, nm=len(mates), ne=len(foes),
                    box=len(S) if len(S) < 12 else 12, al=alive[0], zn=1 if zone_on and gap(head, lead) <= 12 else 0,
                    dirs=out, path=[], ate=0, died=-1)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 2, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            cur = None
            if rnd > 300:
                break
        elif k == 2:
            t = replay.point(p.pointer(0))
            spawn_at[t[1] * w + t[0]] = rnd + p.i32(0)
        elif k == 1:
            actor = p.i32(0)
            cur = None
            b = bodies.get(actor)
            if b is None or sd[actor] != 0:
                continue
            m = mem[actor]
            sr, tm, pe, hot, low, un = m['sr'], m['tm'], m['pe'], m['hot'], m['low'], m['un']
            for t in win(b[0]):
                if sr[t] < 0:
                    un.discard(t)
                sr[t] = rnd
                pe[t] = 1 if t in present else 0
                timer = -1 if barren[t] else max(0, spawn_at[t] - rnd)
                tm[t] = timer
                if 0 <= timer <= 4:
                    g = rnd - low[t]
                    if 6 <= g <= 25:
                        hot[t] = 1
                    if g >= 6:
                        low[t] = rnd
                elif timer > 8:
                    hot[t] = 0
            if len(b) <= 3 and rnd - fed[actor] >= 26:
                cur = analyse(actor, b)
                rows_out.append(cur)
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if cur is not None:
                    cur['ate'] = 1
                fed[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if cur is not None and i == actor:
                    cur['path'].append(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            alive[sd[a]] += 1
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
            fed[c] = rnd
            fed[a] = rnd
            if sd[c] == 0:
                mem[c] = blank()
        elif k == 11:
            i = p.i32(0)
            if cur is not None and i == actor:
                cur['died'] = p.u16(4)
            alive[sd[i]] -= 1
            bodies.pop(i)
            mem.pop(i, None)
    return dict(w=w, h=h, rounds=rnd)


def save(tag, body):
    if tag == 'm3b7-0':
        Path(OUT + 'hg_scan3-m3b7-0.jsonl').write_text(body)
    elif tag == 'm3b7-1':
        Path(OUT + 'hg_scan3-m3b7-1.jsonl').write_text(body)
    elif tag == 'm3b7-2':
        Path(OUT + 'hg_scan3-m3b7-2.jsonl').write_text(body)
    elif tag == 'm3b7-3':
        Path(OUT + 'hg_scan3-m3b7-3.jsonl').write_text(body)
    else:
        Path(OUT + 'hg_scan3-test.jsonl').write_text(body)


def main():
    arm, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    games = sorted(d.name for d in Path(RUNS + arm).iterdir() if (d / 'game.replay').is_file())
    todo = [(n, g) for n, g in enumerate(games) if n % shards == shard]
    if limit:
        todo = todo[::max(1, len(todo) // limit)][:limit]
    out, bad = [], []
    for z, (n, g) in enumerate(todo):
        our = int(g.rsplit('side', 1)[1])
        rows = []
        try:
            summ = scan(RUNS + arm + '/' + g + '/game.replay', our, n, rows)
        except Exception as e:
            bad.append((g, repr(e)[:300]))
            continue
        summ.update(game=g, gi=n, our=our)
        out.append(json.dumps(dict(kind='game', **summ), separators=(',', ':')))
        for r in rows:
            out.append(json.dumps(r, separators=(',', ':')))
        print(z + 1, len(todo), g, len(rows), 'bad', len(bad), flush=True)
    save('test' if limit else arm + '-' + str(shard), '\n'.join(out) + '\n')
    print('done', arm, shard, len(todo), 'bad', bad)


main()
