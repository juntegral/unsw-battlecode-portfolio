"""Last turns of a queen before she is rammed: did she step into reach, sit in reach, or get approached. Run from ROOT."""
import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/codex/astra/stuck-opus', 'data/codex/astra/skku']
import json, glob, os
from collections import Counter
import analyze
R = json.load(open('data/codex/astra/skku-opus/rows.json'))
paths = {}
for mp in glob.glob('data/online/live-one1/b*/game-*.json'):
    gid = int(os.path.basename(mp)[5:-5]); paths[gid] = mp
def reach(L): return (L + 3) // 4 + max(0, L - 2)
tot = [Counter(), Counter()]
for r in R:
    if not (r['atk'][0] or r['atk'][1]): continue
    mp = paths[r['gid']]; j = json.load(open(mp)); rp = os.path.join(os.path.dirname(mp), f"M{r['gid']}.replay")
    d = analyze.details(rp, j); W, H = d['W'], d['H']
    def gap(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); return min(dx, W - dx) + min(dy, H - dy)
    for x in d['deaths']:
        if x['id'] not in d['queens']: continue
        s = x['s']; a = x.get('attack') or {}
        if a.get('id') == x['id'] or a.get('s') == s: continue
        qt = d['qturn'][s]
        if not qt: continue
        last = qt[-1]; prev = qt[-2] if len(qt) > 1 else last
        foe = next((f for f in last['foes'] if f['id'] == a['id']), None)
        d_before = gap(tuple(last['h']), tuple(foe['h'])) if foe else None
        d_after = gap(tuple(x['head']), tuple(foe['h'])) if foe else None
        rc = reach(foe['L']) if foe else None
        moved = tuple(last['h']) != tuple(x['head'])
        still3 = len({tuple(q['h']) for q in qt[-3:]}) == 1 and not moved
        same_round = last['r'] == x['r']
        if foe is None: cls = 'rammer not in her view at her last turn'
        elif d_before <= rc and d_after <= rc: cls = 'in reach before and after her move' + (' (did not move)' if not moved else ' (closer or same)' if d_after <= d_before else ' (moved away, not far enough)')
        elif d_before > rc and d_after <= rc: cls = 'stepped INTO reach'
        else: cls = 'out of computed reach after her move (rammer grew/ate or portal)'
        tot[s][cls] += 1
        tot[s]['queen L<=3'] += x['L'] <= 3
        tot[s]['queen L at death minus L 10 turns earlier <0'] += (x['L'] < qt[-10]['L']) if len(qt) >= 10 else 0
        tot[s]['foes in view at last turn: ' + str(min(len(last['foes']), 4))] += 1
        print(r['gid'], r['seat'], r['map'], 'OUR' if s == 0 else 'their', 'queen r', x['r'], 'L', x['L'], 'L10ago', qt[-10]['L'] if len(qt) >= 10 else None, 'lastturn r', last['r'], 'foes', len(last['foes']), 'rammer L', a.get('L'),
              'd_before', d_before, 'd_after', d_after, 'reach', rc, 'moved', moved, '|', cls, flush=True)
for s, nm in ((0, 'OUR queen rammed'), (1, 'THEIR queen rammed')):
    print(nm, sum(v for k, v in tot[s].items() if k.startswith(('in reach', 'stepped', 'out of', 'rammer not'))))
    for k, v in sorted(tot[s].items()): print('   ', k, v)
