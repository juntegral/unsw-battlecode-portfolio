import sys
sys.dont_write_bytecode=True
import json,csv
from collections import Counter
from pathlib import Path
O=Path(__file__).resolve().parent
G=[json.loads(l) for l in (O/'games.jsonl').read_text().splitlines()]
metrics=['turns','portal_turns','queen_reach','queen_miss','queen_visible_reach','queen_visible_miss','pearl_nearq','pearl_miss','parallel_pairs','parallel_death']
with (O/'per-game.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['game','group','map','bot']+[s+'_'+m for s in ['ours','theirs'] for m in metrics]);w.writeheader()
 for g in G:w.writerow(dict(**{k:g[k] for k in ['game','group','map','bot']},**{s+'_'+m:g['counts'][i].get(m,0) for i,s in enumerate(['ours','theirs']) for m in metrics}))
def row(label,a):
 c=[sum((Counter(g['counts'][s]) for g in a),Counter()) for s in (0,1)]
 pair=lambda k:'/'.join(str(x[k]) for x in c)
 port=' / '.join(f"{x['portal_turns']} ({x['portal_turns']/len(a):.1f})" for x in c)
 qm=' / '.join(f"{x['queen_miss']}/{x['queen_reach']}" for x in c)
 pm=' / '.join(f"{x['pearl_miss']}/{x['pearl_nearq']}" for x in c)
 pp=' / '.join(f"{x['parallel_pairs']} ({x['parallel_death']})" for x in c)
 return f'| {label} | {len(a)} | {port} | {qm} | {pm} | {pp} |'
lines=['| [M] 묶음 | 판 | 포털 턴 총수(판당), 우리 / 상대 | 여왕 미공격/도달, 우리 / 상대 | 진주 미섭취/기회, 우리 / 상대 | 평행 쌍(사망 쌍), 우리 / 상대 |','|---|---:|---:|---:|---:|---:|']
for gr in sorted({g['group'] for g in G}):lines.append(row(gr,[g for g in G if g['group']==gr]))
lines.append(row('전체',G))
(O/'table.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
