import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
out=Path(__file__).parent
font='/System/Library/Fonts/Supplemental/Arial.ttf'
ft=ImageFont.truetype(font,13); fs=ImageFont.truetype(font,10); title=ImageFont.truetype(font,17)
for board in json.loads((out/'boards.json').read_text()):
    M=board['initialMap']; M['initialHEdges']={int(k):v for k,v in M['initialHEdges'].items()} if isinstance(M['initialHEdges'],dict) else M['initialHEdges']; M['initialVEdges']={int(k):v for k,v in M['initialVEdges'].items()} if isinstance(M['initialVEdges'],dict) else M['initialVEdges']; W=M['width']; H=M['height']
    G=json.loads((out/('geometry-'+board['geometry']+'.json')).read_text()); P=G['pocketDetail'][board['pocket']]
    anchor=P['mouth'][0] if P['mouth'] else P['tiles'][0]; ax,ay=anchor%W,anchor//W
    def unwrap(k):
        x,y=k%W,k//W
        return ax+((x-ax+W//2)%W-W//2), ay+((y-ay+H//2)%H-H//2)
    positions=[unwrap(k) for k in P['tiles']+P['mouth']]
    xmin=min(p[0] for p in positions)-3; xmax=max(p[0] for p in positions)+3
    ymin=min(p[1] for p in positions)-3; ymax=max(p[1] for p in positions)+3
    cell=33; cols=xmax-xmin+1; rows=ymax-ymin+1; pw=cols*cell+40; ph=rows*cell+90
    im=Image.new('RGB',(3*pw+20,ph+75),'#f4f6f8'); d=ImageDraw.Draw(im)
    d.text((15,10),f"{board['map']} | replay {board['key']} | team {board['team']} | pocket {P['id']}",font=title,fill='#17212b')
    d.text((15,36),'Pink: pocket  Yellow marker: fountain  White: pearl  Blue ring: mouth  Orange: A  Cyan: B  Numbers: head ids',font=ft,fill='#38495a')
    for n,snap in enumerate(board['snapshots']):
        ox=15+n*pw; oy=100
        d.text((ox,72),f"r{snap['round']}  {snap['label']}",font=ft,fill='#17212b')
        pearls=set(snap['pearls']); pocket=set(P['tiles']); fountains=set(P['fountains'])
        for yy in range(ymin,ymax+1):
            for xx in range(xmin,xmax+1):
                x,y=xx%W,yy%H; k=y*W+x; px=ox+(xx-xmin)*cell; py=oy+(yy-ymin)*cell
                d.rectangle((px,py,px+cell,py+cell),fill='#f8dedf' if k in pocket else '#e6ebef',outline='#ccd4da')
                if k in fountains:d.rectangle((px+2,py+2,px+8,py+8),fill='#f2b705')
                if k in pearls:d.ellipse((px+12,py+12,px+22,py+22),fill='white',outline='#65717b',width=1)
                if k in P['mouth']:d.ellipse((px+3,py+3,px+cell-3,py+cell-3),outline='#415ee7',width=2)
        for dragon in snap['bodies']:
            color='#ef8f32' if dragon['team']=='A' else '#21b8c5'
            for i,k in reversed(list(enumerate(dragon['body']))):
                xx,yy=unwrap(k)
                if not(xmin<=xx<=xmax and ymin<=yy<=ymax):continue
                px=ox+(xx-xmin)*cell;py=oy+(yy-ymin)*cell
                d.rounded_rectangle((px+5,py+5,px+cell-5,py+cell-5),radius=5,fill=color,outline='#243342' if i==0 else color,width=2)
                if i==0:d.text((px+7,py+11),str(dragon['id']),font=fs,fill='#101820')
        for yy in range(ymin,ymax+1):
            for xx in range(xmin,xmax+1):
                x,y=xx%W,yy%H;px=ox+(xx-xmin)*cell;py=oy+(yy-ymin)*cell
                if M['initialHEdges'][y*W+x]==1 or (y==0 and M['initialHEdges'][H*W+x]==1):d.line((px,py,px+cell,py),fill='#26343d',width=4)
                if M['initialVEdges'][y*(W+1)+x]==1 or (x==0 and M['initialVEdges'][y*(W+1)+W]==1):d.line((px,py,px,py+cell),fill='#26343d',width=4)
        for xx in range(xmin,xmax+1):d.text((ox+(xx-xmin)*cell+9,oy+rows*cell+5),str(xx%W),font=fs,fill='#38495a')
        for yy in range(ymin,ymax+1):d.text((ox+cols*cell+4,oy+(yy-ymin)*cell+9),str(yy%H),font=fs,fill='#38495a')
        lengths=', '.join(f"#{x['id']} L{len(x['body'])}" for x in snap['bodies'] if any(k in pocket for k in x['body']))
        d.text((ox,oy+rows*cell+25),lengths[:80],font=fs,fill='#17212b')
    im.save(out/('board-'+board['name']+'.png'))
    print(board['name'],im.size)
