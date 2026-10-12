import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
G=[json.loads(p.read_text()) for p in sorted(OUT.glob('g[0-9]*.json'))]
old=json.loads((OUT.parent/'smallmap/games.json').read_text())
paths={g['gid']:g['path'] for g in old}
lossids={g['gid'] for g in old if g['result']=='loss'}
dimensions={}
for g in G:
 if g['map'] in dimensions: continue
 path=ROOT/paths[g['gid']] if g['gid'] in paths else ROOT/f"data/online/smoke/one5-c1-old/M{g['gid']}.replay"
 root=lr.replay.load(path).root()
 dimensions[g['map']]=tuple(map(int,root.text(0).splitlines()[0].split()[1:3]))
def hidden_foreign(d,g):
 w,h=dimensions[g['map']];x,y=d['before']['head']
 for e in d['at_split']['edges']:
  if e['kind'] not in ('mate','enemy'): continue
  dx,dy=abs(e['xy'][0]-x),abs(e['xy'][1]-y)
  if min(dx,w-dx)>3 or min(dy,h-dy)>3:return True
 return False
groups={'원래 패배 54판':[g for g in G if g['gid'] in lossids],
        '원래 전체 73판':[g for g in G if g['original']],
        'WHQ':[g for g in G if g['label'].endswith('-w1')],
        'Cache':[g for g in G if not g['original']],
        'dev':[g for g in G if g['label'].endswith('-d1')]}
out={}
for name,gs in groups.items():
 ds=[(g,d) for g in gs for d in g['deaths'] if d['side']=='us' and d['postsplit_boxed_proxy']]
 closedchild=[(g,d) for g,d in ds if d['role']=='child' and d['at_split']['exits']==0]
 nonqueen_open=[(g,d) for g,d in closedchild if not d['split_queen'] and d['before']['exits']>0]
 out[name]=dict(closed_role=dict(Counter(d['role'] for g,d in ds if d['at_split']['exits']==0)),
    closed_child=len(closedchild),closed_child_hidden_foreign=sum(hidden_foreign(d,g) for g,d in closedchild),
    nonqueen_open_closed_child=len(nonqueen_open),nonqueen_open_closed_child_hidden_foreign=sum(hidden_foreign(d,g) for g,d in nonqueen_open),
    moved_blockers=dict(Counter('+'.join(sorted(set(e['kind'] for e in d['at_death']['edges'] if e['kind']!='wall'))) for g,d in ds if d['at_split']['exits']>0 and not d['same_head'])),
    r149={})
 for side in ('us','them'):
  sp=[s for g in gs for s in g['splits'] if s['side']==side and s['round']<=149]
  post=[d for g in gs for d in g['deaths'] if d['side']==side and 'split_event' in d and d['split_round']<=149]
  out[name]['r149'][side]=dict(splits=len(sp),deaths=len(post),rate=100*len(post)/len(sp))
(OUT/'supplement.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
