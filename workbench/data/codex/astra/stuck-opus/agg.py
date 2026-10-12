"""stuck-opus: tables from rows-*.jsonl. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/agg.py online|local [pattern ...]"""
import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict
HERE = Path('data/codex/astra/stuck-opus')
PATS = ('a', 'an', 'a2', 'a2n', 'b', 'c', 'c0', 'd', 'and', 'a2nd', 'nd')
ONLINE = ['one11-c1', 'one11-k1', 'one11-p1', 'one12-c1', 'one12-k1', 'one12-p1', 'one13-c1', 'one13-c2', 'one13-k1', 'one13-k2', 'one13-p1', 'one13-p2', 'one13-q1', 'one14-c1', 'one14-p1', 'one14-k1', 'one14-c2', 'one14-q1']
LOCAL = ['h2h_mNps_v13', 'pc_mNps', 'pc_mDone13', 'h2h_mDone13_v5']


def load(names):
    out = []
    for n in names:
        p = HERE / ('rows-%s.jsonl' % n)
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines()]
    return out


def tot(g, side, roles=(0, 1), phases=(0, 1, 2)):
    return {k: sum(g['cnt'][side][ro][ph][k] for ro in roles for ph in phases) for k in PATS + ('n',)}


def cell(gs, pat, roles=(0, 1), phases=(0, 1, 2)):
    if not gs:
        return '      -      '
    u = [tot(g, 0, roles, phases) for g in gs]
    o = [tot(g, 1, roles, phases) for g in gs]
    un, on = sum(x['n'] for x in u), sum(x['n'] for x in o)
    uw, ow = sum(x[pat] for x in u), sum(x[pat] for x in o)
    return '%5.0f %4.1f|%4.1f' % (uw / len(gs), 100 * uw / max(un, 1), 100 * ow / max(on, 1))


def table(gs, keyrow, keycol, pat, roles=(0, 1), phases=(0, 1, 2)):
    rows = sorted({keyrow(g) for g in gs})
    cols = sorted({keycol(g) for g in gs})
    print('pattern %s roles %s phases %s : our wasted dragon-rounds per game, our share %% | their share %%' % (pat, roles, phases))
    print('%-22s' % '' + ''.join('%-18s' % ('%s (n)' % c) for c in cols))
    for r in rows + ['ALL']:
        line = '%-22s' % str(r)[:21]
        for c in cols:
            sel = [g for g in gs if (r == 'ALL' or keyrow(g) == r) and keycol(g) == c]
            line += '%-14s%-4s' % (cell(sel, pat, roles, phases), '(%d)' % len(sel))
        print(line)
    print()


def fam(g):
    m = re.match(r'gx_([a-z]+)_(\d+)x(\d+)', g['map'])
    return m[1] if m else g['map'].replace('ladder_', 'L:')


def size(g):
    return '%05d' % g['cells']


if __name__ == '__main__':
    kind = sys.argv[1]
    pats = sys.argv[2:] or ['an', 'a2n', 'b', 'c', 'd']
    if kind == 'online':
        gs = load(ONLINE)
        print(len(gs), 'online games')
        for p in pats:
            table(gs, lambda g: g['map'], lambda g: g['ver'], p)
        print('non-queen only / queen only, all maps')
        for p in pats:
            table(gs, lambda g: 'nonqueen', lambda g: g['ver'], p, roles=(1,))
            table(gs, lambda g: 'queen', lambda g: g['ver'], p, roles=(0,))
        print('by phase (r<100, 100-349, 350+), all maps')
        for p in pats:
            for ph in range(3):
                table(gs, lambda g: 'phase%d' % ph, lambda g: g['ver'], p, phases=(ph,))
        print('by opponent set')
        for p in pats:
            table(gs, lambda g: g['set'][-2:-1], lambda g: g['ver'], p)
    else:
        gs = load(LOCAL)
        print(len(gs), 'local games')
        for p in pats:
            table(gs, fam, lambda g: g['set'], p)
            table(gs, size, lambda g: g['set'], p)
            table(gs, lambda g: 'portals' if g['portals'] else 'no portals', lambda g: g['set'], p)
    # split deaths
    print('deaths within 3 rounds of a split, per 100 splits (wall / own body / other body), us | them')
    by = defaultdict(lambda: [[0, 0, 0, 0], [0, 0, 0, 0]])
    for g in gs:
        k = g['ver']
        for s in (0, 1):
            by[k][s][3] += g['nsplit'][s]
        for e in g['e']:
            by[k][e['side']][e['reason']] += 1
    for k in sorted(by):
        u, o = by[k]
        print('%-16s us %5.1f / %5.1f / %5.1f (splits %d) | them %5.1f / %5.1f / %5.1f (splits %d)' % (
            k, 100 * u[0] / max(u[3], 1), 100 * u[1] / max(u[3], 1), 100 * u[2] / max(u[3], 1), u[3],
            100 * o[0] / max(o[3], 1), 100 * o[1] / max(o[3], 1), 100 * o[2] / max(o[3], 1), o[3]))
    print()
    print('dead-end cells, per game mean: cells (tips) | stale dead-end pearl-rounds | dead-end pearls eaten us/them (tips us/them) | deaths with head in a dead-end us/them')
    keyf = (lambda g: (g['ver'], g['map'])) if kind == 'online' else (lambda g: (g['set'], fam(g) + ' ' + size(g)))
    acc = defaultdict(list)
    for g in gs:
        acc[keyf(g)].append(g['dstat'])
        acc[(keyf(g)[0], 'ALL')].append(g['dstat'])
    for k in sorted(acc):
        ds = acc[k]
        n = len(ds)
        print('%-14s %-22s n=%-3d cells %5.0f (%4.0f) stale %7.0f | eaten %5.1f / %5.1f (tips %5.1f / %5.1f) | died %5.1f / %5.1f' % (
            k[0], k[1][:22], n, sum(d['cells'] for d in ds) / n, sum(d['tips'] for d in ds) / n, sum(d['stale'] for d in ds) / n,
            sum(d['eat'][0] for d in ds) / n, sum(d['eat'][1] for d in ds) / n, sum(d['eat_tip'][0] for d in ds) / n, sum(d['eat_tip'][1] for d in ds) / n,
            sum(d['die'][0] for d in ds) / n, sum(d['die'][1] for d in ds) / n))
