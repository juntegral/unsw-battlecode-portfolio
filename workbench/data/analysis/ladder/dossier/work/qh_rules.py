"""Scratch (diag-queenhit): candidate rules replayed on every queen turn of qh_turns.jsonl (paper replay: the rule
fires when it would rank another unpenalised tile above the one she took). F(S) = keep off tiles a seen head can
reach within S more turns; A(K) = look-ahead depth; kelp = stand on tiles with fewer kelp sides."""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
DN = 'NESW'
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


def unpen(t, key='risk'):
    sc = [c for c in t['cands'] if c.get('enterable') and c['kind'] == 'open']
    o0 = any(c[key] == 0 and not c['closed'] for c in sc)
    o1 = any(c[key] == 1 and not c['closed'] for c in sc)
    if o0:
        return [c for c in sc if c[key] == 0]
    if o1:
        return [c for c in sc if c[key] <= 1]
    return sc


def value(c, rule):
    kind, n = rule
    if kind == 'F':
        return min(c['arr'], n + 1)
    if kind == 'A':
        return min(c['ah'], n)
    if kind == 'FA':
        return (min(c['arr'], n[0] + 1), min(c['ah'], n[1]))
    if kind == 'AF':
        return (min(c['ah'], n[1]), min(c['arr'], n[0] + 1))
    if kind == 'kelp':
        return -min(c['kelp'], n)
    if kind == 'exits':
        return min(c['exits'], n)
    return 0


def fire(t, rule):
    f = first_step(t)
    if f is None or not f.get('enterable') or f['kind'] != 'open':
        return None
    U = unpen(t)
    if f not in U:
        return None
    best = max(value(c, rule) for c in U)
    mine = value(f, rule)
    if mine >= best:
        return None
    alts = [c for c in U if value(c, rule) == best]
    return mine, best, alts


def report(rule, name, need_head=False, verbose=False):
    c = Counter()
    per = {}
    for g, ts in turns.items():
        for k, t in enumerate(ts):
            if need_head and not any(not e['queen'] for e in t['enemies']):
                continue
            fr = fire(t, rule)
            if fr is None:
                continue
            dead = t['hit_after'] is not None
            near3 = bool(t['near']) and t['near'][0][0] <= 3
            back = len(ts) - 1 - k
            c['fires'] += 1
            if g in hits and back <= 7:
                per.setdefault(g, []).append((back, fr[0], fr[1], ''.join(DN[a['d']] for a in fr[2])))
            else:
                c['fires elsewhere'] += 1
                c['fires elsewhere, near3'] += near3
                c['fires elsewhere, she took a pearl'] += bool(first_step(t).get('pearl'))
                c['fires elsewhere, an alternative has a pearl'] += any(a.get('pearl') for a in fr[2])
    last3 = [g for g, v in per.items() if any(x[0] <= 2 for x in v)]
    print('%-22s fires %4d | deaths with a changed move in the last 8 turns: %2d, in the last 3: %2d | fires on other turns %4d (near3 %d, pearl step given up %d)' % (
        name, c['fires'], len(per), len(last3), c['fires elsewhere'], c['fires elsewhere, near3'], c['fires elsewhere, she took a pearl']))
    if verbose:
        for g in hits:
            if g in per:
                print('     ', g, fates[g]['map'], 'r', fates[g]['fate']['round'], [(x[0], x[1], x[2], x[3]) for x in per[g]])
    return per


print('turns', sum(len(v) for v in turns.values()), 'head-on-hit deaths', len(hits))
print('== fires = turns the rule would move her to another tile; (turns back, her value, best value, better tiles) ==')
for S in (1, 2, 3):
    report(('F', S), 'F(S=%d)' % S, verbose=S == 2)
for K in (2, 3, 4, 6):
    report(('A', K), 'A(K=%d)' % K, verbose=K == 4)
report(('FA', (1, 4)), 'F1 then A4', verbose=True)
report(('FA', (2, 4)), 'F2 then A4', verbose=True)
report(('AF', (2, 4)), 'A4 then F2', verbose=True)
report(('kelp', 2), 'fewer kelp sides (all)')
report(('kelp', 2), 'fewer kelp, head seen', need_head=True, verbose=True)
report(('exits', 2), 'more exits (all)')
report(('exits', 2), 'more exits, head seen', need_head=True)
print()
print('== kelp sides of the tile she stands on ==')
k = defaultdict(Counter)
for g, ts in turns.items():
    for t in ts:
        near3 = bool(t['near']) and t['near'][0][0] <= 3
        b = min(t['head_kelp'], 2)
        k[b]['turns'] += 1
        k[b]['near3'] += near3
        k[b]['hit'] += t['hit_after'] is not None
        k[b]['near3 hit'] += near3 and t['hit_after'] is not None
for b in sorted(k):
    print('  kelp sides', b, dict(k[b]))
