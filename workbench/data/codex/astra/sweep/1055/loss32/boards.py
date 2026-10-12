import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
OUT=Path(__file__).resolve().parent
sections=[]
for gid in (1512561,1512562,1512563):
 d=json.loads((OUT/f'{gid}-details.json').read_text()); b=json.loads((OUT/f'{gid}-scan.json').read_text());qid=b['queens']['us'];qd=next(x for x in b['deaths'] if x['id']==qid); attacker=qd['actor'] if qd['actor']!=qid else next(x['id'] for x in b['deaths'] if x['collision']==qd['collision'] and x['id']!=qid)
 w,h=d['W'],d['H'];g=Geo(w,h,[tuple(map(int,l.split()[1:])) for l in b['text'].splitlines() if l.startswith('EDGE ')])
 boards=[];headers=[]
 for t in [t for t in d['turns'] if t['id']==qid][-3:]:
  x,y=t['body'][0];occ={tuple(c):(int(i),n) for i,bb in t['board'].items() for n,c in enumerate(bb)}; rows=[]
  for dy in range(-3,4):
   top='+';middle=''
   for dx in range(-3,4):
    xy=((x+dx)%w,(y+dy)%h);c=xy[1]*w+xy[0];i,n=occ.get(xy,(-1,-1))
    top+= ('-' if g.moves[c][0][0]==1 else 'P' if g.moves[c][0][0]==2 else ' ')+'+'
    middle+= ('|' if g.moves[c][3][0]==1 else 'P' if g.moves[c][3][0]==2 else ' ')
    middle+= 'Q' if i==qid and n==0 else 'q' if i==qid else 'X' if i==attacker and n==0 else 'x' if i==attacker else ('A' if n==0 else 'a') if i>=0 and d['teams'][str(i)]==0 else ('E' if n==0 else 'e') if i>=0 else '*' if list(xy) in t['pearls'] else '.'
   middle+= '|' if g.moves[c][1][0]==1 else 'P' if g.moves[c][1][0]==2 else ' '
   rows.extend((top,middle))
  rows.append('+'+''.join(('-' if g.moves[((y+3)%h)*w+(x+dx)%w][2][0]==1 else 'P' if g.moves[((y+3)%h)*w+(x+dx)%w][2][0]==2 else ' ')+'+' for dx in range(-3,4)))
  boards.append(rows);headers.append(f"r{t['round']} Q({x},{y})")
 lines=[' | '.join(headers),'```']+['    '.join(parts) for parts in zip(*boards)]+['```']
 sections.append(f'### {gid}\n'+ '\n'.join(lines))
text='[M] 각 판 마지막 여왕 자기 턴 시작의 7×7칸. 중앙 Q=여왕 머리, q=몸; X/x=살해 상대 머리/몸; A/a=아군; E/e=다른 적; *=진주, .=빈칸. 선은 켈프, P는 포털. 좌표는 0부터, 지도의 경계는 순환한다.\n\n'+'\n\n'.join(sections)+'\n'
(OUT/'boards.md').write_text(text)
print(text)
