"""Scratch (diag-queenhit2): every queen death in one arm, rebuilt from q2_scan-<label>.jsonl: her length and how
she came to it, the last turn (rings, clean step, paid escape, what closed the box, own heads near), the turns before.
Usage: python3 .../q2_deaths.py new|main [detail] [game]"""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(new=('agg8-q1', 'agg8-q2'), main=('agg7-m1', 'agg7-m2', 'agg7-m3'))
DN = 'NESW'


def load(arm):
    fates, turns = [], defaultdict(list)
    for label in ARMS[arm]:
        p = WORK / ('q2_scan-%s.jsonl' % label)
        if not p.exists():
            continue
        with p.open() as fh:
            for line in fh:
                r = json.loads(line)
                if r['k'] == 'f':
                    fates.append(r)
                else:
                    turns[r['game']].append(r)
    return fates, turns


def true_reach(n):
    return (n + 3) // 4 + n - 2


def free_of(n):
    return (n + 3) // 4


def end_risk(t):
    e = t.get('end')
    return None if e is None else 2 if e in t['hit'] else 1 if e in t['pay'] else 0


def paid(t):
    a = t.get('action') or {}
    return a.get('kind') == 'move' and len(t.get('path', [])) > free_of(t['L'])


def came_to(ts, k):
    """How she came to the length she has at turn k: the last turn on which her length fell to it or below."""
    L = ts[k]['L']
    for j in range(k - 1, -1, -1):
        t = ts[j]
        if t['L'] > L and t['L_after'] <= L:
            a = t.get('action') or {}
            exposed = t['hit_head'] or t['pay_head']
            can_pay = t['L'] >= 3 and t['esc_open'] <= true_reach(t['L'])
            if a.get('kind') == 'split':
                child = t.get('split_child', 0)
                if t['hit_blocked'] and not exposed:
                    how = 'split with no clean tile, own tile not in reach (line 638)'
                elif exposed:
                    how = 'forced split, own tile in reach (649/685)'
                elif not t['any_enterable']:
                    how = 'split with no tile to enter (695/729)'
                else:
                    how = 'split while waiting or routine (695/768)'
                return dict(how=how, kind='split', turn=j, back=k - j, L=t['L'], child=child, round=t['round'], can_pay=can_pay, open0=t['open0'])
            how = 'paid sprint, no clean step (642/659)' if t['hit_blocked'] else 'paid sprint with a clean step open (743/779)' if t['open0'] else 'paid sprint, other'
            return dict(how=how, kind='sprint', turn=j, back=k - j, L=t['L'], steps=len(t.get('path', [])), round=t['round'], can_pay=can_pay, open0=t['open0'],
                        near=t['near'][0][0] if t['near'] else None)
    return dict(how='never longer since the start', kind='start', turn=0, back=k, L=ts[0]['L'], round=0)


def sides(t):
    s = Counter()
    for c in t['cands']:
        if c['kind'] == 'kelp':
            s['kelp'] += 1
        elif not c['enterable']:
            s[c['occ']] += 1
        else:
            s['ring%d%s' % (c['risk'], 'closed' if c['closed'] else '')] += 1
    return s


def cand_str(t):
    a = t.get('action') or {}
    first = a['dirs'][0] if a.get('kind') == 'move' and a.get('dirs') else None
    out = []
    for c in t['cands']:
        if c['kind'] == 'kelp':
            out.append(DN[c['d']] + ':kelp')
        elif not c['enterable']:
            out.append(DN[c['d']] + ':' + c['occ'])
        else:
            out.append('%s:r%d/o%d/x%d%s%s%s%s' % (DN[c['d']], c['risk'], 4 - c['kelp'], c['exits'], 'c' if c['closed'] else '', 'p' if c['pearl'] else '',
                                                 's' if c['shield'] else '', '*' if c['d'] == first else ''))
    return ' '.join(out)


