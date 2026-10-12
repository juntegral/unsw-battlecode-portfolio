# Scratch (diag-hungry): how a hungry short dragon moves, ours against rank-1 on the ladder and m3b7 locally.
# Followed side only, dragons of length 2 and 3, rounds 0-300. Per layout, per class
#   (hungry 0 = 4-25 rounds since the last meal or birth, 1 = 26+; view 0/1 = a pearl in the 7 by 7 view;
#    mates 0, 1 = 1-2, 2 = 3+ team mates' heads in view)
# counts: turns; tiles away (torus) from where it stood 10 own turns ago (n, sum, 4 or fewer); head on a tile it stood
# on in its last 12 turns; same step as last turn (n, same); tiles it sees for the first time this turn (sum, turns
# with none); nearest pearl on the whole board that no other dragon of its side is nearer to (torus, walls ignored):
# within 3, 4-6, 7-12, none within 12; turns that end in a meal; and the same pearl older than 10 rounds within 12.
# Usage: python3 data/analysis/ladder/dossier/work/hg_lad.py <O|R|L> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque
from pathlib import Path

RUNS = '~/meow-redteam/solo/runs/m3b7/'
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
NF = 17


def scan(path, focal, acc, wins):
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    N = w * h
    wk = (w, h)
    if wk not in wins:
        wins[wk] = [tuple(sorted({((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4)})) for y in range(h) for x in range(w)]
    win = wins[wk]
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    fed = {i: 0 for i in bodies}
    seen = {i: bytearray(N) for i in bodies if sd[i] == 0}
    hist = {i: deque(maxlen=12) for i in bodies if sd[i] == 0}
    pv = [0] * N
    hv = [0] * N
    for i, b in bodies.items():
        if sd[i] == 0:
            for z in win[b[0]]:
                hv[z] += 1
    present = {}
    last = None
    rnd, actor = 0, None

    def gap(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            last = None
            if rnd > 300:
                break
        elif k == 1:
            actor = p.i32(0)
            last = None
            b = bodies.get(actor)
            if b is None or sd[actor] != 0:
                continue
            hd = b[0]
            sn = seen[actor]
            new = 0
            for t in win[hd]:
                if not sn[t]:
                    sn[t] = 1
                    new += 1
            hs = hist[actor]
            idle = rnd - fed[actor]
            if len(b) <= 3 and idle >= 4:
                nm = hv[hd] - 1
                key = (1 if idle >= 26 else 0, 1 if pv[hd] else 0, 0 if nm <= 0 else 1 if nm <= 2 else 2)
                v = acc[key]
                v[0] += 1
                if len(hs) >= 10:
                    d = gap(hs[-10], hd)
                    v[1] += 1
                    v[2] += d
                    v[3] += d <= 4
                if hd in hs:
                    v[4] += 1
                if len(hs) >= 2:
                    v[5] += 1
                    a1, a2 = hs[-1], hs[-2]
                    if (hd % w - a1 % w) % w == (a1 % w - a2 % w) % w and (hd // w - a1 // w) % h == (a1 // w - a2 // w) % h and hd != a1:
                        v[6] += 1
                v[7] += new
                v[8] += new == 0
                best = 13
                age = 0
                heads = None
                for c, born in present.items():
                    d = gap(hd, c)
                    if d < best:
                        if heads is None:
                            heads = [bb[0] for j, bb in bodies.items() if sd[j] == 0 and j != actor]
                        ok = True
                        for m in heads:
                            if gap(m, c) < d:
                                ok = False
                                break
                        if ok:
                            best = d
                            age = rnd - born
                v[9 + (0 if best <= 3 else 1 if best <= 6 else 2 if best <= 12 else 3)] += 1
                if best <= 12 and age > 10:
                    v[14] += 1
                if best <= 12 and best > 3:
                    v[15] += 1
                    v[16] += age
                last = v
            hs.append(hd)
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present[c] = rnd
                for z in win[c]:
                    pv[z] += 1
            else:
                present.pop(c, None)
                for z in win[c]:
                    pv[z] -= 1
                if last is not None:
                    last[13] += 1
                fed[actor] = rnd
                if sd[actor] == 0:
                    hist[actor].clear()
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                if sd[i] == 0:
                    for z in win[b[0]]:
                        hv[z] -= 1
                    for z in win[hd]:
                        hv[z] += 1
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            if sd[a] == 0:
                for z in win[bodies[a][0]]:
                    hv[z] -= 1
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                if sd[a] == 0:
                    for z in win[bodies[i][0]]:
                        hv[z] += 1
            fed[c] = rnd
            fed[a] = rnd
            if sd[c] == 0:
                seen[c] = bytearray(N)
                hist[c] = deque(maxlen=12)
                hist[a].clear()
        elif k == 11:
            i = p.i32(0)
            if sd[i] == 0:
                for z in win[bodies[i][0]]:
                    hv[z] -= 1
                seen.pop(i, None)
                hist.pop(i, None)
            bodies.pop(i)


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'hg_lad-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'hg_lad-O1.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'hg_lad-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'hg_lad-R1.jsonl').write_text(body)
    elif tag == 'L0':
        Path(OUT + 'hg_lad-L0.jsonl').write_text(body)
    else:
        Path(OUT + 'hg_lad-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    if who == 'L':
        games = sorted(d.name for d in Path(RUNS).iterdir() if (d / 'game.replay').is_file())
        rows = [dict(replay=RUNS + g + '/game.replay', side='AB'[int(g.rsplit('side', 1)[1])], layout=g.split('-seed')[0], game=g) for g in games]
    else:
        rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
        rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    accs, bad, wins = {}, [], {}
    for n, r in enumerate(rows):
        a = accs.setdefault(r['layout'], defaultdict(lambda: [0] * NF))
        try:
            scan(r['replay'], r['side'], a, wins)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), 'bad', len(bad), flush=True)
    out = [json.dumps(dict(who=who, layout=lay, acc=[list(kk) + v for kk, v in sorted(a.items())]), separators=(',', ':')) for lay, a in sorted(accs.items())]
    save('test' if limit else who + str(shard), '\n'.join(out) + '\n')
    print('done', who, shard, len(rows), 'bad', bad)


main()
