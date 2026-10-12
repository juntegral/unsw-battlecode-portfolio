# Scratch (diag-opening): tables from op_scan3-*.jsonl (pearl origin; who goes for which pearl) and op_scan4-*.jsonl
# (one-way steps). Values are pooled inside a layout, then averaged over layouts with equal weight; hi/lo/n counts layouts
# where rank-1 is higher / lower / that have the value for both.
# Usage: python3 data/analysis/ladder/dossier/work/op_agg3.py <3|4> [detail word ...]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
F3 = ['op_scan3-O0.jsonl', 'op_scan3-O1.jsonl', 'op_scan3-O2.jsonl', 'op_scan3-O3.jsonl',
      'op_scan3-R0.jsonl', 'op_scan3-R1.jsonl', 'op_scan3-R2.jsonl', 'op_scan3-R3.jsonl']
F4 = ['op_scan4-O0.jsonl', 'op_scan4-O1.jsonl', 'op_scan4-O2.jsonl', 'op_scan4-O3.jsonl',
      'op_scan4-R0.jsonl', 'op_scan4-R1.jsonl', 'op_scan4-R2.jsonl', 'op_scan4-R3.jsonl']


def load(files):
    games = []
    for f in files:
        if not Path(W + f).exists():
            print('missing', f)
            continue
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


class Acc:
    def __init__(self):
        self.num = defaultdict(lambda: defaultdict(float))
        self.den = defaultdict(lambda: defaultdict(float))
        self.order = []

    def add(self, name, tag, lay, n, d):
        if name not in self.num:
            self.order.append(name)
        self.num[name][(tag, lay)] += n
        self.den[name][(tag, lay)] += d

    def lines(self, layouts, detail):
        out = ['%-72s %8s %8s %8s %8s  %s' % ('metric', 'O', 'R', 'Oopp', 'Ropp', 'hi/lo/n')]
        for name in self.order:
            val = lambda tag, l: self.num[name][(tag, l)] / self.den[name][(tag, l)] if self.den[name].get((tag, l)) else None
            both = [l for l in layouts if val('O', l) is not None and val('R', l) is not None]
            if not both:
                continue
            def mean(tag):
                vs = [val(tag, l) for l in both if val(tag, l) is not None]
                return sum(vs) / len(vs) if vs else float('nan')
            hi = sum(1 for l in both if val('R', l) > val('O', l) + 1e-9)
            lo = sum(1 for l in both if val('R', l) < val('O', l) - 1e-9)
            out.append('%-72s %8.2f %8.2f %8.2f %8.2f  %d/%d/%d' % (name, mean('O'), mean('R'), mean('Oo'), mean('Ro'), hi, lo, len(both)))
            if any(w in name for w in detail):
                for l in layouts:
                    row = ['%8.2f' % val(tag, l) if val(tag, l) is not None else '%8s' % '-' for tag in ('O', 'R', 'Oo', 'Ro')]
                    dn = ['%d' % self.den[name].get((tag, l), 0) for tag in ('O', 'R')]
                    out.append('    %-68s %s   n %s' % (l, ' '.join(row), '/'.join(dn)))
        return out


def three(detail):
    games = load(F3)
    layouts = sorted({g['layout'] for g in games})
    a = Acc()
    for g in games:
        if g['last_round'] < 60:
            continue
        for s, tag in (('u', g['who']), ('t', g['who'] + 'o')):
            sd = g['sides'][s]
            lay = g['layout']
            for wl, wins in (('r0-20', (0, 1)), ('r0-60', (0, 1, 2, 3))):
                tot = 0
                for o, nm in (('n', 'natural'), ('o', 'dropped by its own dead'), ('e', 'dropped by the other side')):
                    n = sum(sd['eat'].get('%d|%s' % (wb, o), 0) for wb in wins)
                    tot += n
                    a.add('pearls eaten a game %s: %s' % (wl, nm), tag, lay, n, 1)
                a.add('pearls eaten a game %s: all' % wl, tag, lay, tot, 1)
                a.add('share of eaten pearls %s that its own dead dropped %%' % wl, tag, lay,
                      100.0 * sum(sd['eat'].get('%d|o' % wb, 0) for wb in wins), tot)
            for wl, wins in (('r0-60', ('0', '1')),):
                tot = sum(v[0] for k, v in sd['chase'].items() if k.split('|')[0] in wins)
                for rel, nm in (('solo', 'no mate as near'), ('tie', 'a mate exactly as near'), ('mate', 'a mate nearer')):
                    n = sum(v[0] for k, v in sd['chase'].items() if k.split('|')[0] in wins and k.split('|')[1] != 'X' and k.split('|')[2].rstrip('f') == rel)
                    a.add('pearl-in-view turns %s: %s %%' % (wl, nm), tag, lay, 100.0 * n, tot)
                n = sum(v[0] for k, v in sd['chase'].items() if k.split('|')[0] in wins and k.split('|')[1] == 'X')
                a.add('pearl-in-view turns %s: none within 8 path steps %%' % wl, tag, lay, 100.0 * n, tot)
                n = sum(v[0] for k, v in sd['chase'].items() if k.split('|')[0] in wins and k.split('|')[3] == 'F')
                a.add('pearl-in-view turns %s: an enemy head as near or nearer %%' % wl, tag, lay, 100.0 * n, tot)
                for dc in ('1', '2', '3-4', '5-8'):
                    for rel, nm in (('solo', 'no mate as near'), ('tie', 'mate as near'), ('mate', 'mate nearer')):
                        vs = [v for k, v in sd['chase'].items() if k.split('|')[0] in wins and k.split('|')[1] == dc and k.split('|')[2].rstrip('f') == rel and k.split('|')[3] == '-']
                        t = sum(v[0] for v in vs)
                        pre = 'P at %s, %s, no enemy near: ' % (dc, nm)
                        a.add(pre + 'share of pearl-in-view turns %', tag, lay, 100.0 * t, tot)
                        a.add(pre + 'turn ends nearer or on it %', tag, lay, 100.0 * sum(v[1] for v in vs), t)
                        if dc == '1':
                            a.add(pre + 'eats it this turn %', tag, lay, 100.0 * sum(v[2] for v in vs), t)
                        a.add(pre + 'the turn is a split %', tag, lay, 100.0 * sum(v[3] for v in vs), t)
                        a.add(pre + 'this dragon eats it within 8 rounds %', tag, lay, 100.0 * sum(v[4] for v in vs), t)
                        a.add(pre + 'a mate eats it within 8 rounds %', tag, lay, 100.0 * sum(v[5] for v in vs), t)
                        a.add(pre + 'the enemy eats it within 8 rounds %', tag, lay, 100.0 * sum(v[6] for v in vs), t)
                for dc in ('1', '2', '3-4', '5-8'):
                    vs = [v for k, v in sd['chase'].items() if k.split('|')[0] in wins and k.split('|')[1] == dc and k.split('|')[3] == 'F']
                    t = sum(v[0] for v in vs)
                    pre = 'P at %s, an enemy head as near or nearer: ' % dc
                    a.add(pre + 'turn ends nearer or on it %', tag, lay, 100.0 * sum(v[1] for v in vs), t)
                    a.add(pre + 'our side eats it within 8 rounds %', tag, lay, 100.0 * sum(v[4] + v[5] for v in vs), t)
    body = '\n'.join(a.lines(layouts, detail)) + '\n'
    Path(OUT + 'op_agg3.txt').write_text(body)
    print(body)


