"""qexit-opus: class table of our queen's deaths from qdeath-*.jsonl. Usage: classify.py <jsonl> [rows]"""
import sys, json
from collections import Counter, defaultdict


def cls(d):
    """(class, detail)"""
    if not d['own_turn']:
        a = d['att']
        if a[0] == 'mate':
            return 'M mate head rams her', ''
        f = d.get('f1a')
        seen = d.get('seen_q', -1)
        sm = d.get('seen_mate', 0)
        view = 'seenQ' if seen == 1 else 'seenMate' if sm == 1 else 'unseen'
        pay = 'paid' if d['att_paid'] else 'free'
        mates = [m for m in d.get('mate_sides', []) if m[0] == 'mate']
        if f is None:
            return 'R rammed (no after state)', view
        if f == 0:
            who = 'mate' if mates else 'self/wall'
            return 'R0 rammed with 0 free cells after her move', '%s %s %s' % (view, pay, who)
        if f == 1:
            return 'R1 rammed with 1 free cell after her move', '%s %s %s' % (view, pay, 'mate-side' if mates else 'self/wall')
        return 'R2 rammed with 2+ free cells', '%s %s' % (view, pay)
    r = d['reason']
    if r == 3:
        s1 = d.get('start1') or []
        dr = d.get('dirs') or []
        u = d.get('used', 0)
        tgt = s1[dr[u]] if u < len(dr) and s1 and u == 0 else ['?']
        f1 = d.get('f1')
        return 'H she rams a %s head on her own move' % tgt[0], 'free cells at turn start: %s' % ('0' if f1 == 0 else '1+')
    if r == 4:
        return 'S stop/timeout', ''
    f1 = d.get('f1')
    if f1 is None:
        return 'X no history', ''
    if f1 > 0:
        return 'U own move into wall/body with a free cell', 'reason%d f1=%d used=%s dirs=%s split=%s' % (r, f1, d.get('used'), len(d.get('dirs', [])), d.get('split1'))
    # boxed at her last turn start
    f0a = d.get('f0a')
    cl = d.get('closers') or []
    if f0a is None:
        return 'B? boxed, no previous turn', ''
    if f0a == 0:
        how = 'split' if d.get('split0') else 'move'
        return 'BQ boxed: her own %s left 0 free cells' % how, 'f0=%s' % d.get('f0')
    mates = [c for c in cl if c[0] == 'mate']
    foes = [c for c in cl if c[0] == 'foe']
    if mates and not foes:
        mx = max(c[2] for c in mates)
        return 'BM boxed: a mate took her last free cell', 'L%s %s f0a=%d' % ('2-3' if mx <= 3 else '4+', '/'.join(c[3] for c in mates), f0a)
    if foes and not mates:
        return 'BF boxed: a foe took her last free cell', 'f0a=%d' % f0a
    if foes and mates:
        return 'BX boxed: mate and foe', 'f0a=%d' % f0a
    return 'BO boxed: own body/other', 'f0a=%d closers=%s' % (f0a, cl)


def main():
    allr, seen = [], set()
    for f in sys.argv[1].split(','):
        for l in open(f):
            try:
                d = json.loads(l)
            except Exception:
                continue
            k = ('g', d['game']) if 'game' in d else (d['gid'], d['r'])
            if k not in seen:
                seen.add(k)
                allr.append(d)
    rows = [d for d in allr if 'game' not in d]
    gm = [d for d in allr if 'game' in d]
    print('games', len(gm), 'queen alive at end', sum(d['qalive'] for d in gm), dict(Counter(d['ver'] for d in gm)))
    c = Counter()
    det = defaultdict(Counter)
    by = defaultdict(Counter)
    for d in rows:
        k, x = cls(d)
        d['cls'] = k
        d['det'] = x
        c[k] += 1
        det[k][x] += 1
        by[k][d['ver']] += 1
    print('queen deaths', len(rows))
    for k, n in c.most_common():
        print('%3d  %s   %s' % (n, k, dict(by[k])))
        for x, m in det[k].most_common(8):
            print('        %3d  %s' % (m, x))
    Ls = Counter(min(d['L'], 6) for d in rows)
    print('length at death (6 = 6+):', dict(sorted(Ls.items())))
    print('round <100: %d, 100-199: %d, 200+: %d' % (sum(d['r'] < 100 for d in rows), sum(100 <= d['r'] < 200 for d in rows), sum(d['r'] >= 200 for d in rows)))
    print('after their queen was dead: %d' % sum(d.get('their_q_dead') is not None for d in rows))
    if len(sys.argv) > 2:
        for d in sorted(rows, key=lambda d: (d['cls'], d['ver'], d['gid'])):
            print(d['cls'][:3], d['ver'], d['src'], d['gid'], 'r%d' % d['r'], 'L%d' % d['L'], d['det'], 'att=%s' % d.get('att'), 'hit=%s' % d.get('hit'),
                  'f0=%s f0a=%s f1=%s f1a=%s' % (d.get('f0'), d.get('f0a'), d.get('f1'), d.get('f1a')), 'gap=%s/%s' % (d.get('gap_at_start'), d.get('gap_after')), 'tqd=%s' % d.get('their_q_dead'))


main()
