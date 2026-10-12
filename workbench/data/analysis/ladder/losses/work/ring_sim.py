# Scratch (queen-ring brief, question 1): which (cycle, length) pairs keep a dragon's head sealed at every turn end.
# Rules used (rules/movement.md, execution-order.md): a dragon must move at least one step a turn, the first
# ceil(L / 4) steps are free, and the tile of its own tail is blocked for the step.
# Seal: no free tile next to the head can be reached from open water without crossing the dragon's own body.
# Part A: the red-team cycle (6 by 4, length 23, 6 steps a turn), walked cell by cell, flood test at every stop.
# Part B: every Hamiltonian cycle of every w by h block up to an area, lengths cells-1, cells-2, cells-3.
# Part C: the same blocks against straight kelp (one side, a corner, a corridor).
# Part D: every simple cycle of any shape up to a number of cells (smallest sealed cycle without kelp).
# Usage: python3 data/analysis/ladder/losses/work/ring_sim.py [area cap for B, default 36] [cell cap for D, default 20]
import sys
from collections import deque, Counter

WALL = {'none': lambda n: False,
        'one side': lambda n: n[1] < 0,
        'corner': lambda n: n[1] < 0 or n[0] < 0}
solid = WALL['none']
ROWS = None  # corridor: number of rows between two kelp lines


def is_solid(n):
    return solid(n) or (ROWS is not None and (n[1] < 0 or n[1] >= ROWS))


def nbrs(c):
    x, y = c
    return ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))


def outside(S):
    """Open water connected to the far field (tiles of S and kelp-side tiles excluded)."""
    xs = [c[0] for c in S]
    ys = [c[1] for c in S]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    out = set()
    q = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
         if (x in (x0, x1) or y in (y0, y1)) and not is_solid((x, y))]
    while q:
        c = q.pop()
        if c in out or c in S or is_solid(c) or not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1):
            continue
        out.add(c)
        q.extend(nbrs(c))
    return out


def stops_for(C, gap):
    """Head at C[i], body on the L = len(C) - gap cells behind it, free cells C[i+1..i+gap]. Stop i is good when the
    head and every free cell have no neighbour in open water. Returns L, free steps, good stops, largest step needed."""
    N = len(C)
    out = outside(set(C))
    inner = [all(n not in out for n in nbrs(c)) for c in C]
    L = N - gap
    free = (L + 3) // 4
    good = [i for i in range(N) if all(inner[(i + k) % N] for k in range(gap + 1))]
    if not good:
        return L, free, good, None
    worst = max((good[(j + 1) % len(good)] - good[j] - 1) % N + 1 for j in range(len(good)))
    return L, free, good, worst


def simulate(C, gap, plan=None, laps=3):
    """Independent check: move the body one cell at a time (dies if the next cell is in its body, tail included) and
    at every turn end flood from the free tiles next to the head through everything that is not her body.
    plan: None = from each good stop go to the farthest good stop within the free steps; an int = that many steps
    every turn from index plan_start. Returns (turn ends checked, turn ends exposed, stop cells, free cells seen)."""
    N = len(C)
    S = set(C)
    L, free, good, worst = stops_for(C, gap)
    xs = [c[0] for c in S]
    ys = [c[1] for c in S]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if plan is None:
        i, fixed = good[0], None
    else:
        i, fixed = plan
    goodset = set(good)
    body = deque(C[(i - k) % N] for k in range(L - 1, -1, -1))
    checked = bad = 0
    stops, frees = [], set()
    turns = laps * N if fixed else laps * max(1, len(good))
    for turn in range(turns):
        occ = set(body)
        head = body[-1]
        seen = set()
        q = [n for n in nbrs(head) if n not in occ and not is_solid(n)]
        exposed = False
        while q:
            c = q.pop()
            if c in seen:
                continue
            seen.add(c)
            if not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1):
                exposed = True
                break
            q.extend(n for n in nbrs(c) if n not in occ and n not in seen and not is_solid(n))
        checked += 1
        bad += exposed
        if head not in stops:
            stops.append(head)
        if not exposed:
            frees |= seen
        k = fixed if fixed else max(d for d in range(1, free + 1) if (i + d) % N in goodset)
        assert k <= free
        for d in range(k):
            nxt = C[(i + 1) % N]
            assert nxt not in body, 'hit itself'
            body.append(nxt)
            body.popleft()
            i = (i + 1) % N
    return checked, bad, stops, frees


