import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as LR
from count_local import Geo
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss47')
for p in sorted(OUT.glob('*-detail.json')):
 a=json.loads(p.read_text());w,h=a['w'],a['h'];g=Geo(w,h,a['raw_edges']);q=a['qs'][0];edges=LR.canonical_edges(w,h,a['raw_edges']);xy=lambda c:(c%w,c//w)
 output=[]
 for f in a['qframes']:
  bs={int(k):v for k,v in f['bodies'].items()};head=bs[q][0];hx,hy=xy(head);occ={c:(i,k) for i,b in bs.items() for k,c in enumerate(b)}
  lines=[]
  for dy in range(-3,4):
   top='';row=''
   for dx in range(-3,4):
    x,y=(hx+dx)%w,(hy+dy)%h;c=y*w+x
    north=edges.get(LR.edge_id(w,h,x,y,0),(0,-1))[0];west=edges.get(LR.edge_id(w,h,x,y,3),(0,-1))[0]
    top+=' '+('-' if north==1 else '~' if north==2 else ' ')
    ch='*' if c in f['pearls'] else '.'
    if c in occ:
     i,k=occ[c];ch=('Qq' if i==q else 'Aa' if f['teams'][str(i)]==0 else 'Ee')[int(k>0)]
    row+=('|' if west==1 else ':' if west==2 else ' ')+ch
   lines.extend([top,row])
  print('\n',a['gid'],'round',f['round'],'event',f['event'],'head',xy(head))
  print('\n'.join(lines))
  print('neighbors', [('NESW'[d],kind,xy(t),occ.get(t)) for d,(kind,t) in enumerate(g.moves[head])])
  local={i:[xy(c) for c in b] for i,b in bs.items() if any(min(abs(c%w-hx),w-abs(c%w-hx))<=3 and min(abs(c//w-hy),h-abs(c//w-hy))<=3 for c in b)}
  print('local',local)
  output.append(dict(round=f['round'],event=f['event'],head=xy(head),board=lines,local=local))
 (OUT/f"{a['gid']}-boards.json").write_text(json.dumps(output,ensure_ascii=False,indent=2))
