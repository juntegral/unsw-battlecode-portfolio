"""Final-bot battery so far: each combo's games beside the live bot's same games (result lines; pearls and dragons at r100)."""
import glob, os, re, sys, time
sys.dont_write_bytecode = True
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
sys.path.insert(0, 'tools'); sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
R = os.path.expanduser('~/meow-redteam/solo/runs/')
print(time.strftime('%H:%M:%S'))
def nat(g):
    return sum(1 for r, s, role, origin, kd, L0 in g['eats'] if s == 0 and origin == 'n' and r <= 100)
def table(bases, arms):
    G = {}
    for a in bases + arms:
        try:
            for g in rows(a):
                G.setdefault(g['folder'], {})[a] = g
        except Exception as e:
            print('no rows for', a, e)
    print('%-34s' % 'game', ' '.join('%-22s' % a for a in bases + arms))
    for f in sorted(G):
        if sum(1 for a in arms if a in G[f]) == 0:
            continue
        cells = []
        for a in bases + arms:
            g = G[f].get(a)
            cells.append('%-22s' % ('%3d %2d %-5s L%s' % (nat(g), snap(g, 100)[0][0], g['result'], g.get('rounds', '')) if g else '-'))
        print('%-34s' % f[:34], ' '.join(cells))
table(['nr_mD18', 'qda_mD18'], ['nr_mA19', 'nr_mB19'])
table(['st_mD18'], ['st_mA19', 'st_mC19'])