def four(detail):
    games = load(F4)
    layouts = sorted({g['layout'] for g in games})
    a = Acc()
    for g in games:
        for s, tag in (('u', g['who']), ('t', g['who'] + 'o')):
            sd = g['sides'][s]
            lay = g['layout']
            tab = sd['tab']
            allt = sum(v[0] for v in tab.values())
            sel = lambda win=None, ctx=None, age=None, opt=None: [v for k, v in tab.items() if (win is None or k.split('|')[0] in win) and (ctx is None or k.split('|')[1] in ctx) and (age is None or k.split('|')[2] in age) and (opt is None or k.split('|')[3] in opt)]
            for wl, win in (('r0-100', None), ('r0-30', ('0',)), ('r31-100', ('1',))):
                c = sel(win=win, opt=('C',))
                o = sel(win=win, opt=('O',))
                t = sum(v[0] for v in sel(win=win))
                a.add('%s: turns with a way step and a big one-way step both free, a game' % wl, tag, lay, sum(v[0] for v in c), 1)
                a.add('%s: the same per 100 move turns of short dragons' % wl, tag, lay, 100.0 * sum(v[0] for v in c), t)
                a.add('%s: both free: takes the big one-way step %%' % wl, tag, lay, 100.0 * sum(v[1] for v in c), sum(v[0] for v in c))
                a.add('%s: big one-way steps taken a game (any options)' % wl, tag, lay, sum(v[1] for v in sel(win=win)), 1)
                a.add('%s: turns already in a one-way place, per 100 move turns' % wl, tag, lay, 100.0 * sum(v[0] for v in o), t)
                a.add('%s: small one-way steps taken per 100 move turns' % wl, tag, lay, 100.0 * sum(v[3] for v in sel(win=win)), t)
            for cl, ctx in (('no pearl in view', ('N',)), ('pearl in view', ('P',))):
                c = sel(ctx=ctx, opt=('C',))
                a.add('r0-100, %s: both free: takes the big one-way step %%' % cl, tag, lay, 100.0 * sum(v[1] for v in c), sum(v[0] for v in c))
                a.add('r0-100, %s: both-free turns a game' % cl, tag, lay, sum(v[0] for v in c), 1)
            for al, age in (('grew or born under 12 rounds ago', ('a',)), ('12 to 29 rounds ago', ('b',)), ('30+ rounds ago', ('c',))):
                c = sel(age=age, opt=('C',))
                a.add('r0-100, %s: both free: takes the big one-way step %%' % al, tag, lay, 100.0 * sum(v[1] for v in c), sum(v[0] for v in c))
                a.add('r0-100, %s: both-free turns a game' % al, tag, lay, sum(v[0] for v in c), 1)
                a.add('r0-100, %s: share of move turns of short dragons %%' % al, tag, lay, 100.0 * sum(v[0] for v in sel(age=age)), allt)
            c = sel(age=('b', 'c'), ctx=('N',), opt=('C',))
            a.add('r0-100, no pearl in view and 12+ rounds without growth: both free: takes it %', tag, lay, 100.0 * sum(v[1] for v in c), sum(v[0] for v in c))
            a.add('r0-100, no pearl in view and 12+ rounds without growth: both-free turns a game', tag, lay, sum(v[0] for v in c), 1)
            a.add('start pocket: share of turns r0-60 that start inside it %', tag, lay, 100.0 * sd['inroom'][1], sd['inroom'][0])
            if sd['out'] is not None:
                a.add('start pocket: first round a head is outside it (when by 100)', tag, lay, sd['out'], 1)
            a.add('start pocket: no head outside by round 100 %', tag, lay, 100.0 if sd['out'] is None else 0.0, 1)
            a.add('start pocket: tiles', tag, lay, g['pocket'][s], 1)
    body = '\n'.join(a.lines(layouts, detail)) + '\n'
    Path(OUT + 'op_agg4.txt').write_text(body)
    print(body)


def main():
    which = sys.argv[1]
    detail = sys.argv[2:]
    if which == '3':
        three(detail)
    else:
        four(detail)


main()
