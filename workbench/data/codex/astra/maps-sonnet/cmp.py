import sys
from collections import Counter
a, b = sys.argv[1:3]
def load(p):
    d = {'T': {}, 'E': [], 'D': [], 'H': []}
    for ln in open(p):
        q = ln.split()
        if not q or q[0] == '#': continue
        if q[0] == 'TILE': d['T'][(int(q[1]), int(q[2]))] = (int(q[3]), int(q[4]))
        elif q[0] == 'EDGE': d['E'].append(tuple(q[1:]))
        elif q[0] == 'DRAGON': d['D'].append(tuple(q[1:]))
        else: d['H'].append(ln.strip())
    return d
A, B = load(a), load(b)
print('header equal', A['H'] == B['H'], '| edges equal', A['E'] == B['E'], len(A['E']))
swap = [(str(1 - int(x[0])),) + x[1:] for x in A['D']]
print('dragons equal', A['D'] == B['D'], '| equal after A/B swap', swap == B['D'])
ba = {c for c, v in A['T'].items() if v != (0, 0)}; bb = {c for c, v in B['T'].items() if v != (0, 0)}
print('beds ref', len(ba), 'mine', len(bb), 'common', len(ba & bb), 'only ref', len(ba - bb), 'only mine', len(bb - ba))
print('ref gap values', Counter(A['T'][c] for c in ba).most_common(6))
print('mine gap values', Counter(B['T'][c] for c in bb).most_common(6))
