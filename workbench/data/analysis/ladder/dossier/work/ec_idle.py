# Scratch (diag-economy): how long since a dragon last ate (or was born), and what it sees. Followed side only,
# dragons of length 2 and 3, rounds 0-300. One counter per layout:
#   (band, idle bucket, view) -> turns, pearls eaten on the turn, deaths before its next turn, turns that end the
#   idle spell by a meal. idle = rounds since its last meal or its birth: 0 0-3, 1 4-10, 2 11-25, 3 26-60, 4 61+.
#   view: 0 no pearl in the 7 by 7 view, 1 a pearl in view.
# and ('life', band of birth, bucket of rounds lived, ended by death 1 / still alive at the end or at 4+ 0).
# Usage: python3 data/analysis/ladder/dossier/work/ec_idle.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def ib(n):
    return 0 if n <= 3 else 1 if n <= 10 else 2 if n <= 25 else 3 if n <= 60 else 4


def scan(row, acc, wins):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
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
    focal = row['side']
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    fed = {i: 0 for i in bodies}
    pv = [0] * N
    last = {}
    rnd, actor, band = 0, None, 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            band = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
        elif k == 1:
            actor = p.i32(0)
            b = bodies.get(actor)
            last.pop(actor, None)
            if b is None or sd[actor] != 0 or len(b) > 3 or band == 2:
                continue
            key = (band, ib(rnd - fed[actor]), 1 if pv[b[0]] else 0)
            v = acc[key]
            v[0] += 1
            last[actor] = v
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                for z in win[c]:
                    pv[z] += 1
            else:
                for z in win[c]:
                    pv[z] -= 1
                if sd[actor] == 0:
                    v = last.get(actor)
                    if v is not None:
                        v[1] += 1
                        if rnd - fed[actor] > 3:
                            v[3] += 1
                    fed[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
            fed[c] = rnd
            fed[a] = rnd
        elif k == 11:
            i = p.i32(0)
            if sd[i] == 0:
                v = last.pop(i, None)
                if v is not None:
                    v[2] += 1
            bodies.pop(i)


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'ec_idle-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'ec_idle-O1.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'ec_idle-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'ec_idle-R1.jsonl').write_text(body)
    else:
        Path(OUT + 'ec_idle-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    accs, bad, wins = {}, [], {}
    for n, r in enumerate(rows):
        a = accs.setdefault(r['layout'], defaultdict(lambda: [0, 0, 0, 0]))
        try:
            scan(r, a, wins)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), 'bad', len(bad), flush=True)
    out = [json.dumps(dict(who=who, layout=lay, acc=[list(kk) + v for kk, v in sorted(a.items())]), separators=(',', ':')) for lay, a in sorted(accs.items())]
    save('test' if limit else who + str(shard), '\n'.join(out) + '\n')
    print('done', who, shard, len(rows), 'bad', bad)


main()
