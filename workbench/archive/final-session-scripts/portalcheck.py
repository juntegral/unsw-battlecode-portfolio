"""Check of the subagent's claim: our pearls eaten by r100 per map, one11 against one12 and one13, from the label report caches."""
import json, glob, collections, os, re
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
D = 'data/analysis/ladder/dossier/online/'
cache = json.load(open(D + 'label-report-cache.json'))
rows = cache if isinstance(cache, list) else list(cache.values()) if isinstance(cache, dict) else []
# find per-game rows that carry label, map and checkpoints
def walk(o, out):
    if isinstance(o, dict):
        if 'label' in o and 'map' in o and 'game' in o:
            out.append(o)
        else:
            for v in o.values():
                walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)
games = []
walk(cache, games)
print('rows', len(games))
def pearls100(g):
    s = json.dumps(g)
    m = re.search(r'"100": \[\{[^}]*"pearls": (\d+)', s)
    return int(m.group(1)) if m else None
T = collections.defaultdict(lambda: collections.defaultdict(list))
seen = set()
for g in games:
    lab = g['label']
    m = re.match(r'(one\d+)-', lab)
    if not m or (g['game'], lab) in seen:
        continue
    seen.add((g['game'], lab))
    p = pearls100(g)
    if p is not None:
        T[g['map']][m.group(1)].append(p)
vers = ['one8', 'one10', 'one11', 'one12', 'one13', 'one14']
print('%-16s' % 'map', ' '.join('%-12s' % v for v in vers))
for mp in sorted(T):
    print('%-16s' % mp[:16], ' '.join('%-12s' % ('%.0f (%d)' % (sum(T[mp][v]) / len(T[mp][v]), len(T[mp][v])) if T[mp][v] else '-') for v in vers))
