# Scratch (diag-hungry): reads hg_scan-<arm>-*.jsonl and prints the spell account, the motion of hungry dragons and
# how often the step taken is the best step by each rebuilt term (territory T, target pearl dp, never-seen tile du).
# Usage: python3 data/analysis/ladder/dossier/work/hg_agg.py <arm|test> [section ...]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

WORK = 'data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
REASON = {0: 'wall', 1: 'own body', 2: 'other body', 3: 'head-on', 4: 'no action'}


def load(arm):
    games, rows = {}, defaultdict(list)
    names = [WORK + 'hg_scan-test.jsonl'] if arm == 'test' else [WORK + 'hg_scan-%s-%d.jsonl' % (arm, s) for s in range(4)]
    for nm in names:
        with open(nm) as f:
            for line in f:
                j = json.loads(line)
                if j.get('kind') == 'game':
                    games[j['gi']] = j
                else:
                    rows[j['g']].append(j)
    return games, rows


def kind_of(game):
    q = game.split('-seed')[0].split('_')
    if q[0] == 'ladder':
        return 'ladder'
    return q[1]


def size_of(g):
    n = g['w'] * g['h']
    return 'small' if n <= 700 else 'medium' if n <= 1600 else 'large'


def chosen_dir(r, w, h):
    if not r['path']:
        return -1
    x, y = r['h'] % w, r['h'] // w
    nx, ny = r['path'][0] % w, r['path'][0] // w
    cand = [d for d in range(4) if r['dirs'][d] is not None]
    for d in cand:
        dx, dy = STEP[d]
        if ((x + dx) % w, (y + dy) % h) == (nx, ny) and not r['dirs'][d][5]:
            return d
    port = [d for d in cand if r['dirs'][d][5]]
    if len(port) == 1:
        return port[0]
    return -2


def situation(r):
    if r['box'] < 7:
        return 'boxed in (under 6 free tiles)'
    if r['np'] > 0:
        if r['nt'] > 0:
            d = r['bt'][0]
            return 'pearl in view, a target: ' + ('beside the head' if d <= 1 else '2-3 steps' if d <= 3 else '4-6 steps' if d <= 6 else '7-12 steps')
        if r['nmn'] > 0:
            return 'pearl in view, no target: a team mate is nearer'
        if r['nen'] > 0:
            return 'pearl in view, no target: an enemy is nearer'
        return 'pearl in view, no target: walled off or over 12 steps'
    return 'nothing in view, ' + ('no team mate in view' if r['nm'] == 0 else 'team mates in view')


def spells_of(rs):
    by = defaultdict(list)
    for r in rs:
        by[r['i']].append(r)
    out = []
    for i, lst in by.items():
        lst.sort(key=lambda r: r['r'])
        cur = [lst[0]]
        for r in lst[1:]:
            if r['idle'] < cur[-1]['idle']:
                out.append(cur)
                cur = [r]
            else:
                cur.append(r)
        out.append(cur)
    return out


