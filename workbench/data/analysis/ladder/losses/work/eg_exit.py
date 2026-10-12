# Scratch (early-growth brief): Tower Defense after round 60. Are our dragons at the exit mouth busy with a pearl, or held with nothing in reach?
# Start room = 7 by 7 coordinate block (as in eg_recount.py); exit mouth = the block corner farthest from the board centre, 2 by 2. Prints only.
import sys, json
from collections import Counter
from pathlib import Path

games = []
for n in range(4):
    for line in Path('data/analysis/ladder/losses/work/eg_rows-%d.jsonl' % n).read_text().splitlines():
        g = json.loads(line)
        if g['map_key'].startswith('Tower'):
            games.append(g)


def pct(a, b):
    return '%5.1f%% (%d/%d)' % (100.0 * a / b, a, b) if b else '  n/a'


for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
    for lo, hi in ((0, 29), (30, 59), (60, 74), (75, 89), (90, 120)):
        rows = []
        for g in games:
            W, H = g['w'], g['h']
            st = [t[6] for t in g['turns'] if t[1] == s and t[0] == 0 and t[4] == 1]
            xs, ys = [c % W for c in st], [c // W for c in st]
            left = xs[0] < W // 2
            x0 = xs[0] - 3
            y0 = min(ys) - 2 if left else min(ys) - 1
            ex = x0 if left else x0 + 6
            ey = y0 if left else y0 + 6
            for t in g['turns']:
                if t[1] != s or not lo <= t[0] <= hi:
                    continue
                x, y = t[6] % W, t[6] // W
                ins = x0 <= x <= x0 + 6 and y0 <= y <= y0 + 6
                mouth = ins and abs(x - ex) <= 1 and abs(y - ey) <= 1
                rows.append((ins, mouth, t))
        ins = [r for r in rows if r[0]]
        mouth = [r for r in rows if r[1]]
        nop = [r for r in mouth if r[2][10] is None or r[2][10] > 7]
        print('%s r%3d-%3d turns %5d | in the room %s | at the 2x2 exit corner %s | of those with no known pearl within 7 steps %s | ate at the corner %d' % (
            name, lo, hi, len(rows), pct(len(ins), len(rows)), pct(len(mouth), len(ins)), pct(len(nop), len(mouth)),
            sum(r[2][19] for r in mouth)))
