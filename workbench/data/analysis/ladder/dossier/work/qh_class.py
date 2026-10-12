"""Scratch (diag-queenhit): classes of the queen's head-on-hit deaths, the survived-turn denominator, and the two
candidate rules replayed on every turn. Reads qh_turns.jsonl + qh_fates.json. Usage: python3 .../qh_class.py [runup]"""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
DN = 'NESW'
fates = json.loads((WORK / 'qh_fates.json').read_text())
turns = defaultdict(list)
with (WORK / 'qh_turns.jsonl').open() as fh:
    for line in fh:
        t = json.loads(line)
        turns[t['game']].append(t)


def true_reach(n):
    return (n + 3) // 4 + n - 2


def size_band(cells):
    return '<=700' if cells <= 700 else '701-1200' if cells <= 1200 else '>1200'


def round_band(r):
    return '0-100' if r <= 100 else '101-300' if r <= 300 else '>300'


def first_step(t):
    a = t.get('action')
    if not a or a['kind'] != 'move' or not a['dirs']:
        return None
    d = a['dirs'][0]
    return [c for c in t['cands'] if c['d'] == d][0]


def unpen(t, key):
    """Candidates the ring veto leaves without a penalty (pick_direction, main.cpp:5318-5344)."""
    sc = [c for c in t['cands'] if c.get('enterable') and not (c['kind'] == 'portal' and t['cells'] > 600)]
    o0 = any(c[key] == 0 and not c['closed'] for c in sc)
    o1 = any(c[key] == 1 and not c['closed'] for c in sc)
    if o0:
        return [c for c in sc if c[key] == 0], o0, o1
    if o1:
        return [c for c in sc if c[key] <= 1], o0, o1
    return sc, o0, o1


def ahead_fire(t, K, key='risk', akey='ah'):
    """The look-ahead rule would move her off the tile she took: (actual depth, best depth) or None."""
    f = first_step(t)
    if f is None or not f.get('enterable') or f.get(akey) is None:
        return None
    U, o0, o1 = unpen(t, key)
    U = [c for c in U if c.get(akey) is not None]
    if f not in U or not U:
        return None
    best = max(min(c[akey], K) for c in U)
    mine = min(f[akey], K)
    return (mine, best) if mine < best else None


def end_risk(t):
    e = t.get('end')
    return None if e is None else 2 if e in t['hit'] else 1 if e in t['pay'] else 0


rows = []
for f in fates:
    d = f['fate']
    if d is None or d['mover'] or d['cause'] != 'head-on':
        continue
    ts = turns[f['game']]
    t = ts[-1]
    r = d['rammer']
    seen = [e for e in t['enemies'] if e['id'] == r['id']]
    er = end_risk(t)
    a = t.get('action') or {}
    sides = Counter()
    for c in t['cands']:
        sides['kelp' if c['kind'] == 'kelp' else c['occ'] if not c['enterable'] else 'ring%d' % c['risk'] + ('closed' if c['closed'] else '')] += 1
    if not r['enemy']:
        cls = 'own team'
    elif a.get('kind') != 'move' or not a.get('dirs'):
        cls = 'no move'
    elif not r['existed']:
        cls = 'unseen: split child'
    elif r['is_enemy_queen']:
        cls = 'enemy queen (no ring)'
    elif not seen:
        cls = 'unseen: outside view'
    elif er == 0:
        cls = 'ring small: pearls' if r['steps'] > true_reach(r['L']) else 'ring small: length cut' if seen[0]['reach'] < true_reach(r['L']) else 'ring small: other'
    elif t['open0']:
        cls = 'BUG ringed with clean open'
    else:
        cls = 'boxed: took pay tile' if er == 1 else 'boxed: only hit tiles'
    rows.append(dict(game=f['game'], label=f['label'], map=f['map'], cells=f['cells'], result=f['result'], round=d['round'], L=d['L'], cls=cls,
                     sides=dict(sides), ram=r, seen=seen, t=t, ts=ts))

print('head-on-hit queen deaths', len(rows), 'games', len(fates), 'other queen deaths', Counter((f['fate']['cause'], f['fate']['mover']) for f in fates if f['fate'] and (f['fate']['mover'] or f['fate']['cause'] != 'head-on')),
      'alive', sum(f['fate'] is None for f in fates))
