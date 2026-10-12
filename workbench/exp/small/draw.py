"""Dependency-free PNG rendering of eval/board.js ASCII snapshots, with replay walls."""
import json,pathlib,re,struct,zlib
O=pathlib.Path(__file__).resolve().parent
FONT={
'0':['01110','10001','10011','10101','11001','10001','01110'],'1':['00100','01100','00100','00100','00100','00100','01110'],'2':['01110','10001','00001','00010','00100','01000','11111'],'3':['11110','00001','00001','01110','00001','00001','11110'],'4':['00010','00110','01010','10010','11111','00010','00010'],'5':['11111','10000','10000','11110','00001','00001','11110'],'6':['01110','10000','10000','11110','10001','10001','01110'],'7':['11111','00001','00010','00100','01000','01000','01000'],'8':['01110','10001','10001','01110','10001','10001','01110'],'9':['01110','10001','10001','01111','00001','00001','01110'],
'A':['01110','10001','10001','11111','10001','10001','10001'],'B':['11110','10001','10001','11110','10001','10001','11110'],'C':['01111','10000','10000','10000','10000','10000','01111'],'D':['11110','10001','10001','10001','10001','10001','11110'],'E':['11111','10000','10000','11110','10000','10000','11111'],'F':['11111','10000','10000','11110','10000','10000','10000'],'G':['01111','10000','10000','10111','10001','10001','01111'],'H':['10001','10001','10001','11111','10001','10001','10001'],'I':['01110','00100','00100','00100','00100','00100','01110'],'J':['00001','00001','00001','00001','10001','10001','01110'],'K':['10001','10010','10100','11000','10100','10010','10001'],'L':['10000','10000','10000','10000','10000','10000','11111'],'M':['10001','11011','10101','10101','10001','10001','10001'],'N':['10001','11001','10101','10011','10001','10001','10001'],'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000'],'Q':['01110','10001','10001','10001','10101','10010','01101'],'R':['11110','10001','10001','11110','10100','10010','10001'],'S':['01111','10000','10000','01110','00001','00001','11110'],'T':['11111','00100','00100','00100','00100','00100','00100'],'U':['10001','10001','10001','10001','10001','10001','01110'],'V':['10001','10001','10001','10001','10001','01010','00100'],'W':['10001','10001','10001','10101','10101','11011','10001'],'X':['10001','10001','01010','00100','01010','10001','10001'],'Y':['10001','10001','01010','00100','00100','00100','00100'],'Z':['11111','00001','00010','00100','01000','10000','11111'],
' ':['00000']*7,'/':['00001','00001','00010','00100','01000','10000','10000'],':':['00000','00100','00100','00000','00100','00100','00000'],'-':['00000','00000','00000','11111','00000','00000','00000'],'+':['00000','00100','00100','11111','00100','00100','00000'],'#':['01010','11111','01010','01010','11111','01010','00000'],'.':['00000','00000','00000','00000','00000','00100','00100'],'%':['11001','11010','00100','01000','10110','00110','00000']}
class PNG:
 def __init__(self,w,h):self.w=w;self.h=h;self.a=bytearray([250,251,253])*(w*h)
 def rect(self,x,y,w,h,c):
  for yy in range(max(0,y),min(self.h,y+h)):
   x0=max(0,x);x1=min(self.w,x+w)
   if x1>x0:self.a[(yy*self.w+x0)*3:(yy*self.w+x1)*3]=bytes(c)*(x1-x0)
 def text(self,x,y,s,c=(36,45,61),scale=2):
  for ch in s.upper():
   f=FONT.get(ch,FONT[' '])
   for yy,row in enumerate(f):
    for xx,v in enumerate(row):
     if v=='1':self.rect(x+xx*scale,y+yy*scale,scale,scale,c)
   x+=6*scale
 def circle(self,x,y,rad,c):
  for yy in range(-rad,rad+1):
   ww=int((rad*rad-yy*yy)**.5);self.rect(x-ww,y+yy,ww*2+1,1,c)
 def save(self,p):
  def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v)&0xffffffff)
  raw=b''.join(b'\0'+self.a[y*self.w*3:(y+1)*self.w*3] for y in range(self.h))
  p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',self.w,self.h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
for s in json.load(open(O/'boards.json')):
 text=(O/('board-'+s['name']+'.txt')).read_text();matches=list(re.finditer(r'^--- r(\d+): ours (\d+) dragons.*?\| theirs (\d+).*?\n\+-+\+\n((?:\|[^\n]*\|\n)+)\+-+\+',text,re.M));maps=json.load(open(O/('board-map-'+s['name']+'.json')));W=maps['width'];H=maps['height'];cell=24;pw=W*cell+64;ph=H*cell+105;im=PNG(pw*2+30,ph*((len(matches)+1)//2)+105)
 im.text(24,18,s['name'].replace('_',' ')+' / OUR TEAM '+s['tm'],scale=2)
 im.text(24,45,'BLUE: OURS  RED: ENEMY  GOLD: PEARL  PINK: DROP',scale=1)
 im.text(24,64,'DARK EDGES: KELP  MAGENTA: PORTAL  # / K: LENGTH 10+',scale=1)
 for j,m in enumerate(matches):
  ox=24+(j%2)*pw;oy=102+(j//2)*ph;im.text(ox,oy,f'R{m[1]}  OUR {m[2]} / ENEMY {m[3]}',scale=2);x0=ox+23;y0=oy+33;grid=[line[1:-1] for line in m[4].splitlines()]
  for y in range(H):
   for x in range(W):
    px=x0+x*cell;py=y0+y*cell;v=grid[y][x];im.rect(px,py,cell-1,cell-1,(239,242,247));
    if v in '.x':im.rect(px+2,py+2,cell-5,cell-5,(153,185,226) if v=='.' else (235,183,171))
    elif v in '123456789#XK':
     col=(35,92,177) if v in '123456789#' else (187,66,49);im.rect(px+2,py+2,cell-5,cell-5,col);im.text(px+7,py+5,v,(255,255,255),scale=2)
    elif v in 'o%':im.circle(px+cell//2,py+cell//2,4,(185,143,25) if v=='o' else (213,74,145))
  for y in range(H+1):
   for x in range(W):
    if maps['initialHEdges'][str(y*W+x)]==1:im.rect(x0+x*cell,y0+y*cell-1,cell+1,3,(39,49,64))
  for y in range(H):
   for x in range(W+1):
    if maps['initialVEdges'][str(y*(W+1)+x)]==1:im.rect(x0+x*cell-1,y0+y*cell,3,cell+1,(39,49,64))
  for pair in maps['portals']:
   for edge in pair:
    x=edge['x'];y=edge['y'];side=edge['side'];x+=side=='E';y+=side=='S'
    if side in ['N','S']:im.rect(x0+x*cell,y0+y*cell-1,cell,3,(174,42,188))
    else:im.rect(x0+x*cell-1,y0+y*cell,3,cell,(174,42,188))
  for x in range(W):im.text(x0+x*cell+3,y0-13,str(x),scale=1)
  for y in range(H):im.text(x0-20,y0+y*cell+8,str(y),scale=1)
 im.save(O/('board-'+s['name']+'.png'))
 print('PNG',s['name'],im.w,im.h,len(matches))
