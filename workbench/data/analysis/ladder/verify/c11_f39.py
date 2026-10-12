#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 11 (run of 2026-10-07 11:17 KST), F39: death rate of our lone queen by how many short dragons
an opponent brings within 12 path steps of her at her fresh turns. Reads the x11 shards (own extraction from the raw
replays) and writes f39-1117-numbers.txt. maps.json is read for the dead-end flag of a layout; rows.jsonl is read
only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15'
LINES = []
REASON = ['wall', 'own body', 'other dragon body', 'head-on', 'other']
BY = ['nobody', 'own side', 'other side', 'unresolved']


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def f(x, d=2):
    return 'n/a' if x is None else ('%.' + str(d) + 'f') % x


def lone_stats(g, s, lim=20, same_round=False):
    od = g['qdeath'][1 - s]
    if od is None:
        return None
    d_other = od['round']
    me = g['qdeath'][s]
    my_d = me['round'] if me else None
    T = F = S = Fx = Sx = n_all = n6 = n12 = 0
    last = None
    for r in g['lone']:
        if r[0] != s:
            continue
        rnd = r[1]
        if r[7] > 0:
            last = rnd
        if rnd < d_other or (rnd == d_other and not same_round):
            continue
        n_all += 1
        if r[4] > 0:
            n6 += 1
        if r[3] > 0:
            n12 += 1
        if rnd < 100:
            continue
        T += 1
        if last is not None and rnd - last <= lim:
            F += 1
            S += r[3]
            if my_d is None or rnd < my_d - 20:
                Fx += 1
                Sx += r[3]
    D = 1 if (my_d is not None and my_d >= 100 and d_other < my_d) else 0
    return dict(T=T, F=F, S=S, D=D, Fx=Fx, Sx=Sx, n_all=n_all, n6=n6, n12=n12,
                reason=me['reason'] if D else None, by=me['by'] if D else None)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x11-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
    games = [g for g in games if 'error' not in g]
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo') or 0
        g['band'] = 'under 1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100 on'
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['half'] = 1 if g['completedAt'][:19] < CUT else 2
        g['p1'] = g['map_key'] == 'Portals #1'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['ls'] = [lone_stats(g, 0), lone_stats(g, 1)]
    return order, bad, maps


def pairs_of(gs, s=0, getter=None):
    pr = {}
    for g in gs:
        key = (g['opponentId'], g['code'])
        p = pr.get(key)
        if p is None:
            p = dict(key=key, opp=g['opp'], code=g['code'], games=0, lone_games=0, T=0, F=0, S=0, D=0, Fx=0, Sx=0,
                     Fs=0, Ss=0, elo=[], gl=[], reasons=Counter(), bys=Counter(), dates=Counter())
            pr[key] = p
        p['games'] += 1
        p['elo'].append(g.get('opponentElo') or 0)
        st = getter(g) if getter else g['ls'][s]
        p['gl'].append((g, st))
        if st is None:
            continue
        if st['T'] > 0:
            p['lone_games'] += 1
        for k in ('T', 'F', 'S', 'D', 'Fx', 'Sx'):
            p[k] += st[k]
        if not st['D']:
            p['Fs'] += st['F']
            p['Ss'] += st['S']
        else:
            p['reasons'][REASON[st['reason']]] += 1
            p['bys'][BY[st['by']]] += 1
            p['dates'][(g.get('at_kst') or '')[:13]] += 1
    return pr


def kind_of(p, a_cut=3.0, b_cut=1.5, min_f=150, fk='F', sk='S'):
    if p[fk] < min_f:
        return 'small'
    bring = p[sk] / p[fk]
    return 'A' if bring >= a_cut else 'B' if bring < b_cut else 'mid'


def agg(ps):
    return sum(p['D'] for p in ps), sum(p['T'] for p in ps)


def rate(ps):
    d, t = agg(ps)
    return 1000 * d / t if t else None


def rline(ps):
    d, t = agg(ps)
    return '%d pairs (main %d, v31 %d): %d deaths in %d lone turns, %s per 1,000' % (
        len(ps), sum(1 for p in ps if p['code'] == 'main'), sum(1 for p in ps if p['code'] == 'v31'), d, t, f(1000 * d / t if t else None))