def hamilton(w, h):
    """Every Hamiltonian cycle of the w by h block, once each: (0,0) -> (1,0) -> ... -> (0,1) -> (0,0)."""
    N = w * h
    start, end = (0, 0), (0, 1)
    if h < 2 or N % 2:
        return []
    path = [start, (1, 0)]
    used = {start, (1, 0)}
    res = []
    cells = [(x, y) for y in range(h) for x in range(w)]

    def ok(cur):
        for c in cells:
            if c in used:
                continue
            k = 1 if c == end else 0
            for n in nbrs(c):
                if 0 <= n[0] < w and 0 <= n[1] < h and (n not in used or n == cur):
                    k += 1
            if k < 2:
                return False
        return True

    def go(cur):
        if len(path) == N - 1:
            if end in nbrs(cur):
                res.append(path + [end])
            return
        for n in nbrs(cur):
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in used and n != end:
                used.add(n)
                path.append(n)
                if ok(n):
                    go(n)
                path.pop()
                used.discard(n)

    go((1, 0))
    return res


def draw(C, stops=(), frees=()):
    S = set(C)
    xs = [c[0] for c in S]
    ys = [c[1] for c in S]
    order = {c: k for k, c in enumerate(C)}
    lines = []
    for y in range(min(ys), max(ys) + 1):
        row = ''
        for x in range(min(xs), max(xs) + 1):
            c = (x, y)
            row += ('%3d' % order[c] if c in S else '  .') + ('H' if c in stops else 'f' if c in frees else ' ')
        lines.append('     ' + row)
    return '\n'.join(lines)


def part_a():
    print('== A. red-team cycle (meow-redteam/bot/main.cpp:105-106), 6 by 4, 24 cells ==')
    RX = [3, 3, 4, 5, 5, 4, 4, 5, 5, 4, 3, 3, 2, 2, 1, 0, 0, 1, 1, 0, 0, 1, 2, 2]
    RY = [1, 0, 0, 0, 1, 1, 2, 2, 3, 3, 3, 2, 2, 3, 3, 3, 2, 2, 1, 1, 0, 0, 0, 1]
    C = list(zip(RX, RY))
    assert len(set(C)) == 24 and all(abs(C[k][0] - C[(k + 1) % 24][0]) + abs(C[k][1] - C[(k + 1) % 24][1]) == 1 for k in range(24))
    for gap in (1, 2, 3):
        L, free, good, worst = stops_for(C, gap)
        print('   length %d: free steps %d, good stops (cycle index) %s, largest step needed %s -> %s'
              % (L, free, good, worst, 'SEALED LOOP' if good and worst <= free else 'no sealed loop'))
    for start in range(6):
        checked, bad, stops, frees = simulate(C, 1, plan=(start, 6), laps=3)
        print('   length 23, 6 steps a turn from index %d: %d turn ends walked, %d exposed; stops %s; tiles ever free at a sealed stop %s'
              % (start, checked, bad, stops, sorted(frees)))
    for k in (1, 2, 3, 4, 5):
        checked, bad, stops, frees = simulate(C, 1, plan=(5, k), laps=1)
        print('   length 23, %d steps a turn from index 5: %d turn ends walked, %d exposed' % (k, checked, bad))
    checked, bad, stops, frees = simulate(C, 1, plan=(5, 6), laps=3)
    print(draw(C, stops, frees))
    print('   (number = cycle index, H = head at a turn end, f = the one free tile at a turn end)')


def part_b(area, walls, label, min_h):
    global solid, ROWS
    print('\n== %s. Hamiltonian cycles of w by h blocks, area <= %d, kelp: %s ==' % (label, area, walls))
    print('   block cells cycles | per length (cells-1, -2, -3): length, free steps, cycles with a sealed loop, smallest largest-step; walked check')
    best = []
    for h in range(min_h, 13):
        for w in range(2, 13):
            if w * h > area or w * h % 2 or (walls in ('none', 'corner') and w < h):
                continue
            if walls == 'corridor':
                solid, ROWS = WALL['none'], h
            else:
                solid, ROWS = WALL[walls], None
            cyc = hamilton(w, h)
            if not cyc:
                continue
            cols = []
            for gap in (1, 2, 3):
                n_ok, slack, example = 0, None, None
                turns = exposed = 0
                for C in cyc:
                    L, free, good, worst = stops_for(C, gap)
                    if good and worst <= free:
                        n_ok += 1
                        a, b, stops, frees = simulate(C, gap)
                        turns += a
                        exposed += b
                        if slack is None or worst < slack:
                            slack, example = worst, (C, stops, frees)
                L = w * h - gap
                cols.append('L%d f%d: %d sealed%s' % (L, (L + 3) // 4, n_ok,
                            (', step %d, walked %d turn ends %d exposed' % (slack, turns, exposed)) if n_ok else ''))
                if n_ok:
                    best.append((L, w, h, gap, n_ok, example))
            print('   %2dx%-2d %3d %5d | %s' % (w, h, w * h, len(cyc), ' | '.join(cols)))
    best.sort(key=lambda t: t[:4])
    if best:
        L, w, h, gap, n_ok, (C, stops, frees) = best[0]
        print('   smallest: %d by %d, length %d (%d of the cycles), kelp %s' % (w, h, L, n_ok, walls))
        print(draw(C, stops, frees))
    else:
        print('   none sealed')
    solid, ROWS = WALL['none'], None
    return best


