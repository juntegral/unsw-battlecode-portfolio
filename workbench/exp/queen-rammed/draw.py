import json,copy,pathlib
from canvas import Canvas
OUT=pathlib.Path(__file__).resolve().parent
scenes=json.loads((OUT/'scenes.json').read_text())
A=json.loads((OUT/'main-analysis.json').read_text())
colors={'A':'#327bb3','B':'#e19a47'}
def idx(a,k):return a.get(str(k),0) if isinstance(a,dict) else a[k]
def panel(C,M,s,ox,oy,Q,center,title,radius=4,cell=40,killer=None,route=None,view=False,cycle=None):
 W,H=M['width'],M['height'];cx,cy=center;gx=ox+40;gy=oy+76;n=2*radius+1
 C.text(ox+8,oy,title,scale=2)
 q=next(d for d in s['dragons'] if d['id']==Q)
 C.text(ox+8,oy+26,f'Q#{Q} L{len(q["body"])} HEAD {q["body"][0]["x"]},{q["body"][0]["y"]}',scale=2)
 bodies={(p['x'],p['y']):(d,j) for d in s['dragons'] for j,p in enumerate(d['body'])}
 def xy(p):
  dx=(p['x']-cx+W//2)%W-W//2;dy=(p['y']-cy+H//2)%H-H//2
  return gx+(dx+radius+.5)*cell,gy+(dy+radius+.5)*cell
 for j in range(n):
  y=(cy-radius+j)%H;C.text(ox+7,gy+j*cell+cell//2-7,str(y),scale=2)
  for i in range(n):
   x=(cx-radius+i)%W;px=gx+i*cell;py=gy+j*cell
   C.rect(px,py,cell-1,cell-1,'#eaf0f4')
   if view and abs(i-radius)<=3 and abs(j-radius)<=3:C.rect(px+1,py+1,cell-2,cell-2,'#d8e8ed')
   if j==0:C.text(px+cell//2-8,gy-24,str(x),scale=2)
   if y*W+x in s['pearls']:C.rect(px+cell//2-3,py+cell//2-3,7,7,'#299348')
   if (x,y) in bodies:
    d,b=bodies[x,y];col=colors[d['team']];C.rect(px+5,py+5,cell-10,cell-10,col)
    if d['id']==Q:C.rect(px+2,py+2,cell-4,cell-4,'#a72d83');C.rect(px+6,py+6,cell-12,cell-12,'#d985ba' if b else '#9e267b')
    if b==0:
     C.rect(px+4,py+4,cell-8,cell-8,'#9e267b' if d['id']==Q else '#ce3d3d' if d['id']==killer else col)
     text=str(d['id']);scale=2 if len(text)<=2 else 1;C.text(px+(cell-len(text)*6*scale)//2,py+cell//2-4*scale,text,col='#ffffff',scale=scale)
   he=M['initialHEdges'];ve=M['initialVEdges']
   if idx(he,y*W+x)==1 or y==0 and idx(he,H*W+x)==1:C.line(px,py,px+cell,py,'#243746',4)
   if idx(ve,y*(W+1)+x)==1 or x==0 and idx(ve,y*(W+1)+W)==1:C.line(px,py,px,py+cell,'#243746',4)
   if j==n-1 and idx(he,(y+1)*W+x)==1:C.line(px,py+cell,px+cell,py+cell,'#243746',4)
   if i==n-1 and idx(ve,y*(W+1)+x+1)==1:C.line(px+cell,py,px+cell,py+cell,'#243746',4)
   for pair in M.get('portals',[]):
    for e in pair:
     if e['x']==x and e['y']==y:
      xx,yy={'N':(cell//2,0),'S':(cell//2,cell),'W':(0,cell//2),'E':(cell,cell//2)}[e['side']];C.rect(px+xx-4,py+yy-4,9,9,'#793bb0')
 if cycle:
  pp=cycle['coordinates']+[cycle['coordinates'][0]]
  for a,b in zip(pp,pp[1:]):
   ax,ay=xy(a);bx,by=xy(b)
   if abs(ax-bx)<=cell and abs(ay-by)<=cell:C.line(ax,ay,bx,by,'#29937d',2)
 if route:
  pp,col=route
  for a,b in zip(pp,pp[1:]):
   ax,ay=xy(a);bx,by=xy(b)
   if abs(ax-bx)<=cell and abs(ay-by)<=cell:C.line(ax+9,ay+9,bx+9,by+9,col,3)
  for p in pp[1:]:
   x,y=xy(p);C.rect(x+6,y+6,7,7,col)
 if view:
  x=gx+(radius-3)*cell;y=gy+(radius-3)*cell
  C.line(x,y,x+7*cell,y,'#548b9c',2);C.line(x,y,x,y+7*cell,'#548b9c',2);C.line(x+7*cell,y,x+7*cell,y+7*cell,'#548b9c',2);C.line(x,y+7*cell,x+7*cell,y+7*cell,'#548b9c',2)
def canvas(title,width=1510):
 C=Canvas(width,690);C.rect(0,0,width,690,'#ffffff');C.text(24,20,title,scale=3);C.text(24,53,'QUEEN MAGENTA / ALLIES BY TEAM / HUNTER RED / KELP DARK / PEARLS GREEN',scale=2);return C
s=scenes[0];M=s['map'];C=canvas('1. AROUND UNSW B - CYCLE LOST TO OUR BODIES')
for i,r in enumerate([4,5,6]):
 t=next(t for t in s['queenTurns'] if t['round']==r);panel(C,M,t['state'],15+i*500,98,s['Q'],(42,21),f'R{r} QUEEN TURN',radius=3,cell=55,cycle=t['room']['cycle'])
 C.text(55+i*500,577,f'FREE EXITS {len(t["room"]["freeFirstSteps"])} / CYCLE {t["room"]["cycle"]["C"] if t["room"]["cycle"] else 0}',scale=2)
C.text(24,628,'R4: Q1 S, THEN #9 N TO 42,22. R5: Q1 SPLIT2. R6: NO EXIT, WALL DEATH.',scale=2)
C.save(OUT/'board-1-own-box.png')
s=scenes[1];raw=json.loads((OUT/'raw/g0013.json').read_text());rd=raw['game']['death'];d=next(d for d in A['deaths'] if d['id']=='g0013');C=canvas('2. BIG EMPTY A - OUTSIDE VIEW HUNTER',1120)
for i,(state,title) in enumerate([(rd['lastQueenTurn'],'R258 BEFORE Q MOVE'),(rd['killerTurnState'],'R258 BEFORE HUNTER')]):
 route=[d['killer']['headAtOwnTurn']]+[p['point'] for p in d['killer']['actualPath']]
 panel(C,s['map'],state,15+i*550,98,0,(24,0),title,radius=5,cell=39,killer=33,route=(route,'#b82828'),view=True,cycle=d['lastTurnRoom']['cycle'] if i==0 else None)
C.text(24,630,'Q15 C18 F4. HUNTER #33 L22 F6 M26: SSS. BLUE BOX IS THE 7X7 VIEW.',scale=2)
C.save(OUT/'board-2-outside-hunter.png')
s=scenes[2];raw=json.loads((OUT/'raw/g0056.json').read_text());rd=raw['game']['death'];d=next(d for d in A['deaths'] if d['id']=='g0056');C=canvas('3. DEFAULT B - FREE ESCAPE EXISTS BEFORE CONTACT')
start=rd['lastQueenTurn'];hyp=copy.deepcopy(start);q=next(x for x in hyp['dragons'] if x['id']==1);route=[dict(q['body'][0])];pearls=set(hyp['pearls']);W=s['map']['width']
for _ in range(4):
 n={'x':(q['body'][0]['x']+1)%W,'y':q['body'][0]['y']};route.append(n);q['body'].insert(0,n)
 if n['y']*W+n['x'] not in pearls:q['body'].pop()
 pearls.discard(n['y']*W+n['x'])
hyp['pearls']=list(pearls)
actual=[d['killer']['headAtOwnTurn']]+[p['point'] for p in d['killer']['actualPath']]
for i,(state,title) in enumerate([(start,'R315 QUEEN TURN'),(rd['afterQueenAction'],'ACTUAL E - EXPOSED'),(hyp,'HYPOTHETICAL EEEE')]):
 panel(C,s['map'],state,15+i*500,98,1,(26,29),title,radius=4,cell=43,killer=48,route=(route,'#1b9776') if i==2 else (actual,'#b82828'))
C.text(24,630,'Q19 F5. EEEE IS LEGAL AND FREE. #48 L3 F1 M2 CAN KILL ACTUAL E WITH SW.',scale=2)
C.save(OUT/'board-3-free-escape.png')
print('wrote three replay board PNGs')
