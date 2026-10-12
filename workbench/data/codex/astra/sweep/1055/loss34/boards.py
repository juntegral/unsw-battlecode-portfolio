import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
OUT=Path(__file__).resolve().parent
out=[]
for gid in [1512569,1513119]:
 j=json.loads((OUT/f'{gid}.json').read_text());w,h=j['size'];edges=canonical_edges(w,h,j['edges']);qid=j['base']['queens']['us'];own='AB'.index(j['base']['ours'])
 boards=[]
 for t in j['queen_turns'][-3:]:
  hx,hy=t['head'];occ={tuple(c):('Q' if int(i)==qid and k==0 else 'q' if int(i)==qid else 'A' if z['team']==own and k==0 else 'a' if z['team']==own else 'E' if k==0 else 'e') for i,z in t['bodies'].items() for k,c in enumerate(z['body'])};pearls=set(map(tuple,t['pearls']))
  lines=[f"r{t['r']} Q{qid}@({hx},{hy})".ljust(29),f"x={(hx-3)%w}..{(hx+3)%w}, y={(hy-3)%h}..{(hy+3)%h}".ljust(29)]
  for yy in range(-3,4):
   y=(hy+yy)%h
   top='+';middle=''
   for xx in range(-3,4):
    x=(hx+xx)%w;c=(x,y);north=edges.get(edge_id(w,h,x,y,0),(0,0))[0];west=edges.get(edge_id(w,h,x,y,3),(0,0))[0]
    top+=('---' if north==1 else 'PPP' if north==2 else '   ')+'+'
    middle+=('|' if west==1 else 'P' if west==2 else ' ')+f" {occ.get(c,'*' if c in pearls else '.')} "
   east=edges.get(edge_id(w,h,x,y,1),(0,0))[0];middle+=('|' if east==1 else 'P' if east==2 else ' ')
   lines.extend([top,middle])
  bot='+'
  for xx in range(-3,4):
   k=edges.get(edge_id(w,h,(hx+xx)%w,(hy+3)%h,2),(0,0))[0];bot+=('---' if k==1 else 'PPP' if k==2 else '   ')+'+'
  lines.append(bot);boards.append(lines)
 out.append(f'게임 {gid} [M]\n```text\n'+'\n'.join('   '.join(b[i] for b in boards) for i in range(len(boards[0])))+'\n```')
(OUT/'boards.md').write_text('\n\n'.join(out))
print('\n\n'.join(out))
