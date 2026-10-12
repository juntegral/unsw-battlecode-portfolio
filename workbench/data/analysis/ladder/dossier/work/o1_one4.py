"""Scratch (diag-one1, job G): the opening rows by build against one opponent. Usage: o1_one4.py <set> [<set> ...]"""
import sys, json, os
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
for nm in sys.argv[1:]:
    pp, ps = W + 'o1_pearl-%s.jsonl' % nm, W + 'o1_scan-%s.jsonl' % nm
    if not os.path.exists(pp):
        print(nm, 'missing'); continue
    S = {g['gid']: g for g in map(json.loads, open(ps))}
    P = list(map(json.loads, open(pp)))
    u = lambda g, s, r: (g['units'][s][r] if r < len(g['units'][s]) else (g['units'][s][-1] if g['units'][s] else 0))
    for lab, sel in (('two-dragon small starts', lambda g: g['cells'] <= 1200 and g['start'][0][0] < 4), ('4-long-queen small starts', lambda g: g['cells'] <= 1200 and g['start'][0][0] >= 4), ('big maps', lambda g: g['cells'] > 1200)):
        G = [g for g in P if sel(g)]
        if not G:
            continue
        n = len(G)
        q0 = sum(1 for g in G if any(r == 0 and s == 0 and q for r, s, Lb, Lc, q in g['splits']))
        qe = sum(1 for g in G if any(r <= 20 and s == 0 and q for r, s, Lb, Lc, q in g['splits']))
        wins = sum(S[g['gid']]['result'] == 'win' for g in G)
        elim = sum(S[g['gid']]['result'] == 'loss' and S[g['gid']]['how'] == 'elim' for g in G)
        nat = lambda s, R: sum(1 for g in G for r, sd, role, o, kd, L0 in S[g['gid']]['eats'] if sd == s and r <= R and o == 'n') / n
        print('%-4s %-26s %2d games, won %d, eliminated %d | dragons ours/theirs r0 %.1f/%.1f r10 %.1f/%.1f r25 %.1f/%.1f r50 %.1f/%.1f r100 %.1f/%.1f | natural pearls by r30 %.1f/%.1f, r100 %.1f/%.1f | our queen split in r0: %d games, by r20: %d' % (
            nm, lab, n, wins, elim, *[sum(u(g, s, r) for g in G) / n for r in (0, 10, 25, 50, 100) for s in (0, 1)], nat(0, 30), nat(1, 30), nat(0, 100), nat(1, 100), q0, qe))
    for g in P:
        if g['map'] in ('Queen Of Spades', 'Australia', 'Stripes'):
            s = S[g['gid']]
            m = [[r for r, sd, role, o, kd, L0 in s['eats'] if sd == k][:3] for k in (0, 1)]
            qd = [d[0] for d in s['deaths'] if d[6] and d[1] == 0]
            print('     %-16s %s %s | first three meals ours %s theirs %s | pearls by r30 %d/%d | dragons r25 %d/%d r100 %d/%d | our queen died %s' % (g['map'], s['result'], s['how'], m[0], m[1],
                  sum(1 for r, sd, *_ in s['eats'] if sd == 0 and r <= 30), sum(1 for r, sd, *_ in s['eats'] if sd == 1 and r <= 30), u(g, 0, 25), u(g, 1, 25), u(g, 0, 100), u(g, 1, 100), qd or 'alive'))
