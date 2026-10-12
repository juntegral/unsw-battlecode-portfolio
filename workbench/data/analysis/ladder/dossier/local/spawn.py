#!/usr/bin/env python3
"""Matched local spawn counts; exact countdowns from replay kind-2 events.

Cases are side/tile/round opportunities (any qualifying head), at round start
AFTER spawning and BEFORE turns. Steps include every substep of that round by
qualifying dragons. Countdown 1/2 means an attempt at r+1/r+2. Distances use
open edges and portals. Spawn/death/opportunity counts cover raw r0..300;
birth/eating windows are inclusive. Eating counts use consumption rounds;
birth-round eating and wait use birth cohorts followed to the game's end.
Blocked attempts: empty-entry head vs trailing segment, within current length
L rounds, with split provenance retained; other includes entry after a meal
and any segment without a recent empty entry. Rates are per-game, paired means
on games with denominators in BOTH arms; NA means no such games. Early endings
carry terminal standings to checkpoints, but never invent opportunities.
Only files next to this script are written; no games or network are started.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter, deque
from pathlib import Path
from replay_format import Message, load, point
from count_local import Geo

HERE = Path(__file__).resolve().parent
RUNS = Path('~/meow-redteam/solo/runs')
MAPS = Path('~/meow-redteam/maps')
CACHE = HERE/'spawn-rows.jsonl'
WINDOWS = {'early': (0, 100), 'mid': (101, 300), 'all': (0, 10**9)}


def read(path):
    binary = HERE.parent/'target/tg_unpack'
    if not binary.is_file():
        return load(path).root()
    blob = path.read_bytes()
    if blob[:2] == b'\x1f\x8b':
        blob = gzip.decompress(blob)
    raw = subprocess.run([str(binary)], input=blob, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, check=True).stdout
    return Message(raw).root()


def inventory(arm, substring):
    if Path(arm).name != arm or arm in ('.', '..') or not (RUNS/arm).is_dir():
        raise ValueError(f'unknown arm directory: {arm}')
    out = {}
    for path in sorted((RUNS/arm).glob('*/game.replay')):
        m = re.fullmatch(r'(.+)-seed(\d+)-side([01])', path.parent.name)
        if m and (not substring or substring in m[1]):
            out[m[1], int(m[2]), int(m[3])] = path.resolve()
    return out


def scan(path, key, map_path):
    slug, seed, own = key
    root = read(path)
    result = root.pointer(4)
    assert result is not None and result.bit(0), 'unfinished replay'
    w = h = 0
    raw, teams, bodies, parameters = [], {}, {}, {}
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q[0] == 'TILE':
            x, y, lo, hi = map(int, q[1:5])
            parameters[y*w+x] = (lo, hi)
        elif q[0] == 'DRAGON':
            i = len(bodies)
            teams[i] = int(q[1])
            bodies[i] = deque((int(q[4+2*k])*w+int(q[3+2*k]), -999, False)
                              for k in range(int(q[2])))
    true = {}
    for line in map_path.read_text().splitlines():
        q = line.split('#', 1)[0].split()
        if q and q[0] == 'TILE':
            x, y, lo, hi = map(int, q[1:5])
            true[y*w+x] = (lo, hi)
    assert true == parameters, 'replay/map TILE parameters differ'
    g = Geo(w, h, raw)
    side = lambda i: int(teams[i] != own)
    tile = lambda p: p[1]*w+p[0]
    active = {c for c, (_, hi) in parameters.items() if hi > 0}
    due, schedules, born_at = {}, {}, set()
    rnd, actor = -1, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 2, 3):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
        elif k == 2:
            c, v = tile(point(p.pointer(0))), p.i32(0)
            assert c in active and parameters[c][0] <= v <= parameters[c][1]
            if rnd == -1:
                assert c not in due
            else:
                assert due[c] == rnd, ('countdown mismatch', rnd, c, due.get(c))
            due[c] = rnd+v
            schedules.setdefault(due[c], set()).add(c)
        elif actor is None and p.u32(0):
            born_at.add((rnd, tile(point(p.pointer(0)))))
    assert set(due) == active, 'missing initial countdowns'
    last = rnd
    stats = [Counter(), Counter()]
    occ = {}
    for i, body in bodies.items():
        for seg in body:
            assert seg[0] not in occ
            occ[seg[0]] = i
    present, snaps = {}, {}
    rnd, actor, just_ate = -1, None, None
    opportunities, step_hits = {}, set()
    setup_needed = False
    checks = Counter()

    def snapshot():
        return [sum(side(i) == s for i in bodies) for s in (0, 1)]

    def finish_round():
        if rnd < 0:
            return
        for (s, c, countdown), ids in opportunities.items():
            st = stats[s]
            st[f'case{countdown}'] += 1
            st[f'on{countdown}'] += int((s, c, countdown) in step_hits)
        snaps[rnd] = snapshot()
        opportunities.clear()
        step_hits.clear()

    def setup():
        nonlocal setup_needed
        setup_needed = False
        if rnd > 300:
            return
        heads = [{b[0][0]: i for i, b in bodies.items() if side(i) == s} for s in (0, 1)]
        for countdown in (1, 2):
            if rnd+countdown > last:
                continue
            for c in schedules.get(rnd+countdown, ()):
                if c in occ or c in present:
                    continue
                # Exclude a reset in between (interval-1/2 tiles can have repeated attempts).
                if any(c in schedules.get(rr, ()) for rr in range(rnd+1, rnd+countdown)):
                    continue
                adj = set(g.adj[c])-{c}
                dist2 = {t for a in adj for t in g.adj[a]}-adj-{c}
                for s in (0, 1):
                    ids = {heads[s][a] for a in adj if a in heads[s]}
                    if ids:
                        opportunities[s, c, countdown] = ids
                    if countdown == 2 and not ids and c not in heads[s] and any(t in heads[s] for t in dist2):
                        stats[s]['two_cases'] += 1
                        stats[s]['two_born'] += int((rnd+2, c) in born_at)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 2, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if setup_needed:
                setup()
            finish_round()
            rnd, actor, just_ate = p.i32(0), None, None
            setup_needed = True
        elif k == 1:
            if setup_needed:
                setup()
            actor, just_ate = p.i32(0), None
            if rnd <= 300:
                stats[side(actor)]['turns'] += 1
        elif k == 2 and rnd >= 0:
            c = tile(point(p.pointer(0)))
            assert actor is None
            if (rnd, c) in born_at:
                assert c not in occ
                checks['born'] += 1
            elif c in occ:
                i = occ[c]
                b = bodies[i]
                entry = next(z for z in b if z[0] == c)
                empty = entry[2] and 1 <= rnd-entry[1] <= len(b)
                category = ('head' if b[0][0] == c else 'trail') if empty else 'other'
                if rnd <= 300:
                    stats[side(i)]['blocked'] += 1
                    stats[side(i)]['blocked_'+category] += 1
                checks['blocked'] += 1
            else:
                assert c in present, ('free failed spawn', rnd, c)
                checks['pearl_blocked'] += 1
        elif k == 3:
            c = tile(point(p.pointer(0)))
            if p.u32(0):
                assert c not in present
                natural = actor is None
                present[c] = (rnd, natural)
                if natural:
                    assert (rnd, c) in born_at
                    for win, (lo, hi) in WINDOWS.items():
                        if lo <= rnd <= hi:
                            for st in stats:
                                st['born_'+win] += 1
            else:
                birth, natural = present.pop(c)
                assert actor is not None
                just_ate = c
                if natural:
                    st = stats[side(actor)]
                    for win, (lo, hi) in WINDOWS.items():
                        if lo <= rnd <= hi:
                            st['eaten_'+win] += 1
                        if lo <= birth <= hi:
                            st['cohort_eaten_'+win] += 1
                            st['instant_'+win] += int(birth == rnd)
                            st['wait_'+win] += rnd-birth
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
            b = bodies[i]
            if b[0][0] != hd:
                was_empty = hd != just_ate and hd not in present
                b.appendleft((hd, rnd, was_empty))
                assert hd not in occ
                occ[hd] = i
                for countdown in (1, 2):
                    op = (side(i), hd, countdown)
                    if i in opportunities.get(op, ()):
                        step_hits.add(op)
                just_ate = None
            while len(b) > 1 and b[-1][0] != tl:
                del occ[b.pop()[0]]
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            old = {z[0]: z for z in bodies[parent]}
            for c in old:
                del occ[c]
            teams[child] = teams[parent] = p.u16(8)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(old[tile(point(x))] for x in p.pointer(z))
                for seg in bodies[i]:
                    assert seg[0] not in occ
                    occ[seg[0]] = i
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if rnd <= 300 and reason in (0, 1, 2):
                stats[side(i)][('wall', 'own', 'another')[reason]] += 1
            for seg in bodies.pop(i):
                del occ[seg[0]]
    if setup_needed:
        setup()
    finish_round()
    winner = result.u16(6) if result.u16(4) == 1 else None
    for z in (0, 1):
        s = int(z != own)
        st = result.pointer(z)
        assert (sum(side(i) == s for i in bodies), max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                sum(len(b) for i, b in bodies.items() if side(i) == s)) == tuple(st.i32(o) for o in (0, 4, 8))
        stats[s]['longest'] = st.i32(4)
        stats[s]['win'] = int(winner == z)
        for rr in (100, 300):
            stats[s][f'alive{rr}'] = snaps.get(rr, snaps[last] if last < rr else None)[s]
        stats[s]['born_0_300'] = stats[s]['born_early']+stats[s]['born_mid']
        assert stats[s]['blocked'] == sum(stats[s]['blocked_'+c] for c in ('head', 'trail', 'other'))
    meta_path = path.with_name('result.json')
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        assert not (meta.get('crash') or meta.get('error') or meta.get('bot_errors')), 'bot error'
        assert meta.get('winner', winner) == winner
        assert meta.get('rounds', last+1) == last+1
    return dict(map=slug, seed=seed, side=own, last_round=last, measures=[dict(s) for s in stats], checks=dict(checks),
                method='exact kind-2 initial/reset countdowns, validated against true map intervals')


def metrics():
    out = []
    count = lambda name: lambda c: c.get(name, 0)
    rate = lambda num, den, scale=100: lambda c: scale*c.get(num, 0)/c[den] if c.get(den) else None
    for tick in (1, 2):
        out += [(f'c{tick} cases/game', count(f'case{tick}')),
                (f'c{tick} step-on %', rate(f'on{tick}', f'case{tick}'))]
    for cat in ('', '_head', '_trail', '_other'):
        name = 'blocked'+cat
        out.append((f'{name}: /game; /100 births', (count(name), rate(name, 'born_0_300'))))
    out.append(('2 away / c2: cases/game; born %', (count('two_cases'), rate('two_born', 'two_cases'))))
    for win in WINDOWS:
        out += [(f'{win}: natural births; eaten /game', (count('born_'+win), count('eaten_'+win))),
                (f'{win}: birth-round eaten %; wait rounds', (rate('instant_'+win, 'born_'+win), rate('wait_'+win, 'cohort_eaten_'+win, 1)))]
    out += [('wins (count)', count('win')), ('alive end r100; r300', (count('alive100'), count('alive300'))),
            ('wall; own; another deaths /1000 turns', tuple(rate(n, 'turns', 1000) for n in ('wall', 'own', 'another'))),
            ('longest at end', count('longest'))]
    return out


def report(selected, arms, hits, counted):
    n = len(selected[arms[0]])
    lines = [f'Matched games/arm={n}; maps={len({r["map"] for r in selected[arms[0]]})}; cache reused={hits}, counted={counted}.',
             'Exact countdowns: replay kind-2 initial/reset events; true .map intervals checked; no mirror inference.',
             'Spawn/block/step/death: r0-300. early=0-100, mid=101-300, all=whole game; eats use eating rounds.',
             'Cases=side/tile/round with any qualifying head; all its substeps count. Birth-cohort waits followed to end.',
             'Blocked head/trail=recent empty entry (age<=current L); other=meal/older/initial entry. Checkpoints carry final state.',
             'Cells=ours / opponent; components separated by commas. Paired game means; each rate uses pairs with both denominators.',
             f'| measure | {arms[0]} | {arms[1]} | paired {arms[1]} minus {arms[0]} |', '|---|---|---|---|']
    for label, fns in metrics():
        fns = fns if isinstance(fns, tuple) else (fns,)
        values = [[], [], []]
        for s in (0, 1):
            parts = [[], [], []]
            for fn in fns:
                pairs = [(fn(a['measures'][s]), fn(b['measures'][s])) for a, b in zip(selected[arms[0]], selected[arms[1]])]
                pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
                if not pairs:
                    nums = [None]*3
                else:
                    scale = 1 if label == 'wins (count)' else 1/len(pairs)
                    nums = [sum(a for a, b in pairs)*scale, sum(b for a, b in pairs)*scale,
                            sum(b-a for a, b in pairs)*scale]
                for j, v in enumerate(nums):
                    parts[j].append('NA' if v is None else f'{v:+.3f}' if j == 2 else f'{v:.3f}')
            for j in range(3):
                values[j].append(','.join(parts[j]))
        lines.append('| '+label+' | '+' | '.join(' / '.join(v) for v in values)+' |')
    assert len(lines) <= 30
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('armA')
    parser.add_argument('armB')
    parser.add_argument('--maps', help='map-name substring')
    args = parser.parse_args()
    arms = (args.armA, args.armB)
    if arms[0] == arms[1]:
        parser.error('use two distinct arms')
    inv = {a: inventory(a, args.maps) for a in arms}
    common = sorted(set(inv[arms[0]]) & set(inv[arms[1]]))
    maps = {}
    for p in MAPS.rglob('*.map'):
        maps.setdefault(p.stem, []).append(p)
    version = hashlib.sha256(b''.join(p.read_bytes() for p in (Path(__file__), HERE/'replay_format.py', HERE/'count_local.py', HERE/'maps2/semantics.json'))).hexdigest()
    cache = {}
    if CACHE.exists():
        for line in CACHE.read_text().splitlines():
            r = json.loads(line)
            cache[r['replay']] = r
    selected = {a: [] for a in arms}
    hits = counted = 0
    for arm in arms:
        for key in common:
            candidates = maps.get(key[0], [])
            assert candidates, f'missing true map: {key[0]}'
            assert len({p.read_bytes() for p in candidates}) == 1, f'ambiguous map: {key[0]}'
            mp = candidates[0]
            path = inv[arm][key]
            st = path.stat()
            signature = [version, st.st_size, st.st_mtime_ns, hashlib.sha256(mp.read_bytes()).hexdigest()]
            row = cache.get(str(path))
            if row and row.get('_signature') == signature:
                hits += 1
            else:
                row = scan(path, key, mp)
                after = path.stat()
                assert (st.st_size, st.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'replay changed; rerun'
                row.update(replay=str(path), arm=arm, _signature=signature)
                with CACHE.open('a') as handle:
                    handle.write(json.dumps(row, separators=(',', ':'))+'\n')
                cache[str(path)] = row
                counted += 1
                if counted % 8 == 0:
                    print(f'Counted {counted}/{2*len(common)} games', file=sys.stderr, flush=True)
            selected[arm].append(row)
    print(report(selected, arms, hits, counted), end='')


if __name__ == '__main__':
    main()
