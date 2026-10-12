"""Scratch (diag-opening2): tables from o2_scan-*.jsonl.
Usage: python3 data/analysis/ladder/dossier/work/o2_agg.py <tally|class|pearls|terms|card|cmap|view> [args]
Groups: ours = followed side of O (by arm) and L; opp = the other side there; R = rank-1 (followed side of R), Ropp."""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict, Counter
from statistics import median

WORK = Path('data/analysis/ladder/dossier/work')
DOS = Path('data/analysis/ladder/dossier')
FILES = ('o2_scan-O0.jsonl', 'o2_scan-L0.jsonl', 'o2_scan-R0.jsonl')
TERMS = ('centre', 'room', 'terr', 'cramped', 'pearl', 'soon', 'hot', 'unseen', 'portal', 'far', 'eat', 'look', 'mate', 'pocket', 'sc', 'queen')


def load():
    games, turns = {}, defaultdict(list)
    for f in FILES:
        p = WORK / f
        if not p.exists():
            print('missing', f)
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if r['k'] == 'g':
                key = (r['src'], r['g'])
                games[key] = r
                cur = key
            else:
                turns[cur].append(r)
    return games, turns


def group(g, side):
    if g['src'] == 'O':
        return ('O ' + g['arm']) if side == 0 else 'O opp'
    if g['src'] == 'L':
        return 'L ours' if side == 0 else 'L opp'
    return 'R rank1' if side == 0 else 'R opp'


def show(grp, name):
    gf = [x for x in sys.argv[4].split(',') if x] if len(sys.argv) > 4 else []
    lf = [x for x in sys.argv[5].split(',') if x] if len(sys.argv) > 5 else []
    return (not gf or any(grp.startswith(x) for x in gf)) and (not lf or any(name.startswith(x) for x in lf))


def tb(d, wt):
    return 0.0 if d < 0 else max(0.0, wt * (260 - 40 * d))


