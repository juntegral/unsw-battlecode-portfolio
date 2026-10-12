"""Scratch (diag-topaah): extra tables from ta_scan-*.jsonl: rams by who is longer, queen states at the end, the late game."""
import json
from statistics import mean, median
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TAGS = (('a', ['a']), ('a0', ['a0']), ('l', ['l']), ('c0', ['c0-0', 'c0-1', 'c0-2', 'c0-3']), ('c1', ['c1']), ('g', ['g']), ('q', ['q']), ('m', ['m']), ('t', ['t']))


def m(v):
    v = [x for x in v if x is not None]
    return 'NA' if not v else '%.1f' % mean(v)


def main():
    for tag, files in TAGS:
        gs = []
        for f in files:
            p = Path(WORK + 'ta_scan-' + f + '.jsonl')
            if p.exists():
                gs += [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        if not gs:
            continue
        n = len(gs)
        print('==', tag, 'games', n, 'won', sum(1 for g in gs if g['win'] == 1), 'layouts', len({(g['map'], g['w'], g['h'], len(g['starts'][0])) for g in gs}))
        r100 = [x for g in gs for x in g['rams'] if x[1] == 0 and x[6] and x[0] <= 100]
        rall = [x for g in gs for x in g['rams'] if x[1] == 0 and x[6]]
        e100 = [x for g in gs for x in g['rams'] if x[1] == 1 and x[6] and x[0] <= 100]
        print('  rams started by r100: %.1f a game (mover longer %.0f%%, equal %.0f%%, shorter %.0f%%); whole game mover longer %.0f%%; rams received by r100 %.1f a game' % (
            len(r100) / n, 100 * sum(1 for x in r100 if x[2] > x[3]) / max(1, len(r100)), 100 * sum(1 for x in r100 if x[2] == x[3]) / max(1, len(r100)),
            100 * sum(1 for x in r100 if x[2] < x[3]) / max(1, len(r100)), 100 * sum(1 for x in rall if x[2] > x[3]) / max(1, len(rall)), len(e100) / n))
        st = {}
        for g in gs:
            k = (g['final'][0]['ql'] > 0, g['final'][1]['ql'] > 0)
            a, b = st.get(k, (0, 0))
            st[k] = (a + int(g['win'] == 1), b + 1)
        print('  end state (own queen alive, their queen alive) -> won/games:', {('%s/%s' % ('A' if k[0] else 'D', 'A' if k[1] else 'D')): v for k, v in sorted(st.items())})
        qd = [d[0] for g in gs for d in g['deaths'] if d[1] == 0 and d[5] == 1]
        print('  own queen dies in %.0f%% of games, median round %s' % (100 * len(qd) / n, median(qd) if qd else 'NA'))
        for name, sel in (('boards up to 1200 cells', lambda g: g['w'] * g['h'] <= 1200), ('boards above 1200', lambda g: g['w'] * g['h'] > 1200)):
            sub = [g for g in gs if sel(g)]
            late = [g for g in sub if g['last_round'] >= 400]
            if not sub:
                continue
            def sn(mark, key):
                return [g['snaps'][mark][0][key] for g in sub if mark in g['snaps']]
            line = '  %s: games %d (to r400: %d); longest r200 %s r300 %s; second r300 %s; total r200 %s r300 %s; alive r300 %s' % (
                name, len(sub), len(late), m(sn('200', 'longest')), m(sn('300', 'longest')), m(sn('300', 'second')), m(sn('200', 'total')), m(sn('300', 'total')), m(sn('300', 'alive')))
            if late:
                def c(k, wi=2):
                    return sum(g['cnt'][0][wi].get(k, 0) for g in late)
                def h(k, wi=2):
                    return sum(g['coh'][0][wi].get(k, 0) for g in late)
                t = max(1, c('turns'))
                free = sum(1 for g in late for d in g['deaths'] if d[1] == 0 and d[2] >= 2 and d[4] == 1 and d[0] > 300)
                line += '; after r300: pearls/1k %.1f, natural harvest %.0f%%, adjacent missed %.0f%%, splits/1k %.1f, deaths with a free tile/1k %.1f; final longest %s second %s' % (
                    1000 * c('eaten') / t, 100 * h('e_n') / max(1, h('b_n')), 100 * c('adj_missed') / max(1, c('adj_turns')), 1000 * c('splits') / t, 1000 * free / t,
                    m([g['final'][0]['longest'] for g in late]), m([g['final'][0]['second'] for g in late]))
            print(line)


main()
