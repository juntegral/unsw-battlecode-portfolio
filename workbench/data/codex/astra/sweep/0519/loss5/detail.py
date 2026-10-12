import json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import canonical_edges,edge_id
from pathlib import Path
P=Path(__file__).resolve().parent
out=[]
for g in (1492099,1492102,1492103):
 s=json.loads((P/f'{g}-summary.json').read_text());d=json.loads((P/f'{g}-turns.json').read_text());W,H=s['W'],s['H'];teams=d['teams'];edges=canonical_edges(W,H,d['edges']);q=str(s['queens'][0]);qt=[t for t in d['turns'] if str(t['i'])==q]
 def board(t):
  hx,hy=t['h'];occ={tuple(c):('Q' if i==q else 'A' if teams[i]==0 else 'E') if k==0 else ('q' if i==q else 'a' if teams[i]==0 else 'e') for i,b in t['bodies'].items() for k,c in enumerate(b)};pearls=set(map(tuple,t['pearls']));lines=[]
  for dy in range(-3,4):
   y=(hy+dy)%H;top='';row=''
   for dx in range(-3,4):
    x=(hx+dx)%W;kn=edges.get(edge_id(W,H,x,y,0),(0,0))[0];kw=edges.get(edge_id(W,H,x,y,3),(0,0))[0]
    top+='+'+('-' if kn==1 else 'P' if kn==2 else ' ');row+=('|' if kw==1 else 'P' if kw==2 else ' ')+occ.get((x,y),'*' if (x,y) in pearls else '.')
   ke=edges.get(edge_id(W,H,(hx+3)%W,y,1),(0,0))[0];lines.extend([top+'+',row+('|' if ke==1 else 'P' if ke==2 else ' ')])
  y=(hy+3)%H;lines.append(''.join('+'+('-' if (k:=edges.get(edge_id(W,H,(hx+dx)%W,y,2),(0,0))[0])==1 else 'P' if k==2 else ' ') for dx in range(-3,4))+'+')
  return '\n'.join(lines)
 out.append(f'\n## {g}')
 for t in qt[-3:] if s['qdeath'] else []:
  out.append(f"r{t['r']} queen #{q} L{t['L']} head {t['h']} dirs {t['dirs']} end {t['end']}\n```text\n{board(t)}\n```")
  print(g,t['r'],'logs',t['logs'],'near',[(i,len(b),b[0]) for i,b in t['bodies'].items() if abs((b[0][0]-t['h'][0]+W//2)%W-W//2)<=3 and abs((b[0][1]-t['h'][1]+H//2)%H-H//2)<=3])
 keys=['q','long','total']
 for k in keys:
  nonloss=[int(r) for r,st in s['snaps'].items() if st[0][k]>=st[1][k]]
  print(g,'persistent deficit',k,max(nonloss)+1 if nonloss else 0)
 if g==1492099:
  for t in d['turns']:
   if t['r'] in (359,360,361) and t['i'] in (176,102,25,138):print('leader moment', {k:v for k,v in t.items() if k not in ('bodies','pearls')})
 if g==1492102:
  for t in d['turns']:
   if t['r'] in (17,18,19) and t['i'] in (0,4):print('devil',t['r'],t['i'],t['logs'])
 if g==1492103:
  for t in qt:
   if t['r'] in (0,37,82,144,160,200,300,301,350,389,499):print('trauma',t['r'],'L',t['L'],'units',sum(teams[i]==0 for i in t['bodies']),'logs',t['logs'])
(P/'boards.md').write_text('\n'.join(out))
