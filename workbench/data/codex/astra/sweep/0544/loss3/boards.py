import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['tools','data/analysis/ladder/dossier']
import ladder_replay as lr
from count_dossier import Geo
P=Path(__file__).resolve().parent
out=['# [M] 여왕 마지막 세 차례: 7×7 칸과 경계','Q/q=우리 여왕 머리/몸, A/a=아군 머리/몸, X/x=적 머리/몸, *=진주, .=빈칸. |/---=켈프, P=포털. 좌표는 토러스, 차례 시작 참상태. 각 판은 7×7칸이며 칸 사이 경계가 별도 행·열을 차지한다.']
for g in (1493884,1493888):
 d=json.loads((P/f'{g}-detail.json').read_text());w,h=d['w'],d['h'];root=lr.replay.load(f'data/online/smoke/one8-c2-old/M{g}.replay').root();geo=Geo(w,h,[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')])
 for t in d['queen_turns'][-3:]:
  b=t['before'];head=b['0'][0];xs=[(head%w+dx)%w for dx in range(-3,4)];ys=[(head//w+dy)%h for dy in range(-3,4)];grid={c:'.' for c in geo.window(head)}
  for c in t['pearls']:
   if c in grid:grid[c]='*'
  visible=[]
  for i,bb in b.items():
   if any(c in grid for c in bb):visible.append(f'#{i} {"A" if d["teams"][i]==0 else "B"} L{len(bb)} head=({bb[0]%w},{bb[0]//w})')
   for k,c in enumerate(bb):
    if c in grid:grid[c]=('Q' if i=='0' else 'A' if d['teams'][i]==0 else 'X') if k==0 else ('q' if i=='0' else 'a' if d['teams'][i]==0 else 'x')
  out+=['',f'## {g} r{t["round"]}, Q=({head%w},{head//w}), action={t["action"]}',f'x={xs}, y={ys}','```']
  for y in ys:
   out.append('+'+'+'.join({0:'   ',1:'---',2:' P '}[geo.moves[y*w+x][0][0]] for x in xs)+'+')
   row=''
   for x in xs:row+={0:' ',1:'|',2:'P'}[geo.moves[y*w+x][3][0]]+' '+grid[y*w+x]+' '
   row+={0:' ',1:'|',2:'P'}[geo.moves[y*w+xs[-1]][1][0]];out.append(row)
  out.append('+'+'+'.join({0:'   ',1:'---',2:' P '}[geo.moves[ys[-1]*w+x][2][0]] for x in xs)+'+')
  out+=['```','; '.join(visible)]
(P/'boards.md').write_text('\n'.join(out)+'\n')
