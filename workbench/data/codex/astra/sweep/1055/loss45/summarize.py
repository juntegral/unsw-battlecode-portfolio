import sys,json
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path(__file__).resolve().parent
summary=[];boards=[]
for gid in [1509102,1509107,1509108]:
 a=json.loads((OUT/f'{gid}-details.json').read_text());base=json.loads((OUT/f'{gid}-base.json').read_text());led=json.loads((OUT/f'{gid}-ledger.json').read_text());w=a['w'];h=a['h'];geo=Geo(w,h,a['edges']);qid=base['queens']['us'];att=next(x['actor'] for x in base['deaths'] if x['id']==qid)
 xy=lambda c:(c%w,c//w)
 qt=[t for t in a['turns'] if t['id']==qid];teams=a['teams']
 def permanent(fn):
  bad=[int(r) for r,s in base['snapshots'].items() if not fn(s)]
  return max(bad)+1 if bad else min(map(int,base['snapshots']))
 turncount=[]
 for lo,hi in [(0,100),(101,200)]:
  row=[]
  for side in ['0','1']:
   ts=[t for t in a['turns'] if lo<=t['r']<=hi and str(teams[str(t['id'])])==side]
   row.append({'turns':len(ts),'eats':sum(t['eats'] for t in ts),'eating_turns':sum(t['eats']>0 for t in ts),'empty_moves':sum(t['eats']==0 and t.get('action',{}).get('kind')==0 for t in ts),'splits':sum('split' in t for t in ts)})
  turncount.append([lo,hi,row])
 eqpos=[b[str(base['queens']['them'])][0] for t in a['turns'] if t['r']>=qt[-1]['r'] for b in [t['bodies']] if str(base['queens']['them']) in b]
 row={'gid':gid,'final':base['final'],'end':base['last_round'],'qdeath':qt[-1]['r'],'permanent_total_deficit':permanent(lambda s:s['us']['total']<s['them']['total']),'permanent_q_deficit':permanent(lambda s:s['us']['queen_length']<s['them']['queen_length']),'turn_counts':turncount,'closest':a['closest_after_qdeath'],'near':a['near5_distinct'],'enemy_queen_at_death':xy(next(d['bodies'][str(base['queens']['them'])][0] for d in a['queen_death_states'] if d['id']==qid)),'enemy_queen_positions':len(set(eqpos)),'enemy_queen_x':sorted(set(c%w for c in eqpos)),'enemy_queen_y':sorted(set(c//w for c in eqpos))}
 summary.append(row)
 def board(t):
  hd=t['bodies'][str(qid)][0];hx,hy=xy(hd); grid=[[' ']*15 for _ in range(15)];ps=set(t['pearls']);occ={c:(int(i),k) for i,b in t['bodies'].items() for k,c in enumerate(b)}
  for yy in range(7):
   for xx in range(7):
    c=((hy+yy-3)%h)*w+(hx+xx-3)%w
    char='*' if c in ps else '.'
    if c in occ:
     i,k=occ[c]
     char=('Q' if k==0 else 'q') if i==qid else ('X' if k==0 else 'x') if i==att else ('A' if k==0 else 'a') if teams[str(i)]==0 else ('E' if k==0 else 'e')
    grid[2*yy+1][2*xx+1]=char
    for d,(kind,dst) in enumerate(geo.moves[c]):
     dy,dx=[(-1,0),(0,1),(1,0),(0,-1)][d]
     if kind:grid[2*yy+1+dy][2*xx+1+dx]=('|' if d%2 else '-') if kind==1 else 'P'
  return [''.join(line) for line in grid]
 last=qt[-3:];gs=[board(t) for t in last]
 boards.append(f"[M] {gid}: Q#{qid}, X#{att}; 차례 시작 중심/행동: "+'; '.join(f"r{t['r']} {xy(t['bodies'][str(qid)][0])} → "+('분열' if 'split' in t else ''.join('NESW'[d] for d in t['action']['dirs'])) for t in last)+'\n\n```text\n'+'\n'.join('   '.join(g[y] for g in gs) for y in range(15))+'\n```\n')
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
(OUT/'boards.md').write_text('\n'.join(boards))
print(json.dumps(summary,ensure_ascii=False,indent=2))
