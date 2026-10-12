"""Scratch (diag-topqueen): how the close episodes around a queen end, and what becomes of the pursuing heads. Reads tq2_chase-*.jsonl.
Episode = consecutive turns of hers that start with a non-queen enemy head within 3 steps. Pursuers = every such head in the episode.
Usage: python3 tq2_chasetab.py [list <arm>]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
FILES = ['top3-0', 'top3-1', 't91-0', 't91-1', 't264-0', 't264-1', 't306-0', 't306-1', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2']
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    if src == 'top1':
        return 'o%d' % t if t in NAMED else 'oopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    if lab in ('L1', 'L2'):
        return 'v%d' % t
    return 'x' + lab


def pct(a, b):
    return '%.0f' % (100.0 * a / b) if b else '-'


def main():
    C = defaultdict(Counter)
    listing = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == 'list' else None
    for tag in FILES:
        p = W / ('tq2_def-%s.jsonl' % tag)
        if not p.exists():
            p = W / ('tq2_chase-%s.jsonl' % tag)
        if not p.exists():
            continue
        with open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                g = json.loads(line)
                dby = defaultdict(list)
                for d in g['deaths']:
                    dby[d[1]].append(d)
                for s in (0, 1):
                    a = arm_of(g, s)
                    c = C[a]
                    c['games'] += 1
                    c['turns'] += g['turns'][s]
                    c['mate_rams_near'] += g['near'][s][0]
                    c['enemy_rams_mate_near'] += g['near'][s][1]
                    f = g['fate'][s]
                    q = g['queen'][s]
                    eps = []
                    cur = None
                    for r in g['qturns'][s]:
                        if cur is not None and r[0] == cur[-1][0] + 1:
                            cur.append(r)
                        else:
                            cur = [r]
                            eps.append(cur)
                    for ep in eps:
                        n = len(ep)
                        c['eps'] += 1
                        c['epturns'] += n
                        ids = set()
                        for r in ep:
                            ids.update(r[2])
                        c['pursuers'] += len(ids)
                        r0, r1 = ep[0][1], ep[-1][1]
                        c['sprints'] += sum(1 for r in ep if r[5] >= 2)
                        if f is not None and f[4] == ep[-1][0]:
                            end = 'queen rammed' if (f[2] == 3 and not f[3]) else 'queen died on her move'
                        else:
                            end = None
                            for i in ids:
                                for d in dby.get(i, ()):
                                    if r0 <= d[0] <= r1 + 1:
                                        if d[3] == 3 and d[5] >= 0 and d[5] != q:
                                            k = 'pursuer rammed by a mate' if d[4] != i else 'pursuer rammed a mate'
                                        elif d[3] == 3:
                                            k = 'pursuer and queen (her move)'
                                        else:
                                            k = 'pursuer died alone'
                                        if end is None or k.startswith('pursuer rammed'):
                                            end = k
                            if end is None:
                                end = 'opened'
                        c['end ' + end] += 1
                        c['len_' + ('1' if n == 1 else '2-3' if n <= 3 else '4-9' if n <= 9 else '10+')] += 1
                        if n >= 4:
                            c['long'] += 1
                            c['long ' + end] += 1
                        c['n8'] += int(n >= 8)
                        c['n8ram'] += int(n >= 8 and end == 'queen rammed')
                        c['ram_all'] += int(end == 'queen rammed')
                        c['ram4'] += int(n >= 4 and end == 'queen rammed')
                        c['Lq'] += ep[0][3]
                        c['longer'] += int(ep[0][3] > max(ep[0][6]))
                        c['p2'] += int(min(ep[0][6]) <= 2)
                        c['o5'] += ep[0][4]
                        c['o5_0'] += int(ep[0][4] == 0)
                        if listing == a and n >= 6:
                            print(g['game'], g.get('map'), 'r%d-%d' % (r0, r1), n, 'turns, her length', ep[0][3], '>', ep[-1][3], 'mates within 5:', [r[4] for r in ep][:12], 'pursuers', sorted(ids), 'lens', ep[0][6], end)
    if listing:
        return
    order = [a for a in ('f454', 'f70', 'f306', 'f157', 'f91', 'f545', 'f19', 'fopp', 'o306', 'o91', 'o264', 'o842', 'oopp', 'v157', 'v306', 'v454', 'v87', 'xB7Q', 'xMAIN', 'B7Q', 'MAIN', 'L1', 'L2') if a in C]
    ends = ('queen rammed', 'queen died on her move', 'pursuer rammed by a mate', 'pursuer rammed a mate', 'pursuer died alone', 'pursuer and queen (her move)', 'opened')
    print('arm | games | episodes per game | turns per episode | pursuers per episode | 1 / 2-3 / 4-9 / 10+ turns (%) | ends (%): ' + ' / '.join(ends) + ' | episodes of 4+ turns: n; same ends | mates within 5 tiles at start: mean; none (%) | her sprints per 100 episode turns | head-ons between a mate and an enemy within 5 tiles of her, per game: mate moved / enemy moved | episodes of 8+ turns: n, ended in a ram | rams ending an episode: all / after 4+ turns / after 8+ | her mean length at start; she is longer than every pursuer %; a pursuer is 2 long %')
    for a in order:
        c = C[a]
        e = c['eps']
        print(a, '|', c['games'], '|', '%.2f' % (e / c['games']), '|', '%.2f' % (c['epturns'] / e) if e else '-', '|', '%.2f' % (c['pursuers'] / e) if e else '-', '|',
              '/'.join(pct(c['len_' + k], e) for k in ('1', '2-3', '4-9', '10+')), '|', '/'.join(pct(c['end ' + k], e) for k in ends), '|', c['long'], ';',
              '/'.join(pct(c['long ' + k], c['long']) for k in ends), '|', '%.2f' % (c['o5'] / e) if e else '-', pct(c['o5_0'], e), '|', pct(c['sprints'], c['epturns']), '|',
              '%.2f / %.2f' % (c['mate_rams_near'] / c['games'], c['enemy_rams_mate_near'] / c['games']), '|', c['n8'], c['n8ram'], '|', c['ram_all'], c['ram4'], c['n8ram'], '|',
              '%.1f' % (c['Lq'] / e) if e else '-', pct(c['longer'], e), pct(c['p2'], e))


main()
