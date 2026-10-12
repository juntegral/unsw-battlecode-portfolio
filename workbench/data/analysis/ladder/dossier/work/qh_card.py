"""Scratch (diag-queenhit): the two carded rules on paper. KEEP(S): among the tiles the ring veto leaves unpenalised,
prefer the one a seen head needs more turns to reach (capped at S+1). AHEAD(K): then prefer the one from which she can
keep walking K turns ahead of the seen heads. Prints every changed move in a death run-up with the true state of the
tile the rule would take, the hazard by arrival time of the tile she ended on, and the cost on all other turns."""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
DN = 'NESW'
S, K = 2, 4
fates = dict((f['game'], f) for f in json.loads((WORK / 'qh_fates.json').read_text()))
turns = defaultdict(list)
with (WORK / 'qh_turns.jsonl').open() as fh:
    for line in fh:
        t = json.loads(line)
        turns[t['game']].append(t)
hits = [g for g, f in fates.items() if f['fate'] and not f['fate']['mover'] and f['fate']['cause'] == 'head-on']


def first_step(t):
    a = t.get('action')
    if not a or a['kind'] != 'move' or not a['dirs']:
        return None
    return [c for c in t['cands'] if c['d'] == a['dirs'][0]][0]


def unpen(t):
    sc = [c for c in t['cands'] if c.get('enterable') and c['kind'] == 'open']
    o0 = any(c['risk'] == 0 and not c['closed'] for c in sc)
    o1 = any(c['risk'] == 1 and not c['closed'] for c in sc)
    return [c for c in sc if c['risk'] == 0] if o0 else [c for c in sc if c['risk'] <= 1] if o1 else sc


def val(c, mode):
    keep = min(c['arr'], S + 1)
    ahead = min(c['ah'], K)
    return (keep,) if mode == 'keep' else (ahead,) if mode == 'ahead' else (ahead, keep)


def fire(t, mode):
    f = first_step(t)
    if f is None or not f.get('enterable') or f['kind'] != 'open':
        return None
    U = unpen(t)
    if f not in U:
        return None
    best = max(val(c, mode) for c in U)
    if val(f, mode) >= best:
        return None
    return f, [c for c in U if val(c, mode) == best]


for mode in ('keep', 'ahead', 'both'):
    c = Counter()
    deaths = {}
    for g, ts in turns.items():
        for k, t in enumerate(ts):
            fr = fire(t, mode)
            if fr is None:
                continue
            back = len(ts) - 1 - k
            c['changed moves'] += 1
            if g in hits and back <= 7:
                deaths.setdefault(g, []).append((back, t, fr))
            else:
                near3 = bool(t['near']) and t['near'][0][0] <= 3
                c['elsewhere'] += 1
                c['elsewhere near3'] += near3
                c['elsewhere: she took a pearl'] += bool(fr[0].get('pearl'))
                c['elsewhere: a head in view'] += any(not e['queen'] for e in t['enemies'])
    strict = []
    print('==', mode, 'S=%d K=%d' % (S, K), dict(c), '| deaths with a changed move in the last 8:', len(deaths), 'last 3:', sum(any(x[0] <= 2 for x in v) for v in deaths.values()))
    for g in hits:
        for back, t, (f, alts) in deaths.get(g, []):
            ok = [a for a in alts if not [x for x in a['danger'] if x[0] >= 0] and not a['closed']]
            good = bool(ok) and back <= 2 and max(a['ah'] for a in ok) > back
            if good and g not in strict:
                strict.append(g)
            if mode == 'both':
                print('   ', g, fates[g]['map'], 'death r', fates[g]['fate']['round'], '| %d back (r%d): took %s keep %d ahead %d | rule takes %s' % (
                    back, t['round'], DN[f['d']], min(f['arr'], S + 1), f['ah'],
                    ' or '.join('%s keep %d ahead %d%s%s' % (DN[a['d']], min(a['arr'], S + 1), a['ah'], ' closed' if a['closed'] else '', ' TRULY REACHABLE' if [x for x in a['danger'] if x[0] >= 0] else '') for a in alts)),
                      '| counted' if good else '')
    print('   counted as prevented (changed move in her last 3 turns, new tile open, out of true reach that round, look-ahead longer than the turns she had left):', len(strict), strict)

print()
print('== hazard by how soon a seen head could reach the tile she ended on (single steps, a head in view) ==')
hz = defaultdict(Counter)
for g, ts in turns.items():
    for k, t in enumerate(ts):
        f = first_step(t)
        if f is None or not f.get('enterable') or f['kind'] != 'open' or not any(not e['queen'] for e in t['enemies']):
            continue
        a = min(f['arr'], 4)
        hz[a]['turns'] += 1
        hz[a]['hit this round'] += t['hit_after'] is not None
        hz[a]['hit within 2 more rounds'] += g in hits and len(ts) - 1 - k <= 2
        hz[a]['had a later tile'] += any(min(c['arr'], 4) > a for c in unpen(t)) and f in unpen(t)
for a in sorted(hz):
    print('   arrival', a, dict(hz[a]))
pe = Counter()
for g, ts in turns.items():
    for t in ts:
        f = first_step(t)
        pe['moves'] += f is not None
        pe['pearl steps'] += bool(f and f.get('pearl'))
print('   her moves', dict(pe))
