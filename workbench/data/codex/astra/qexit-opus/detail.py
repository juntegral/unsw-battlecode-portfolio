import sys, json
from collections import Counter
rows = [json.loads(l) for f in sys.argv[1].split(',') for l in open(f)]
rows = [d for d in rows if 'game' not in d]
_s = set()
rows = [d for d in rows if (d['gid'], d['r']) not in _s and not _s.add((d['gid'], d['r']))]


def sd(s):
    return ' '.join((x[0] if x[0] in ('free', 'wall') else '%s%d%s' % (x[0], x[2], x[3][0])) for x in s)


c = Counter()
c2 = Counter()
c3 = Counter()
c4 = Counter()
for d in rows:
    if d['own_turn']:
        if d.get('f1') == 0:
            s = d['start1']
            kinds = sorted(set((x[0] if x[0] in ('wall', 'own') else x[0] + ('H' if x[3] == 'head' else 'B') + ('L4+' if x[0] == 'mate' and x[2] > 3 else '')) for x in s))
            c['boxed at last turn start: ' + '+'.join(kinds)] += 1
            if len(sys.argv) > 2:
                print(d['ver'], d['gid'], 'r%d' % d['r'], 'L%d' % d['L'], 'reason', d['reason'], sd(s), 'f0=%s f0a=%s split0=%s L0=%s f00=%s f00a=%s' % (d.get('f0'), d.get('f0a'), d.get('split0'), d.get('L0'), d.get('f00'), d.get('f00a')), 'closers', d.get('closers'))
    else:
        a = d['att']
        if a[0] != 'foe':
            continue
        L = d.get('attL_at_start', a[2])
        reach_free = -(-L // 4)
        g1 = d.get('gap_at_start')
        g2 = d.get('gap_after')
        key = 'seen' if d.get('seen_q') == 1 else 'unseen'
        f = d.get('f1a')
        c2[(key, 'f1a=%s' % (f if f is None or f < 2 else '2+'), 'attL=%s' % (L if L < 5 else '5+'), 'steps=%d' % a[3], 'gap_after=%s' % g2)] += 1
        c3[(key, 'queenL=%s' % (d['L'] if d['L'] < 5 else '5+'), 'split_last_turn=%s' % d.get('split1'), 'gap %s' % ('closer' if g2 is not None and g1 is not None and g2 < g1 else 'same' if g2 == g1 else 'farther'), 'in_free_reach_after=%s' % (g2 is not None and g2 <= reach_free))] += 1
        c4[(key, 'gap_start=%s' % g1, 'gap_after=%s' % g2, 'steps=%d' % a[3], 'paid=%d' % d['att_paid'])] += 1
        if len(sys.argv) > 2 and key == 'seen':
            print(d['ver'], d['gid'], 'r%d' % d['r'], 'L%d' % d['L'], 'att', a, 'gap %s->%s' % (g1, g2), 'f1=%s f1a=%s split=%s dirs=%s tqd=%s' % (d.get('f1'), f, d.get('split1'), d.get('dirs'), d.get('their_q_dead')))
for k, n in c.most_common():
    print(n, k)
print()
for k, n in sorted(c3.items(), key=lambda x: -x[1])[:30]:
    print(n, *k)
print()
for k, n in sorted(c4.items(), key=lambda x: -x[1])[:40]:
    print(n, *k)