print('by label', Counter(r['label'] for r in rows))
print()
print('== classes ==')
order = [c for c, _ in Counter(r['cls'] for r in rows).most_common()]
for c in order:
    rs = [r for r in rows if r['cls'] == c]
    print('%-28s all %2d | r0-100 %2d r101-300 %2d r>300 %2d | <=700 %2d 701-1200 %2d >1200 %2d | L2 %2d L3 %2d L4+ %2d | %s' % (
        c, len(rs), sum(round_band(r['round']) == '0-100' for r in rs), sum(round_band(r['round']) == '101-300' for r in rs), sum(round_band(r['round']) == '>300' for r in rs),
        sum(size_band(r['cells']) == '<=700' for r in rs), sum(size_band(r['cells']) == '701-1200' for r in rs), sum(size_band(r['cells']) == '>1200' for r in rs),
        sum(r['L'] == 2 for r in rs), sum(r['L'] == 3 for r in rs), sum(r['L'] >= 4 for r in rs), ' '.join(str(r['game']) for r in rs)))
print('totals: r0-100 %d r101-300 %d r>300 %d | <=700 %d 701-1200 %d >1200 %d' % (
    sum(round_band(r['round']) == '0-100' for r in rows), sum(round_band(r['round']) == '101-300' for r in rows), sum(round_band(r['round']) == '>300' for r in rows),
    sum(size_band(r['cells']) == '<=700' for r in rows), sum(size_band(r['cells']) == '701-1200' for r in rows), sum(size_band(r['cells']) == '>1200' for r in rows)))
print()
print('rammer crossed a portal', sum(bool(r['ram'].get('portal')) for r in rows), '| rammer a visible head at her last turn', sum(bool(r['seen']) for r in rows),
      '| clean single step open at her last turn', sum(r['t']['open0'] for r in rows), '| by class', dict(Counter(r['cls'] for r in rows if r['t']['open0'])))
print('clean two-step sprint in view at her last turn, deaths with no clean single step:', [(r['game'], r['L'], r['t']['sprint2']) for r in rows if not r['t']['open0']])
print('== boxed deaths: what closed the four sides at her last turn ==')
box = [r for r in rows if r['cls'].startswith('boxed')]
for r in box:
    s = r['sides']
    kelp = s.get('kelp', 0)
    ally = s.get('allyB', 0) + s.get('allyH', 0)
    r['boxkind'] = 'kelp on 2+ sides' if kelp >= 2 else 'ally body/head on a side' if ally else '2+ enemy heads, 0-1 kelp' if len([e for e in r['t']['enemies'] if not e['queen']]) >= 2 else 'one enemy, 0-1 kelp'
    print(' ', r['game'], r['map'], 'r', r['round'], 'L', r['L'], r['cls'], '|', r['boxkind'], '|', s, '| rammer L', r['ram']['L'], 'steps', r['ram']['steps'], 'heads in view', len([e for e in r['t']['enemies'] if not e['queen']]))
print(' ', Counter(r['boxkind'] for r in box))
print('  rammer length at its turn', Counter(r['ram']['L'] for r in rows), 'steps', Counter(r['ram']['steps'] for r in rows), 'queen length', Counter(r['L'] for r in rows))
print()
print('== denominator: her turns with an enemy head within 3 steps of her head ==')
den = Counter()
for g, ts in turns.items():
    for t in ts:
        near3 = bool(t['near']) and t['near'][0][0] <= 3
        inview = any(not e['queen'] for e in t['enemies'])
        dead = t['hit_after'] is not None
        den['turns'] += 1
        den['turns head in view'] += inview
        den['turns near3'] += near3
        den['near3 survived'] += near3 and not dead and t.get('end') is not None
        den['near3 hit'] += near3 and dead
        den['hit not near3'] += dead and not near3
        den['inview survived'] += inview and not dead and t.get('end') is not None
        if near3 and not dead and t.get('end') is not None:
            den['near3 survived, no clean tile'] += not t['open0']
            er = end_risk(t)
            den['near3 survived, ended on pay tile'] += er == 1
            den['near3 survived, ended on hit tile'] += er == 2
