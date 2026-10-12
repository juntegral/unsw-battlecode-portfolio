"""Scratch (diag-one1, job B): table of turn classes r0-100. Usage: o1_earlytab.py <set[:bot]> <all|small|big> [window 0|1|2|all]"""
import sys, json
from collections import Counter
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
spec, cls = sys.argv[1], sys.argv[2]
win = sys.argv[3] if len(sys.argv) > 3 else 'all'
name, _, bot = spec.partition(':')
gs = []
for l in open(W + 'o1_mid-%s.jsonl' % name):
    g = json.loads(l)
    if bot and g['bot'] != bot:
        continue
    if cls == 'all' or (cls == 'big') == (g['cells'] > 1200):
        gs.append(g)
n = len(gs)
T = [Counter(), Counter(), Counter()]
for g in gs:
    for s, w, k, v in g['C']:
        if win == 'all' or int(win) == w:
            T[s][k] += v
print('==', spec, cls, 'games', n, 'window', win, '| per game: ours | theirs   (share of turns)')
o, t = T[0], T[1]
def row(lab, k, share=True):
    a, b = o[k] / n, t[k] / n
    if share:
        print('%-28s %7.1f %7.1f   %5.1f%% %5.1f%%' % (lab, a, b, 100 * o[k] / max(1, o['turns']), 100 * t[k] / max(1, t['turns'])))
    else:
        print('%-28s %7.1f %7.1f' % (lab, a, b))
row('natural pearls born', 'born', False) if False else print('%-28s %7.1f' % ('natural pearls born', T[2]['born'] / n))
row('natural pearls eaten', 'pearls nat', False)
row('dead pearls eaten', 'pearls dead', False)
row('deaths', 'deaths', False)
row('  head-on', 'death head-on', False)
row('dead length', 'dead length', False)
row('dragon turns', 'turns', False)
for k in ('foe head in view', 'on the other side of the board', 'eat', 'split', 'died', 'blind', 'walled', 'mate', 'approach', 'away'):
    row(k, k)
for k in sorted(set(o) | set(t)):
    if k.startswith('away') and k != 'away' or k.startswith('blind:') or k.startswith('own pearl') or k.startswith('q:') or k.startswith('turns L') or k.startswith('O4+') or k.startswith('Q4+'):
        row('  ' + k, k)
print('pearl in view share: %.1f%% %.1f%%; eat | pearl in view: %.1f%% %.1f%%; eat per 100 turns %.1f %.1f' % (
    100 * o['pearl in view'] / max(1, o['turns']), 100 * t['pearl in view'] / max(1, t['turns']),
    100 * o['eat'] / max(1, o['pearl in view']), 100 * t['eat'] / max(1, t['pearl in view']),
    100 * o['eat'] / max(1, o['turns']), 100 * t['eat'] / max(1, t['turns'])))