def rr(A, B):
    da, ta = agg(A)
    db, tb = agg(B)
    if not da or not db or not ta or not tb:
        return None, None, None
    r = (da / ta) / (db / tb)
    se = math.sqrt(1 / da + 1 / db)
    return r, r * math.exp(-1.96 * se), r * math.exp(1.96 * se)


def spearman(xs, ys):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def main():
    games, bad, maps = load()
    say('games read', len(games), 'errors', len(bad), '; final state equals the result block in',
        sum(1 for g in games if g['final_ok']), '; games with anomalies', sum(1 for g in games if g['anomalies']))
    SET = [g for g in games if g['code'] in ('main', 'v31') and g['free'] and not g['p1']]
    say('games in the set (main or v31, free layout, not Portals #1):', len(SET), dict(Counter(g['code'] for g in SET)))
    pr = pairs_of(SET)
    kinds = defaultdict(list)
    for p in pr.values():
        kinds[kind_of(p)].append(p)
    A, B, MID, SMALL = kinds['A'], kinds['B'], kinds['mid'], kinds['small']
    say('')
    say('=== 1. the claim as defined (lone turn = round after their queen died; fresh = seen within 20 rounds) ===')
    say('all pairs:', rline(list(pr.values())), '; fresh turns', sum(p['F'] for p in pr.values()))
    say('kind A (bring 3.0 or more):', rline(A))
    say('kind B (bring under 1.5): ', rline(B))
    say('between:                  ', rline(MID))
    say('under 150 fresh turns:    ', rline(SMALL))
    r, lo, hi = rr(A, B)
    say('rate ratio A over B: %s (95 percent by death counts alone %s to %s)' % (f(r), f(lo), f(hi)))
    for code in ('main', 'v31'):
        a = [p for p in A if p['code'] == code]
        b = [p for p in B if p['code'] == code]
        m = [p for p in MID if p['code'] == code]
        r, lo, hi = rr(a, b)
        say('%s: A %s | B %s | between %s | ratio %s (%s to %s)' % (code, rline(a), rline(b), rline(m), f(r), f(lo), f(hi)))
    say('')
    say('--- every pair with 150 or more fresh turns, by bring ---')
    big = sorted([p for p in pr.values() if p['F'] >= 150], key=lambda p: -p['S'] / p['F'])
    for p in big:
        say('    %-34s %-4s rating %4.0f  games %2d (lone %2d)  fresh %4d  bring %s  lone turns %4d  deaths %2d  rate %5s  kind %s  causes %s by %s' % (
            p['opp'][:34], p['code'], sum(p['elo']) / len(p['elo']), p['games'], p['lone_games'], p['F'], f(p['S'] / p['F']), p['T'], p['D'],
            f(1000 * p['D'] / p['T'] if p['T'] else None, 1), kind_of(p), dict(p['reasons']), dict(p['bys'])))
    say('')
    say('--- one opponent ---')
    byd = sorted(A, key=lambda p: -p['D'])
    top = byd[0]
    rest = [p for p in A if p is not top]
    say('kind A, the pair with the most deaths: %s %s, %d deaths in %d turns; without it: %s; ratio to B %s' % (
        top['opp'], top['code'], top['D'], top['T'], rline(rest), f(rr(rest, B)[0])))
    oppd = Counter()
    for p in A:
        oppd[p['key'][0]] += p['D']
    oid = oppd.most_common(1)[0][0]
    rest2 = [p for p in A if p['key'][0] != oid]
    say('kind A, the opponent (both codes) with the most deaths: %s, %d deaths; without it: %s; ratio to B %s' % (oid, oppd[oid], rline(rest2), f(rr(rest2, B)[0])))
    rs = []
    for p in A + B:
        a = [q for q in A if q is not p]
        b = [q for q in B if q is not p]
        rs.append((rr(a, b)[0], p['opp'], p['code']))
    rs.sort()
    say('one pair left out at a time (A and B): ratio %s (without %s %s) to %s (without %s %s)' % (f(rs[0][0]), rs[0][1], rs[0][2], f(rs[-1][0]), rs[-1][1], rs[-1][2]))
    a3 = sorted(A, key=lambda p: -p['D'])[3:]
    say('without the three A pairs with the most deaths: %s; ratio %s' % (rline(a3), f(rr(a3, B)[0])))
    a_cur, b_cur = list(A), list(B)
    dropped = []
    for _ in range(3):
        best = None
        for p in a_cur + b_cur:
            a = [q for q in a_cur if q is not p]
            b = [q for q in b_cur if q is not p]
            v = rr(a, b)[0]
            if v is not None and (best is None or v < best[0]):
                best = (v, p)
        dropped.append('%s %s' % (best[1]['opp'], best[1]['code']))
        a_cur = [q for q in a_cur if q is not best[1]]
        b_cur = [q for q in b_cur if q is not best[1]]
    say('without the three pairs whose removal lowers the ratio most (%s): A %s | B %s | ratio %s' % ('; '.join(dropped), rline(a_cur), rline(b_cur), f(rr(a_cur, b_cur)[0])))
    say('')
    say('--- chance, with the pair as the unit ---')
    obs = rr(A, B)[0]
    rng = random.Random(17)
    pool = A + B
    hi_n = done = 0
    for _ in range(10000):
        idx = list(range(len(pool)))
        rng.shuffle(idx)
        a = [pool[i] for i in idx[:len(A)]]
        b = [pool[i] for i in idx[len(A):]]
        da, ta = agg(a)
        db, tb = agg(b)
        if not db or not ta:
            continue
        done += 1
        if (da / ta) / (db / tb) >= obs - 1e-12:
            hi_n += 1
    say('kind labels shuffled among the %d A and B pairs: ratio %s, %d of %d shuffles at least as large' % (len(pool), f(obs), hi_n, done))
    hi_n = done = 0
    for _ in range(10000):
        a, b = [], []
        for code in ('main', 'v31'):
            sub = [p for p in pool if p['code'] == code]
            na = sum(1 for p in A if p['code'] == code)
            idx = list(range(len(sub)))
            rng.shuffle(idx)
            a += [sub[i] for i in idx[:na]]
            b += [sub[i] for i in idx[na:]]
        da, ta = agg(a)
        db, tb = agg(b)
        if not db or not ta:
            continue
        done += 1
        if (da / ta) / (db / tb) >= obs - 1e-12:
            hi_n += 1
    say('the same with labels shuffled inside each code: %d of %d at least as large' % (hi_n, done))
    out = []
    for _ in range(4000):
        a = [A[rng.randrange(len(A))] for _ in A]
        b = [B[rng.randrange(len(B))] for _ in B]
        v = rr(a, b)[0]
        if v is not None:
            out.append(v)
    out.sort()
    say('pairs resampled inside each kind, ratio 95 percent: %s to %s (%d resamples with a ratio)' % (f(out[int(0.025 * len(out))]), f(out[int(0.975 * len(out))]), len(out)))
    xs = [p['S'] / p['F'] for p in big]
    ys = [p['D'] / p['T'] for p in big]
    sp = spearman(xs, ys)
    cnt = 0
    for _ in range(10000):
        yy = list(ys)
        rng.shuffle(yy)
        if spearman(xs, yy) >= sp - 1e-12:
            cnt += 1
    say('rank correlation of bring and death rate over the %d pairs with 150 or more fresh turns: %s; %d of 10,000 shuffles at least as large' % (len(big), f(sp), cnt))
    for code in ('main', 'v31'):
        sub = [p for p in big if p['code'] == code]
        say('    %s: %d pairs, rank correlation %s' % (code, len(sub), f(spearman([p['S'] / p['F'] for p in sub], [p['D'] / p['T'] for p in sub]))))
    say('')
    say('--- the cuts (3.0, 1.5, 150) ---')
    for min_f in (100, 150, 200, 300):
        for a_cut, b_cut in ((3.0, 1.5), (2.5, 1.5), (3.5, 1.5), (3.0, 2.0), (3.0, 1.0), (2.5, 2.5), (2.0, 2.0)):
            a = [p for p in pr.values() if kind_of(p, a_cut, b_cut, min_f) == 'A']
            b = [p for p in pr.values() if kind_of(p, a_cut, b_cut, min_f) == 'B']
            da, ta = agg(a)
            db, tb = agg(b)
            say('    fresh %d or more, A from %.1f, B under %.1f: A %d pairs %d in %d (%s) | B %d pairs %d in %d (%s) | ratio %s' % (
                min_f, a_cut, b_cut, len(a), da, ta, f(1000 * da / ta if ta else None), len(b), db, tb, f(1000 * db / tb if tb else None), f(rr(a, b)[0])))
    say('thirds of the %d pairs by bring:' % len(big))
    n3 = len(big) // 3
    for lab, sub in (('top third', big[:n3]), ('middle', big[n3:len(big) - n3]), ('bottom third', big[len(big) - n3:])):
        say('    %s: %s; bring %s to %s' % (lab, rline(sub), f(sub[-1]['S'] / sub[-1]['F']), f(sub[0]['S'] / sub[0]['F'])))
    say('')
    say('--- is bring just the kill being counted? ---')
    for lab, fk, sk in (('bring from fresh turns more than 20 rounds before her death (and all fresh turns of games she survives)', 'Fx', 'Sx'),
                        ('bring from games in which she does not die as a lone queen', 'Fs', 'Ss')):
        for min_f in (150, 100):
            a = [p for p in pr.values() if kind_of(p, 3.0, 1.5, min_f, fk, sk) == 'A']
            b = [p for p in pr.values() if kind_of(p, 3.0, 1.5, min_f, fk, sk) == 'B']
            m = [p for p in pr.values() if kind_of(p, 3.0, 1.5, min_f, fk, sk) == 'mid']
            say('%s, %d or more such turns: A %s | B %s | between %s | ratio %s' % (lab, min_f, rline(a), rline(b), rline(m), f(rr(a, b)[0])))
    say('how much the last 20 rounds weigh: A pairs bring %s with them and %s without; B pairs %s and %s' % (
        f(sum(p['S'] for p in A) / sum(p['F'] for p in A)), f(sum(p['Sx'] for p in A) / max(1, sum(p['Fx'] for p in A))),
        f(sum(p['S'] for p in B) / sum(p['F'] for p in B)), f(sum(p['Sx'] for p in B) / max(1, sum(p['Fx'] for p in B)))))
    # split halves: kind from one half of a pair's games, deaths and turns from the other half
    tot = {'A': [0, 0, 0], 'B': [0, 0, 0], 'mid': [0, 0, 0]}
    for p in pr.values():
        gl = sorted(p['gl'], key=lambda x: x[0]['game'])
        halves = [[x for i, x in enumerate(gl) if i % 2 == 0], [x for i, x in enumerate(gl) if i % 2 == 1]]
        for h in (0, 1):
            F = sum(x[1]['F'] for x in halves[h] if x[1])
            S = sum(x[1]['S'] for x in halves[h] if x[1])
            if F < 75:
                continue
            bring = S / F
            k = 'A' if bring >= 3.0 else 'B' if bring < 1.5 else 'mid'
            tot[k][0] += sum(x[1]['D'] for x in halves[1 - h] if x[1])
            tot[k][1] += sum(x[1]['T'] for x in halves[1 - h] if x[1])
            tot[k][2] += 1
    say('split halves (kind from every other game of a pair with 75 or more fresh turns there, deaths and turns from the remaining games): A %d in %d (%s) from %d half-pairs | B %d in %d (%s) from %d | between %d in %d (%s) from %d | ratio %s' % (
        tot['A'][0], tot['A'][1], f(1000 * tot['A'][0] / tot['A'][1] if tot['A'][1] else None), tot['A'][2],
        tot['B'][0], tot['B'][1], f(1000 * tot['B'][0] / tot['B'][1] if tot['B'][1] else None), tot['B'][2],
        tot['mid'][0], tot['mid'][1], f(1000 * tot['mid'][0] / tot['mid'][1] if tot['mid'][1] else None), tot['mid'][2],
        f((tot['A'][0] / tot['A'][1]) / (tot['B'][0] / tot['B'][1]) if tot['A'][1] and tot['B'][0] else None)))
    say('')
    say('--- layouts ---')
    lay = defaultdict(lambda: [0, 0])
    for g in SET:
        st = g['ls'][0]
        if st:
            lay[(g['code'], g['map_key'])][0] += st['D']
            lay[(g['code'], g['map_key'])][1] += st['T']
    lay2 = defaultdict(lambda: [0, 0])
    for (c, k), v in lay.items():
        lay2[k][0] += v[0]
        lay2[k][1] += v[1]
    say('deaths per 1,000 lone turns by layout (both codes): ' + '; '.join('%s %d in %d (%s)' % (k, v[0], v[1], f(1000 * v[0] / v[1] if v[1] else None, 1)) for k, v in sorted(lay2.items())))
    for lab, ps in (('A', A), ('B', B), ('between', MID)):
        exp_c = exp_p = 0.0
        d = 0
        tl = Counter()
        for p in ps:
            for g, st in p['gl']:
                if st is None:
                    continue
                d += st['D']
                tl[g['map_key']] += st['T']
                v = lay[(g['code'], g['map_key'])]
                exp_c += st['T'] * v[0] / v[1] if v[1] else 0
                v2 = lay2[g['map_key']]
                exp_p += st['T'] * v2[0] / v2[1] if v2[1] else 0
        say('kind %s: deaths seen %d; expected from its layouts at the all-pairs rate of the same code %s (seen over expected %s); at the both-codes layout rate %s (%s); its lone turns by layout: %s' % (
            lab, d, f(exp_c, 1), f(d / exp_c if exp_c else None), f(exp_p, 1), f(d / exp_p if exp_p else None),
            ', '.join('%s %d' % (k, v) for k, v in tl.most_common(6))))
    say('')
    say('--- what the deaths are ---')
    for lab, ps in (('A', A), ('B', B), ('between', MID)):
        rs_ = Counter()
        bs_ = Counter()
        dt = Counter()
        for p in ps:
            rs_.update(p['reasons'])
            bs_.update(p['bys'])
            dt.update(p['dates'])
        lg = sum(p['lone_games'] for p in ps)
        d, t = agg(ps)
        say('kind %s: by engine reason %s; killed by %s; games with lone turns from r100 %d, she dies in %s of them; lone turns a lone game %s; mean rating %s; deaths by KST hour %s' % (
            lab, dict(rs_), dict(bs_), lg, f(d / lg if lg else None), f(t / lg if lg else None, 1),
            f(sum(sum(p['elo']) for p in ps) / max(1, sum(len(p['elo']) for p in ps)), 0), dict(sorted(dt.items()))))
        de, te = sum(p['bys'].get('other side', 0) for p in ps), t
        say('    deaths at the hands of the other side per 1,000 lone turns: %s (%d)' % (f(1000 * de / te if te else None), de))
    say('')
    say('=== 2. game results per kind ===')
    allg = defaultdict(lambda: [0, 0, 0, 0])
    for g in games:
        v = allg[(g['opponentId'], g['code'])]
        v[1] += 1
        v[0] += 1 if g['win'] else 0
        if g['free'] and not g['p1']:
            v[3] += 1
            v[2] += 1 if g['win'] else 0
    for lab, ps in (('A', A), ('between', MID), ('B', B), ('under 150 fresh turns', SMALL)):
        w = sum(allg[p['key']][0] for p in ps)
        n = sum(allg[p['key']][1] for p in ps)
        w2 = sum(allg[p['key']][2] for p in ps)
        n2 = sum(allg[p['key']][3] for p in ps)
        se = math.sqrt((w / n) * (1 - w / n) / n) if n else 0
        parts = []
        for code in ('main', 'v31'):
            wc = sum(allg[p['key']][0] for p in ps if p['code'] == code)
            nc = sum(allg[p['key']][1] for p in ps if p['code'] == code)
            parts.append('%s %d of %d' % (code, wc, nc))
        say('kind %s: wins %d of %d games (%s, plus or minus %s) on all layouts; %d of %d on the layouts of the set; %s; mean rating %s' % (
            lab, w, n, f(w / n if n else None, 3), f(1.96 * se, 3), w2, n2, ', '.join(parts),
            f(sum(sum(p['elo']) for p in ps) / max(1, sum(len(p['elo']) for p in ps)), 0)))
    say('')
    say('=== 3. the 6-step flag in the new main games ===')
    for lab, pred in (('free layouts without Portals #1', lambda g: g['free'] and not g['p1']), ('free layouts with Portals #1', lambda g: g['free'])):
        new = [g for g in games if g['code'] == 'main' and pred(g) and int(g['battle']) > 1289717]
        for sr in (False, True):
            tot1 = [0, 0]
            tot0 = [0, 0]
            for g in new:
                a = lone_stats(g, 0, 20, sr)
                b = lone_stats(g, 1, 20, sr)
                if a:
                    tot1[0] += a['n6']
                    tot1[1] += a['n_all']
                if b:
                    tot0[0] += b['n6']
                    tot0[1] += b['n_all']
            say('%s, %d main games after battle 1289717, lone turn %s: a short enemy head within 6 path steps in %d of %d of our lone-queen turns and %d of %d of theirs' % (
                lab, len(new), 'from the round the other queen died' if sr else 'from the round after', tot1[0], tot1[1], tot0[0], tot0[1]))
    say('battles after 1289717 in the data:', sorted(set(g['battle'] for g in games if int(g['battle']) > 1289717)))
    say('')
    say('=== 4. the definition, read the other way ===')
    for lab, lim, sr in (('lone turn from the round their queen died (same round counted)', 20, True), ('fresh = seen within 19 rounds', 19, False)):
        pr2 = pairs_of(SET, 0, lambda g: lone_stats(g, 0, lim, sr))
        a = [p for p in pr2.values() if kind_of(p) == 'A']
        b = [p for p in pr2.values() if kind_of(p) == 'B']
        m = [p for p in pr2.values() if kind_of(p) == 'mid']
        say('%s: A %s | B %s | between %s' % (lab, rline(a), rline(b), rline(m)))
    say('')
    say('=== 5. the same count for their lone queen (our short dragons near her), for scale ===')
    pt = pairs_of(SET, 1)
    ka = [p for p in pt.values() if kind_of(p) == 'A']
    kb = [p for p in pt.values() if kind_of(p) == 'B']
    km = [p for p in pt.values() if kind_of(p) == 'mid']
    say('their lone queen, all pairs: %s' % rline(list(pt.values())))
    say('pairs where WE bring 3.0 or more: %s | under 1.5: %s | between: %s' % (rline(ka), rline(kb), rline(km)))
    say('')
    say('=== 6. compare with rows.jsonl (read last) ===')
    rows = {}
    for ln in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            rows[r['game']] = r
    agree = Counter()
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            agree['missing in rows'] += 1
            continue
        code = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        ok = (code == g['code'] and r['map_key'] == g['map_key'] and r['win'] == g['win'] and r['last_round'] == g['last_round']
              and r['queen']['us']['death_round'] == (g['qdeath'][0]['round'] if g['qdeath'][0] else None)
              and r['queen']['them']['death_round'] == (g['qdeath'][1]['round'] if g['qdeath'][1] else None)
              and r['opponent_id'] == g.get('opponentId'))
        agree['agree' if ok else 'differ'] += 1
    say('code, layout, winner, last round, queen death rounds and opponent against rows.jsonl:', dict(agree))
    for lab, ps in (('A', A), ('between', MID), ('B', B)):
        w = n = 0
        keys = set(p['key'] for p in ps)
        for r in rows.values():
            code = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
            if (r['opponent_id'], code) in keys:
                n += 1
                w += 1 if r['win'] else 0
        say('kind %s wins by rows.jsonl: %d of %d' % (lab, w, n))
    out = open(P + 'f39-1117-numbers.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
