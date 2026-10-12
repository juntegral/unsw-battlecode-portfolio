"""Scratch (diag-toprams): first strike on paper. Turn starts of a non-queen dragon of 2 to 4 (rounds 0 to rmax) with an enemy head in view
inside the bot's lunge search (plain or over a pearl), by what the rules say: now = agg8 rule; switches = one shorter or pearl path;
level / behind = worth by one and reachable but own heads in view (itself counted) equal to / fewer than enemy heads.
Usage: python3 tr_edge.py <tags> [rmax]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
ME = 1119
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah'}
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
K = defaultdict(Counter)
for tag in tags:
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        gm = json.loads(line)
        os_ = 0 if gm['a'] == ME else 1
        opp = NAMES.get(gm['b'] if os_ == 0 else gm['a'])
        aggr = gm['cells'] <= 1200
        for row in gm['rows']:
            if row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4:
                continue
            who = 'ours' if row['s'] == os_ else 'theirs'
            edge = row['nA'] + 1 - row['nE']
            units = row['un'] >= (1 if aggr else 8)
            st = {}
            for e in row['near']:
                if not e[4] or not (e[9] or e[10]):
                    continue
                worth1 = e[5] >= row['L'] - 1
                if e[14]:
                    s_ = 'now'
                elif e[15]:
                    s_ = 'switches'
                elif worth1 and units and edge == 0:
                    s_ = 'level'
                elif worth1 and units and edge < 0:
                    s_ = 'behind'
                elif not worth1:
                    s_ = 'two shorter'
                else:
                    s_ = 'other'
                st[e[0]] = s_
            if not st:
                continue
            order = ('now', 'switches', 'level', 'behind', 'two shorter', 'other')
            top = min(st.values(), key=order.index)
            hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
            for c in (who + ' v ' + opp, who + ' all'):
                k = K[c]
                k[top + ': turns'] += 1
                if row.get('dead') == 3:
                    k[top + ': rammed'] += 1
                if hit:
                    k[top + ': hit before next turn'] += 1
                    s_ = st.get(gm['rams'][row['hit']]['mid'])
                    if s_:
                        k[s_ + ': hit by that very head'] += 1
keys = sorted({x for c in K for x in K[c]})
cols = sorted(K)
print('| row | ' + ' | '.join(cols) + ' |')
for x in keys:
    print('| ' + x + ' | ' + ' | '.join(str(K[c].get(x, 0)) for c in cols) + ' |')
