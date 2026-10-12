"""Scratch (diag-topqueen): in the close episodes around a queen, how often a mate has her and the pursuer in view, and how
often it could ram the pursuer if QUEEN_DEFEND_RADIUS were 5 (the mate sees both inside its 7 by 7, the pursuer is within 5 tiles
of her, the mate is 10 long or less; in reach = Manhattan distance to the pursuer's head within the mate's ram reach, kelp and
bodies ignored, so an upper bound). Reads tq2_def-*.jsonl. Usage: python3 tq2_deftab.py [rows]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    return 'v%d' % t if lab in ('L1', 'L2') else 'x' + lab


def main():
    C = defaultdict(Counter)
    rows = []
    for tag in ('top3-0', 'top3-1', 'q1', 'l1', 'l2', 'm1', 'm2', 'm3'):
        p = W / ('tq2_def-%s.jsonl' % tag)
        if not p.exists():
            continue
        with open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                g = json.loads(line)
                w, h = g['w'], g['h']

                def dxy(a, b):
                    dx = abs(a % w - b % w)
                    dy = abs(a // w - b // w)
                    return min(dx, w - dx), min(dy, h - dy)

                for s in (0, 1):
                    a = arm_of(g, s)
                    c = C[a]
                    f = g['fate'][s]
                    c['games'] += 1
                    c['deaths'] += int(f is not None)
                    c['rams'] += int(f is not None and f[2] == 3 and not f[3])
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
                        c['turns'] += n
                        ram = f is not None and f[4] == ep[-1][0] and f[2] == 3 and not f[3]
                        c['ep_ram'] += int(ram)
                        seen_at, reach_at, new_at = [], [], []
                        for k, r in enumerate(ep):
                            qh = r[7]
                            ts = tr = tn = 0
                            for pid, pl, pt in r[8]:
                                qx, qy = dxy(qh, pt)
                                if qx + qy > 5:
                                    continue
                                for mid, ml, mt in r[9]:
                                    ax, ay = dxy(mt, pt)
                                    bx, by = dxy(mt, qh)
                                    if max(ax, ay) > 3 or max(bx, by) > 3 or ml > 10:
                                        continue
                                    ts = 1
                                    reach = (ml + 3) // 4 + ml - 2
                                    reach = min(reach, (3 if w * h <= 1200 else 4) if ml <= 4 else 8)
                                    if ax + ay <= reach:
                                        tr = 1
                                        if not (ml <= 4 and pl >= ml):
                                            tn = 1
                            c['t_seen'] += ts
                            c['t_reach'] += tr
                            c['t_new'] += tn
                            if ts:
                                seen_at.append(k)
                            if tr:
                                reach_at.append(k)
                            if tn:
                                new_at.append(k)
                        c['ep_seen'] += int(bool(seen_at))
                        c['ep_reach'] += int(bool(reach_at))
                        if not ram:
                            c['calm_reach_turns'] += len(reach_at)
                            c['calm_reach_eps'] += int(bool(reach_at))
                        if ram:
                            c['ram_seen'] += int(bool(seen_at))
                            c['ram_seen2'] += int(any(k <= n - 3 for k in seen_at))
                            c['ram_reach'] += int(bool(reach_at))
                            c['ram_reach1'] += int(any(k <= n - 2 for k in reach_at))
                            rows.append((a, g['game'], g.get('map'), 'r%d-%d' % (ep[0][1], ep[-1][1]), n, 'first view at turn', seen_at[:1], 'first reach', reach_at[:1], 'mates within 7, last turns', [len(r[9]) for r in ep][-5:]))
    print('arm | games; her deaths; rams | episodes; ending in a ram | episode turns; a mate has both in view; a mate could ram (of those not allowed today) | episodes with a view; with a reach | rams: a mate had both in view on any turn / 2+ turns before the hit / could ram on any turn / before the last turn | episodes not ending in a ram: with a reach, reach turns')
    for a in ('f454', 'f70', 'f306', 'f157', 'fopp', 'v157', 'v306', 'v454', 'v87', 'xB7Q', 'xMAIN', 'B7Q', 'L1', 'L2', 'MAIN'):
        c = C[a]
        if not c['games']:
            continue
        print(a, '|', c['games'], c['deaths'], c['rams'], '|', c['eps'], c['ep_ram'], '|', c['turns'], '%d (%.0f%%)' % (c['t_seen'], 100.0 * c['t_seen'] / max(1, c['turns'])),
              '%d (%d)' % (c['t_reach'], c['t_new']), '|', c['ep_seen'], c['ep_reach'], '|', c['ram_seen'], c['ram_seen2'], c['ram_reach'], c['ram_reach1'], '|', c['calm_reach_eps'], c['calm_reach_turns'])
    if len(sys.argv) > 1:
        for r in rows:
            if r[0] in ('B7Q', 'L1', 'L2'):
                print(r)


main()
