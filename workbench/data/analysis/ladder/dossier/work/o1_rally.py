"""Scratch (diag-one1, job H): end rally arm against its base on the same local games.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_rally.py <rally arm> <base arm>"""
import sys, statistics as st
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
A, B = sys.argv[1], sys.argv[2]
ga = {g['folder']: g for g in rows(A)}
gb = {g['folder']: g for g in rows(B)}


def m(g):
    e = g['ends']
    stops = [d for d in g['deaths'] if d[1] == 0 and d[4] == 'stop' and d[5] > 0 and d[0] > 400]
    lead = [(d[0], d[2]) for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[0] > 400 and d[2] >= 20 and d[3] == 1]
    longr = [(d[0], d[2]) for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[0] > 400 and d[2] >= 20]
    return dict(u400=snap(g, 400)[0][0], uend=e[0][0], stops=len(stops), stopL=sum(d[2] for d in stops), L400=snap(g, 400)[0][2], Lend=e[0][2], oL400=snap(g, 400)[1][2], oLend=e[1][2],
                T400=snap(g, 400)[0][1], Tend=e[0][1], oTend=e[1][1], q=e[0][3], oq=e[1][3], qlead=int(e[0][3] > 0 and e[0][3] == e[0][2]), lead=lead, longr=longr,
                win=int(g['result'] == 'win'), how=g['how'], rams_on=sum(1 for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[0] > 400), last=g['last'])


keys = ['u400', 'uend', 'stops', 'stopL', 'L400', 'Lend', 'oLend', 'T400', 'Tend', 'oTend', 'q', 'rams_on', 'win']
ta, tb, n = {k: [] for k in keys}, {k: [] for k in keys}, 0
for f in sorted(set(ga) & set(gb)):
    a, b = m(ga[f]), m(gb[f])
    n += 1
    for k in keys:
        ta[k].append(a[k]); tb[k].append(b[k])
    for lab, x, g in ((A, a, ga[f]), (B, b, gb[f])):
        print('%-40s %-8s %-4s %-7s | dragons r400/end %2d/%2d | stops r401+ %3d (length %3d) | longest r400/end %3d/%3d (theirs %3d/%3d) | total r400/end %3d/%3d (theirs %3d) | queen %d/%d%s | long bodies rammed after r400 %s (the longest: %s)' % (
            f[:40], lab, g['result'], x['how'], x['u400'], x['uend'], x['stops'], x['stopL'], x['L400'], x['Lend'], x['oL400'], x['oLend'], x['T400'], x['Tend'], x['oTend'], x['q'], x['oq'], ' (she is the longest)' if x['qlead'] else '', x['longr'], x['lead']))
print()
print('pairs', n)
for k in keys:
    if n:
        print('%-8s %s %7.1f   %s %7.1f   rally higher in %d, lower in %d' % (k, A, st.mean(ta[k]), B, st.mean(tb[k]), sum(x > y for x, y in zip(ta[k], tb[k])), sum(x < y for x, y in zip(ta[k], tb[k]))))
