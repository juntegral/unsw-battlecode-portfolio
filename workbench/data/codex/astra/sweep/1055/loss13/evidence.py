import sys,json,importlib.util
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
p=Path('data/codex/astra/sweep/0410/loss1/analyze.py');s=importlib.util.spec_from_file_location('reader',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
O=Path(__file__).resolve().parent
out={};boards=[]
for gid in (1504489,1504492,1504493):
 a=json.loads((O/f'{gid}.json').read_text());ts=json.loads((O/f'{gid}-turns.json').read_text());ss=json.loads((O/f'{gid}-snapshots.json').read_text())
 root=m.lr.replay.load(Path(f'data/online/smoke/one12-k1-old/M{gid}.replay')).root();w,h=a['dim'];raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];geo=m.Geo(w,h,raw)
 facts={'total_deficit_since':max((int(r) for r,v in ss.items() if v[0]['total']>=v[1]['total']),default=-1)+1,'queen_splits':[],'windows':[],'last_options':[]}
 for t in ts:
  if t['id']==a['queens'][0] and 'split' in t:facts['queen_splits'].append([t['round'],t['split'],sum(1 for k in t['bodies'] if int(k) in {x['id'] for x in ts if x['side']==0})])
 for lo,hi in [(0,18),(19,34),(35,49),(0,100),(101,300),(301,499)]:
  facts['windows'].append([lo,hi,[{'turns':len(z),'eats':sum(t['eats'] for t in z),'noeat':sum(t['eats']==0 for t in z)} for side in [0,1] for z in [[t for t in ts if t['side']==side and lo<=t['round']<=hi]]]])
 for t in a['queen_turns']:
  center=t['start'][1]*w+t['start'][0];occ={c:int(i) for i,b in t['bodies'].items() for c in b};opts=[]
  for d,n in enumerate(geo.nxt[center]):opts.append(['NESW'[d],None if n<0 else [n%w,n//w],None if n<0 else occ.get(n),bool(geo.por[center][d])])
  facts['last_options'].append([t['round'],opts])
  boards.append(f"### [M] {gid} r{t['round']} #{t['id']} L{t['L']} 중심 {t['start']}\n\n```text\n"+'\n'.join(t['board']['grid'])+'\n```\n\n머리 (dx,dy,L): '+json.dumps(t['board']['heads'])+'\n\n경계 (dx,dy,N/E/S/W,#=켈프/P=포털): '+json.dumps(t['board']['edges'])+'\n')
 if gid==1504492:
  positions=a['enemy_q_positions'];facts['enemy_queen_postdeath_bounds']=[min(p[1][0] for p in positions),max(p[1][0] for p in positions),min(p[1][1] for p in positions),max(p[1][1] for p in positions)]
  qcells={p[1][1]*w+p[1][0] for p in positions};seen=set(qcells);q=deque(qcells)
  while q:
   c=q.popleft()
   for n in geo.nxt[c]:
    if n>=0 and n not in seen:seen.add(n);q.append(n)
  facts['enemy_component_cells']=len(seen);facts['our_turns_in_enemy_component']=sum(t['start'][1]*w+t['start'][0] in seen for t in ts if t['side']==0 and t['round']>=9)
 out[gid]=facts
(O/'evidence.json').write_text(json.dumps(out,indent=2));(O/'boards.md').write_text('\n'.join(boards));print(json.dumps(out,ensure_ascii=False))
