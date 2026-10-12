#!/usr/bin/env python3
# Dependency-free PNG board renderer. Data: deep.js snapshots from mass_ledger rules=123.
import json,struct,zlib,pathlib,os
OUT=pathlib.Path(__file__).resolve().parent
FONT={
'A':'01110 10001 10001 11111 10001 10001 10001','B':'11110 10001 10001 11110 10001 10001 11110','C':'01111 10000 10000 10000 10000 10000 01111','D':'11110 10001 10001 10001 10001 10001 11110','E':'11111 10000 10000 11110 10000 10000 11111','F':'11111 10000 10000 11110 10000 10000 10000','G':'01111 10000 10000 10111 10001 10001 01111','H':'10001 10001 10001 11111 10001 10001 10001','I':'11111 00100 00100 00100 00100 00100 11111','J':'00111 00010 00010 00010 10010 10010 01100','K':'10001 10010 10100 11000 10100 10010 10001','L':'10000 10000 10000 10000 10000 10000 11111','M':'10001 11011 10101 10101 10001 10001 10001','N':'10001 11001 10101 10011 10001 10001 10001','O':'01110 10001 10001 10001 10001 10001 01110','P':'11110 10001 10001 11110 10000 10000 10000','Q':'01110 10001 10001 10001 10101 10010 01101','R':'11110 10001 10001 11110 10100 10010 10001','S':'01111 10000 10000 01110 00001 00001 11110','T':'11111 00100 00100 00100 00100 00100 00100','U':'10001 10001 10001 10001 10001 10001 01110','V':'10001 10001 10001 10001 10001 10001 00100','W':'10001 10001 10001 10101 10101 10101 01010','X':'10001 10001 01010 00100 01010 10001 10001','Y':'10001 10001 01010 00100 00100 00100 00100','Z':'11111 00001 00010 00100 01000 10000 11111',
'0':'01110 10001 10011 10101 11001 10001 01110','1':'00100 01100 00100 00100 00100 00100 01110','2':'01110 10001 00001 00010 00100 01000 11111','3':'11110 00001 00001 01110 00001 00001 11110','4':'00010 00110 01010 10010 11111 00010 00010','5':'11111 10000 10000 11110 00001 00001 11110','6':'01110 10000 10000 11110 10001 10001 01110','7':'11111 00001 00010 00100 01000 01000 01000','8':'01110 10001 10001 01110 10001 10001 01110','9':'01110 10001 10001 01111 00001 00001 01110',
'#':'01010 01010 11111 01010 11111 01010 01010','-':'00000 00000 00000 11111 00000 00000 00000',':':'00000 00100 00100 00000 00100 00100 00000',',':'00000 00000 00000 00000 00100 00100 01000','/':'00001 00010 00010 00100 01000 01000 10000','=':'00000 00000 11111 00000 11111 00000 00000','(':'00010 00100 01000 01000 01000 00100 00010',')':'01000 00100 00010 00010 00010 00100 01000','+':'00000 00100 00100 11111 00100 00100 00000','.':'00000 00000 00000 00000 00000 00110 00110'}
def rgb(s):return bytes.fromhex(s.lstrip('#'))
class Canvas:
 def __init__(self,w,h):self.w=w;self.h=h;self.b=bytearray(rgb('#f6f8fa')*(w*h))
 def rect(self,x,y,w,h,col):
  x=int(x);y=int(y);w=int(w);h=int(h);x0=max(0,x);y0=max(0,y);x1=min(self.w,x+w);y1=min(self.h,y+h);r=rgb(col)*max(0,x1-x0)
  for yy in range(y0,y1):self.b[(yy*self.w+x0)*3:(yy*self.w+x1)*3]=r
 def line(self,x0,y0,x1,y1,col,width=1):
  x0,y0,x1,y1=map(int,[x0,y0,x1,y1]);dx=abs(x1-x0);dy=-abs(y1-y0);sx=1 if x0<x1 else -1;sy=1 if y0<y1 else -1;err=dx+dy
  while True:
   self.rect(x0-width//2,y0-width//2,width,width,col)
   if x0==x1 and y0==y1:break
   e2=2*err
   if e2>=dy:err+=dy;x0+=sx
   if e2<=dx:err+=dx;y0+=sy
 def text(self,x,y,s,col='#17212b',scale=1):
  for i,ch in enumerate(str(s).upper()):
   for yy,row in enumerate(FONT.get(ch,'00000 '*6+'00000').split()):
    for xx,v in enumerate(row):
     if v=='1':self.rect(x+i*6*scale+xx*scale,y+yy*scale,scale,scale,col)
 def save(self,f):
  def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
  scan=b''.join(b'\0'+self.b[y*self.w*3:(y+1)*self.w*3] for y in range(self.h))
  f.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',self.w,self.h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))
COL={'A':'#2778b9','B':'#df852a'}
def panel(C,g,s,ox,oy,queen,center=None,radius=8,cell=22,attacker=None):
 W,H=s['W'],s['H'];q=next((d for d in s['dragons'] if d['id']==queen),None)
 if center is None:center=q['body'][0] if q else next(v['death']['head'] for v in g['queens'].values() if v['id']==queen)
 cx,cy=center['x'],center['y'];n=2*radius+1;gx=ox+32;gy=oy+44
 C.text(ox+3,oy,f"R{s['round']} {s.get('stage','ROUND START')}",scale=1)
 C.text(ox+3,oy+15,f"Q#{queen} L{q['length'] if q else 0} CENTER {cx},{cy}",scale=1)
 pearls=set(s['pearls']);body={}
 for d in s['dragons']:
  for i,p in enumerate(d['body']):body[p['y']*W+p['x']]=(d,i)
 for j in range(n):
  y=(cy-radius+j)%H;C.text(ox+4,gy+j*cell+6,str(y),scale=1)
  for i in range(n):
   x=(cx-radius+i)%W;px=gx+i*cell;py=gy+j*cell;k=y*W+x
   C.rect(px,py,cell-1,cell-1,'#e6edf0')
   if j==0:C.text(px+3,gy-12,str(x),scale=1)
   if k in pearls:C.rect(px+cell//2-2,py+cell//2-2,5,5,'#46a048')
   if k in body:
    d,idx=body[k];color=COL[d['team']]
    if d['id']==queen:C.rect(px+2,py+2,cell-5,cell-5,'#9c338d');C.rect(px+5,py+5,cell-11,cell-11,color)
    else:C.rect(px+5,py+5,cell-11,cell-11,color)
    if idx==0:
     C.rect(px+2,py+2,cell-5,cell-5,color)
     if d['id']==queen or d['id']==attacker:
      border='#b3298a' if d['id']==queen else '#b92323'
      C.line(px+1,py+1,px+cell-3,py+1,border,2);C.line(px+1,py+1,px+1,py+cell-3,border,2);C.line(px+cell-3,py+1,px+cell-3,py+cell-3,border,2);C.line(px+1,py+cell-3,px+cell-3,py+cell-3,border,2)
     text=str(d['id']);C.text(px+(cell-len(text)*6)//2,py+7,text,col='#ffffff')
   he=s['initialHEdges'];ve=s['initialVEdges']
   if he[y*W+x]==1 or y==0 and he[H*W+x]==1:C.line(px,py,px+cell,py,'#22323e',2)
   if ve[y*(W+1)+x]==1 or x==0 and ve[y*(W+1)+W]==1:C.line(px,py,px,py+cell,'#22323e',2)
   if j==n-1 and (he[(y+1)*W+x]==1):C.line(px,py+cell,px+cell,py+cell,'#22323e',2)
   if i==n-1 and (ve[y*(W+1)+x+1]==1):C.line(px+cell,py,px+cell,py+cell,'#22323e',2)
   for pair in s.get('portals') or []:
    for e in pair:
     if e['x']==x and e['y']==y:
      dx,dy={'N':(cell//2,0),'S':(cell//2,cell),'W':(0,cell//2),'E':(cell,cell//2)}[e['side']];C.rect(px+dx-2,py+dy-2,5,5,'#8036ab')
def triptych(name,queen,picks,center=None,attacker=None,title=None):
 g=json.loads((OUT/(name+'.json')).read_text());p=[]
 for r,stage in picks:p.append(next(s for s in g['snapshots'] if s['round']==r and (stage is None or s.get('stage','')==stage)))
 C=Canvas(1250,500);C.text(14,13,title or name,scale=2);C.text(14,36,'A BLUE / B ORANGE / QUEEN MAGENTA / PEARL GREEN / KELP DARK / PORTAL PURPLE',scale=1)
 for i,s in enumerate(p):panel(C,g,s,12+i*415,62,queen,center,attacker=attacker)
 C.save(OUT/(name+'.png'))
stat=os.statvfs(OUT)
if stat.f_bavail*stat.f_frsize<21*1024**3:raise RuntimeError('PAUSE disk')
triptych('game-815244',1,[(300,'round start'),(450,'round start'),(499,'round start')],title='815244 STOCKFISH / DEFAULT / GROWING QUEEN')
triptych('game-815352',1,[(400,'round start'),(450,'round start'),(499,'round start')],title='815352 YUECI LI / TRAUMA / DISTANT ENEMIES')
triptych('game-814547',0,[(300,'round start'),(400,'round start'),(499,'round start')],center={'x':19,'y':13},title='814547 FANDAGONG / SCHOOLTIME / L2 LOOP')
triptych('game-815034',1,[(308,'round start'),(308,'before attacker #726'),(309,'round start')],center={'x':35,'y':2},attacker=726,title='815034 / NEWBORN #726 NWW HITS L21 QUEEN')
triptych('game-814624',1,[(338,'round start'),(339,'before attacker #650'),(340,'round start')],center={'x':6,'y':6},attacker=650,title='814624 / #650 EE HITS TONY S L8 QUEEN')
triptych('game-814724',1,[(116,'round start'),(117,'before attacker #28'),(118,'round start')],center={'x':16,'y':2},attacker=28,title='814724 / REPEATING LOOP #28 AND QUEEN ARRIVAL')
triptych('exp-v16-q1-q1-sprint2-proxy4_king-australia-B-1',1,[(400,'round start'),(413,'round start'),(414,'round start')],center={'x':35,'y':36},title='Q1 AUSTRALIA B / L19 ESCAPE-SPLIT AND TRAP')
triptych('exp-q2-cand2d-hunter-bot-hunter-islands-B-1',1,[(207,'round start'),(208,'before attacker #106'),(209,'round start')],center={'x':10,'y':5},attacker=106,title='Q2 ISLANDS B / #106 NWW HITS L44 QUEEN')
# All six survivors at round start 499, one compact plate.
C=Canvas(860,1435);C.text(14,12,'ALL SIX R500 SURVIVORS / R499 BOARDS',scale=2);C.text(14,35,'HEAD IDS SHOWN. MAGENTA MARKS THE QUEEN BODY. COORDINATES WRAP.',scale=1)
for i,(gid,qid) in enumerate([(815244,1),(815352,1),(814623,0),(814625,0),(814627,0),(814547,0)]):
 g=json.loads((OUT/f'game-{gid}.json').read_text());s=next(s for s in g['snapshots'] if s['round']==499);x=10+(i%2)*425;y=68+(i//2)*455;C.text(x,y-14,str(gid),scale=1);panel(C,g,s,x,y,qid)
C.save(OUT/'survivors.png')
print('wrote 9 PNG board pictures')