def classify(f, ts):
    d = f['fate']
    t = ts[-1]
    a = t.get('action') or {}
    L = t['L']
    reach = true_reach(L)
    can_pay = L >= 3 and t['esc_open'] <= reach
    if d['mover']:
        fatal = d.get('fatal') or {}
        if d['cause'] == 'head-on':
            return 'mover: ran into a head'
        box = 'no clean step' if not t['open0'] else 'clean step open'
        return 'mover: %s, %s' % (d['cause'], box)
    if d['cause'] != 'head-on':
        return 'other: ' + d['cause']
    r = d['rammer']
    seen = [e for e in t['enemies'] if e['id'] == r['id']]
    er = end_risk(t)
    if not r['enemy']:
        return 'own team'
    if not r['existed']:
        return 'unseen: split child'
    if r['is_enemy_queen']:
        return 'enemy queen (no ring)'
    if not seen:
        return 'unseen: outside view'
    if a.get('kind') != 'move' or not a.get('dirs'):
        return 'split or no move on the last turn'
    if er == 0:
        return 'ring small: pearls' if r['steps'] > true_reach(r['L']) else 'ring small: length cut' if seen[0]['reach'] < true_reach(r['L']) else 'ring small: other'
    if t['open0']:
        return 'ringed tile taken with a clean one open'
    return 'boxed: took pay tile' if er == 1 else 'boxed: only hit tiles'


