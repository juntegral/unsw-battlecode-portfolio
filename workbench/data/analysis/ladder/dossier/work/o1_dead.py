"""Scratch (diag-one1): deaths in a window by cause x length x rounds since split x free sides; who eats the drop."""
import sys, json
from collections import Counter, defaultdict
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/')
from o1_ledger import load
name = sys.argv[1]
lo, hi = int(sys.argv[2]), int(sys.argv[3])
gs = load(name)
n = len(gs)
for s in (0, 1):
    print('== side', 'ours' if s == 0 else 'theirs', name, lo, hi, 'per game')
    C = defaultdict(Counter)
    for g in gs:
        for d in g['deaths']:
            if d[1] != s or not (lo < d[0] <= hi):
                continue
            k = d[4]
            c = C[k]
            L = d[2]
            c['n'] += 1
            c['len'] += L
            c['L2' if L == 2 else 'L3' if L == 3 else 'L4' if L == 4 else 'L5-9' if L <= 9 else 'L10+'] += 1
            c['len_L10+'] += L if L >= 10 else 0
            c['len_L5-9'] += L if 5 <= L <= 9 else 0
            ss = d[7]
            c['split<=1' if 0 <= ss <= 1 else 'split2-5' if 2 <= ss <= 5 else 'split6+'] += 1
            c['free0' if d[5] == 0 else 'free1+'] += 1
            c['queen'] += d[6]
            c['top'] += d[3]
            c['drop'] += d[15]
            c['own'] += d[10]
            c['foe'] += d[11]
            c['ownQT'] += d[12]
            c['own10'] += d[13]
            c['foe10'] += d[14]
            c['mates5>0'] += d[8] > 0
            c['foes5>0'] += d[9] > 0
    keys = ['n', 'len', 'L2', 'L3', 'L4', 'L5-9', 'L10+', 'len_L5-9', 'len_L10+', 'split<=1', 'split2-5', 'split6+', 'free0', 'free1+', 'top', 'drop', 'own', 'foe', 'ownQT', 'own10', 'foe10', 'mates5>0', 'foes5>0']
    print('%-10s' % 'cause' + ''.join('%9s' % k for k in keys))
    tot = Counter()
    for k in ('rammed', 'rams', 'stop', 'wall', 'own body', 'mate body', 'foe body', 'mate head'):
        print('%-10s' % k + ''.join('%9.1f' % (C[k][x] / n) for x in keys))
        tot.update(C[k])
    print('%-10s' % 'all' + ''.join('%9.1f' % (tot[x] / n) for x in keys))
