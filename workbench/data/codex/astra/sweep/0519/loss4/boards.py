import json,html
from pathlib import Path
OUT=Path(__file__).resolve().parent
lines=['<table>']
for gid in (1492096,1492097,1492098):
 a=json.loads((OUT/f'detail-{gid}.json').read_text());ts=a['queen_turns']
 lines.append('<tr>'+''.join(f'<th>{gid} r{t["r"]}, ({t["head"][0]},{t["head"][1]}), '+''.join('NESW'[d] for d in t['dirs'])+'</th>' for t in ts)+'</tr>')
 cells=[]
 for t in ts:
  grid=[[' ']*15 for _ in range(15)]
  for y in range(0,15,2):
   for x in range(0,15,2):grid[y][x]='+'
  for y,row in enumerate(t['board']['rows']):
   for x,c in enumerate(row):grid[2*y+1][2*x+1]=c
  for dx,dy,dr,k,pid in t['board']['edges']:
   x=2*(dx+3)+1;y=2*(dy+3)+1
   ox,oy={'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}[dr]
   grid[y+oy][x+ox]=':' if k==2 else '-' if dr in 'NS' else '|'
  cells.append('<td><pre>'+html.escape('\n'.join(''.join(row) for row in grid))+'</pre></td>')
 lines.append('<tr>'+''.join(cells)+'</tr>')
lines.append('</table>')
p=OUT/'report.md';s=p.read_text().replace('후보96=39(Default 제외 Tower)+127(Default)가 아니라 **166=39+127**턴','후보 **166=39(Tower)+127(Default)**턴')
s=s.replace('<!-- BOARDS -->','\n'.join(lines));p.write_text(s)