def main():
    arm = sys.argv[1]
    detail = 'detail' in sys.argv
    only = [int(x) for x in sys.argv[2:] if x.isdigit()]
    fates, turns = load(arm)
    print('arm', arm, 'games', len(fates), 'queen turns', sum(len(v) for v in turns.values()),
          'alive at end', sum(f['fate'] is None for f in fates), 'wins', sum(f['result'] == 'win' for f in fates))
    print('deaths', Counter((f['fate']['cause'], 'mover' if f['fate']['mover'] else 'hit') for f in fates if f['fate']))
    cls = Counter()
    rows = []
    for f in fates:
        d = f['fate']
        if d is None:
            continue
        ts = turns[f['game']]
        t = ts[-1]
        c = classify(f, ts)
        ct = came_to(ts, len(ts) - 1)
        s = sides(t)
        L = t['L']
        can_pay = L >= 3 and t['esc_open'] <= true_reach(L)
        heads = [e for e in t['enemies'] if not e['queen']]
        a3 = sum(1 for x in t['allies'] if x[0] <= 3)
        a5 = sum(1 for x in t['allies'] if x[0] <= 5)
        row = dict(f=f, t=t, ts=ts, cls=c, came=ct, sides=s, can_pay=can_pay, a3=a3, a5=a5, heads=len(heads))
        rows.append(row)
        cls[c] += 1
    print()
    print('== classes ==')
    for c, n in cls.most_common():
        rs = [r for r in rows if r['cls'] == c]
        print('%-44s %2d | L2 %2d L3 %2d L4+ %2d | %s' % (c, n, sum(r['t']['L'] == 2 for r in rs), sum(r['t']['L'] == 3 for r in rs), sum(r['t']['L'] >= 4 for r in rs),
                                                  ' '.join(str(r['f']['game']) for r in rs)))
    hits = [r for r in rows if not r['f']['fate']['mover'] and r['f']['fate']['cause'] == 'head-on']
    print()
    print('== head-on hits', len(hits), '==')
    print('queen length', sorted(Counter(r['t']['L'] for r in hits).items()), '| rammer length', sorted(Counter(r['f']['fate']['rammer']['L'] for r in hits).items()),
          '| rammer steps', sorted(Counter(r['f']['fate']['rammer']['steps'] for r in hits).items()))
    print('how she came to her length (all deaths):')
    for key, n in Counter((min(r['t']['L'], 4), r['came']['how']) for r in rows).most_common():
        print('   L%s%s  %-58s %d' % (key[0], '+' if key[0] == 4 else ' ', key[1], n))
    print('how she came to her length (head-on hits):')
    for key, n in Counter((min(r['t']['L'], 4), r['came']['how']) for r in hits).most_common():
        print('   L%s%s  %-58s %d' % (key[0], '+' if key[0] == 4 else ' ', key[1], n))
    print('turns between coming to that length and the death, L2 hits:', sorted(r['came']['back'] for r in hits if r['t']['L'] == 2))
    box = [r for r in hits if r['cls'].startswith('boxed') or r['cls'].startswith('split')]
    bk = Counter()
    for r in box:
        s = r['sides']
        ally = s.get('allyB', 0) + s.get('allyH', 0)
        kind = 'kelp on 2+ sides' if s.get('kelp', 0) >= 2 else 'ally body/head on a side' if ally else '2+ enemy heads, 0-1 kelp' if r['heads'] >= 2 else 'one enemy, 0-1 kelp'
        r['boxkind'] = kind
        bk[kind] += 1
    print('what closed the box (boxed + split deaths, %d):' % len(box), dict(bk))
    print('clean single step open on the last turn:', sum(r['t']['open0'] for r in hits), '| paid escape open (L3+, clean seen tile within her paid reach):',
          sum(r['can_pay'] for r in hits), '| clean tile 2 steps off but she is 2 long:', sum(r['t']['L'] == 2 and r['t']['esc_open'] <= 2 for r in hits),
          '| clean tile within 3 steps, any length:', sum(r['t']['esc_open'] <= 3 for r in hits))
    print('own heads within 3 tiles at the last turn (hits):', sorted(Counter(min(r['a3'], 2) for r in hits).items()), 'within 5:', sorted(Counter(min(r['a5'], 2) for r in hits).items()))
    print()
    print('== every death ==')
    for r in rows:
        f, t, ts, d = r['f'], r['t'], r['ts'], r['f']['fate']
        if only and f['game'] not in only:
            continue
        ct = r['came']
        W = f['W']
        print('%d %s %dx%d vs %s %s | r%d %s %s L%d | %s' % (f['game'], f['map'], f['W'], f['H'], f['opponent'][:8], f['result'], d['round'], d['cause'], 'mover' if d['mover'] else 'hit', d['L'], r['cls']))
        print('    came to L%d: %s at r%d (L%d, %d turns before)%s' % (t['L'], ct['how'], ct['round'], ct['L'], ct['back'],
              '' if ct['kind'] == 'start' else ' paid escape open then: %s, clean step open then: %s' % (ct.get('can_pay'), ct.get('open0'))))
        if d['mover']:
            fa = d.get('fatal') or {}
            print('    own move: dirs %s died on step %d, edge kind %s known %s, target occupied at turn start %s, now %s, in view %s' % (
                ''.join(DN[x] for x in d['dirs']), d['used'] + 1, fa.get('edge'), fa.get('known'), fa.get('occ_start'), fa.get('occ_now'), fa.get('in_view')))
        else:
            rm = d['rammer']
            print('    rammer #%d L%d steps %d existed %s seen %s | from %s' % (rm['id'], rm['L'], rm['steps'], rm['existed'], any(e['id'] == rm['id'] for e in t['enemies']),
                  ((rm['start'] % W - t['head'] % W), (rm['start'] // W - t['head'] // W))))
        print('    last turn: heads in view %d nearest %s | open0 %s open1 %s boxed %s exposed %s | clean tile depth any %d open %d, can pay %s | sides %s | own heads <=3: %d <=5: %d %s' % (
            r['heads'], t['near'][0][:3] if t['near'] else None, t['open0'], t['open1'], t['hit_blocked'], t['hit_head'] or t['pay_head'], t['esc_any'], t['esc_open'], r['can_pay'],
            dict(r['sides']), r['a3'], r['a5'], t['allies'][:3]))
        if detail or only:
            for tt in ts[-6:]:
                a = tt.get('action') or {}
                print('      r%d L%d>%s near %s heads %s kelp %d | %s | %s%s %s esc %d/%d allies %s' % (
                    tt['round'], tt['L'], tt.get('L_after'), tt['near'][0][0] if tt['near'] else None, [(e['id'], e['L']) for e in tt['enemies'] if not e['queen']], tt['head_kelp'],
                    cand_str(tt), a.get('kind'), '' if a.get('kind') != 'move' else ':' + ''.join(DN[x] for x in a['dirs']), 'BOXED' if tt['hit_blocked'] else '',
                    tt['esc_any'], tt['esc_open'], [x[0] for x in tt['allies'][:3]]))


main()
