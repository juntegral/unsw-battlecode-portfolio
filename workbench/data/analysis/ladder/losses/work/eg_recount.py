# Scratch (early-growth brief): independent recount of the Tower Defense numbers, straight from the replays.
# Different from eg_scan/eg_home on purpose: the start room is taken as the 7 by 7 block of coordinates round the start heads
# (not by path distance), and heads are read at the END of each round (not at turn start). Prints only.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
from statistics import median
from pathlib import Path

per = json.loads(Path('data/analysis/ladder/losses/split/per-game.json').read_text())
td = [r for r in per if r['map_key'].startswith('Tower')]
print('Tower Defense main games in per-game.json:', len(td), dict(Counter(r['group'] for r in td)), dict(Counter(r['result'] for r in td)))
inside = {'u': Counter(), 't': Counter()}
total = {'u': Counter(), 't': Counter()}
near = {'u': Counter(), 't': Counter()}
first_out = {'u': [], 't': []}
for r in td:
    root = replay.load(Path(r['replay'])).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    heads, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(heads)
            heads[i] = (int(q[3]), int(q[4]))
            teams[i] = 'AB'[int(q[1])]
    ours = r['our_side']
    box = {}
    for s in 'ut':
        hs = [heads[i] for i in heads if (teams[i] == ours) == (s == 'u')]
        xs, ys = [h[0] for h in hs], [h[1] for h in hs]
        assert max(xs) - min(xs) == 0 and max(ys) - min(ys) == 3, (r['game'], hs)
        # start heads sit at column offset 3 and rows 2 and 5 of the block when the block is on the left; mirrored on the right
        left = xs[0] < W // 2
        x0 = xs[0] - 3
        y0 = min(ys) - 2 if left else min(ys) - 1
        box[s] = (x0, y0)
    out = {'u': None, 't': None}
    rnd, started = 0, False

    def tally(n):
        for i, h in heads.items():
            s = 'u' if teams[i] == ours else 't'
            x0, y0 = box[s]
            b = 'r0-59' if n <= 59 else 'r60-89' if n <= 89 else 'r90-120'
            total[s][b] += 1
            ins = x0 <= h[0] <= x0 + 6 and y0 <= h[1] <= y0 + 6
            inside[s][b] += int(ins)
            if not ins and out[s] is None:
                out[s] = n
            if ins:
                # the 3 by 3 corner of the block nearest the board centre (W/2, H/2)
                cx = x0 + 6 if x0 + 3 < W // 2 else x0
                cy = y0 + 6 if y0 + 3 < H // 2 else y0
                near[s][b] += int(abs(h[0] - cx) <= 2 and abs(h[1] - cy) <= 2)
    for ev in root.pointer(3):
        k = ev.u16(0)
        p = ev.pointer(0)
        if k == 0:
            if started:
                tally(rnd)
            started = True
            rnd = p.i32(0)
            if rnd > 120:
                break
        elif k == 9:
            i = p.i32(0)
            heads[i] = tuple(replay.point(p.pointer(0)))
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                heads[i] = tuple(replay.point(list(p.pointer(z))[0]))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            heads.pop(p.i32(0))
    for s in 'ut':
        first_out[s].append(out[s])
for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
    got = sorted(x for x in first_out[s] if x is not None)
    print(name, 'first round end with a head outside the block: median', median(got) if got else None, 'min', got[0] if got else None,
          '| none by r59:', sum(1 for x in first_out[s] if x is None or x > 59), '| none by r120:', sum(1 for x in first_out[s] if x is None), 'of', len(td))
    for b in ('r0-59', 'r60-89', 'r90-120'):
        print('   %-8s heads at round end %6d | inside the block %5.1f%% (%d) | of those in the 3x3 corner nearest the centre %5.1f%% (%d)' % (
            b, total[s][b], 100.0 * inside[s][b] / total[s][b], inside[s][b], 100.0 * near[s][b] / max(1, inside[s][b]), near[s][b]))
