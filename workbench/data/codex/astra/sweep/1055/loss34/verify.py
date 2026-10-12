import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows={}
for gid in [1512569,1512570,1513119]:
 j=json.loads((OUT/f'{gid}.json').read_text());b=j['base'];own='AB'.index(b['ours'])
 assert b['bots'][b['ours']]=='21377'
 for s,key in enumerate(['us','them']):
  f=b['final'][key];assert j['ledger']['ends'][s][:4]==[f['alive'],f['total'],f['longest'],f['queen_length']]
  assert sum(t['eats'] for t in j['turns'] if t['side']==(own if s==0 else 1-own))==f['pearls']
 ss=b['snapshots'];ts=[t for t in j['turns'] if t['side']==own and t['r']<=100]
 row={'final_verified':True,'permanent_total_deficit_round':1+max(int(r) for r,x in ss.items() if x['us']['total']>=x['them']['total']),'permanent_queen_deficit_round':1+max(int(r) for r,x in ss.items() if x['us']['queen_length']>=x['them']['queen_length']),'r0_100':{'turns':len(ts),'eating_turns':sum(t['eats']>0 for t in ts),'split_turns':sum('split' in t for t in ts)},'nearest_after_queen_death':j['mindistance'],'near5_rounds':len(j['near'])}
 if gid==1512570:
  row['queen_no_eat_r74_304']=sum(t['eats'] for t in j['queen_turns'] if 74<=t['r']<=304)
  row['own_head_x_r0_100']=[min(t['head'][0] for t in ts),max(t['head'][0] for t in ts)]
 if gid==1513119:
  t=j['queen_turns'][-1];w,h=j['size'];hx,hy=t['head'];bd=t['bodies']['28']['body'];vis=[p for p in bd if min(abs(p[0]-hx),w-abs(p[0]-hx))<=3 and min(abs(p[1]-hy),h-abs(p[1]-hy))<=3];edge=[p for p in vis if min(abs(p[0]-hx),w-abs(p[0]-hx))==3 or min(abs(p[1]-hy),h-abs(p[1]-hy))==3]
  assert len(vis)==1 and not edge
  row['r74_enemy28']={'actual_length':len(bd),'visible_parts':len(vis),'view_edge_parts':len(edge),'body':bd}
 rows[gid]=row
(OUT/'verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('3/3 replay bot IDs, final states and pearl counts agree; portal-truncated body case verified.')
