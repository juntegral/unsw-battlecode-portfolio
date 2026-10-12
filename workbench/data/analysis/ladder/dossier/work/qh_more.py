"""Scratch (diag-queenhit): side counts from qh_turns.jsonl + qh_fates.json: hazard by queen length, what a ram offer
is worth (did the enemy take it), queen splits near heads, allies that could have traded with the rammer, chase lengths."""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
fates = dict((f['game'], f) for f in json.loads((WORK / 'qh_fates.json').read_text()))
turns = defaultdict(list)
with (WORK / 'qh_turns.jsonl').open() as fh:
    for line in fh:
        t = json.loads(line)
        turns[t['game']].append(t)


def true_reach(n):
    return (n + 3) // 4 + n - 2


def man(a, b, W, H):
    dx, dy = abs(a % W - b % W), abs(a // W - b // W)
    return min(dx, W - dx) + min(dy, H - dy)


def cheb(a, b, W, H):
    dx, dy = abs(a % W - b % W), abs(a // W - b // W)
    return max(min(dx, W - dx), min(dy, H - dy))


c = Counter()
byL = defaultdict(Counter)
offer = Counter()
for g, ts in turns.items():
    for t in ts:
        near3 = bool(t['near']) and t['near'][0][0] <= 3
        dead = t['hit_after'] is not None
        L = min(t['L'], 5)
        if near3:
            byL[L]['near3'] += 1
            byL[L]['hit'] += dead
        byL[L]['turns'] += 1
        e = t.get('end')
        if e is None:
            continue
        # the tile she ended on could truly be reached by an enemy head this round (length and edges as they stood)
        dg = [x for x in t['danger'].get(str(e), []) if x[0] >= 0]
        risk = 2 if e in t['hit'] else 1 if e in t['pay'] else 0
        if dg:
            offer['offered'] += 1
            offer['offered, taken'] += dead
            offer['offered ring%d' % risk] += 1
            offer['offered ring%d, taken' % risk] += dead
            free = any(x[1] <= (x[2] + 3) // 4 for x in dg)
            offer['offered free step' if free else 'offered paid only'] += 1
            offer[('offered free step' if free else 'offered paid only') + ', taken'] += dead
        elif dead:
            offer['hit without a true-reach offer (pearls, child, model)'] += 1
print('== hazard by queen length (5 = 5 or more) ==')
for L in sorted(byL):
    print('  L', L, dict(byL[L]))
print('== ram offers: she ended her turn on a tile an enemy head could truly reach that round ==')
print(' ', dict(offer))

print('== queen splits ==')
sp = Counter()
for g, ts in turns.items():
    for k, t in enumerate(ts):
        a = t.get('action') or {}
        if a.get('kind') != 'split':
            continue
        heads = [e for e in t['enemies'] if not e['queen']]
        sp['splits'] += 1
        sp['splits L%d' % min(t['L'], 6)] += 1
        sp['splits with a head in view'] += bool(heads)
        sp['splits with a head within 6 steps'] += bool(t['near']) and t['near'][0][0] <= 6
        sp['splits round<=100'] += t['round'] <= 100
print(' ', dict(sp))
for g, f in fates.items():
    d = f['fate']
    if d is None or d['mover'] or d['cause'] != 'head-on':
        continue
    ts = turns[g]
    last = [(t['round'], t['L'], len([e for e in t['enemies'] if not e['queen']]), t['near'][0][0] if t['near'] else None) for t in ts if (t.get('action') or {}).get('kind') == 'split']
    paid = [(t['round'], t['L'], t['L_after']) for t in ts[-12:] if (t.get('action') or {}).get('kind') == 'move' and t.get('L_after', 0) < t['L']]
    maxL = max(t['L'] for t in ts)
    print('  ', g, 'death r', d['round'], 'L', d['L'], 'max L ever', maxL, 'splits', len(last), 'last split (round, L, heads in view, nearest)', last[-1] if last else None, 'paid sprints in last 12 turns', paid)

print('== allies near the rammer on her last turns ==')
al = Counter()
for g, f in fates.items():
    d = f['fate']
    if d is None or d['mover'] or d['cause'] != 'head-on':
        continue
    ts = turns[g]
    Wd, H = f['W'], f['H']
    rid = str(d['rammer']['id'])
    found = []
    for back, t in enumerate(reversed(ts[-3:])):
        if rid not in t['local']:
            continue
        rh = t['local'][rid][1][0]
        for i, (own, b) in t['local'].items():
            if not own or int(i) == f['Q']:
                continue
            dist = man(b[0], rh, Wd, H)
            sees = cheb(b[0], rh, Wd, H) <= 3
            if sees and dist <= min(true_reach(len(b)), 3):
                found.append((back, int(i), len(b), dist))
    own5 = sum(1 for i, (own, b) in ts[-1]['local'].items() if own and int(i) != f['Q'] and man(b[0], ts[-1]['head'], Wd, H) <= 5)
    al['deaths'] += 1
    al['an ally head within 5 tiles of her at the last turn'] += own5 > 0
    al['an ally could reach the rammer head (sees it, within its own steps, cap 3) in the last 3 turns'] += bool(found)
    al['... on her last turn'] += any(x[0] == 0 for x in found)
    print('  ', g, 'allies within 5:', own5, 'could ram (turns back, id, L, dist):', found[:4])
print(' ', dict(al))

print('== chases: runs of consecutive turns with an enemy head within 3 steps ==')
runs = Counter()
lens_dead, lens_live = [], []
for g, ts in turns.items():
    run = 0
    for t in ts:
        near3 = bool(t['near']) and t['near'][0][0] <= 3
        if near3:
            run += 1
            if t['hit_after'] is not None:
                lens_dead.append(run)
                run = 0
        else:
            if run:
                lens_live.append(run)
            run = 0
    if run:
        lens_live.append(run)
print('  runs ending in the hit', len(lens_dead), sorted(Counter(lens_dead).items()))
print('  runs she left alive', len(lens_live), sorted(Counter(min(x, 10) for x in lens_live).items()))
