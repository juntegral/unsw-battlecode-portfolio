import json, math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
small=ImageFont.truetype(FONT,10); mid=ImageFont.truetype(FONT,14); title=ImageFont.truetype(FONT,19)
def walls(d,M,ox,oy,c):
 W,H=M['width'],M['height']; he=M['initialHEdges'];ve=M['initialVEdges']
 def val(a,k):return a.get(str(k),0) if isinstance(a,dict) else a[k]
 for y in range(H):
  for x in range(W):
   px,py=ox+x*c,oy+y*c
   if val(he,y*W+x)==1 or (y==0 and val(he,H*W+x)==1):d.line((px,py,px+c,py),fill='#334155',width=max(1,c//7))
   if val(ve,y*(W+1)+x)==1 or (x==0 and val(ve,y*(W+1)+W)==1):d.line((px,py,px,py+c),fill='#334155',width=max(1,c//7))
for board in json.loads((O/'boards.json').read_text()):
 M=board['initialMap'];W,H=M['width'],M['height'];G=json.loads((O/('geometry-'+board['geometry']+'.json')).read_text());c=22 if W<=32 else 16;pw=W*c+48;ph=H*c+115
 im=Image.new('RGB',(pw*3+20,ph+60),'#f8fafc');d=ImageDraw.Draw(im)
 d.text((14,10),f"{board['map']} winner {board['team']} | game {board['key']} | cluster winner N={board['clusterN']}",fill='#0f172a',font=title)
 d.text((14,36),'Before first move; amber=A, cyan=B; labeled circles=head ids; pale pink=winner middle; white dots=pearls; purple edges=paired portals',fill='#475569',font=mid)
 for j,snap in enumerate(board['snapshots']):
  ox,oy=14+j*pw,94;d.text((ox,70),f"r{snap['round']}   A heads={sum(x['team']=='A' for x in snap['bodies'])}   B heads={sum(x['team']=='B' for x in snap['bodies'])}",font=mid,fill='#0f172a')
  for k in range(W*H):
   x,y=k%W,k//W;px,py=ox+x*c,oy+y*c;d.rectangle((px,py,px+c,py+c),fill='#fee2e2' if G['bin'][board['team']][k]==2 else '#e2e8f0',outline='#cbd5e1')
  for k in snap['pearls']:
   x,y=k%W,k//W;d.ellipse((ox+x*c+c*.4,oy+y*c+c*.4,ox+x*c+c*.65,oy+y*c+c*.65),fill='white',outline='#64748b')
  for dragon in snap['bodies']:
   color='#e89e26' if dragon['team']=='A' else '#22b8cf'
   for i,k in reversed(list(enumerate(dragon['body']))):
    x,y=k%W,k//W;px,py=ox+x*c,oy+y*c;box=(px+3,py+3,px+c-3,py+c-3)
    if i==0:d.ellipse(box,fill=color,outline='#111827',width=2);d.text((px+4,py+c*.2),str(dragon['id']),fill='#111827',font=small)
    else:d.rounded_rectangle(box,radius=3,fill=color)
  walls(d,M,ox,oy,c)
  for pi,pair in enumerate(M.get('portals',[])):
   for endpoint in pair:
    x,y,side=endpoint['x'],endpoint['y'],endpoint['side'];px,py=ox+x*c,oy+y*c
    if side=='N':box=(px,py,px+c,py)
    elif side=='S':box=(px,py+c,px+c,py+c)
    elif side=='W':box=(px,py,px,py+c)
    else:box=(px+c,py,px+c,py+c)
    d.line(box,fill='#a855f7',width=4);d.text((px+1,py+1),'P'+str(pi),font=small,fill='#7e22ce')
  for x in range(W):
   if x%2==0:d.text((ox+x*c+4,oy+H*c+5),str(x),font=small,fill='#475569')
  for y in range(H):
   if y%2==0:d.text((ox+W*c+3,oy+y*c+4),str(y),font=small,fill='#475569')
 im.save(O/('board-'+board['map'].replace('/','-').replace(' ','_')+'.png'))
# Per-cell pooled head share, all snapshots on the same scale within a map.
T=json.loads((O/'tables.json').read_text())
CP=[5,10,15,20,25,35,50]
for key,m in T['maps'].items():
 if m['layout']=='?':continue
 classes=[(n,m['classes'].get(n)) for n in ['elite-winners','elite-losers','set:cand-stack11-online','set:v1-w1','set:v1-w2','local:v11c']];classes=[(n,c) for n,c in classes if c]
 W,H=m['width'],m['height'];cell=6;pw=W*cell+24;ph=H*cell+50;maxv=max((x/cp['heads'] for _,c in classes for cp in c['checkpoint'].values() if cp['heads'] for x in cp['heatmapNormalized']),default=1)
 im=Image.new('RGB',(pw*len(CP)+30,ph*len(classes)+75),'#f8fafc');d=ImageDraw.Draw(im)
 d.text((12,10),f'{key} | head tile heatmaps normalized to side A | full population',font=title,fill='#0f172a');d.text((12,36),f'Color: pooled tile heads / all heads at checkpoint. Shared scale 0 to {maxv:.3f}; black=0. N is games reaching checkpoint.',font=mid,fill='#475569')
 for row,(name,c) in enumerate(classes):
  for col,r in enumerate(CP):
   cp=c['checkpoint'].get(str(r));ox,oy=22+col*pw,96+row*ph
   d.text((ox,oy-25),f'{name} r{r} N={cp["N"] if cp else 0}',font=small,fill='#0f172a')
   if not cp:continue
   for k,x in enumerate(cp['heatmapNormalized']):
    v=(x/cp['heads']/maxv)**.45 if cp['heads'] else 0;color=(int(255*v),int(220*v),int(80*v));px,py=ox+(k%W)*cell,oy+(k//W)*cell;d.rectangle((px,py,px+cell-1,py+cell-1),fill=color)
   mg=json.loads((O/('geometry-'+m['geometrySignatures'][0]+'.json')).read_text())
   walls(d,mg['initialMap'],ox,oy,cell)
   for xx in range(0,W,max(4,W//8)):d.text((ox+xx*cell,oy+H*cell+1),str(xx),font=small,fill='#475569')
   for yy in range(0,H,max(4,H//6)):d.text((ox-16,oy+yy*cell),str(yy),font=small,fill='#475569')
   d.text((ox,oy+H*cell+15),f'heads={cp["meanHeads"]:.1f}; middle={cp["pooledShares"][2]:.1%}',font=small,fill='#475569')
 im.save(O/('heatmap-'+key.replace('/','-').replace(' ','_')+'.png'))
print('rendered boards and heatmaps')
