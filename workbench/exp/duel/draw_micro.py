from verify import guard
import json,pathlib,math
from draw import PNG
O=pathlib.Path(__file__).resolve().parent
def main():
 guard()
 for spec in json.load(open(O/'boards.json')):
  guard()
  slug=spec['slug'];data=json.load(open(O/'boards'/(slug+'-micro.json')));frames=data['frames'];cols=3;pw=270;ph=300;cell=28;im=PNG(cols*pw+30,math.ceil(len(frames)/cols)*ph+80)
  im.text(15,15,'GAME '+str(data['game'])+' / DECISION VIEW',scale=2);im.text(15,40,'BLUE: A   RED: B   GOLD: PEARL   PINK: DROP',scale=1)
  for j,f in enumerate(frames):
   ox=15+j%cols*pw;oy=80+j//cols*ph;x0=ox+25;y0=oy+55
   im.text(ox,oy,f"R{f['r']} ID{f['id']} L{f['len']}",scale=2);im.text(ox,oy+25,f['team']+' '+f['when'],scale=2)
   for c in f['cells']:
    x=c['dx']+3;y=c['dy']+3;px=x0+x*cell;py=y0+y*cell;im.rect(px,py,cell-1,cell-1,(238,242,247))
    if c['team']:
     col=(39,91,171) if c['team']=='A' else (188,63,48)
     if c['head']:
      im.rect(px+2,py+2,cell-5,cell-5,col);im.text(px+8,py+7,str(c['len']) if c['len']<10 else '#',(255,255,255),scale=2)
     else:im.rect(px+3,py+3,cell-7,cell-7,(148,183,225) if c['team']=='A' else (232,180,171))
    if c['pearl']:im.circle(px+cell//2,py+cell//2,4,(208,76,145) if c['drop'] else (185,141,25))
    for side in ('north','west','south','east'):
     v=c.get(side,0)
     if v not in (1,2):continue
     col=(37,44,60) if v==1 else (172,38,185)
     if side=='north':im.rect(px,py-1,cell+1,3,col)
     elif side=='west':im.rect(px-1,py,3,cell+1,col)
     elif side=='south' and y==6:im.rect(px,py+cell-1,cell+1,3,col)
     elif side=='east' and x==6:im.rect(px+cell-1,py,3,cell+1,col)
    if y==0:im.text(px+5,y0-15,str(c['x']),scale=1)
    if x==0:im.text(x0-20,py+10,str(c['y']),scale=1)
  im.save(O/'boards'/(slug+'-micro.png'));print('MICRO',slug,len(frames))
if __name__=='__main__':main()
