"""Scratch (diag-wipeout): timelines and cause tables from wo_scan rows.
Usage: python3 data/analysis/ladder/dossier/work/wo_tl.py <O|L|R> [detail] [label-prefix]
Wipe-out = our side ends with no dragon. Peak round = last round at the maximum count. Half round = first round after
it with the count below half the peak. Window = the 60 rounds up to and including the half round."""
import sys, json, math
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(src):
    rows = []
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def size(c):
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


def marks(g, s=0):
    al = [x[4 * s] for x in g['snap']]
    peak = max(al)
    pr = max(r for r, a in enumerate(al) if a == peak)
    hr = next((r for r in range(pr, len(al)) if al[r] * 2 < peak), None)
    return peak, pr, hr


def zone(z):
    return 'own' if z < 0.35 else 'their' if z > 0.65 else 'mid'


def kind(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate head-on'
        return 'rammed' if d['role'] == 'hit' else 'rams (mover)'
    if c == 'other body':
        return 'body: ' + d.get('hit', '?')
    if c in ('wall', 'own body'):
        return c + (' boxed' if d.get('free', 0) == 0 else ' free')
    if c == 'no action':
        return 'no action' + (' boxed' if d.get('free', 0) == 0 else ' by choice')
    return c


def table(deaths, title, games):
    n = len(deaths)
    print('  %s: %d deaths in %d games (%.1f a game), length %d' % (title, n, games, n / max(games, 1), sum(d['L'] for d in deaths)))
    if not n:
        return
    by = defaultdict(list)
    for d in deaths:
        by[kind(d)].append(d)
    for k, ds in sorted(by.items(), key=lambda t: -len(t[1])):
        zs = Counter(zone(d['z']) for d in ds)
        line = '    %-20s %4d %5.1f%% | len mean %.1f (L2 %.0f%% L3 %.0f%% L4+ %.0f%%) q %d top>=5 %d | zone own/mid/their %d/%d/%d | own heads<=5 mean %.2f none %.0f%% | foes<=5 %.2f' % (
            k, len(ds), 100 * len(ds) / n, sum(d['L'] for d in ds) / len(ds),
            100 * sum(d['L'] == 2 for d in ds) / len(ds), 100 * sum(d['L'] == 3 for d in ds) / len(ds), 100 * sum(d['L'] >= 4 for d in ds) / len(ds),
            sum(d['q'] for d in ds), sum(1 for d in ds if d['top'] and d['L'] >= 5),
            zs['own'], zs['mid'], zs['their'], sum(d['o5'] for d in ds) / len(ds), 100 * sum(d['o5'] == 0 for d in ds) / len(ds),
            sum(d['e5'] for d in ds) / len(ds))
        print(line)
        if k == 'rammed':
            ms = [d['m'] for d in ds]
            paid = [max(0, m['steps'] - math.ceil(m['L0'] / 4)) for m in ms]
            print('      rammer L0: 2 %.0f%% 3 %.0f%% 4 %.0f%% 5+ %.0f%% mean %.2f | steps 1 %.0f%% 2 %.0f%% 3+ %.0f%% | paid any %.0f%% mean %.2f | victim longer %.0f%% same %.0f%% shorter %.0f%% than rammer L0' % (
                100 * sum(m['L0'] == 2 for m in ms) / len(ms), 100 * sum(m['L0'] == 3 for m in ms) / len(ms), 100 * sum(m['L0'] == 4 for m in ms) / len(ms),
                100 * sum(m['L0'] >= 5 for m in ms) / len(ms), sum(m['L0'] for m in ms) / len(ms),
                100 * sum(m['steps'] == 1 for m in ms) / len(ms), 100 * sum(m['steps'] == 2 for m in ms) / len(ms), 100 * sum(m['steps'] >= 3 for m in ms) / len(ms),
                100 * sum(x > 0 for x in paid) / len(ms), sum(paid) / len(ms),
                100 * sum(d['L'] > d['m']['L0'] for d in ds) / len(ds), 100 * sum(d['L'] == d['m']['L0'] for d in ds) / len(ds), 100 * sum(d['L'] < d['m']['L0'] for d in ds) / len(ds)))
    side = deaths[0]['s']
    drop = sum(d['drop'] for d in deaths)
    print('    drops %d: eaten within 5 rounds by the dead side %d (%.0f%%), by the other side %d (%.0f%%); ever %d / %d' % (
        drop, sum(d['eat5'][side] for d in deaths), 100 * sum(d['eat5'][side] for d in deaths) / max(drop, 1),
        sum(d['eat5'][1 - side] for d in deaths), 100 * sum(d['eat5'][1 - side] for d in deaths) / max(drop, 1),
        sum(d['eat'][side] for d in deaths), sum(d['eat'][1 - side] for d in deaths)))


def shape(g):
    peak, pr, hr = marks(g)
    al = [x[0] for x in g['snap']]
    fall = peak - al[hr]
    best = max(al[r] - al[min(r + 20, hr)] for r in range(pr, hr + 1))
    ds = [d for d in g['deaths'] if d['s'] == 0 and pr < d['r'] <= hr]
    enemy = sum(1 for d in ds if kind(d) in ('rammed', 'rams (mover)', 'body: enemy'))
    share = enemy / max(len(ds), 1)
    if best * 2 >= fall and hr - pr > 20:
        cls = 'one battle'
    elif hr - pr <= 20:
        cls = 'one battle'
    elif share >= 0.5:
        cls = 'bleed by contact'
    else:
        cls = 'bleed by own deaths'
    return cls, best, fall, share


def main():
    src = sys.argv[1]
    detail = len(sys.argv) > 2 and sys.argv[2] == 'detail'
    prefix = sys.argv[3] if len(sys.argv) > 3 else ''
    rows = [g for g in load(src) if g['src'].startswith(prefix)]
    out = [g for g in rows if g['final'][0] == 0]
    won = [g for g in rows if g['final'][4] == 0]
    print(src, prefix, 'games', len(rows), 'we wiped out', len(out), 'they wiped out', len(won), 'results', Counter(g['result'] for g in rows))
    for sz in ('<=700', '701-1200', '>1200'):
        a = [g for g in rows if size(g['cells']) == sz]
        print('  size', sz, 'games', len(a), 'we out', sum(g['final'][0] == 0 for g in a), 'they out', sum(g['final'][4] == 0 for g in a), 'wins', sum(g['result'] == 'win' for g in a))
    if src == 'O':
        for key in sorted(set((g['src'], g['opp']) for g in rows)):
            a = [g for g in rows if (g['src'], g['opp']) == key]
            print('  ', key, 'games', len(a), 'we out', sum(g['final'][0] == 0 for g in a), 'they out', sum(g['final'][4] == 0 for g in a), 'wins', sum(g['result'] == 'win' for g in a))
    shapes = Counter()
    wu, wt, pre_u = [], [], []
    agg = defaultdict(list)
    for g in sorted(out, key=lambda g: g['gid']):
        peak, pr, hr = marks(g)
        sn = g['snap']
        cls, best, fall, share = shape(g)
        shapes[(size(g['cells']), cls)] += 1
        lo = max(0, hr - 60)
        du = [d for d in g['deaths'] if d['s'] == 0 and lo < d['r'] <= hr]
        dt = [d for d in g['deaths'] if d['s'] == 1 and lo < d['r'] <= hr]
        wu += du
        wt += dt
        rc = dict((x[0], x[1:]) for x in g['rc'])
        tot = [sum(rc.get(r, [0] * 10)[k] for r in range(lo + 1, hr + 1)) for k in range(10)]
        agg['peak'].append(peak); agg['pr'].append(pr); agg['hr'].append(hr); agg['last'].append(g['last'])
        agg['their_at_half'].append(sn[hr][4]); agg['our_at_half'].append(sn[hr][0])
        agg['q_dead_before_half'].append(int(sn[hr][3] == 0))
        agg['tot'].append(tot)
        agg['their_peak_before'].append(int(max(x[4] for x in sn[:hr + 1]) > peak))
        if detail:
            at = lambda r: '%d/%d v %d/%d' % (sn[min(r, g['last'])][0], sn[min(r, g['last'])][1], sn[min(r, g['last'])][4], sn[min(r, g['last'])][5])
            print('%s %d %s %s %d cells | peak %d at r%d (%s) | half r%d (%s) | last r%d | q dies r%s | r50 %s r100 %s r150 %s r200 %s | %s: worst-20 %d of %d, contact share %.2f | window: our deaths %d splits %d eats %d+%d; their deaths %d splits %d eats %d+%d' % (
                g['src'], g['gid'], g['opp'][:8], g['map'][:14], g['cells'], peak, pr, at(pr), hr, at(hr), g['last'],
                next((r for r, x in enumerate(sn) if x[3] == 0), None), at(50), at(100), at(150), at(200), cls, best, fall, share,
                len(du), tot[1], tot[2], tot[3], len(dt), tot[6], tot[7], tot[8]))
    print('shapes', sorted(shapes.items()))
    if out:
        med = lambda v: sorted(v)[len(v) // 2]
        print('medians: peak %d at r%d, half r%d, last r%d; our count at half %d, theirs %d; queen already dead at half %d of %d; their count above our peak by half round %d' % (
            med(agg['peak']), med(agg['pr']), med(agg['hr']), med(agg['last']), med(agg['our_at_half']), med(agg['their_at_half']),
            sum(agg['q_dead_before_half']), len(out), sum(agg['their_peak_before'])))
        T = [sum(t[k] for t in agg['tot']) for k in range(10)]
        print('window totals: our turns %d splits %d eats nat %d drop %d steps %d | their turns %d splits %d eats nat %d drop %d steps %d' % tuple(T))
        table(wu, 'OUR deaths in the window', len(out))
        table(wt, 'THEIR deaths in the window', len(out))
        cross = [d for d in wu + wt if d['c'] == 'head-on' and d['cross'] and d['role'] == 'mover']
        print('  cross head-ons in the window: started by us %d, by them %d' % (sum(d['s'] == 0 for d in cross), sum(d['s'] == 1 for d in cross)))


main()
