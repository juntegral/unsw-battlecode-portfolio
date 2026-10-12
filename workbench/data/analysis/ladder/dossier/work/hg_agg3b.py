# Scratch (diag-hungry): loops and ties in the offline rebuild (hg_scan3 rows).
#   loop step  = the step taken lands on a tile the head stood on in its last 12 turns
#   tie        = two or more steps on offer within 1 point of the best rebuilt score (the bot adds 0 to 1 point of
#                id-and-round noise, main.cpp 5459, so such a turn is decided by that noise)
#   straight   = the step taken repeats the last turn's step
# Prints, by situation: share of loop steps, ties, straight steps; for loop steps what the step is aimed at and which
# term decides it; and what a bonus of H points on the straight-on step would change on the turns the rebuild explains.
# Usage: python3 data/analysis/ladder/dossier/work/hg_agg3b.py <arm|test>
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter, deque
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TERMS = ('territory', 'pearl target', 'soon', 'hot', 'unseen', 'far gain', 'look', 'mate head beside', 'spawn clear')


def tb(d):
    return max(0.0, 260.0 - 40.0 * d) if d >= 0 else 0.0


def total(v, drop=None):
    room, terr, dp, ds, dh, du, eat, adj, sc, cr, look, portal = v[:12]
    if drop == 'pearl target':
        dp = -1
    if drop == 'soon':
        ds = -1
    if drop == 'hot':
        dh = -1
    if drop == 'unseen':
        du = -1
    b = max(2.0 * tb(dp), 0.45 * tb(ds), 1.2 * tb(dh), 0.2 * tb(du))
    near = [x for x in (dp, ds, dh, du) if x >= 0]
    far = 2.0 * max(0, 80 - min(near)) if near else 0.0
    return (1.5 * room + (0.0 if drop == 'territory' else 1.5 * terr) - cr + b + (0.0 if drop == 'far gain' else far) + 300.0 * eat
            + (0.0 if drop == 'look' else look) - (0.0 if drop == 'mate head beside' else 450.0 * adj) - (0.0 if drop == 'spawn clear' else 300.0 * sc) - 150.0 * portal)


def aim(v):
    dp, ds, dh, du = v[2:6]
    b = [2.0 * tb(dp), 0.45 * tb(ds), 1.2 * tb(dh), 0.2 * tb(du)]
    far = ''
    if max(b) > 0:
        k = b.index(max(b))
    else:
        near = [x for x in (dp, ds, dh, du) if x >= 0]
        if not near:
            return 'nothing named'
        k = [dp, ds, dh, du].index(min(near))
        far = ', over 6 steps'
    if k == 0:
        return ('a pearl in view' if v[12] == 2 else 'a remembered pearl') + far
    if k == 1:
        return ('a remembered spawn tile with a pearl or one due' if v[13] >= 1 else 'a remembered spawn tile, stale') + far
    if k == 2:
        return 'a hot tile' + far
    return 'the nearest never-seen tile' + far


def pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '-'


