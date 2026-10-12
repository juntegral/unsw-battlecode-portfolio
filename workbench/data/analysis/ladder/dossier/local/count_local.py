#!/usr/bin/env python3
"""Port isl_zone / au_scan / au_scan2 / au_net definitions to local wire replays.

Run from any directory. Only output files beside this script are written.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from statistics import mean
from replay_format import load, point
from ram_defs import find_heads, measures as ram_measures

HERE = Path(__file__).resolve().parent
DEFAULT_RUNS = Path('~/meow-redteam/solo/runs')
import os as _os
ARMS = ('base',) + tuple(sorted(d for d in _os.listdir(_os.path.expanduser('~/meow-redteam/solo/runs')) if _os.path.isdir(_os.path.join(_os.path.expanduser('~/meow-redteam/solo/runs'), d)) and d not in ('base', 'ident') and not d.startswith('sanity')))
WINDOWS = ((101, 150), (151, 200), (201, 300), (301, 400))
MEET_WINDOWS = ((0, 100), (101, 300), (301, 499))
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LEADER_FIELDS = ('leader_deaths_301_499', 'leader_deaths_rammed_301_499',
                 'leader_death_rounds', 'leader_death_lengths', 'leader_death_allies5',
                 'longest_r450', 'longest_peak_301_499', 'longest_kept_share',
                 'leader_pearls_301_499', 'leader_turns_enemy3_301_499',
                 'leader_turns_enemy3_multistep_301_499')


def edge_id(w, h, x, y, d):
    return (2*y*(w+1)+x if d == 0 else (2*y+1)*(w+1)+(x+1)%w if d == 1
            else 2*((y+1)%h)*(w+1)+x if d == 2 else (2*y+1)*(w+1)+x)


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = {}
        for e, k, p in raw:
            row, x = divmod(e, w+1)
            if row % 2 == 0 and x == w:
                continue
            e = 2*((row//2)%h)*(w+1)+x if row % 2 == 0 else row*(w+1)+x%w
            if e not in edges or k > edges[e][0]:
                edges[e] = k, p
        portals = defaultdict(list)
        for e, (k, p) in edges.items():
            if k == 2:
                portals[p].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d, (dx, dy) in enumerate(STEP):
                    e = edge_id(w, h, x, y, d)
                    k, pid = edges.get(e, (0, -1))
                    if k == 2:
                        partner, = [z for z in portals[pid] if z != e]
                        ry, px = divmod(partner, w+1)
                        dest = ((ry//2-(d == 0))%h)*w+(px-(d == 3))%w
                    else:
                        dest = ((y+dy)%h)*w+(x+dx)%w
                    row.append((k, dest))
                self.moves.append(row)
        self.adj = [sorted({t for k, t in row if k != 1}) for row in self.moves]
        self.wins = {}

    def window(self, src):
        if src not in self.wins:
            y, x = divmod(src, self.w)
            self.wins[src] = frozenset(((y+dy)%self.h)*self.w+(x+dx)%self.w
                                      for dy in range(-3, 4) for dx in range(-3, 4))
        return self.wins[src]


def start_len(e):
    for p in range(8):
        L0 = e['Lm'] + p
        if p == max(0, e['k']-1-(L0+3)//4):
            return L0
    return e['Lm']


def scan(path, arm, map_slug, seed, our_side):
    root = load(path).root()
    bodies, teams, raw = {}, {}, []
    w = h = 0
    map_name = map_slug
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'MAP_NAME':
            map_name = ' '.join(q[1:])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    assert w > 0 and h > 0
    tile = lambda p: p[1]*w+p[0]
    side = lambda i: 'ours' if teams[i] == our_side else 'theirs'
    queens = {s: min(i for i in bodies if side(i) == s) for s in ('ours', 'theirs')}
    g = Geo(w, h, raw)
    heads = {b[0]: i for i, b in bodies.items()}
    occ = Counter(c for b in bodies.values() for c in b)
    alive = Counter(side(i) for i in bodies)
    counts = {s: Counter() for s in ('ours', 'theirs')}
    present, snaps, starts, meetings = {}, {}, {}, []
    rnd, actor, cur, used = -1, None, None, 0
    turn_deaths = []
    ram_chances, ram_meetings, expected = [], [], deque()
    ram_half, queen300 = None, False
    queen_mover = dict.fromkeys(counts, False)
    turn_leaders = {}
    leader_lists = {s: {f: [] for f in LEADER_FIELDS[2:5]} for s in counts}

    def man(a, c):
        dx, dy = abs(a % w-c % w), abs(a // w-c // w)
        return min(dx, w-dx)+min(dy, h-dy)

    def peak():
        if 301 <= rnd <= 499:
            for i, b in bodies.items():
                s = side(i)
                counts[s]['longest_peak_301_499'] = max(counts[s]['longest_peak_301_499'], len(b))

    def snapshot():
        return {s: dict(alive=alive[s], longest=max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                        total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                        queen_alive=queens[s] in bodies) for s in counts}

    def reach_heads(src, depth, s):
        out, d, q = [], {src: 0}, deque([src])
        while q:
            c = q.popleft()
            if d[c] >= depth:
                continue
            for t in g.adj[c]:
                if t in d:
                    continue
                d[t] = d[c]+1
                i = heads.get(t)
                if i is not None and side(i) != s:
                    out.append((d[t], i))
                    continue
                if occ[t]:
                    continue
                q.append(t)
        return out

    def finish():
        nonlocal cur
        if cur is not None and cur['leader_enemy3']:
            counts[cur['s']]['leader_turns_enemy3_multistep_301_499'] += int(used > 1)
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if hs:
            assert len(hs) == 2 and any(d['id'] == actor for d in hs)
            m = next(d for d in hs if d['id'] == actor)
            v = next(d for d in hs if d['id'] != actor)
            for row in cur['ram_rows'].values():
                row[22] = 1 if row[6] == v['id'] else 2
            e = dict(r=rnd, ms=m['s'], cross=m['s'] != v['s'], Lm=m['L'], Lv=v['L'],
                     k=used+1, eat={'ours': 0, 'theirs': 0}, drop=0)
            meetings.append(e)
            for pr in cur['drops'] if cur else ():
                pr['ho'] = e
                e['drop'] += 1
        turn_deaths.clear()
        if cur is not None and cur['skip_eligible']:
            c = counts[cur['s']]
            window = next((f'{lo}_{hi}' for lo, hi in WINDOWS[:2] if lo <= cur['r'] <= hi), None)
            if window:
                c['skip_n_'+window] += 1
                c['skip_'+window] += int(not cur['ate'])
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            if rnd >= 0:
                snaps[rnd] = snapshot()
            rnd, actor = p.i32(0), None
            starts[rnd] = dict(alive)
            if rnd == 300:
                queen300 = queens['ours'] in bodies
            turn_leaders = {}
            peak()
        elif k == 1:
            actor, used = p.i32(0), 0
            s = side(actor)
            body, L = bodies[actor], len(bodies[actor])
            hd = body[0]
            longest = {ss: max((len(bb) for i, bb in bodies.items() if side(i) == ss), default=0) for ss in counts}
            turn_leaders = {i: len(bb) for i, bb in bodies.items() if len(bb) >= 15 and len(bb) == longest[side(i)]}
            is_leader = L == longest[s] and 301 <= rnd <= 499
            enemy3 = is_leader and L >= 15 and any(side(i) != s and len(bb) <= 9 and man(hd, bb[0]) <= 3 for i, bb in bodies.items())
            counts[s]['leader_turns_enemy3_301_499'] += int(enemy3)
            adj = [t for kind, t in g.moves[hd] if kind != 1 and t in present]
            enemy_near_pearl = False
            for c in adj:
                for i, b in bodies.items():
                    if side(i) != s:
                        dx, dy = abs(c%w-b[0]%w), abs(c//w-b[0]//w)
                        if min(dx, w-dx)+min(dy, h-dy) <= 2:
                            enemy_near_pearl = True
            cap = 'under59' if alive['ours'] < 59 else 'ge59'
            cur = dict(id=actor, s=s, r=rnd, ate=0, drops=[],
                       leader=is_leader, leader_enemy3=enemy3,
                       skip_eligible=actor != queens[s] and bool(adj) and not enemy_near_pearl,
                       track=101 <= rnd <= 300 and actor != queens[s] and 2 <= L <= 4,
                       cap=cap, can=False, edge=False, L0=L, ram_rows={})
            if actor != queens[s] and 2 <= L <= 4:
                for j, dist, free, ov, ev_, vis, lng, big in find_heads(g, hd, L, s, heads, bodies, side, occ, present):
                    row = [0]*25
                    for index, value in {0:rnd, 1:s, 2:actor, 3:L, 4:0, 6:j, 7:len(bodies[j]),
                                         10:dist, 11:free, 12:ov, 13:ev_, 16:vis, 17:alive[s],
                                         19:lng, 20:big}.items():
                        row[index] = value
                    ram_chances.append(row)
                    cur['ram_rows'][j] = row
            if cur['track']:
                can = [j for dist, j in reach_heads(hd, L-1, s) if len(bodies[j]) >= L]
                a = e = 0
                for c in g.window(hd):
                    i = heads.get(c)
                    if i is not None and i != actor:
                        if side(i) == s:
                            a += 1
                        else:
                            e += 1
                cur.update(can=bool(can), edge=a >= e)
                if can and a >= e:
                    counts[s]['chances_'+cap] += 1
        elif k == 3:
            c = tile(point(p.pointer(0)))
            if p.bit(0):
                rec = None
                if expected:
                    xy, rec = expected.popleft()
                    assert xy == c, 'ram death-drop sequence mismatch'
                pr = dict(b=rnd, ho=None, ram=rec)
                present[c] = pr
                if actor is not None and cur is not None:
                    cur['drops'].append(pr)
            else:
                pr = present.pop(c)
                rec = pr['ram']
                if rec is not None and rnd-rec[0]['r'] <= 15:
                    x, which = rec
                    x[which+('m' if side(actor) == x['ms'] else 'v')] += 1
                assert actor is not None
                s = side(actor)
                for lo, hi in WINDOWS:
                    if lo <= rnd <= hi:
                        counts[s][f'pearls_{lo}_{hi}'] += 1
                if pr['ho'] is not None and rnd-pr['b'] <= 15:
                    pr['ho']['eat'][s] += 1
                if cur is not None:
                    cur['ate'] += 1
                    if cur['leader']:
                        counts[s]['leader_pearls_301_499'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                b.appendleft(hd)
                heads[hd] = i
                occ[hd] += 1
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
            peak()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            for lo, hi in WINDOWS:
                if lo <= rnd <= hi:
                    counts[s][f'splits_{lo}_{hi}'] += 1
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
                teams[i] = p.u16(8)
                heads[bodies[i][0]] = i
                occ.update(bodies[i])
            alive[s] += 1
            peak()
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            if 301 <= rnd <= 499 and i in turn_leaders:
                counts[s]['leader_deaths_301_499'] += 1
                counts[s]['leader_deaths_rammed_301_499'] += int(reason == 3 and i != actor and side(actor) != s)
                leader_lists[s]['leader_death_rounds'].append(rnd)
                leader_lists[s]['leader_death_lengths'].append(len(bodies[i]))
                leader_lists[s]['leader_death_allies5'].append(sum(z != i and side(z) == s and man(bodies[i][0], bb[0]) <= 5 for z, bb in bodies.items()))
            rec = None
            if reason == 3 and i != actor:
                L0 = cur['L0']
                ram_half = dict(r=rnd, ms=side(actor), mid=actor, vid=i, cross=side(actor) != s,
                                L0=L0, Ld=len(bodies[actor]), Lv=len(bodies[i]),
                                mq=int(actor == queens[side(actor)]),
                                mtop=int(L0 >= max((len(bb) for z, bb in bodies.items()
                                                   if z != actor and side(z) == side(actor)), default=0)),
                                dm=0, dv=(len(bodies[i])+1)//2, mm=0, mv=0, vm=0, vv=0)
                ram_meetings.append(ram_half)
                rec = (ram_half, 'v')
            elif reason == 3 and i == actor:
                assert ram_half is not None and ram_half['mid'] == actor and ram_half['r'] == rnd
                ram_half['dm'] = (len(bodies[i])+1)//2
                rec = (ram_half, 'm')
            for seg, c in enumerate(bodies[i]):
                if seg % 2 == 0:
                    expected.append((c, rec))
            turn_deaths.append(dict(id=i, reason=reason, s=s, L=len(bodies[i])))
            for lo, hi in WINDOWS:
                if lo <= rnd <= hi:
                    counts[s][f'deaths_{lo}_{hi}'] += 1
            if reason == 3 and i == actor:
                queen_mover[s] |= i == queens[s]
                if cur and cur['track'] and cur['can'] and cur['edge']:
                    counts[s]['taken_'+cur['cap']] += 1
            if heads.get(bodies[i][0]) == i:
                del heads[bodies[i][0]]
            for c in bodies.pop(i):
                occ[c] -= 1
            alive[s] -= 1
    finish()
    snaps[rnd] = snapshot()
    result = root.pointer(4)
    assert result.bit(0), 'unfinished replay'
    for z in (0, 1):
        s = 'ours' if z == our_side else 'theirs'
        st = result.pointer(z)
        fin = snaps[rnd][s]
        assert (fin['alive'], fin['longest'], fin['total']) == (st.i32(0), st.i32(4), st.i32(8)), 'final standings mismatch'
        assert len(bodies.get(queens[s], ())) == st.i32(12), 'queen standings mismatch'
    measures = {}
    for s in counts:
        c, m = counts[s], {}
        for rr in (100, 150, 200, 300, 400):
            # Ended games retain their terminal state for later checkpoints.
            snap = snaps.get(rr, snaps[rnd] if rr > rnd else None)
            assert snap is not None, 'missing raw round checkpoint'
            m[f'alive_r{rr}'] = snap[s]['alive']
            if rr in (300, 400):
                for f in ('longest', 'total'):
                    m[f'{f}_r{rr}'] = snap[s][f]
        for f in ('alive', 'longest', 'total', 'queen_alive'):
            m[f'{f}_end'] = snaps[rnd][s][f]
        for lo, hi in WINDOWS:
            for f in ('pearls', 'splits', 'deaths'):
                m[f'{f}_{lo}_{hi}'] = c[f'{f}_{lo}_{hi}']
        for lo, hi in WINDOWS[:2]:
            key = f'{lo}_{hi}'
            for f in ('skip_n', 'skip'):
                m[f'{f}_{key}'] = c[f'{f}_{key}']
            m['skip_share_'+key] = c['skip_'+key]/max(1, c['skip_n_'+key])
        m['under56_share_151_400'] = sum(starts.get(rr, {s: snaps[rnd][s]['alive']})[s] < 56 for rr in range(151, 401))/250
        for lo, hi in MEET_WINDOWS:
            m[f'meetings_started_{lo}_{hi}'] = sum(e['cross'] and e['ms'] == s and lo <= e['r'] <= hi for e in meetings)
        for cap in ('under59', 'ge59'):
            for f in ('chances', 'taken'):
                m[f'{f}_{cap}'] = c[f'{f}_{cap}']
            m['take_rate_'+cap] = c['taken_'+cap]/max(1, c['chances_'+cap])
        m['meeting_net_101_300'] = 0
        for e in meetings:
            if e['cross'] and 101 <= e['r'] <= 300:
                m['meeting_net_101_300'] += e['eat'][s] - (start_len(e) if e['ms'] == s else e['Lv'])
        m['queen_died_as_mover'] = queen_mover[s]
        for f in LEADER_FIELDS:
            if f in leader_lists[s]:
                m[f] = leader_lists[s][f]
            elif f == 'longest_r450':
                m[f] = snaps.get(450, snaps[rnd] if rnd < 450 else {})[s]['longest']
            elif f == 'longest_kept_share':
                m[f] = m['longest_end']/c['longest_peak_301_499'] if c['longest_peak_301_499'] else 0
            else:
                m[f] = c[f]
        m.update(ram_measures(ram_chances, ram_meetings, s, w*h, queen300))
        measures[s] = m
    winner = result.u16(6) if result.u16(4) == 1 else None
    return dict(map=map_slug, map_name=map_name, cells=f'{w}x{h}', width=w, height=h, seed=seed,
                side=our_side, arm=arm, winner=winner, result='draw' if winner is None else 'win' if winner == our_side else 'loss',
                how=('elimination', 'round_limit')[result.u16(2)], last_round=rnd,
                measures=measures, our_counts=[snaps[rr]['ours']['alive'] for rr in sorted(snaps)],
                base_subset_under56_r150=measures['ours']['alive_r150'] < 56,
                meetings=meetings, ram_meetings=ram_meetings)


def fmt(v):
    return '—' if v is None else f'{v:.3f}'.rstrip('0').rstrip('.')


def metric_value(value):
    return mean(value) if isinstance(value, list) and value else 0 if isinstance(value, list) else float(value)


def make_table(rows, skipped):
    metrics = list(rows[0]['measures']['ours']) if rows else []
    lines = ['# Local mechanism counts', '', 'Values are game means; each measure is ours / theirs. Rounds are raw and inclusive.']
    for section, chosen in (('A. All games', rows), ('B. BASE under 56 at end of r150',
        [r for r in rows if any(b['arm'] == 'base' and key(b) == key(r) and b['base_subset_under56_r150'] for b in rows)])):
        lines += ['', '## '+section, '', '| arm | games | won | mean width×height; seed; side; last round | winner 0/1/draw; ending elimination/limit | '+ ' | '.join(metrics)+' |',
                  '|'+ '---|'*(5+len(metrics))]
        for arm in ARMS:
            rs = [r for r in chosen if r['arm'] == arm]
            vals = [' / '.join(fmt(mean(metric_value(r['measures'][s][m]) for r in rs)) if rs else '—' for s in ('ours', 'theirs')) for m in metrics]
            metadata = (f'{fmt(mean(r["width"] for r in rs))}×{fmt(mean(r["height"] for r in rs))}; '
                        f'{fmt(mean(r["seed"] for r in rs))}; {fmt(mean(r["side"] for r in rs))}; '
                        f'{fmt(mean(r["last_round"] for r in rs))}') if rs else '—'
            categories = '/'.join(str(sum(r['winner'] == v for r in rs)) for v in (0, 1, None))
            categories += '; '+ '/'.join(str(sum(r['how'] == v for r in rs)) for v in ('elimination', 'round_limit'))
            lines.append(f'| {arm} | {len(rs)} | {sum(r["result"] == "win" for r in rs)} | {metadata} | {categories} | '+' | '.join(vals)+' |')
    base = {key(r): r for r in rows if r['arm'] == 'base'}
    pairs = [(base[key(r)], r) for r in rows if r['arm'] != 'base' and key(r) in base]
    dm = ['pearls_151_200', 'splits_151_200', 'skip_share_151_200', 'alive_r200', 'alive_r300',
          'longest_end', 'meetings_started_101_300', 'take_rate_under59', 'meeting_net_101_300', 'wins']
    lines += ['', '## C. Paired against BASE', '', '| arm | pairs | differing count sequences | '+' | '.join(dm)+' |', '|'+ '---|'*(3+len(dm))]
    for arm in ARMS[1:]:
        ps = [(b, r) for b, r in pairs if r['arm'] == arm]
        vals = []
        for m in dm:
            ds = [(int(r['result'] == 'win')-int(b['result'] == 'win')) if m == 'wins'
                  else r['measures']['ours'][m]-b['measures']['ours'][m] for b, r in ps]
            vals.append(fmt(mean(ds)) if ds else '—')
        lines.append(f'| {arm} | {len(ps)} | {sum(b["our_counts"] != r["our_counts"] for b, r in ps)} | '+' | '.join(vals)+' |')
    lines += ['', '## D. Each pair', '', '| map, seed, side, arm | result base → arm | our r150/r300 base → arm | longest end base → arm |', '|---|---|---|---|']
    for b, r in pairs:
        bm, rm = b['measures']['ours'], r['measures']['ours']
        lines.append(f'| {r["map"]}, {r["seed"]}, {r["side"]}, {r["arm"]} | {b["result"]} → {r["result"]} | {bm["alive_r150"]}/{bm["alive_r300"]} → {rm["alive_r150"]}/{rm["alive_r300"]} | {bm["longest_end"]} → {rm["longest_end"]} |')
    lines += ['', 'Notes: ladder definitions retained: skip enemy distance is toroidal Manhattan from every adjacent pearl, not the actor; chance edge is allied heads excluding actor ≥ enemies in wrapped 7×7; both sides use OUR count at turn start for the 59 split. Taken means mover head-on death at a qualifying chance (including same-team head-ons, exactly au_scan2).',
              'Local port: raw roundStart values (show.py adds 1 only for display); lowest starting id per side replaces actor > 1 queen exclusion. Body updates retain the ladder conditional append; final counts/lengths/queen are asserted against engine standings. No geometry or movement-cost definitions changed.',
              'Net uses au_net start_len search p=0..7 and au_scan recovery of pearls spawned during the collision turn and eaten within 15 rounds; recovery after r300 is retained. Rates use max(1, denominator) as ladder scripts. Zero eligible turns give rate 0; raw denominators are included.',
              'Games ending early carry terminal snapshots to later checkpoints; round-share uses 250 scheduled rounds (terminal count after game end). B uses BASE end-of-round r150; C compares actual end-of-round count sequences including their lengths. Metadata numeric means and winner/ending category counts are above; map labels are per game in rows.jsonl and D.',
              'Skipped games: '+ ('; '.join(skipped) if skipped else 'none')+'.']
    lines += ['', 'Leader port (fd_ram.py / fd_esc.py): tied longest dragons all qualify; distances are wrapped Manhattan, allies exclude the leader, small enemies are length ≤9, and successful head-changing body updates count steps (a fatal attempted step does not). Both sides are counted.',
              'Brief differences: raw inclusive r301–499 and length ≥15 replace fd_ram r>200/L≥8 and fd_esc feeding-start/L≥10. Death qualification uses all leaders at the start of the current acting dragon’s turn, including passive victims, rather than fd_ram’s death-time longest check. Death lists contain death-time length and nearby allies (fd_ram own5_now), not the previous own-turn snapshot (own5). Deaths include all causes; rammed requires enemy mover head-on death. Pearl leader status is fixed at its own turn start, with no minimum length. Enemy3 exposures follow fd_esc turn-start logic, with successful multistep turns counted at turn end.',
              'Peak includes round-start state and every body update/split in r301–499; r450 is end-of-round with terminal carry-forward. Kept share is final longest / peak, or 0 when peak is 0 (early-ending games have no late-window observations). List columns in this table and leader.py are means of per-game event means, using 0 for empty lists; rows.jsonl retains the original lists. No existing row field is changed.']
    lines += ['', 'Ram port (at_scan.py / at_more.py): chances are per non-queen length-2–4 turn and enemy head, all raw rounds. The same 8-step pearl-aware search, lexicographic state pruning and occupied-tile blocking are retained. Free/paid classes use path distance versus ceil(L/4), even when pearls cover costs. Outnumbered includes self and means own heads ≤ enemy heads (one against one qualifies). Target classes use full target length; H uses visible parts.',
              'Added is exactly H and fails(..., even=True), including hunt/feeding-hunt exemptions and unit/size/step clauses, not merely the count/round test. Feed is reconstructed once for both sides from OUR queen at the START of raw r300 on >600 cells (otherwise 400), exactly at_more; no r300 snapshot means feed 400. This differs from the existing end-of-round checkpoints, whose names and values are retained.',
              'Ram collision records retain turn-start mover L0, death-time Ld and victim Lv. Twice-class qualification uses Lv ≥ 2*L0 for every cross-team mover, with no mover length or queen restriction; length/swing and tied-longest/queen counts are summed per side per game. mtop compares L0 with surviving allies at victim death, as at_scan. ram_meetings retains each event and body-specific drop recovery.',
              'New meeting net and swing use at_scan death-drop attribution (alternating body parts, followed through 15 inclusive raw rounds) and turn-start mover length, exactly at_more.swing; early game endings truncate recovery. Existing meetings and meeting_net_101_300 retain their older definitions unchanged. ram_headons_started and ram_meeting_net cover all raw rounds and cross-team meetings; net includes passive victims. rams.py pools added take rate and twice-class swing across events; all other values are game means, with matched B−A differences.']
    if False:
        raise ValueError(f'table requires {len(lines)} lines for {len(pairs)} pairs; cannot omit requested pair lines')
    return '\n'.join(lines)+'\n'


def key(r):
    return r['map'], r['seed'], r['side']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args()
    version = hashlib.sha256(Path(__file__).read_bytes()+(HERE/'replay_format.py').read_bytes()+(HERE/'ram_defs.py').read_bytes()).hexdigest()
    cache = {}
    if (HERE/'rows.jsonl').exists():
        for line in (HERE/'rows.jsonl').read_text().splitlines():
            try:
                r = json.loads(line)
                cache[r['replay']] = r
            except (ValueError, KeyError):
                pass
    rows, skipped = [], []
    for arm in ARMS:
        for folder in sorted((args.runs/arm).glob('*')):
            if not folder.is_dir():
                continue
            match = re.fullmatch(r'(.+)-seed(\d+)-side([01])', folder.name)
            if not match:
                skipped.append(f'{arm}/{folder.name}: unrecognized game directory')
                continue
            path = folder/'game.replay'
            label = f'{arm}/{folder.name}'
            if not path.exists():
                skipped.append(label+': no replay yet')
                continue
            try:
                meta = json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {}
                if meta.get('bot_errors') or meta.get('crash') or meta.get('error'):
                    skipped.append(label+': crash/bot errors in result.json')
                    continue
                st = path.stat()
                signature = [version, st.st_size, st.st_mtime_ns]
                cached = cache.get(str(path.resolve()))
                if cached and cached.get('_signature') == signature:
                    row = cached
                else:
                    slug, seed, side = match.groups()
                    row = scan(path, arm, slug, int(seed), int(side))
                    assert path.stat().st_mtime_ns == st.st_mtime_ns, 'replay changed during scan; rerun'
                    row.update(replay=str(path.resolve()), _signature=signature)
                if meta:
                    assert meta.get('winner', row['winner']) == row['winner'], 'result.json winner mismatch'
                    assert meta.get('rounds', row['last_round']+1) == row['last_round']+1, 'result.json rounds mismatch'
                rows.append(row)
            except Exception as error:
                skipped.append(f'{label}: {type(error).__name__}: {error}')
    table = make_table(rows, skipped)
    (HERE/'rows.jsonl').write_text(''.join(json.dumps(r, separators=(',', ':'))+'\n' for r in rows))
    (HERE/'table.md').write_text(table)
    print(f'{len(rows)} games counted, {len(skipped)} skipped; table {len(table.splitlines())} lines')


if __name__ == '__main__':
    main()
