"""End phase (after r350) on games that reach r499: feeders that stop, pearls they drop, who eats them (leader/queen, other own, enemy),
and growth of the longest dragon. Also restricted to the map+side pairs present in both newer arms. Usage: feed.py"""
import json
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
def load(arm):
    return {json.loads(l)['folder']: json.loads(l) for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines()}
A = {a: load(a) for a in ('h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5')}
common = {f for f in A['h2h_mDone11_v8'] if f in A['h2h_mDone10_v8'] and A['h2h_mDone11_v8'][f]['last'] >= 499 and A['h2h_mDone10_v8'][f]['last'] >= 499}
def table(arm, keep, tag):
    gs = [g for f, g in A[arm].items() if g['last'] >= 499 and (keep is None or f in keep)]
    print('%s %s: %d games, newer wins %d losses %d' % (arm, tag, len(gs), sum(g['result'] == 'win' for g in gs), sum(g['result'] == 'loss' for g in gs)))
    for s, nm in ((0, 'NEW'), (1, 'old')):
        st = [d for g in gs for d in g['deaths'] if d[1] == s and d[4] == 'stop' and d[0] > 350]
        drop = sum(d[15] for d in st)
        top = sum(d[12] for d in st)
        own = sum(d[10] for d in st)
        foe = sum(d[11] for d in st)
        L = lambda r: sum(g['snaps'][str(r)][s][2] for g in gs) / len(gs)
        tops = [e for g in gs for e in g['eats'] if e[1] == s and e[0] > 350 and e[2] in 'tq']
        n_top_nat = sum(1 for e in tops if e[3] == 'n')
        n_top_own = sum(1 for e in tops if e[3] == 'own')
        n_top_foe = sum(1 for e in tops if e[3] == 'foe')
        ram = [d for g in gs for d in g['deaths'] if d[1] == s and d[4] == 'rammed' and d[3] == 1 and d[0] > 350 and d[2] >= 10]
        print('  %s: feeders %d per game %.0f, length %d, pearls dropped %d: eaten by leader/queen %d (%.0f%%), by any own %d (%.0f%%), by enemy %d (%.0f%%) | leader eats after r350 per game: natural %.1f own-corpse %.1f enemy-corpse %.1f | longest r350 %.1f r400 %.1f r450 %.1f r475 %.1f end %.1f | the side\'s longest dragon (10+) rammed after r350: %d times, length %d' % (
            nm, len(st), len(st) / len(gs), sum(d[2] for d in st), drop, top, 100 * top / max(1, drop), own, 100 * own / max(1, drop), foe, 100 * foe / max(1, drop),
            n_top_nat / len(gs), n_top_own / len(gs), n_top_foe / len(gs), L(350), L(400), L(450), L(475), L(499), len(ram), sum(d[2] for d in ram)))
for arm in A:
    table(arm, None, 'all r499 games')
print()
for arm in ('h2h_mDone11_v8', 'h2h_mDone10_v8'):
    table(arm, common, 'common map+side pairs')
