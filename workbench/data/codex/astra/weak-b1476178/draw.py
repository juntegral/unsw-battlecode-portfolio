import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,html
from moments import Board
OUT=Path(__file__).resolve().parent
x=json.loads((OUT/'moments.json').read_text());B=Board(Path('data/online/live-one1/b1476178/M1476178.replay'))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="480" viewBox="0 0 1140 480">','<rect width="1140" height="480" fill="white"/>','<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#125ba1"/></marker></defs>','<g font-family="sans-serif" font-size="12">','<text x="25" y="25" font-size="18">[M] 1476178: queen #0, start of turns r84 / r85 / r86 (zero-based)</text>']
for panel,r in enumerate((84,85,86)):
 t=next(t for t in x['turns'] if t['id']==0 and t['r']==r);ox=40+panel*375;oy=95;sz=42
 def center(c):return (ox+(c[0]+.5)*sz,oy+(c[1]-8+.5)*sz)
 svg.append(f'<text x="{ox}" y="65" font-size="17">r{r}: L{t["L"]}, '+('S' if r==84 else 'E,S (one paid)' if r==85 else 'E; rammed by #40')+'</text>')
 for yy in range(8,15):
  svg.append(f'<text x="{ox-24}" y="{oy+(yy-8+.6)*sz}">{yy}</text>')
  for xx in range(7):
   px=ox+xx*sz;py=oy+(yy-8)*sz
   svg.append(f'<rect x="{px}" y="{py}" width="42" height="42" fill="#f5f8fa" stroke="#cbd5df"/>')
   for d,n in enumerate(B.adj[xx,yy]):
    if n is None:
     p1,p2=[((px,py),(px+sz,py)),((px+sz,py),(px+sz,py+sz)),((px,py+sz),(px+sz,py+sz)),((px,py),(px,py+sz))][d]
     svg.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#172d18" stroke-width="5"/>')
 for xx in range(7):svg.append(f'<text x="{ox+(xx+.4)*sz}" y="{oy-10}">{xx}</text>')
 for c in t['pearls']:
  if 0<=c[0]<7 and 8<=c[1]<15:
   cx,cy=center(c);svg.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#c99a00"/>')
 for i,b in t['bodies'].items():
  for k,c in enumerate(b):
   if not(0<=c[0]<7 and 8<=c[1]<15):continue
   cx,cy=center(c);col='#2079b5' if t['teams'][i]==0 else '#c03d32';rad=13 if k==0 else 8
   svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{col}" opacity="{1 if k==0 else .45}"/>')
   if k==0:svg.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white">{i}</text>')
 path=[tuple(t['h'])]+[tuple(c) for c in t['steps']]
 points=' '.join(f'{center(c)[0]},{center(c)[1]}' for c in path)
 svg.append(f'<polyline points="{points}" fill="none" stroke="#125ba1" stroke-width="4" marker-end="url(#arrow)"/>')
 if r==86:
  cx,cy=center((3,12));ax,ay=center((3,11));svg.append(f'<line x1="{ax+8}" y1="{ay}" x2="{cx+8}" y2="{cy}" stroke="#c03d32" stroke-width="3" stroke-dasharray="5 3"/>');svg.append(f'<text x="{cx+13}" y="{cy+5}" fill="#c03d32">X</text>')
svg+=['<text x="25" y="425">Blue: ours; red: enemies; large circles: heads (ID); small: body. Dark edges: kelp; gold: pearls. Blue arrow: action.</text>','<text x="25" y="449">r86: north is own body; south/west are kelp; east (3,12) is the only legal step. #40 then steps south into it.</text>','</g></svg>']
(OUT/'queen-last-three.svg').write_text('\n'.join(svg))