def part_d(cap):
    print('\n== D. every simple cycle of at most %d cells, any shape, no kelp ==' % cap)
    known = {4: 1, 6: 2, 8: 7, 10: 28, 12: 124, 14: 588, 16: 2938, 18: 15268, 20: 81826, 22: 449572, 24: 2521270}
    OFF, WD = 32, 64
    used = bytearray(WD * WD)
    path = [OFF, OFF + 1]
    used[OFF] = used[OFF + 1] = 1
    TGT = WD + OFF
    counts = Counter()
    tested = Counter()
    sealed = {}
    moves = ((0, -1, -WD), (1, 0, 1), (0, 1, WD), (-1, 0, -1))

    def found():
        n = len(path) + 1
        counts[n] += 1
        xs = [k % WD for k in path]
        ys = [k // WD for k in path]
        if (max(xs) - min(xs) - 1) * (max(ys) - 1) < 4:  # enclosed tiles lie strictly inside the bounding box; with fewer than 4 no loop is possible
            return
        C = [(k % WD - OFF, k // WD) for k in path] + [(0, 1)]
        tested[n] += 1
        for gap in (1, 2, 3):
            L, free, good, worst = stops_for(C, gap)
            if good and worst <= free:
                a, b, stops, frees = simulate(C, gap)
                assert b == 0
                sealed.setdefault((n, gap), []).append((C, stops, frees))

    def go(x, y, key, n):
        for dx, dy, dk in moves:
            nx, ny = x + dx, y + dy
            if ny < 0 or (ny == 0 and nx <= 0):
                continue
            nk = key + dk
            if nk == TGT:
                found()
                continue
            if used[nk] or abs(nx) + abs(ny - 1) > cap - n - 1:
                continue
            used[nk] = 1
            path.append(nk)
            go(nx, ny, nk, n + 1)
            path.pop()
            used[nk] = 0

    go(1, 0, OFF + 1, 2)
    for n in sorted(counts):
        print('   %2d cells: %7d cycles (known count of self-avoiding polygons %s), %6d with room for 4 enclosed tiles, sealed: %s'
              % (n, counts[n], known.get(n), tested[n],
                 ', '.join('length %d: %d' % (n - g, len(sealed[(n, g)])) for g in (1, 2, 3) if (n, g) in sealed) or 'none'))
    for (n, gap) in sorted(sealed):
        shapes = Counter()
        first = {}
        for C, stops, frees in sealed[(n, gap)]:
            S = set(C)
            x0 = min(c[0] for c in S)
            y0 = min(c[1] for c in S)
            keyset = frozenset((c[0] - x0, c[1] - y0) for c in S)
            shapes[keyset] += 1
            first.setdefault(keyset, (C, stops, frees))
        print('   %d cells, length %d: %d sealed cycles on %d distinct tile sets (rotations and mirrors counted separately)'
              % (n, n - gap, len(sealed[(n, gap)]), len(shapes)))
        for keyset, k in shapes.most_common(3):
            C, stops, frees = first[keyset]
            xs = [c[0] for c in keyset]
            ys = [c[1] for c in keyset]
            print('   tile set %d by %d, %d cycles; one of them:' % (max(xs) + 1, max(ys) + 1, k))
            print(draw(C, stops, frees))


def main():
    area = int(sys.argv[1]) if len(sys.argv) > 1 else 36
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    sys.setrecursionlimit(10000)
    part_a()
    if area:
        part_b(area, 'none', 'B', 3)
        part_b(min(area, 30), 'one side', 'C1', 2)
        part_b(min(area, 30), 'corner', 'C2', 2)
        part_b(min(area, 30), 'corridor', 'C3', 2)
    if cap:
        part_d(cap)


main()
