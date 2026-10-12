"""Scratch (diag-longest): job 1 tables. python3 lg_report.py  -> prints the class table and the live arm's rows,
writes every race game of the three arms to lg_games.txt."""
import json
from pathlib import Path
from statistics import median
from collections import Counter

WORK = Path('data/analysis/ladder/dossier/work')
FULL = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/lg_games.txt'
ARMS = dict(MAIN=('m1', 'm2', 'm3'), B7=('b1', 'b2'), B7Q=('q1', 'q2'))
MARKS = (100, 150, 200, 250, 300, 350, 400, 450, 499)
CAUSE = ('wall', 'own body', 'a body', 'it rammed', 'rammed', 'unpaid sprint', 'bad split', 'no action')
CATS = ('natural', 'fed', 'own dead', 'their dead')


def load(tags):
    out = []
    for t in tags:
        p = WORK / ('lg_scan-%s.jsonl' % t)
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l]
    return out


def at(g, r, k):
    s = g['snaps']
    return s[min(r, len(s) - 1)][k]


def bqd(g):
    return g['qdeath'][0] is not None and g['qdeath'][1] is not None


def in_race(g):
    return g['decided'] in ('longest', 'total') or (g['decided'] == 'elimination' and bqd(g))


def crossing(g):
    sn = g['snaps']
    n = len(sn)
    lead = 1 if sn[-1][1] > sn[-1][0] else 0 if sn[-1][0] > sn[-1][1] else -1
    if lead < 0:
        return None
    X = 0
    for r in range(n - 1, -1, -1):
        if sn[r][1 - lead] >= sn[r][lead]:
            X = r + 1
            break
    if X >= n or X == 0:
        return dict(lead=lead, X=X, cls='start', txt='from the start')
    lose = 1 - lead
    prev = sn[X - 1]
    b, a = prev[lose], sn[X][lose]
    txt = '%d:%d > %d:%d' % (prev[0], prev[1], sn[X][0], sn[X][1])
    if a < b:
        ds = [d for d in g['tdeaths'] if d['s'] == lose and X - 1 <= d['r'] <= X and d['L'] >= b]
        sp = [t for t in g['tsplits'] if t[1] == lose and t[0] == X and t[2] >= b]
        if ds:
            d = ds[-1]
            code = (0, 1, 2, 3 if d['own'] else 4, 5 + (d['act'] if d['act'] is not None else 2))[min(d['reason'], 4)]
            cls = 'rammed' if code == 4 else 'died'
            txt += '; longest %d %s' % (d['L'], CAUSE[code])
            r = d.get('ram')
            if r:
                th = r.get('then')
                txt += ' by a %d from %d tiles in %d steps (%d free), %s, %d of its own within 5' % (
                    r['L'], r['mdist'], r['steps'], r['free'], 'no record' if th is None else 'in view' if th[0] <= 3 else 'out of view', d['own5'])
        elif sp:
            cls = 'split'
            txt += '; longest split %d into %d + %d' % (sp[0][2], sp[0][3], sp[0][4])
        elif b < 6:
            cls = 'short'
            txt += '; longest of %d lost (no leader yet)' % b
        else:
            cls = 'shrank'
            txt += '; longest paid segments'
    else:
        eats = Counter(CATS[e[2]] for e in g['roundeat'] if e[0] == X and e[1] == lead)
        cls = 'fed' if eats.get('fed') else 'outgrown'
        txt += '; the other longest ate ' + (', '.join('%d %s' % (v, k) for k, v in sorted(eats.items())) or 'nothing recorded')
    if b < 8:
        cls = 'short'
    return dict(lead=lead, X=X, cls=cls, txt=txt)


def row(g):
    c = crossing(g)
    seq = ' '.join('%d:%d' % (at(g, m, 0), at(g, m, 1)) for m in MARKS)
    end = g['decided'][:4] + ('' if g['last'] >= 499 else ' r%d' % g['last'])
    if c is None:
        return '| %d | %s | %d | %s | %s | %s | - | level |' % (g['game'], g['opp'][:3], g['cells'], 'won' if g['win'] else 'lost', end, seq)
    return '| %d | %s | %d | %s | %s | %s | %s r%d | %s |' % (g['game'], g['opp'][:3], g['cells'], 'won' if g['win'] else 'lost', end, seq,
                                                         'they' if c['lead'] == 1 else 'we', c['X'], c['txt'])


def main():
    full = []
    for arm, tags in ARMS.items():
        G = load(tags)
        if not G:
            continue
        dec = Counter(g['decided'] for g in G)
        race = [g for g in G if in_race(g)]
        lost = [g for g in race if not g['win']]
        cl = Counter()
        xs = []
        ours_at = []
        for g in lost:
            c = crossing(g)
            if c is None:
                cl['level'] += 1
                continue
            cl[c['cls']] += 1
            xs.append(c['X'])
            ours_at.append(g['snaps'][max(c['X'] - 1, 0)][0])
        wl = Counter()
        for g in race:
            if g['win']:
                c = crossing(g)
                wl[c['cls'] if c else 'level'] += 1
        print('%s: games %d, won %d | decided: queen %d, longest %d, total %d, elimination %d (both queens dead first %d) | race games %d: won %d, lost %d' % (
            arm, len(G), sum(g['win'] or 0 for g in G), dec['queen'], dec['longest'], dec['total'], dec['elimination'],
            sum(1 for g in G if g['decided'] == 'elimination' and bqd(g)), len(race), len(race) - len(lost), len(lost)))
        print('   lost: passed for good at median r%d (before r200: %d, r200-399: %d, r400+: %d); our longest just before, median %d; what happened: %s' % (
            median(xs) if xs else 0, sum(1 for x in xs if x < 200), sum(1 for x in xs if 200 <= x < 400), sum(1 for x in xs if x >= 400),
            median(ours_at) if ours_at else 0, dict(cl)))
        print('   won: what happened when we passed: %s' % dict(wl))
        full.append('## %s' % arm)
        full.append('| game | opp | cells | result | by | ours:theirs longest at r100 150 200 250 300 350 400 450 500 | passed | at that round |')
        full.append('|---|---|---:|---|---|---|---|---|')
        for g in sorted(race, key=lambda g: (g['opp'], g['game'])):
            full.append(row(g))
        full.append('')
    Path(FULL).write_text('\n'.join(full) + '\n')


main()
