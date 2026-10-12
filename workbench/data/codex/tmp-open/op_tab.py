#!/usr/bin/env python3
"""op_tab.py <baseline arm> <test arm>... : opening table from op_<arm>.jsonl on the games every named arm has."""
import sys
import json
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parent


def rows(arm):
    return {r['game']: r for r in map(json.loads, open(HERE/f'op_{arm}.jsonl'))}


def m(xs):
    xs = [x for x in xs if x is not None]
    return f'{mean(xs):.1f}' if xs else '-'


def main():
    names = sys.argv[1:]
    arms = [rows(a) for a in names]
    games = sorted(g for g in arms[-1] if all(g in a for a in arms))
    sets = [[a[g] for g in games] for a in arms]
    print(f'games {len(games)}')
    line = lambda name, f: print(f'| {name} | ' + ' | '.join(f(R) for R in sets) + ' |')
    print('| count | ' + ' | '.join(names) + ' |\n|---|' + '---|' * len(names))
    line('queen first split round, mean (median; games she never split)',
         lambda R: f"{m([r['queen_first_split'] for r in R])} ({median([r['queen_first_split'] for r in R if r['queen_first_split'] is not None] or [0])}; {sum(r['queen_first_split'] is None for r in R)})")
    line('starter first split round, mean over starters (never)',
         lambda R: f"{m([x for r in R for x in r['first_split']])} ({sum(x is None for r in R for x in r['first_split'])} of {sum(len(r['first_split']) for r in R)})")
    line('starters of 4+ that split in round 0 / such starters',
         lambda R: f"{sum(x == 0 for r in R for x, L in zip(r['first_split'], r['starters']) if L >= 4)} / {sum(L >= 4 for r in R for L in r['starters'])}")
    for f, lab in (('n', 'own dragons'), ('tot', 'total length'), ('pearls', 'pearls eaten')):
        marks = (10, 20, 40, 60, 100, 300) if f == 'n' else (20, 40, 100, 300)
        line(f'{lab} at r' + ', r'.join(map(str, marks)), lambda R: ', '.join(m([r[f'{f}_r{k}'] for r in R]) for k in marks))
    pg = [g for g in games if arms[0][g]['portal_edges'] > 0]
    for key, lab in (('portal', 'any starter line'), ('portal_nq', 'a non-queen starter line')):
        print(f"| portal maps ({len(pg)} games): {lab} through a portal by r10, r20 | "
              + ' | '.join(f"{sum(R[g][key+'_r10'] for g in pg)}, {sum(R[g][key+'_r20'] for g in pg)}" for R in arms) + ' |')
    line('queen length at r40, r100, r150 (dead = 0)', lambda R: ', '.join(m([r[f'q_r{k}'] for r in R]) for k in (40, 100, 150)))
    line('queen alive at r40, r100, r150 (games)', lambda R: ', '.join(str(sum(r[f'q_r{k}'] > 0 for r in R)) for k in (40, 100, 150)))
    line('queen turns at 4+ in r0-40 a game; split on them', lambda R: f"{m([r['qturn4'] for r in R])}; {sum(r['qsplit4'] for r in R)} of {sum(r['qturn4'] for r in R)}")
    line('queen dead by r40: games (round, length, cause)', lambda R: f"{sum(1 for r in R if r['qdeath'] and r['qdeath'][0] <= 40)} " + ' '.join(f"({r['qdeath'][0]},{r['qdeath'][2]},{r['qdeath'][3]})" for r in R if r['qdeath'] and r['qdeath'][0] <= 40))
    line('queen turns r0-40 at length 2 with an enemy head within 4 (games with any)', lambda R: f"{sum(r['q2hunt'] for r in R)} ({sum(r['q2hunt'] > 0 for r in R)})")
    line('own deaths in r0-5; children born r0-1 dead within 10 rounds', lambda R: f"{sum(len(r['deaths_r5']) for r in R)}; {sum(len(r['deaths_child10']) for r in R)}")
    line('own deaths by r40 a game', lambda R: m([r['ndeaths_r40'] for r in R]))
    print()
    for g in games:
        for name, a in zip(names, arms):
            r = a[g]
            qd = r['qdeath']
            print(f"{name[:7]} {g[:40]:40} st{r['starters']} fs{r['first_split']} n {r['n_r10']},{r['n_r20']},{r['n_r40']},{r['n_r60']},{r['n_r100']},{r['n_r300']} "
                  f"p {r['pearls_r20']},{r['pearls_r40']} tot {r['tot_r40']},{r['tot_r100']},{r['tot_r300']} port {r['portal_r10']}{r['portal_r20']} "
                  f"q {r['q_r40']},{r['q_r100']},{r['q_r150']} q4 {r['qsplit4']}/{r['qturn4']} q2h {r['q2hunt']} qd {qd[:4] if qd else None} d5 {len(r['deaths_r5'])} rd {r['rounds']} | {r['result'][:60]}")


if __name__ == '__main__':
    main()
