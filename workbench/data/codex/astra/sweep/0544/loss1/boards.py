import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
OUT=Path(__file__).parent
parts=[]
for gid,att in [(1493878,182),(1493879,150),(1493880,-1)]:
 d=json.loads((OUT/f'{gid}.json').read_text());w,h=d['w'],d['h'];g=Geo(w,h,d['edges']);q=d['queens'][0]
 ts=[t for t in d['queen_turns'] if t['id']==q][-3:];boards=[]
 for t in ts:
  hd=t['start'][0];rows=[[' ']*15 for _ in range(15)]
  occ={c:('Q' if int(i)==q and n==0 else 'q' if int(i)==q else ('X' if n==0 else 'x') if int(i)==att else ('A' if d['teams'][i]==0 else 'E') if n==0 else ('a' if d['teams'][i]==0 else 'e')) for i,b in t['bodies'].items() for n,c in enumerate(b)}
  for yy in range(7):
   for xx in range(7):
    c=((hd//w+yy-3)%h)*w+(hd%w+xx-3)%w;ry,rx=2*yy+1,2*xx+1
    rows[ry][rx]=occ.get(c,'*' if c in t['pearls'] else '.')
    for dr,(dy,dx) in enumerate([(-1,0),(0,1),(1,0),(0,-1)]):
     k,_=g.moves[c][dr]
     if k:rows[ry+dy][rx+dx]=':' if k==2 else '-' if dy else '|'
  boards.append([''.join(r) for r in rows])
 parts.append(f"**{gid} [M]** — "+' / '.join(f"r{t['r']} Q=({t['start'][0]%w},{t['start'][0]//w})" for t in ts)+'\n\n```text\n'+'\n'.join('   '.join(bs[y] for bs in boards).rstrip() for y in range(15))+'\n```\n')
(OUT/'boards.md').write_text('\n'.join(parts))