print(' ', dict(den))
gs = Counter()
for g, ts in turns.items():
    gs['games'] += 1
    gs['games with a survived near3 turn'] += any(t['near'] and t['near'][0][0] <= 3 and t['hit_after'] is None and t.get('end') is not None for t in ts)
print(' ', dict(gs))
print()
print('== rule A: look-ahead depth K (walk one tile a turn, stay out of the growing reach of the heads she sees) ==')
for K in (2, 3, 4, 5, 6):
    c = Counter()
    saved = []
    for g, ts in turns.items():
        for t in ts:
            fr = ahead_fire(t, K)
            if fr is None:
                continue
            dead = t['hit_after'] is not None
            near3 = bool(t['near']) and t['near'][0][0] <= 3
            c['fires'] += 1
            c['fires, survived turn'] += not dead
            c['fires, survived, near3'] += (not dead) and near3
            c['fires, took a pearl'] += bool(first_step(t).get('pearl'))
    for r in rows:
        hits = []
        for back, t in enumerate(reversed(r['ts'][-8:])):
            fr = ahead_fire(t, K)
            if fr is not None:
                hits.append((back, fr))
        r['fireA%d' % K] = hits
        if hits:
            saved.append(r['game'])
    print('  K=%d' % K, dict(c), '| deaths with a firing turn in the last 8:', len(saved), 'by class', dict(Counter(r['cls'] for r in rows if r['fireA%d' % K])))
print()
print('== rule B: wider pay ring (pearls on the way do not use up reach; a head cut by the view edge counts as 4 long) ==')
c = Counter()
for g, ts in turns.items():
    for t in ts:
        f = first_step(t)
        if f is None or not f.get('enterable'):
            continue
        U, o0, o1 = unpen(t, 'risk')
        Uw, w0, w1 = unpen(t, 'risk_w')
        dead = t['hit_after'] is not None
        near3 = bool(t['near']) and t['near'][0][0] <= 3
        c['moves'] += 1
        if o0 and not w0:
            c['clean tile lost (now boxed)'] += 1
            c['clean tile lost, survived'] += not dead
        if f in U and f not in Uw and Uw:
            c['diverted'] += 1
            c['diverted, survived'] += not dead
            c['diverted, survived, near3'] += (not dead) and near3
            c['diverted, hit followed'] += dead
print(' ', dict(c))
for r in rows:
    t = r['t']
    f = first_step(t)
    if f is None:
        continue
    Uw, w0, w1 = unpen(t, 'risk_w')
    print('  ', r['game'], r['cls'], '| took', DN[f['d']], 'risk', f.get('risk'), 'risk_w', f.get('risk_w'), '| wide: clean open', w0, 'pay open', w1,
          '| alternatives', [(DN[c['d']], c['risk_w'], 'closed' if c['closed'] else 'open', [tuple(x) for x in c['danger']]) for c in t['cands'] if c.get('enterable') and c is not f])
if 'runup' in sys.argv:
    print()
    print('== run-up: the last 8 turns of each death (d:risk/ahead/exits, * = taken, ! = rule A K=4 would move her) ==')
    for r in rows:
        print(r['game'], r['map'], r['cells'], 'r', r['round'], 'L', r['L'], r['cls'], r.get('boxkind', ''))
        for t in r['ts'][-8:]:
            f = first_step(t)
            a = t.get('action') or {}
            fr = ahead_fire(t, 4)
            heads = [(e['id'], e['L']) for e in t['enemies'] if not e['queen']]
            print('    r%d L%d near %s heads %s | %s | %s %s' % (
                t['round'], t['L'], t['near'][0][0] if t['near'] else None, heads,
                ' '.join('%s:%s' % (DN[c['d']], 'kelp' if c['kind'] == 'kelp' else c['occ'] if not c['enterable'] else '%d/%s/%d%s%s%s' % (c['risk'], c['ah'], c['exits'], 'c' if c['closed'] else '', 'p' if c['pearl'] else '', '*' if c is f else '')) for c in t['cands']),
                a.get('kind'), ('FIRE %s' % (fr,)) if fr else ''))
