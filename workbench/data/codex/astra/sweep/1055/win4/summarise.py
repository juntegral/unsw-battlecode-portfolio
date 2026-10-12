import sys
sys.dont_write_bytecode=True
import json, importlib.util
from pathlib import Path
from collections import Counter, defaultdict

OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sonar_counter',Path.cwd().parent/'battlecode/work/card_42_check.py')
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)

def summary(g):
 sys.path.insert(0,'data/analysis/ladder/dossier/local')
 import scoreboard as sb
 root=sb.load_replay(Path(g['replay'])).root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
 qid=min(t['id'] for t in g['turns'] if t['ours'])
 us=[t for t in g['turns'] if t['ours']]
 qt=[t for t in us if t['queen']]
 out=dict(gid=g['gid'],map=g['map'],side=g['side'],last_round=g['last_round'],final=g['final'],ahead=g['ahead'],
  qdeath=g['qdeath'],eqdeath=g['eqdeath'],deficit_last=g['queen_deficits'][-1:] ,deficit_max=max(g['queen_deficits'],key=lambda t:t['them']-t['us'],default=None),
  adjacent_ram=g['q_one_step'][:2],adjacent_ram_n=len(g['q_one_step']),count_halved=g['count_halved'][:2],
  log_tags=dict(Counter(t['text'].split()[0] for t in g['logs'] if t['ours'])),turns=len(us),
  q_L2=sum(t['length']==2 for t in qt),q_L3=sum(t['length']==3 for t in qt),q_L4plus=sum(t['length']>=4 for t in qt),q_turns=len(qt),
  q_split=sum(t['queen'] and t['ours'] for t in g['splits']),q_safe_L4_nosplit=sum(t['length']==4 and t['units']>=2 and t['action']==0 for t in qt),
  eat_first_compatible=sum(bool(t['safe_pearl']) and bool(t['path']) and t['path'][0][1] in t['safe_pearl'] for t in us),
  safe_pearl_opportunities=sum(bool(t['safe_pearl']) for t in us),
  safe_pearl_pass=sum(bool(t['safe_pearl']) and not t['eaten'] for t in us),
  zero_step_moves=sum(t['action']==0 and not t['path'] and t['end'] is not None for t in us),
  heading_first12=sum(t['round']<12 and not t['queen'] and t['action']==0 and bool(t['path']) for t in us),
  long_sprints=sum(not t['queen'] and t['length']>=8 and t['steps']>=2 for t in us),
  long_sprints_threat_near=sum(not t['queen'] and t['length']>=8 and t['steps']>=2 and t['enemy_dist']<=3 for t in us),
  long_sprints_examples=[{k:t[k] for k in ('round','id','length','steps','enemy_dist','path')} for t in us if not t['queen'] and t['length']>=8 and t['steps']>=2 and t['enemy_dist']<=3][:3],
  eat_examples=[{k:t[k] for k in ('round','id','length','safe_pearl','path','eaten')} for t in us if t['safe_pearl'] and t['path'] and t['path'][0][1] in t['safe_pearl']][:2],
  pass_examples=[{k:t[k] for k in ('round','id','length','safe_pearl','path','action')} for t in us if t['safe_pearl'] and not t['eaten']][:2],
  queen_defend_rams=[],own_mover_rams=0,own_mover_longer_trade=0)
 q_by_round={t['round']:t for t in qt}
 for d in g['deaths']:
  if d['side']=='them' and d['reason']==3:
   partner=next((z for z in g['deaths'] if z['round']==d['round'] and z['actor']==d['actor'] and z['id']==d['actor'] and z['side']=='us'),None)
   if partner:
    out['own_mover_rams']+=1
    out['own_mover_longer_trade']+=partner['length']>d['length']
    q=q_by_round.get(d['round'])
    if q and d['id']>1:
     a,b=q['head'],d['body'][0][1]*w+d['body'][0][0]
     dx,dy=abs(a%w-b%w),abs(a//w-b//w)
     if min(dx,w-dx)+min(dy,h-dy)<=3:
      out['queen_defend_rams'].append(dict(round=d['round'],actor=partner['id'],target=d['id'],our_length=partner['length'],target_length=d['length']))
 key=codec.make_key(w,h,codec.team_tag(g['side']));cache={};streams={};far=[];bad=0
 for p in g['pings']:
  if not p['ours']:continue
  wire=p['message']
  if wire not in cache:cache[wire]=codec.unseal(key,wire,streams)
  plain=cache[wire]
  if plain is None:bad+=1;continue
  if plain>>63 and ((plain>>38)&0x7fff)==0x5B:
   far.append(dict(round=p['round'],id=p['id'],hit=p['hit'],cell=plain&0x3fff,parts=((plain>>14)&0x3fff)+1,when=(plain>>28)&0x1ff,origin=p['origin'],end=p['end']))
 unique={(p['round'],p['id'],p['cell'],p['when']) for p in far}
 hits={(p['round'],p['id'],p['cell'],p['when']) for p in far if p['hit']==qid}
 out.update(far_rays=len(far),far_transmissions=len(unique),far_hit_queen=len(hits),far_examples=far[:3],far_queen_examples=[p for p in far if p['hit']==qid][:3],sonar_invalid=bad)
 loops=[]
 grouped=defaultdict(list)
 for t in us:grouped[t['id']].append(t)
 for i,ts in grouped.items():
  for n in range(19,len(ts)):
   win=ts[n-19:n+1]
   if win[-1]['round']-win[0]['round']==19 and all(t['action']==0 and t['end'] is not None and not t['eaten'] for t in win) and len({t['head'] for t in win})<=4:
    loops.append(dict(id=i,start=win[0]['round'],end=win[-1]['round'],queen=win[0]['queen'],cells=sorted({t['head'] for t in win})))
 out['loop_windows']=len(loops);out['loop_examples']=loops[:3]
 return out

if __name__=='__main__':
 rows=[]
 for p in sorted(OUT.glob('[0-9]*.json')):
  row=summary(json.loads(p.read_text()));rows.append(row)
  print(json.dumps(row,ensure_ascii=False),flush=True)
 (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
