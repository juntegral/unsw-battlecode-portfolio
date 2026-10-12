# Scratch (diag-drops): recount of the leader-round step by another method. Written apart from dr_scan.py: whole-board state
# as (x, y) lists, grid neighbours on the torus with walls and portals ignored, every 4th game of each side.
# A turn counts when the dragon is 2 or 3 long, not its side's first dragon, a pearl lies on one of the 4 grid neighbours
# of its head and a longer team mate's head is within 9 tiles of that pearl (mate near) or none is (no mate).
# Not taken = no pearl was removed from a neighbour tile during the turn. Phases by round: 101-150, 151-200, 201-300, 301-350, 351-400.
# Usage: python3 data/analysis/ladder/dossier/work/dr_recount.py
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
from pathlib import Path


def one(row, out):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    size = 'big' if w * h > 1200 else 'small'
    body, team = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(body)
            body[i] = [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2]))]
            team[i] = int(q[1])
    focal = 'AB'.index(row['side'])
    first = {t: min(i for i in body if team[i] == t) for t in (0, 1)}
    pearls = set()
    rnd, cur = 0, None

    def close():
        if cur is None:
            return
        key, near = cur
        taken = any(c not in pearls for c in near)
        out[key + ('n',)] += 1
        out[key + ('miss',)] += 0 if taken else 1

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            cur = None
            rnd = p.i32(0)
        elif k == 1:
            close()
            cur = None
            a = p.i32(0)
            L = len(body[a])
            if 101 <= rnd <= 400 and L <= 3 and a != first[team[a]]:
                x, y = body[a][0]
                near = [c for c in (((x + 1) % w, y), ((x - 1) % w, y), (x, (y + 1) % h), (x, (y - 1) % h)) if c in pearls]
                if near:
                    mate = False
                    for j, b in body.items():
                        if team[j] == team[a] and j != a and len(b) > L:
                            for c in near:
                                dx, dy = abs(b[0][0] - c[0]), abs(b[0][1] - c[1])
                                if min(dx, w - dx) + min(dy, h - dy) <= 9:
                                    mate = True
                    ph = 0 if rnd <= 150 else 1 if rnd <= 200 else 2 if rnd <= 300 else 3 if rnd <= 350 else 4
                    who = row['who'] if team[a] == focal else row['who'] + 'O'
                    cur = ((who, size, ph, 'mate near' if mate else 'no mate'), near)
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = body[i]
            if b[0] != hd:
                b.insert(0, hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                body[i] = [replay.point(c) for c in p.pointer(z)]
                team[i] = p.u16(8)
        elif k == 11:
            body.pop(p.i32(0))
    close()


def main():
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    out = Counter()
    n = Counter()
    for who in 'OR':
        sub = sorted([r for r in rows if r['who'] == who], key=lambda r: r['game'])[::4]
        for r in sub:
            one(r, out)
            n[who] += 1
    print('games', dict(n))
    for size in ('big', 'small'):
        for cls in ('mate near', 'no mate'):
            for who in ('O', 'R', 'OO', 'RO'):
                cells = []
                for ph in range(5):
                    k = (who, size, ph, cls)
                    cells.append('%5.1f (%d)' % (100 * out[k + ('miss',)] / max(1, out[k + ('n',)]), out[k + ('n',)]))
                print('%-5s %-9s %-3s not taken %% by phase: %s' % (size, cls, who, ' | '.join(cells)))


main()
