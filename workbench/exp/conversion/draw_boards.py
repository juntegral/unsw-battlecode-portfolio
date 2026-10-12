"""Replay board figures, adapted from exp/pocket/draw_boards.py. No generated artwork."""
import gzip, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
out=Path(__file__).parent
font='/System/Library/Fonts/Supplemental/Arial.ttf'
ft=ImageFont.truetype(font,14); small=ImageFont.truetype(font,11); title=ImageFont.truetype(font,18)
reads=json.loads((out/'deep-reads.json').read_text())
chosen=[]
for mapname in ['Slithery Fight/a','Trauma/a','Autarky/a']:
    candidates=[r for r in reads if r['pick']['map']==mapname and r['pick']['selection'].startswith('late L>=8')]
    chosen.append(candidates[-1])
for read in chosen:
    f=json.loads(gzip.decompress((out/('deep-'+read['name']+'.json.gz')).read_bytes()))
    M=f['map']; W,H=M['width'],M['height']; target=f['target']; ax,ay=target['lineHead']%W,target['lineHead']//W
    def unwrap(k):
        x,y=k%W,k//W
        return ax+((x-ax+W//2)%W-W//2), ay+((y-ay+H//2)%H-H//2)
    positions=[unwrap(p['k']) for p in target['drops']]+[unwrap(target['head']),unwrap(target['lineHead'])]
    xmin=min(x for x,y in positions)-3; xmax=max(x for x,y in positions)+3
    ymin=min(y for x,y in positions)-3; ymax=max(y for x,y in positions)+3
    cell=max(18,min(32,430//max(xmax-xmin+1,ymax-ymin+1)))
    cols,rows=xmax-xmin+1,ymax-ymin+1; pw=cols*cell+36; ph=rows*cell+178
    frames=f['frames']; before=next(x for x in frames if x['label']=='immediately before feeder death')
    after=next((x for x in frames if x['label']=='two rounds later'),frames[-1]); last=frames[-1]
    im=Image.new('RGB',(3*pw+24,ph),'#f5f7f9'); d=ImageDraw.Draw(im)
    p=f['pick']; d.text((14,10),f"{p['map']} | game {p['gameId']} | feeder #{p['id']} L{p['len']} -> line #{p['lineId']}",font=title,fill='#162536')
    d.text((14,39),'N=1 selected replay. Gold rings: this sacrifice drops. Blue: king line. Orange: feeder. Red: enemy.',font=ft,fill='#34485b')
    d.text((14,60),f"Static head distance {target['distance']}; receipts line/ally/enemy/uncollected = {target['toLine']}/{target['toAlly']}/{target['toEnemy']}/{target['none']}.",font=ft,fill='#34485b')
    def arr(a): return {int(k):v for k,v in a.items()} if isinstance(a,dict) else a
    he,ve=arr(M['initialHEdges']),arr(M['initialVEdges'])
    for n,s in enumerate([before,after,last]):
        ox=12+n*pw; oy=118
        d.text((ox,94),f"r{s['round']} | {s['label']}",font=ft,fill='#162536')
        pearls={v['k']:v for v in s['pearls']}; highlight={v['k'] for v in target['drops']}
        for yy in range(ymin,ymax+1):
            for xx in range(xmin,xmax+1):
                x,y=xx%W,yy%H; k=y*W+x;px=ox+(xx-xmin)*cell;py=oy+(yy-ymin)*cell
                d.rectangle((px,py,px+cell,py+cell),fill='#e6edf3',outline='#ccd6df')
                if k in highlight:d.ellipse((px+2,py+2,px+cell-2,py+cell-2),outline='#cfa227',width=2)
                if k in pearls:d.ellipse((px+cell*.35,py+cell*.35,px+cell*.65,py+cell*.65),fill='#ffdf66' if pearls[k]['origin']==target['idx'] else 'white',outline='#75838d')
        for dragon in s['bodies']:
            color='#ef983b' if dragon['id']==target['id'] else '#376cb6' if dragon['id']==s['lineId'] else '#ce6774' if dragon['team']!=p['team'] else '#90a69c'
            for i,k in reversed(list(enumerate(dragon['body']))):
                xx,yy=unwrap(k)
                if not(xmin<=xx<=xmax and ymin<=yy<=ymax):continue
                px=ox+(xx-xmin)*cell;py=oy+(yy-ymin)*cell
                d.rounded_rectangle((px+4,py+4,px+cell-4,py+cell-4),radius=4,fill=color,outline='#18384d' if i==0 else color,width=2)
                if i==0:d.text((px+5,py+cell*.3),str(dragon['id']),font=small,fill='white' if dragon['id']==s['lineId'] else '#142633')
        for yy in range(ymin,ymax+1):
            for xx in range(xmin,xmax+1):
                x,y=xx%W,yy%H;px=ox+(xx-xmin)*cell;py=oy+(yy-ymin)*cell
                if he[y*W+x]==1 or (y==0 and he[H*W+x]==1):d.line((px,py,px+cell,py),fill='#283b46',width=3)
                if ve[y*(W+1)+x]==1 or (x==0 and ve[y*(W+1)+W]==1):d.line((px,py,px,py+cell),fill='#283b46',width=3)
        for xx in range(xmin,xmax+1):d.text((ox+(xx-xmin)*cell+5,oy+rows*cell+5),str(xx%W),font=small,fill='#34485b')
        for yy in range(ymin,ymax+1):d.text((ox+cols*cell+4,oy+(yy-ymin)*cell+5),str(yy%H),font=small,fill='#34485b')
    filename='board-'+p['map'].replace(' ','_').replace('/','_')+'.png';im.save(out/filename);print(filename,im.size)
