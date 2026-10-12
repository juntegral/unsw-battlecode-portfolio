"""Scratch (diag-wipeout): rounds 0-60 on two-dragon starts (total length 6 or less, 1200 cells or fewer): what the
queen (lowest starting id), the other starter and the later dragons of each side do. Turns, pearls eaten, and on turns
that begin with an enemy head within 5 tiles: ended farther from it, nearer, same, rammed it, died otherwise.
Usage: python3 data/analysis/ladder/dossier/work/wo_queen.py <O|L|R> [nostripes] [last round]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict, Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1')


def jobs(src):
    out = []
    if src == 'O':
        for label in LABELS:
            folder = Path('data/online/smoke') / (label + '-new')
            if not folder.is_dir():
                continue
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if rp.exists():
                    out.append((rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us' or r['cells'] > 1200:
                continue
            st = r['all_starting_dragons']['us']
            if len(st) != 2 or sum(d['length'] for d in st) > 6:
                continue
            rp = Path(r['replay'])
            out.append((rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
    return out


def scan(path, j, team, last):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    if W * H > 1200:
        return None
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    if sum(1 for i in bodies if side(i) == 0) != 2 or sum(len(b) for i, b in bodies.items() if side(i) == 0) > 6:
        return None
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starters = set(bodies)

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def role(i):
        return 'queen' if i in queens else 'starter' if i in starters else 'later'

    T = Counter()
    rnd, actor = -1, None
    cur = None

    def close():
        nonlocal cur
        if cur is None:
            return
        i, key = cur['i'], cur['key']
        if cur['foe'] is not None:
            if i not in bodies:
                oc = 'rammed it' if cur['ram'] else 'died'
            else:
                d1 = gap(bodies[i][0], cur['foe'])
                oc = 'farther' if d1 > cur['d0'] else 'nearer' if d1 < cur['d0'] else 'same'
            T[key + ('foe5', oc)] += 1
            T[key + ('foe5', 'n')] += 1
            rel = 'longer' if cur['Lf'] > cur['L'] else 'shorter' if cur['Lf'] < cur['L'] else 'equal'
            T[key + ('foe5 ' + rel, oc)] += 1
            T[key + ('foe5 ' + rel, 'n')] += 1
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
            if rnd > last:
                break
        elif k == 1:
            close()
            actor = p.i32(0)
            b = bodies[actor]
            s = side(actor)
            key = (s, role(actor))
            T[key + ('turns', 'n')] += 1
            best = None
            for z, bb in bodies.items():
                if side(z) != s:
                    g = gap(b[0], bb[0])
                    if g <= 5 and (best is None or g < best[0]):
                        best = (g, bb[0], len(bb))
            cur = dict(i=actor, key=key, L=len(b), foe=best[1] if best else None, d0=best[0] if best else None,
                       Lf=best[2] if best else 0, ram=False)
        elif k == 3:
            if not p.u32(0) and actor is not None:
                T[(side(actor), role(actor), 'eats', 'n')] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            T[(side(parent), role(parent), 'splits', 'n')] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            T[(side(i), role(i), 'deaths', 'n')] += 1
            if reason == 3 and i == actor and cur is not None:
                cur['ram'] = True
            bodies.pop(i)
    close()
    return T, W * H


def main():
    src = sys.argv[1]
    nostripes = len(sys.argv) > 2 and sys.argv[2] == 'nostripes'
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    cls = {}
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            cls[g['gid']] = 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'
    tot = defaultdict(Counter)
    games = Counter()
    for path, j, team in jobs(src):
        if nostripes and j['mapName'] == 'Stripes':
            continue
        res = scan(path, j, team, last)
        if res is None:
            continue
        T, cells = res
        for grp in (cls[j['id']], 'ALL', 'ALL queen rules on (over 600 cells)' if cells > 600 else 'ALL queen rules off (600 cells or fewer)'):
            games[grp] += 1
            tot[grp].update(T)
    print(src, 'rounds 0-%d' % last, 'no Stripes' if nostripes else '', dict(games))
    for grp in ('OUT', 'KILL', 'REST', 'ALL', 'ALL queen rules on (over 600 cells)', 'ALL queen rules off (600 cells or fewer)'):
        T = tot[grp]
        n = max(games[grp], 1)
        print(grp, games[grp])
        for s, nm in ((0, 'us'), (1, 'them')):
            for rl in ('queen', 'starter', 'later'):
                t = T[(s, rl, 'turns', 'n')]
                f = T[(s, rl, 'foe5', 'n')]
                line = '   %-4s %-7s turns %.1f a game, eats %.2f a game (%.1f/100 turns), splits %.2f, deaths %.2f | enemy head within 5 on %.0f%% of turns: farther %.0f%% nearer %.0f%% same %.0f%% rammed it %.1f%% died %.1f%%' % (
                    nm, rl, t / n, T[(s, rl, 'eats', 'n')] / n, 100 * T[(s, rl, 'eats', 'n')] / max(t, 1), T[(s, rl, 'splits', 'n')] / n, T[(s, rl, 'deaths', 'n')] / n,
                    100 * f / max(t, 1), 100 * T[(s, rl, 'foe5', 'farther')] / max(f, 1), 100 * T[(s, rl, 'foe5', 'nearer')] / max(f, 1),
                    100 * T[(s, rl, 'foe5', 'same')] / max(f, 1), 100 * T[(s, rl, 'foe5', 'rammed it')] / max(f, 1), 100 * T[(s, rl, 'foe5', 'died')] / max(f, 1))
                print(line)
                for rel in ('longer', 'equal', 'shorter'):
                    f2 = T[(s, rl, 'foe5 ' + rel, 'n')]
                    if f2 >= 20:
                        print('          enemy head %s: %d turns, farther %.0f%% nearer %.0f%% rammed it %.1f%% died %.1f%%' % (
                            rel, f2, 100 * T[(s, rl, 'foe5 ' + rel, 'farther')] / f2, 100 * T[(s, rl, 'foe5 ' + rel, 'nearer')] / f2,
                            100 * T[(s, rl, 'foe5 ' + rel, 'rammed it')] / f2, 100 * T[(s, rl, 'foe5 ' + rel, 'died')] / f2))


main()
