"""Scratch (diag-toprams): a head whose body leaves the 7 by 7 view counted as one longer (at least 3), on paper.
New mark = tile within 2 tiles (torus Manhattan) of a head of 2 to 4 in view that shows fewer parts than its length; the keep-out rule
(traders charged, pearl steps unchanged) then changes a turn whose chosen tile was unmarked before. Usage: python3 tr_cut.py <tags> [rmax]"""
import sys, json
from collections import Counter
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
ME = 1119
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
K = Counter()
for tag in tags:
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        gm = json.loads(line)
        os_ = 0 if gm['a'] == ME else 1
        w, h = gm['w'], gm['h']

        def near2(t, e):
            dx = abs(t % w - e[16])
            dy = abs(t // w - e[17])
            return min(dx, w - dx) + min(dy, h - dy) <= 2

        for row in gm['rows']:
            if row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4 or row.get('dead') is not None:
                continue
            who = 'ours' if row['s'] == os_ else 'theirs'
            cut = [e for e in row['near'] if e[1] <= 4 and e[4] and e[5] < e[1]]
            K[who + ' turns'] += 1
            if not cut:
                continue
            K[who + ' turns with a cut head of 2-4 in view'] += 1
            ch = None
            for o in row['opt']:
                if o[0] == row.get('first', -1):
                    ch = o
            if ch is None or ch[1] or ch[5]:
                continue
            if not any(near2(ch[0], e) for e in cut):
                continue
            if not any((not o[5]) and not any(near2(o[0], e) for e in cut) for o in row['opt']):
                continue
            K[who + ' turns changed'] += 1
            if 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM:
                K[who + ' rams avoided'] += 1
                if gm['rams'][row['hit']]['mid'] in [e[0] for e in cut]:
                    K[who + ' rams avoided, by the cut head'] += 1
for k in sorted(K):
    print(k, K[k])