def main():
    arm = sys.argv[1]
    names = [WORK + 'hg_scan3-test.jsonl'] if arm == 'test' else [WORK + 'hg_scan3-%s-%d.jsonl' % (arm, s) for s in range(4)]
    st = defaultdict(Counter)
    loop_aim = defaultdict(Counter)
    loop_dec = defaultdict(Counter)
    plain_dec = defaultdict(Counter)
    head_sim = defaultdict(Counter)
    for nm in names:
        hist = {}
        with open(nm) as f:
            for line in f:
                r = json.loads(line)
                if r.get('kind') == 'game':
                    hist = {}
                    continue
                key = r['i']
                h = hist.get(key)
                if h is None or r['idle'] < h['idle'] or r['r'] > h['r'] + 1:
                    h = dict(heads=deque(maxlen=12), face=-1, idle=r['idle'], r=r['r'])
                    hist[key] = h
                legal = [d for d in range(4) if r['dirs'][d] is not None]
                ch = [d for d in legal if r['path'] and r['dirs'][d][14] == r['path'][0]]
                view = 'pearl in view' if r['np'] > 0 else 'nothing in view'
                mates = 'no mate' if r['nm'] == 0 else '1-2 mates' if r['nm'] <= 2 else '3+ mates'
                keys = ((view, mates), (view, 'all'), ('all', 'all'))
                usable = bool(ch) and len(legal) >= 2 and r['box'] >= 7 and r['ne'] == 0
                if usable:
                    c = ch[0]
                    tot = {d: total(r['dirs'][d]) for d in legal}
                    top = max(tot.values())
                    ok = tot[c] >= top - 1.0
                    ties = sum(1 for d in legal if tot[d] >= top - 1.0)
                    loop = r['path'][0] in h['heads']
                    face = h['face']
                    for k in keys:
                        s = st[k]
                        s['n'] += 1
                        s['loop'] += loop
                        s['explained'] += ok
                        s['tie'] += ties >= 2
                        s['tie and explained'] += ties >= 2 and ok
                        s['within 6'] += sum(1 for d in legal if tot[d] >= top - 6.0) >= 2
                        if face >= 0:
                            s['face known'] += 1
                            s['straight'] += c == face
                            s['straight on offer'] += face in legal
                        if loop:
                            loop_aim[k][aim(r['dirs'][c])] += 1
                            loop_aim[k]['n'] += 1
                    if ok:
                        changed = [t for t in TERMS if total(r['dirs'][c], t) < max(total(r['dirs'][d], t) for d in legal) - 1.0]
                        for k in keys:
                            tgt = loop_dec[k] if loop else plain_dec[k]
                            tgt['n'] += 1
                            tgt['tie (noise decides)'] += ties >= 2
                            for t in changed:
                                tgt[t] += 1
                        if face >= 0 and face in legal:
                            for k in keys:
                                hs = head_sim[k]
                                hs['n'] += 1
                                hs['straight now'] += c == face
                                for H in (3, 6, 10, 20):
                                    t2 = dict(tot)
                                    t2[face] += H
                                    hs['straight with +%d' % H] += t2[face] >= max(t2.values()) - (1.0 if c == face else 0.0)
                                hs['loop now'] += loop
                                for H in (6, 10):
                                    t2 = dict(tot)
                                    t2[face] += H
                                    hs['loop step undone by +%d' % H] += loop and c != face and t2[face] >= max(t2.values())
                    h['face'] = c if len(r['path']) == 1 else -1
                else:
                    h['face'] = -1
                h['heads'].append(r['h'])
                h['idle'] = r['idle']
                h['r'] = r['r']
    print('== by situation: turns; loop steps; ties (2+ steps within 1 point of the best); 2+ steps within 6 points; straight steps')
    for k in sorted(st):
        s = st[k]
        print('  %-34s n %6d | loop %s | explained %s | tie %s | within 6 %s | straight %s (straight-on step on offer %s)' % (
            ' | '.join(k), s['n'], pct(s['loop'], s['n']), pct(s['explained'], s['n']), pct(s['tie'], s['n']), pct(s['within 6'], s['n']),
            pct(s['straight'], s['face known']), pct(s['straight on offer'], s['face known'])))
    print('\n== loop steps: what the step is aimed at')
    for k in sorted(loop_aim):
        c = loop_aim[k]
        print('  [%s] n %d: %s' % (' | '.join(k), c['n'], '; '.join('%s %s' % (a, pct(v, c['n'])) for a, v in c.most_common() if a != 'n')))
    print('\n== the step changes when the term is removed: loop steps | other steps (turns the rebuild explains)')
    for k in sorted(loop_dec):
        a, b = loop_dec[k], plain_dec[k]
        print('  [%s] loop n %d, other n %d' % (' | '.join(k), a['n'], b['n']))
        print('      ' + ', '.join('%s %s | %s' % (t, pct(a[t], a['n']), pct(b[t], b['n'])) for t in ('tie (noise decides)',) + TERMS))
    print('\n== a bonus of H points on the straight-on step (first order: this turn only; turns the rebuild explains, straight-on step on offer)')
    for k in sorted(head_sim):
        hs = head_sim[k]
        print('  [%s] n %d: straight now %s; with +3 %s, +6 %s, +10 %s, +20 %s | loop steps now %s, undone by +6 %s, by +10 %s' % (
            ' | '.join(k), hs['n'], pct(hs['straight now'], hs['n']), pct(hs['straight with +3'], hs['n']), pct(hs['straight with +6'], hs['n']),
            pct(hs['straight with +10'], hs['n']), pct(hs['straight with +20'], hs['n']), pct(hs['loop now'], hs['n']),
            pct(hs['loop step undone by +6'], hs['loop now']), pct(hs['loop step undone by +10'], hs['loop now'])))


main()
