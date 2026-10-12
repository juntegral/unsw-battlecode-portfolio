"""watch17-opus report from cache.json. Usage (from ROOT): python3 -B data/codex/astra/watch17-opus/rep.py"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path('data/codex/astra/watch17-opus')
C = json.loads((HERE / 'cache.json').read_text())
G = [g for g in C.values() if g.get('ver')]
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}


def how(g):
    qa = 'q %d' % g['qfin'] if g['qfin'] else 'q dead'
    qb = 'q %d' % g['eqfin'] if g['eqfin'] else 'q dead'
    if g['alive'][0] == 0 or g['alive'][1] == 0:
        w = 'wipe(%d:%d dragons)' % tuple(g['alive'])
    elif g['qfin'] != g['eqfin']:
        w = 'queen length'
    elif g['longest'][0] != g['longest'][1]:
        w = 'longest %d:%d' % tuple(g['longest'])
    else:
        w = 'total %d:%d' % tuple(g['tot'])
    return '%s vs %s, %s, end r%d reason %d' % (qa, qb, w, g['last'], g['end_reason'])


def line(g):
    res = 'WIN ' if g['win'] else 'LOSS' if g['win'] is False else 'DRAW'
    qd = ('queen died r%d at len %d (%s)' % (g['qdead'][0], g['qdead'][1], RS.get(g['qdead'][2], g['qdead'][2]))) if g['qdead'] else 'queen alive len %d' % g['qfin']
    big = [s for s in g['qsplits'] if s['before'] >= 10]
    sp = 'splits from 10+: ' + (', '.join('r%d %d>%d (foe at %d)' % (s['r'], s['before'], s['after'], s['nd']) for s in big) if big else 'none')
    shed9 = [s for s in g['qsplits'] if s['before'] <= 9 and s['after'] == 2 and s['before'] >= 4]
    odd = []
    a = g['acts'][0]
    if a.get('timeout'):
        odd.append('TIMEOUTS %d' % a['timeout'])
    if a.get('none'):
        odd.append('no-action %d' % a['none'])
    if g['deaths'][0].get('4'):
        odd.append('reason-4 deaths %d' % g['deaths'][0]['4'])
    if g['still'][0][0] >= 6:
        odd.append('dragon %d still %d rounds to r%d' % (g['still'][0][1], g['still'][0][0], g['still'][0][2]))
    for c in g['collapse']:
        if c[1]:
            odd.append('COLLAPSE r%d from %d dragons' % (c[0], c[2]))
    if g.get('serverLog'):
        odd.append('serverLog present')
    return '%s %-7s %-15s %-17s %s | %s | %s | %s; sheds to 2 from <=9: %d | odd: %s' % (
        g['id'], g['set'][-7:], (g['map'] or '')[:15], (g['opp'] or '')[:17], res, how(g), qd, sp, len(shed9), '; '.join(odd) or 'none')


out = []
for ver in ('one17', 'one18', 'one19', 'one20', 'one21'):
    gs = sorted((g for g in G if g['ver'] == ver), key=lambda g: g['id'])
    out.append('## %s games: %d (wins %d)' % (ver, len(gs), sum(1 for g in gs if g['win'])))
    for g in gs:
        out.append(line(g))

out.append('')
out.append('## health baselines per version/set (our side)')
out.append('set                n  win  qdead  timeouts  no-act  r4deaths  still>=6  collapse  splits10+  shed2from10+  shed2from<=9  medLast')
by = defaultdict(list)
for g in G:
    by[(g['ver'], g['set'])].append(g)
for key in sorted(by):
    gs = by[key]
    lasts = sorted(g['last'] for g in gs)
    out.append('%-8s %-9s %3d %4d %6d %9d %7d %9d %9d %9d %10d %13d %13d %8d' % (
        key[0], key[1], len(gs), sum(1 for g in gs if g['win']), sum(1 for g in gs if g['qdead']),
        sum(g['acts'][0].get('timeout', 0) for g in gs), sum(g['acts'][0].get('none', 0) for g in gs),
        sum(g['deaths'][0].get('4', 0) for g in gs), sum(1 for g in gs if g['still'][0][0] >= 6),
        sum(1 for g in gs for c in g['collapse'] if c[1]),
        sum(1 for g in gs for s in g['qsplits'] if s['before'] >= 10),
        sum(1 for g in gs for s in g['qsplits'] if s['before'] >= 10 and s['after'] == 2),
        sum(1 for g in gs for s in g['qsplits'] if 4 <= s['before'] <= 9 and s['after'] == 2), lasts[len(lasts) // 2]))

out.append('')
out.append('## mechanism: round starts with our queen >= 10 and an enemy head within 3 (torus manhattan)')
out.append('ver     games  turns  episodes | action: stay  move1  move2+  split(to2)  | dead<=3r  dead<=5r  dead<=20r | per episode: q dead within 3r of any turn')
for ver in ('one15', 'one16', 'one17', 'one18', 'one19', 'one20', 'one21'):
    gs = [g for g in G if g['ver'] == ver]
    T = [(g, t) for g in gs for t in g['mech']]
    n = len(T)
    if not n:
        out.append('%-7s %5d  no such turns' % (ver, len(gs)))
        continue
    stay = sum(1 for g, t in T if t['mv'] == 0 and not t['split'])
    m1 = sum(1 for g, t in T if t['mv'] == 1 and not t['split'])
    m2 = sum(1 for g, t in T if t['mv'] >= 2 and not t['split'])
    sp = sum(1 for g, t in T if t['split'])
    sp2 = sum(1 for g, t in T if t['split'] and t['after'] == 2)
    d3 = sum(1 for g, t in T if t['a3'] == 'dead')
    d5 = sum(1 for g, t in T if t['a5'] == 'dead')
    d20 = sum(1 for g, t in T if t['a20'] == 'dead')
    eps = 0
    epd = 0
    for g in gs:
        rs = sorted(t['r'] for t in g['mech'])
        dead3 = {t['r'] for t in g['mech'] if t['a3'] == 'dead'}
        prev = None
        cur = []
        groups = []
        for r in rs:
            if prev is not None and r - prev > 3:
                groups.append(cur)
                cur = []
            cur.append(r)
            prev = r
        if cur:
            groups.append(cur)
        eps += len(groups)
        epd += sum(1 for gr in groups if any(r in dead3 for r in gr))
    out.append('%-7s %5d %6d %9d | %5d(%2d%%) %5d(%2d%%) %5d(%2d%%) %4d(%d) | %4d(%4.1f%%) %4d(%4.1f%%) %4d(%4.1f%%) | %d of %d (%4.1f%%)' % (
        ver, len(gs), n, eps, stay, 100 * stay // n, m1, 100 * m1 // n, m2, 100 * m2 // n, sp, sp2,
        d3, 100 * d3 / n, d5, 100 * d5 / n, d20, 100 * d20 / n, epd, eps, 100 * epd / max(eps, 1)))

out.append('')
out.append('## the same, enemy head within 1 or 2 only (closest spots)')
for ver in ('one15', 'one16', 'one17', 'one18', 'one19', 'one20', 'one21'):
    T = [(g, t) for g in G if g['ver'] == ver for t in g['mech'] if t['nd'] <= 2]
    n = len(T)
    if n:
        d3 = sum(1 for g, t in T if t['a3'] == 'dead')
        sp2 = sum(1 for g, t in T if t['split'] and t['after'] == 2)
        out.append('%-7s turns %4d  shed-to-2 %3d  dead<=3r %3d (%4.1f%%)' % (ver, n, sp2, d3, 100 * d3 / n))

out.append('')
out.append('## one17 mechanism turns, listed (game round qlen foe-dist foe-len n3 -> moved split after | +3 +5 +20)')
for g in sorted((g for g in G if g['ver'] in ('one17', 'one18', 'one19', 'one20', 'one21')), key=lambda g: g['id']):
    for t in g['mech']:
        out.append('%s %-12s r%-4d q%-3d d%d L%-3d n%d -> mv%d %s after %-3d | %s %s %s' % (
            g['id'], (g['map'] or '')[:12], t['r'], t['ql'], t['nd'], t['nl'], t['n3'], t['mv'], 'SPLIT' if t['split'] else '-', t['after'], t['a3'], t['a5'], t['a20']))

out.append('')
out.append('## sheds from 10+ to 2 in one15/one16 (what one17 removes)')
for g in sorted((g for g in G if g['ver'] in ('one15', 'one16')), key=lambda g: g['id']):
    for s in g['qsplits']:
        if s['before'] >= 10 and s['after'] == 2:
            out.append('%s %s %-12s r%d %d>2 foe at %d; queen %s; %s' % (g['id'], g['ver'], (g['map'] or '')[:12], s['r'], s['before'], s['nd'],
                       'died r%d' % g['qdead'][0] if g['qdead'] else 'alive %d' % g['qfin'], 'WIN' if g['win'] else 'LOSS'))
txt = '\n'.join(out)
(HERE / 'rep.txt').write_text(txt + '\n')
print(txt)