def parts(row, o, k, release, centre=True, variant=None):
    """Score terms of one step on offer; a dict term -> value (signed)."""
    dest, room, terr, tailhit, dp, ds, dh, du, dpo, dk, eat, sc, pocket, look, mate, cd, pk, kr, dsa, dpa = o
    L, r = row['L'], row['r']
    on = row['cm'] and r < row['cr'] and L <= 4 and row['ne'] - row['nm'] <= row['mg']
    released = release and row['cm'] and r < row['cr'] and L <= 4 and row['st'] >= 12
    cr = 0.0
    want = 3.0 * L + 8.0
    if room < want:
        cr += 400.0 * (want - room)
    if room < L + 2.0:
        cr += 5000.0 * (L + 2.0 - room)
    if not tailhit and not (released and room >= 6 * L + 8.0):
        cr += 600.0
    t = dict.fromkeys(TERMS, 0.0)
    t['room'] = 1.5 * room
    t['terr'] = 1.5 * terr
    t['cramped'] = -cr
    if row['isq']:
        q = 0.0
        if ((not tailhit) and room < want) or room < L + 8:
            q += 6000.0
        if kr > 0:
            q += 6000.0 + 400.0 * kr
        t['queen'] = -q
    cand = (('pearl', tb(dp, 2.0)), ('soon', tb(ds, 0.45)), ('hot', tb(dh, 1.2)), ('unseen', tb(du, 0.2)), ('portal', tb(dpo, 0.4)))
    name, val = max(cand, key=lambda kv: kv[1])
    if val > 0:
        t[name] = val
    far = [x for x in (dp, ds, dh, du) if x >= 0]
    if far:
        t['far'] = 2.0 * max(0, 80 - min(far))
    grown = L + eat
    full = pocket < 48 and grown > pocket // 2
    if full:
        t['pocket'] = -1000.0 * (grown - pocket // 2)
    if eat and not full:
        t['eat'] = 300.0
    if sc:
        t['sc'] = -300.0
    if centre and on and max(tb(dp, 2.0), tb(dh, 1.2)) <= 0.0:
        off = False
        if variant == 'units2':
            off = row['al'] <= 2
        elif variant == 'units3':
            off = row['al'] <= 3
        elif variant == 'nq':
            off = row['ro'] == 'o'
        elif variant == 'spawn':
            off = row.get('mdk', -1) >= 0 and row['mdk'] <= row['cd']
        elif variant == 'unfed':
            off = row.get('unfed', 0) == 1
        if not off:
            t['centre'] = -40.0 * ((min(du, 30) if du >= 0 else 30) if released else cd)
    if mate:
        t['mate'] = -450.0
    t['look'] = look
    if pk == 1:
        t['portal'] -= 150.0
    t['tie'] = 0.25 * ((row['i'] * 31 + r * 17 + k * 7) % 5)
    return t


def scores(row, release, centre=True, variant=None, drop=None):
    """Returns ([score or None] * 4, [parts or None] * 4)."""
    out, ps = [None] * 4, [None] * 4
    base = None
    blind = []
    for k, o in enumerate(row['o']):
        if o is None:
            continue
        if len(o) == 2:
            blind.append(k)
            continue
        t = parts(row, o, k, release, centre, variant)
        if drop:
            t[drop] = 0.0
        ps[k] = t
        out[k] = sum(t.values())
        if o[16] == 0:
            b = out[k] - t['tie'] - max(t['pearl'], t['soon'], t['hot'], t['unseen'], max(t['portal'], 0.0))
            if base is None or b > base:
                base = b
    for k in blind:
        if base is not None:
            out[k] = base + 88.0 + 0.25 * ((row['i'] * 31 + row['r'] * 17 + k * 7) % 5)
            ps[k] = dict(blind=out[k])
    return out, ps


def best(sc):
    v = [(s, -k) for k, s in enumerate(sc) if s is not None]
    return -max(v)[1] if v else -1


def pct(a, b):
    return '%.0f%%' % (100.0 * a / b) if b else 'NA'


def med(v):
    return median(v) if v else float('nan')


def mean(v):
    return sum(v) / len(v) if v else float('nan')


def lay(g):
    return '%s %dx%d' % (g['map'], g['w'], g['h'])


def tally(games, turns):
    acc = defaultdict(lambda: defaultdict(list))
    for key, g in games.items():
        for side in (0, 1):
            for name in (lay(g), 'ALL', 'ALL but Stripes' if g['map'] != 'Stripes' else None):
                if name is None:
                    continue
                a = acc[(group(g, side), name)]
                a['n'].append(1)
                a['won'].append(1 if (g['won'] if side == 0 else (None if g['won'] is None else not g['won'])) else 0)
                for i, (ro, s, head, ln, cd) in g['starters'].items():
                    if s != side:
                        continue
                    ev = g['eats'][i]
                    for lim in (20, 40):
                        a['%s%d' % (ro, lim)].append(sum(1 for e in ev if e[0] <= lim))
                    a[ro + 'first'].append(ev[0][0] if ev else 99)
                se = g['side_eats'][side]
                a['p2'].append(se[1] if len(se) > 1 else 99)
                a['p4'].append(se[3] if len(se) > 3 else 99)
                sp = g['side_splits'][side]
                a['s1'].append(sp[0] if sp else 99)
                for r in ('20', '40'):
                    a['al' + r].append(g['marks'][r][side])
                    a['ln' + r].append(g['marks'][r][4 + side])
    print('group | layout | games, wins | 2nd starter pearls by r20, r40 | queen r20, r40 | first pearl round median: 2nd, queen | side 2nd pearl, 4th pearl, first split (median round) | dragons r20, r40 | length r40')
    for (grp, name), a in sorted(acc.items()):
        print('%-9s | %-24s | %3d, %3d | %.2f, %.2f | %.2f, %.2f | %s, %s | %s, %s, %s | %.1f, %.1f | %.1f' % (
            grp, name, len(a['n']), sum(a['won']), mean(a['o20']), mean(a['o40']), mean(a['q20']), mean(a['q40']),
            med(a['ofirst']), med(a['qfirst']), med(a['p2']), med(a['p4']), med(a['s1']), mean(a['al20']), mean(a['al40']), mean(a['ln40'])))


def step_class(r):
    if r['ate'] or (r['dpk'] >= 0 and r.get('dpk2', 1 << 30) < r['dpk'] and r['dpk2'] >= 0):
        return 'pearl'
    c = r['cd2'] < r['cd']
    u = r['du'] >= 0 and (r['du2'] < r['du'])
    return 'centre+unseen' if c and u else 'centre' if c else 'unseen' if u else 'elsewhere'


def classes(games, turns, last, role):
    acc = defaultdict(Counter)
    for key, g in games.items():
        for r in turns[key]:
            if r['r'] > last or r['ro'] != role:
                continue
            for name in (lay(g), 'ALL', 'ALL but Stripes' if g['map'] != 'Stripes' else None):
                if name is None:
                    continue
                a = acc[(group(g, r['s']), name)]
                a['turns'] += 1
                a['act ' + r['act']] += 1
                a['sum np'] += r['np']
                a['sum dsp'] += r['dsp'] if r['dsp'] >= 0 else 0
                a['sum cd'] += r['cd']
                if r['act'] != 'm':
                    continue
                a['moves'] += 1
                view = 'blind' if r['np'] == 0 else 'view'
                a[view] += 1
                a[view + ' ' + step_class(r)] += 1
                a[view + ' nearer centre'] += r['cd2'] < r['cd']
                a[view + ' farther centre'] += r['cd2'] > r['cd']
                a[view + ' nearer unseen'] += r['du'] >= 0 and r['du2'] < r['du']
                a[view + ' nearer spawn'] += r['dsp2'] < r['dsp']
                a[view + ' farther spawn'] += r['dsp2'] > r['dsp']
                a[view + ' on spawn'] += r['dsp'] == 0 or r['dsp2'] == 0
                if r['np'] == 0:
                    if r['dpk'] >= 0:
                        a['blind remembered'] += 1
                        a['blind remembered nearer'] += r['dpk2'] >= 0 and r['dpk2'] < r['dpk']
                    if r['dks'] >= 0:
                        a['blind kspawn'] += 1
                        a['blind kspawn nearer'] += r['dks2'] < r['dks']
                        a['blind kspawn sum'] += r['dks']
                else:
                    took = r['ate'] > 0 or (r['dpv2'] >= 0 and r['dpv2'] < r['dpv'])
                    a['view took'] += took
                    a['view ate'] += r['ate'] > 0
                    dm, df, dv = r.get('dm', -1), r.get('df', -1), r['dpv']
                    who = ('mate nearer' + (' (queen)' if r.get('mq') else ' (other)')) if 0 <= dm < dv else 'enemy nearer' if 0 <= df < dv else 'mate level' if dm == dv else 'self 7+ steps' if dv >= 7 else 'self within 6'
                    a['who ' + who] += 1
                    if not took:
                        a['not ' + who] += 1
                        a['not nearer centre'] += r['cd2'] < r['cd']
                        a['not nearer unseen'] += r['du'] >= 0 and r['du2'] < r['du']
    for (grp, name), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        b, v = a['blind'], a['view']
        nt = v - a['view took']
        print('%-9s | %-24s | turns %d: move %s split %s none %s | pearls in view a turn %.2f | to nearest spawn tile %.1f, to centre %.1f' % (
            grp, name, a['turns'], pct(a['act m'], a['turns']), pct(a['act s'], a['turns']), pct(a['act n'], a['turns']),
            a['sum np'] / max(a['turns'], 1), a['sum dsp'] / max(a['turns'], 1), a['sum cd'] / max(a['turns'], 1)))
        print('     no pearl in view %d (%s of moves): nearer centre %s, farther %s | nearer unseen %s | nearer spawn tile %s, farther %s, on one %s | class: pearl %s, centre+unseen %s, centre %s, unseen %s, elsewhere %s | remembered pearl %d, nearer %s | known spawn tile %d (mean %.1f steps), nearer %s' % (
            b, pct(b, a['moves']), pct(a['blind nearer centre'], b), pct(a['blind farther centre'], b), pct(a['blind nearer unseen'], b),
            pct(a['blind nearer spawn'], b), pct(a['blind farther spawn'], b), pct(a['blind on spawn'], b),
            pct(a['blind pearl'], b), pct(a['blind centre+unseen'], b), pct(a['blind centre'], b), pct(a['blind unseen'], b), pct(a['blind elsewhere'], b),
            a['blind remembered'], pct(a['blind remembered nearer'], a['blind remembered']),
            a['blind kspawn'], a['blind kspawn sum'] / max(a['blind kspawn'], 1), pct(a['blind kspawn nearer'], a['blind kspawn'])))
        print('     pearl in view %d: ate %s, ate or nearer %s | who is nearest (all): %s | not taken %d: %s | of them nearer centre %s, nearer unseen %s' % (
            v, pct(a['view ate'], v), pct(a['view took'], v),
            ', '.join('%s %d' % (k[4:], n) for k, n in sorted(a.items()) if k.startswith('who ')),
            nt, ', '.join('%s %d' % (k[4:], n) for k, n in sorted(a.items()) if k.startswith('not ') and 'nearer centre' not in k and 'nearer unseen' not in k),
            pct(a['not nearer centre'], nt), pct(a['not nearer unseen'], nt)))


def pearls(games, turns):
    acc = defaultdict(lambda: defaultdict(list))
    stat = defaultdict(lambda: defaultdict(list))
    for key, g in games.items():
        w, h = g['w'], g['h']
        cx, cy = w // 2, h // 2
        cds = [min(abs(t % w - cx), w - abs(t % w - cx)) + min(abs(t // w - cy), h - abs(t // w - cy)) for t in g['spawn']]
        for i, (ro, s, head, ln, cd) in g['starters'].items():
            for name in (lay(g), 'ALL'):
                st = stat[name]
                if s == 0:
                    st['spawn tiles'].append(len(g['spawn']))
                    st['spawn cd'].append(mean(cds))
                    st['start cd'].append(cd)
                    st['outward share'].append(mean([1 if c > cd else 0 for c in cds]))
                    st['inward share'].append(mean([1 if c < cd else 0 for c in cds]))
                    st['born r0'].append(g['nat0'])
                for n, e in enumerate(g['eats'][i][:3]):
                    if e[0] > 60:
                        continue
                    a = acc[(group(g, s), name, ro, n)]
                    a['round'].append(e[0])
                    a['d0'].append(e[5])
                    a['out'].append(1 if e[4] > cd else 0)
                    a['in'].append(1 if e[4] < cd else 0)
                    a['wall'].append(1 if e[6] >= 1 else 0)
                    a['wall2'].append(1 if e[6] >= 2 else 0)
                    a['ownhalf'].append(1 if e[8] < e[7] else 0)
                    a['nat'].append(e[2])
                    a['born0'].append(1 if e[3] == 0 and e[2] else 0)
                    a['wait'].append(e[0] - e[3])
                    a['pcd'].append(e[4])
    for name, st in sorted(stat.items()):
        print('%-24s | spawn tiles %.0f (pearls at round 0: %.1f) | their mean centre distance %.1f, the starters %.1f | spawn tiles farther from the centre than the starter %s, nearer %s' % (
            name, mean(st['spawn tiles']), mean(st['born r0']), mean(st['spawn cd']), mean(st['start cd']), pct(mean(st['outward share']), 1), pct(mean(st['inward share']), 1)))
    print('group | layout | role | n-th pearl | eaten (count) | round median | path steps from its start, median | tile farther from centre than the start, nearer | beside 1+ kelp edge, 2+ | nearer own starts than theirs | natural | born in round 0 | rounds the pearl lay, median | tile centre distance mean')
    for (grp, name, ro, n), a in sorted(acc.items()):
        print('%-9s | %-24s | %s | %d | %4d | r%s | %s | %s, %s | %s, %s | %s | %s | %s | %s | %.1f' % (
            grp, name, 'queen' if ro == 'q' else 'second', n + 1, len(a['round']), med(a['round']), med(a['d0']),
            pct(sum(a['out']), len(a['out'])), pct(sum(a['in']), len(a['in'])), pct(sum(a['wall']), len(a['wall'])), pct(sum(a['wall2']), len(a['wall2'])),
            pct(sum(a['ownhalf']), len(a['ownhalf'])), pct(sum(a['nat']), len(a['nat'])), pct(sum(a['born0']), len(a['born0'])), med(a['wait']), mean(a['pcd'])))


def route(games, turns, role):
    acc = defaultdict(lambda: defaultdict(list))
    for key, g in games.items():
        w, h = g['w'], g['h']
        per = defaultdict(list)
        for r in turns[key]:
            if r['ro'] == role:
                per[r['i']].append(r)
        for i, rows in per.items():
            s = rows[0]['s']
            for name in (lay(g), 'ALL'):
                a = acc[(group(g, s), name)]
                a['n'].append(1)
                portal = [r['r'] for r in rows if r['act'] == 'm' and min(abs(r['h'] % w - r['nh'] % w), w - abs(r['h'] % w - r['nh'] % w)) + min(abs(r['h'] // w - r['nh'] // w), h - abs(r['h'] // w - r['nh'] // w)) > 1]
                for lim in (10, 20, 40):
                    a['portal%d' % lim].append(1 if any(x <= lim for x in portal) else 0)
                seen = [r['r'] for r in rows if r['np'] > 0]
                a['first view'].append(seen[0] if seen else 99)
                for mark in (5, 10, 15, 20, 30):
                    at = [r for r in rows if r['r'] == mark]
                    if at:
                        a['ds0 %d' % mark].append(at[0]['ds0'] if at[0]['ds0'] < 1000 else 0)
                        a['cd %d' % mark].append(at[0]['cd'])
                        a['dsp %d' % mark].append(at[0]['dsp'])
                        a['dpa %d' % mark].append(at[0]['dpa'] if at[0]['dpa'] >= 0 else 30)
                        a['alive %d' % mark].append(1)
                    else:
                        a['alive %d' % mark].append(0)
                early = [r for r in rows if r['r'] <= 20]
                a['np20'].append(sum(1 for r in early if r['np'] > 0) / max(len(early), 1))
                a['back20'].append(sum(1 for r in early if r['act'] == 'm' and r['ds0'] < 1000 and r['dsp2'] > r['dsp']) / max(len(early), 1))
    print('group | layout | starters | through a portal by r10, r20, r40 | first round with a pearl in view (median) | share of turns r0-20 with a pearl in view | path steps from its start at r5, r10, r15, r20 | centre distance r10, r20 | steps to nearest spawn tile r10, r20 | steps to nearest pearl on the board r10, r20 | alive r30')
    for (grp, name), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        print('%-9s | %-24s | %3d | %s, %s, %s | r%s | %s | %.1f, %.1f, %.1f, %.1f | %.1f, %.1f | %.1f, %.1f | %.1f, %.1f | %s' % (
            grp, name, len(a['n']), pct(sum(a['portal10']), len(a['n'])), pct(sum(a['portal20']), len(a['n'])), pct(sum(a['portal40']), len(a['n'])),
            med(a['first view']), pct(mean(a['np20']), 1), mean(a['ds0 5']), mean(a['ds0 10']), mean(a['ds0 15']), mean(a['ds0 20']),
            mean(a['cd 10']), mean(a['cd 20']), mean(a['dsp 10']), mean(a['dsp 20']), mean(a['dpa 10']), mean(a['dpa 20']), pct(sum(a['alive 30']), len(a['n']))))


def paths(games, turns, prefix, role, last, side):
    first = Counter()
    for key, g in sorted(games.items()):
        if not g['map'].startswith(prefix):
            continue
        w, h = g['w'], g['h']
        per = defaultdict(list)
        for r in turns[key]:
            if r['ro'] == role and r['s'] == side and r['r'] <= last:
                per[r['i']].append(r)
        for i, rows in per.items():
            # mirror the second side onto the first (point symmetry) so all paths read from the same start
            flip = g['starters'][str(i)][2] % w > w // 2
            def xy(t):
                x, y = t % w, t // w
                return (w - 1 - x, h - 1 - y) if flip else (x, y)
            seq = []
            blind = known = 0
            for r in rows:
                if r['act'] == 'm':
                    d = 'NESW'[r['dir']] if r.get('dir', -1) >= 0 else '?'
                    if flip and d in 'NESW':
                        d = 'SWNE'['NESW'.index(d)]
                    jump = min(abs(r['h'] % w - r['nh'] % w), w - abs(r['h'] % w - r['nh'] % w)) + min(abs(r['h'] // w - r['nh'] // w), h - abs(r['h'] // w - r['nh'] // w)) > 1
                    seq.append(d.lower() if jump else d)
                else:
                    seq.append('*' if r['act'] == 's' else '.')
                if 'o' in r:
                    blind += any(o is not None and len(o) == 2 for o in r['o'])
                    known += any(o is not None and len(o) > 2 and o[16] == 1 for o in r['o'])
            s = ''.join(seq)
            first[(group(g, side), s[:4])] += 1
            print('%-9s %8d %s start %s end %s | %s | turns with an unknown portal on offer %d, a known one %d | pearls by r40 %d' % (
                group(g, side), g['gid'], 'won ' if g['won'] else 'lost', xy(rows[0]['h']), xy(rows[-1]['h']), s, blind, known,
                sum(1 for e in g['eats'][str(i)] if e[0] <= 40)))
    print('first four steps:', sorted(first.items(), key=lambda kv: (kv[0][0], -kv[1])))


def head(games, turns, last):
    acc = defaultdict(Counter)
    for key, g in games.items():
        if g['src'] == 'R' or 'face' not in g:
            continue
        facing = dict((int(i), d) for i, d in g['face'].items())
        for r in turns[key]:
            if 'o' not in r:
                continue
            hd = facing.get(r['i'], -1)
            if r['act'] == 'm' and r.get('dir', -1) >= 0:
                facing[r['i']] = r['dir']
            if r['r'] > last or r['act'] != 'm' or sum(1 for o in r['o'] if o is not None) < 2:
                continue
            sc, ps = scores(r, rel(g))
            b = best(sc)
            for name in (lay(g), 'ALL'):
                a = acc[(group(g, 0), name, 'queen' if r['ro'] == 'q' else 'second')]
                a['turns'] += 1
                a['blind turns'] += r['np'] == 0
                a['straight played'] += r.get('dir', -1) == hd
                if hd < 0 or sc[hd] is None or ps[hd] is None or 'blind' in ps[hd]:
                    continue
                a['straight on offer'] += 1
                a['model straight'] += b == hd
                top = max(s for s in sc if s is not None)
                gap = top - sc[hd]
                a['within 1'] += b != hd and gap <= 1.0
                for bonus, nm in ((1.5, 'b1.5'), (3.0, 'b3'), (6.0, 'b6')):
                    if b != hd and gap < bonus:
                        a['chg ' + nm] += 1
                        a['chg blind ' + nm] += r['np'] == 0
                        a['chg expl ' + nm] += b == r.get('dir', -1)
                        ob, ov = r['o'][b], r['o'][hd]
                        a['chg farther centre ' + nm] += ov[15] > ob[15]
                        a['chg nearer spawn ' + nm] += ov[18] < ob[18]
                        a['chg farther spawn ' + nm] += ov[18] > ob[18]
    print('group | layout | starter | move turns r0-%d with 2+ steps | straight on is on offer | it is what was played | the rebuild picks it | another step leads it by 1 point or less | step changes with +1.5; +3; +6 | of the +1.5 changes: no pearl in view, old step was the one played, new step farther from centre, nearer a spawn tile, farther from one' % last)
    for (grp, name, ro), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        n, c = a['turns'], a['chg b1.5']
        print('%-9s | %-24s | %-6s | %5d | %5d | %s | %s | %4d | %4d (%s); %4d; %4d | %s, %s, %s, %s, %s' % (
            grp, name, ro, n, a['straight on offer'], pct(a['straight played'], n), pct(a['model straight'], a['straight on offer']), a['within 1'],
            c, pct(c, n), a['chg b3'], a['chg b6'], pct(a['chg blind b1.5'], c), pct(a['chg expl b1.5'], c), pct(a['chg farther centre b1.5'], c),
            pct(a['chg nearer spawn b1.5'], c), pct(a['chg farther spawn b1.5'], c)))


def keep(games, turns, last):
    acc = defaultdict(Counter)
    for key, g in games.items():
        if 'face' not in g:
            continue
        facing = dict((int(i), d) for i, d in g['face'].items())
        w, h = g['w'], g['h']
        for r in turns[key]:
            hd = facing.get(r['i'], -1)
            if r['act'] == 'm' and r.get('dir', -1) >= 0:
                facing[r['i']] = r['dir']
            if r['r'] > last or r['act'] != 'm' or hd < 0:
                continue
            for name in (lay(g), 'ALL'):
                a = acc[(group(g, r['s']), name, 'queen' if r['ro'] == 'q' else 'second')]
                view = 'blind' if r['np'] == 0 else 'view'
                a[view] += 1
                a[view + ' straight'] += r['dir'] == hd
                a[view + ' back'] += r['dir'] == (hd ^ 2)
                if r['r'] == 0:
                    a['r0'] += 1
                    a['r0 straight'] += r['dir'] == hd
                if r['r'] <= 4:
                    a['r0-4'] += 1
                    a['r0-4 straight'] += r['dir'] == hd
    print('group | layout | starter | no pearl in view, move turns r0-%d | step straight ahead | pearl in view: turns, straight | round 0: straight ahead | rounds 0-4: straight ahead' % last)
    for (grp, name, ro), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        print('%-9s | %-24s | %-6s | %5d | %s | %5d, %s | %s of %d | %s of %d' % (
            grp, name, ro, a['blind'], pct(a['blind straight'], a['blind']), a['view'], pct(a['view straight'], a['view']),
            pct(a['r0 straight'], a['r0']), a['r0'], pct(a['r0-4 straight'], a['r0-4']), a['r0-4']))


def rel(g):
    return g['src'] == 'O'


def terms(games, turns, last, role):
    acc = defaultdict(Counter)
    for key, g in games.items():
        if g['src'] == 'R':
            continue
        for r in turns[key]:
            if 'o' not in r or r['r'] > last or r['ro'] not in role or r['act'] != 'm' or r.get('dir', -1) < 0:
                continue
            if sum(1 for o in r['o'] if o is not None) < 2:
                continue
            view = 'no pearl' if r['np'] == 0 else 'pearl'
            for name in (lay(g), 'ALL'):
                for vv in (view, 'any'):
                    a = acc[(group(g, 0), name, vv)]
                    a['n'] += 1
                    a['foe'] += r['ne'] > 0
                    sc, ps = scores(r, rel(g))
                    b = best(sc)
                    ok = b == r['dir']
                    a['fit'] += ok
                    a['fit nofoe'] += ok and r['ne'] == 0
                    a['nofoe'] += r['ne'] == 0
                    a['chance'] += 1.0 / sum(1 for o in r['o'] if o is not None)
                    a['fit nocentre'] += best(scores(r, rel(g), centre=False)[0]) == r['dir']
                    a['fit otherrel'] += best(scores(r, not rel(g))[0]) == r['dir']
                    tk = ps[r['dir']]
                    if tk is None or 'blind' in tk:
                        a['taken blind/none'] += 1
                        continue
                    a['centre on taken'] += tk['centre'] != 0.0
                    a['centre on any'] += any(p is not None and p.get('centre', 0.0) != 0.0 for p in ps)
                    if not ok:
                        continue
                    a['explained'] += 1
                    for t in ('centre', 'terr', 'unseen', 'soon', 'hot', 'pearl', 'far', 'look', 'mate', 'cramped', 'sc', 'tie', 'room'):
                        a['flip ' + t] += best(scores(r, rel(g), drop=t)[0]) != b
                    alt = [(s, k) for k, s in enumerate(sc) if s is not None and k != b and ps[k] is not None and 'blind' not in ps[k]]
                    if not alt:
                        continue
                    k2 = max(alt)[1]
                    diff = [(tk[t] - ps[k2][t], t) for t in TERMS]
                    top = max(diff)
                    a['top ' + (top[1] if top[0] > 0.5 else 'tie noise')] += 1
                    a['topn'] += 1
    for (grp, name, vv), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        n, e = a['n'], a['explained']
        print('%-9s | %-24s | %-8s | turns %d (enemy head in view %s) | rebuild names the step %s (chance %s; no enemy in view %s) | without the centre term %s | stall release %s %s | centre term on for the step taken %s, for any step %s' % (
            grp, name, vv, n, pct(a['foe'], n), pct(a['fit'], n), pct(a['chance'], n), pct(a['fit nofoe'], a['nofoe']), pct(a['fit nocentre'], n),
            'off' if grp.startswith('O') else 'on', pct(a['fit otherrel'], n), pct(a['centre on taken'], n), pct(a['centre on any'], n)))
        print('       explained %d: step changes without: %s' % (e, ', '.join('%s %s' % (k[5:], pct(v, e)) for k, v in sorted(a.items(), key=lambda kv: -kv[1]) if k.startswith('flip ') and v)))
        print('       largest term, step taken against the next best: %s' % ', '.join('%s %s' % (k[4:], pct(v, a['topn'])) for k, v in sorted(a.items(), key=lambda kv: -kv[1]) if k.startswith('top ')))


def card(games, turns, last):
    acc = defaultdict(Counter)
    for key, g in games.items():
        if g['src'] == 'R':
            continue
        fed = Counter()
        for r in turns[key]:
            if 'o' not in r:
                continue
            r['unfed'] = 1 if fed[r['i']] == 0 else 0
            if r['ate']:
                fed[r['i']] += r['ate']
            dks = [o[9] for o in r['o'] if o is not None and len(o) > 2 and o[9] >= 0]
            r['mdk'] = min(dks) - 1 if dks else -1
            if r['r'] > last or r['act'] == 's':
                continue
            if sum(1 for o in r['o'] if o is not None) < 2:
                continue
            sc, ps = scores(r, rel(g))
            b = best(sc)
            on = any(p is not None and p.get('centre', 0.0) != 0.0 for p in ps)
            for name in (lay(g), 'ALL'):
                for ro in (r['ro'], 'both'):
                    for variant in ('off', 'units2', 'units3', 'nq', 'spawn', 'unfed'):
                        a = acc[(group(g, 0), name, ro, variant)]
                        a['turns'] += 1
                        a['centre on'] += on
                        if not on:
                            continue
                        v = best(scores(r, rel(g), centre=(variant != 'off'), variant=variant)[0])
                        still = any(p is not None and p.get('centre', 0.0) != 0.0 for p in scores(r, rel(g), centre=(variant != 'off'), variant=variant)[1])
                        a['rule off'] += not still
                        if v == b:
                            continue
                        a['changed'] += 1
                        a['changed explained'] += b == r.get('dir', -9)
                        ob, ov = r['o'][b], r['o'][v]
                        if len(ob) == 2 or len(ov) == 2:
                            a['changed blind'] += 1
                            continue
                        a['cmp'] += 1
                        a['nearer spawn'] += ov[18] < ob[18]
                        a['farther spawn'] += ov[18] > ob[18]
                        a['nearer pearl'] += ov[19] < ob[19]
                        a['farther pearl'] += ov[19] > ob[19]
                        a['nearer unseen'] += 0 <= ov[7] < ob[7]
                        a['farther centre'] += ov[15] > ob[15]
                        a['d spawn'] += ov[18] - ob[18] if max(ov[18], ob[18]) < 1000 else 0
                        a['d pearl'] += ov[19] - ob[19] if max(ov[19], ob[19]) < 1000 else 0
    print('group | layout | starter | variant | turns with 2+ steps on offer r0-%d | centre term on | rule switched off by the variant | step changes | of them the old step was the one played | new step: nearer a spawn tile, farther | nearer the nearest pearl on the board, farther | nearer an unseen tile | farther from the centre' % last)
    for (grp, name, ro, variant), a in sorted(acc.items()):
        if not show(grp, name):
            continue
        c = a['cmp']
        print('%-9s | %-24s | %-4s | %-6s | %5d | %5d (%s) | %5d | %4d (%s of turns) | %s | %s, %s | %s, %s | %s | %s' % (
            grp, name, ro, variant, a['turns'], a['centre on'], pct(a['centre on'], a['turns']), a['rule off'], a['changed'], pct(a['changed'], a['turns']),
            pct(a['changed explained'], a['changed']), pct(a['nearer spawn'], c), pct(a['farther spawn'], c), pct(a['nearer pearl'], c), pct(a['farther pearl'], c),
            pct(a['nearer unseen'], c), pct(a['farther centre'], c)))


def cmap():
    seen = {}
    for f in ('per-game.jsonl', 'target/per-game-top1.jsonl'):
        for line in (DOS / f).read_text().splitlines():
            r = json.loads(line)
            st = r['all_starting_dragons']['us']
            seen[(r['map_name'], r['width'], r['height'])] = sorted(d['length'] for d in st)
    for (name, w, h), st in sorted(seen.items(), key=lambda kv: kv[0][1] * kv[0][2]):
        n = w * h
        long_map = w >= 2 * h
        on = n <= 1000 and (long_map or n <= 700)
        print('%-18s %3dx%-3d %5d cells | start %s | center_map %s | rounds %s | wide %s | tall (h >= 2w) %s' % (
            name, w, h, n, st, 'ON' if on else 'off', (60 if long_map else 30) if on else '-', long_map, h >= 2 * w))


def view(games, turns, gid, last):
    for key, g in games.items():
        if g['gid'] != gid:
            continue
        w = g['w']
        print(g['gid'], g['src'], g['arm'], lay(g), 'opp', g['opp'], 'won', g['won'], 'center_map', g['cm'], g['cr'], 'starters', g['starters'])
        print('eats', {i: [(e[0], (e[1] % w, e[1] // w)) for e in v] for i, v in g['eats'].items()})
        print('marks', g['marks'])
        for r in turns[key]:
            if r['r'] > last:
                continue
            xy = lambda t: '(%d,%d)' % (t % w, t // w) if t >= 0 else '-'
            line = 'r%-2d #%d %s s%d L%d %s cd%d np%d dpv%d dpa%d du%d dsp%d al%d/%d st%d %s->%s%s' % (
                r['r'], r['i'], r['ro'], r['s'], r['L'], xy(r['h']), r['cd'], r['np'], r['dpv'], r['dpa'], r['du'], r['dsp'], r['al'], r['op'], r['st'], r['act'], xy(r['nh']),
                ' ATE' if r['ate'] else '')
            if 'o' in r and r['act'] == 'm':
                sc, ps = scores(r, rel(g))
                b = best(sc)
                line += ' | dir %s model %s' % ('NESW'[r['dir']] if r['dir'] >= 0 else '?', 'NESW'[b] if b >= 0 else '?')
                for k in range(4):
                    if ps[k] is None:
                        continue
                    line += ' | %s %.0f [' % ('NESW'[k], sc[k]) + ' '.join('%s %.0f' % (t[:4], v) for t, v in ps[k].items() if abs(v) >= 0.5 and t != 'room') + ']'
            print(line)


def main():
    cmd = sys.argv[1]
    if cmd == 'cmap':
        cmap()
        return
    games, turns = load()
    print('games', Counter((g['src'], g['arm']) for g in games.values()))
    if cmd == 'tally':
        tally(games, turns)
    elif cmd == 'class':
        classes(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 40, sys.argv[3] if len(sys.argv) > 3 else 'o')
    elif cmd == 'pearls':
        pearls(games, turns)
    elif cmd == 'terms':
        terms(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 40, sys.argv[3] if len(sys.argv) > 3 else 'o')
    elif cmd == 'card':
        card(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == 'route':
        route(games, turns, sys.argv[3] if len(sys.argv) > 3 else 'o')
    elif cmd == 'paths':
        paths(games, turns, sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == 'head':
        head(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == 'keep':
        keep(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == 'view':
        view(games, turns, int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 40)


main()