def tgap(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '-'


def main():
    arm = sys.argv[1]
    games, rows = load(arm)
    print('games', len(games), 'spell turns', sum(len(v) for v in rows.values()))
    # ---- the 3b table, local
    print('\n== rounds since last meal (short dragons, rounds 0-300): ours | local opponent; equal weight per map and pooled')
    per_map = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    for g in games.values():
        mp = g['game'].split('-seed')[0]
        for s, band, b, view, turns, pearls, deaths in g['acc']:
            v = per_map[mp][(s, b)]
            v[0] += turns
            v[1] += turns if view == 0 else 0
            v[2] += pearls
            v[3] += deaths
    for b in range(5):
        cells = []
        for s in (0, 1):
            sh, nv, pe, de = [], [], [], []
            tt = [0, 0, 0, 0, 0]
            for mp, d in per_map.items():
                tot = sum(d[(s, bb)][0] for bb in range(5))
                v = d[(s, b)]
                if tot:
                    sh.append(100.0 * v[0] / tot)
                if v[0]:
                    nv.append(100.0 * v[1] / v[0])
                    pe.append(1000.0 * v[2] / v[0])
                    de.append(1000.0 * v[3] / v[0])
                tt[0] += tot
                for z in range(4):
                    tt[z + 1] += v[z]
            cells.append('share %.1f (pooled %.1f) noview %.1f pearls/1000 %.0f deaths/1000 %.0f' % (mean(sh), 100.0 * tt[1] / tt[0], mean(nv), mean(pe), mean(de)))
        print(('0-3', '4-10', '11-25', '26-60', '61+')[b], '|', cells[0], '|', cells[1])
    for s in (0, 1):
        sh = []
        hi = []
        for mp, d in per_map.items():
            tot = sum(d[(s, bb)][0] for bb in range(5))
            sh.append(100.0 * (d[(s, 3)][0] + d[(s, 4)][0]) / tot)
            nvall = sum(d[(s, bb)][1] for bb in range(5))
            hi.append(100.0 * (d[(s, 3)][1] + d[(s, 4)][1]) / max(1, nvall))
        print('side', s, 'share of short turns at 26+: mean per map %.1f, min %.1f, max %.1f; share of no-view turns held by them %.1f' % (mean(sh), min(sh), max(sh), mean(hi)))
    # by band
    for s in (0, 1):
        bt = defaultdict(lambda: [0, 0])
        for g in games.values():
            for ss, band, b, view, turns, pearls, deaths in g['acc']:
                if ss == s:
                    bt[band][0] += turns
                    bt[band][1] += turns if b >= 3 else 0
        print('side', s, 'by rounds 0-100, 101-200, 201-300: share at 26+', [pct(bt[z][1], bt[z][0]) for z in range(3)], 'turns', [bt[z][0] for z in range(3)])
    # ---- spells
    print('\n== spells')
    allsp = []
    per_game = {}
    for gi, g in games.items():
        sp = spells_of(rows.get(gi, []))
        per_game[gi] = sp
        for s in sp:
            allsp.append((gi, s))
    print('spells', len(allsp), 'per game mean %.1f median %.1f' % (mean(len(v) for v in per_game.values()), median(len(v) for v in per_game.values())))
    ln = [s[-1]['idle'] for gi, s in allsp]
    print('rounds without a meal at the end of the spell: median %d, mean %.1f, 60+ %s, 100+ %s' % (median(ln), mean(ln), pct(sum(x >= 60 for x in ln), len(ln)), pct(sum(x >= 100 for x in ln), len(ln))))
    ends = Counter()
    for gi, s in allsp:
        r = s[-1]
        g = games[gi]
        if r['ate']:
            e = 'ate'
        elif r['died'] >= 0:
            e = 'died: ' + REASON.get(r['died'] % 10, '?')
        elif r['r'] >= 299 or r['r'] >= g['rounds'] - 1:
            e = 'still hungry at round 300 or the end'
        else:
            e = 'other'
        ends[e] += 1
    print('ends', [(k, v, pct(v, len(allsp))) for k, v in ends.most_common()])
    kk = defaultdict(lambda: [0, 0, 0, 0])
    for gi, g in games.items():
        key = (kind_of(g['game']), size_of(g))
        v = kk[key]
        v[0] += 1
        v[1] += len(per_game[gi])
        v[2] += len(rows.get(gi, []))
        v[3] += sum(a[4] for a in g['acc'] if a[0] == 0)
    print('by map kind and size: games, spells per game, share of short turns inside spells')
    for key in sorted(kk):
        v = kk[key]
        print('  ', key, v[0], '%.1f' % (v[1] / v[0]), pct(v[2], v[3]))
    # ---- where the time goes
    print('\n== where the spell turns go (first that holds)')
    sit = Counter()
    sit_band = defaultdict(Counter)
    ate = Counter()
    tot = 0
    feed = 0
    for gi, rs in rows.items():
        for r in rs:
            s = situation(r)
            sit[s] += 1
            sit_band[0 if r['r'] <= 100 else 1 if r['r'] <= 200 else 2][s] += 1
            ate[s] += r['ate']
            tot += 1
            feed += 1 if (r['r'] > 200 and r['al'] >= 56) else 0
    for k, v in sit.most_common():
        print('  %-58s %7d %6s | by band %s | ends in a meal that turn %s' % (k, v, pct(v, tot), ' '.join(pct(sit_band[z][k], sum(sit_band[z].values())) for z in range(3)), pct(ate[k], v)))
    print('  spell turns after round 200 with 56 or more of ours alive (feeding phase on):', feed, pct(feed, tot))
    print('  view: pearl in view', pct(sum(1 for rs in rows.values() for r in rs if r['np'] > 0), tot))
    # room of target pearls
    rm = Counter()
    for rs in rows.values():
        for r in rs:
            if r['nt'] > 0 and r['box'] >= 7:
                d, room = r['bt']
                L = r['L']
                rm[('beside' if d <= 1 else '2-3' if d <= 3 else '4+', 'trapped' if room < L + 2 else 'tight' if room < 3 * L + 8 else 'room')] += 1
    print('  target pearl by distance and room behind it:', sorted(rm.items()))
    mm = Counter()
    for rs in rows.values():
        for r in rs:
            if r['np'] > 0 and r['nt'] == 0 and r['nmn'] > 0 and r['box'] >= 7:
                mm[(min(r['bm'][0], 7), min(r['bm'][1], 7))] += 1
    print('  mate-nearer pearl (my steps, mate steps):', sorted(mm.items()))
    nmv = Counter()
    for rs in rows.values():
        for r in rs:
            nmv[min(r['nm'], 3)] += 1
    print('  team mates in view 0/1/2/3+:', [pct(nmv[z], tot) for z in range(4)])
    # ---- motion
    print('\n== motion inside spells')
    mot = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    disp = defaultdict(list)
    for gi, s in allsp:
        g = games[gi]
        w, h = g['w'], g['h']
        prevd = None
        for n, r in enumerate(s):
            d = chosen_dir(r, w, h)
            cls = ('view' if r['np'] > 0 else 'noview') + ('+mates' if r['nm'] > 0 else '')
            v = mot[cls]
            v[0] += 1
            recent = [x['h'] for x in s[max(0, n - 12):n]]
            if r['h'] in recent:
                v[1] += 1
            if d >= 0 and prevd is not None and prevd >= 0:
                v[2] += 1
                if d == prevd:
                    v[3] += 1
                if d == (prevd + 2) % 4:
                    v[4] += 1
            v[5] += len(r['path'])
            prevd = d
            if n >= 10:
                a, b = s[n - 10]['h'], r['h']
                disp[cls].append(tgap(a % w, b % w, w) + tgap(a // w, b // w, h))
    for cls in sorted(mot):
        v = mot[cls]
        dd = disp[cls]
        print('  %-14s turns %7d head on a tile it stood on in its last 12 turns %s | same direction as last turn %s, reversed %s | steps per turn %.2f | tiles away from where it was 10 turns ago: median %s, 4 or fewer %s' % (
            cls, v[0], pct(v[1], v[0]), pct(v[3], v[2]), pct(v[4], v[2]), v[5] / max(1, v[0]), median(dd) if dd else '-', pct(sum(x <= 4 for x in dd), len(dd))))
    # distinct tiles per 20 turns
    dt = []
    for gi, s in allsp:
        for a in range(0, len(s) - 19, 20):
            dt.append(len({x['h'] for x in s[a:a + 20]}))
    if dt:
        print('  distinct head tiles per 20 spell turns: median %s, 10 or fewer %s' % (median(dt), pct(sum(x <= 10 for x in dt), len(dt))))
    # ---- which term the step follows
    print('\n== which rebuilt term the step taken is best by (turns with a single step known and 2+ steps on offer)')
    res = defaultdict(lambda: Counter())
    spread = defaultdict(list)
    for gi, rs in rows.items():
        g = games[gi]
        w, h = g['w'], g['h']
        for r in rs:
            d = chosen_dir(r, w, h)
            legal = [k for k in range(4) if r['dirs'][k] is not None]
            if d < 0 or len(legal) < 2 or r['box'] < 7:
                continue
            T = {k: r['dirs'][k][0] for k in legal}
            dp = {k: r['dirs'][k][3] for k in legal if r['dirs'][k][3] >= 0}
            du = {k: r['dirs'][k][4] for k in legal if r['dirs'][k][4] >= 0}
            tmax, tmin = max(T.values()), min(T.values())
            cls = ('target pearl within 6' if dp and min(dp.values()) <= 6 else 'no target') + (', mates in view' if r['nm'] > 0 else ', no mate in view') + (', enemy in view' if r['ne'] > 0 else '')
            c = res[cls]
            c['n'] += 1
            c['chance'] += 1.0 / len(legal)
            tflat = tmax - tmin < 0.05
            c['T flat'] += tflat
            tb = T[d] >= tmax - 0.05
            if not tflat:
                c['T varies'] += 1
                c['T best'] += tb
                c['T chance'] += sum(1 for k in legal if T[k] >= tmax - 0.05) / len(legal)
                spread[cls].append(1.5 * (tmax - sorted(T.values())[-2]) if len(legal) > 1 else 0)
            if dp:
                c['dp any'] += 1
                c['dp best'] += (d in dp and dp[d] == min(dp.values()))
            ub = None
            if du and not (len(du) == len(legal) and max(du.values()) == min(du.values())):
                c['du varies'] += 1
                ub = d in du and du[d] == min(du.values())
                c['du best'] += ub
                c['du chance'] += sum(1 for k in legal if k in du and du[k] == min(du.values())) / len(legal)
                c['du near (6 or less)'] += min(du.values()) + 1 <= 6
            if not du:
                c['no never-seen tile within 80'] += 1
            if not tflat and ub is not None and tb != ub:
                c['T and du disagree'] += 1
                c['... step is T-best'] += tb
                c['... step is du-best'] += ub
    for cls in sorted(res):
        c = res[cls]
        print('  [%s] n %d' % (cls, c['n']))
        print('     territory differs between steps %s; then step is T-best %s (chance %s); median gap best to second %.1f points' % (
            pct(c['T varies'], c['n']), pct(c['T best'], c['T varies']), pct(c['T chance'], c['T varies']), median(spread[cls]) if spread[cls] else 0))
        print('     target pearl: step is nearest-pearl step %s of %d' % (pct(c['dp best'], c['dp any']), c['dp any']))
        print('     never-seen: differs %s (of these within 6 steps %s); step is du-best %s (chance %s); none within 80 steps %s' % (
            pct(c['du varies'], c['n']), pct(c['du near (6 or less)'], c['du varies']), pct(c['du best'], c['du varies']), pct(c['du chance'], c['du varies']), pct(c['no never-seen tile within 80'], c['n'])))
        print('     T and du disagree %d: step T-best %s, du-best %s' % (c['T and du disagree'], pct(c['... step is T-best'], c['T and du disagree']), pct(c['... step is du-best'], c['T and du disagree'])))
    # ---- result table baseline
    print('\n== per-arm result line')
    wins = sum(1 for g in games.values() if g['winner'] == g['our'])
    e3 = mean(g['eaten300'][0] for g in games.values())
    dr = Counter()
    for g in games.values():
        for s, reason, short, n in g['deaths']:
            if s == 0:
                dr[REASON.get(reason, '?')] += n
    short = sum(a[4] for g in games.values() for a in g['acc'] if a[0] == 0)
    hung = sum(a[4] for g in games.values() for a in g['acc'] if a[0] == 0 and a[2] >= 3)
    print('games %d wins %d | spells per game %.1f | share of short turns in spells %s | pearls by round 300 per game %.1f | deaths by round 300 per game: %s' % (
        len(games), wins, len(allsp) / len(games), pct(hung, short), e3, ', '.join('%s %.1f' % (k, v / len(games)) for k, v in sorted(dr.items()))))


main()
