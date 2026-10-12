import pathlib,sys,json,re
ROOT=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'exp/duel'))
from draw import PNG
def render(slug,title=None):
 text=(O/(slug+'.txt')).read_text();M=json.load(open(O/(slug+'-map.json')));W=M['width'];H=M['height'];maps={k:{str(i):v for i,v in enumerate(M[k])}if isinstance(M[k],list)else M[k]for k in ['initialHEdges','initialVEdges']}
 matches=re.findall(r'--- r(\d+): ours (\d+).*?total (\d+) \| theirs (\d+).*?total (\d+)\n\+[-]+\+\n((?:\|.*?\|\n)+)',text)
 if not matches:raise ValueError('No board snapshots '+slug)
 cell=max(12,min(22,900//W));pw=W*cell+55;ph=H*cell+60;cols=2 if len(matches)>1 else 1
 im=PNG(pw*cols+30,ph*((len(matches)+cols-1)//cols)+102);tf=O/(slug+'-turn.json');turn=json.load(open(tf))if tf.exists()else None
 im.text(20,14,title or (f"GAME {turn['game']} {turn['map']} TEAM {turn['team']} ID {turn['id']}"if turn else slug),scale=2);im.text(20,39,'BLUE: OBSERVED TEAM  RED: OPPONENT  GOLD: NATURAL PEARL  PINK: DROP',scale=1)
 im.text(20,56,'BLACK EDGES: KELP  PURPLE: PORTAL  HEAD NUMBER = LENGTH CAPPED 10+',scale=1)
 for j,m in enumerate(matches):
  ox=20+(j%cols)*pw;oy=90+(j//cols)*ph;stage=('BEFORE'if j==0 else 'AFTER')+' 'if turn else '';im.text(ox,oy,f'{stage}R{m[0]} HEADS {m[1]} MASS {m[2]} / ENEMY HEADS {m[3]} MASS {m[4]}',scale=1);x0=ox+20;y0=oy+24;grid=[line[1:-1]for line in m[5].splitlines()]
  for y in range(H):
   for x in range(W):
    px=x0+x*cell;py=y0+y*cell;v=grid[y][x];im.rect(px,py,cell-1,cell-1,(239,242,247))
    if v in '.x':im.rect(px+2,py+2,cell-5,cell-5,(153,185,226)if v=='.'else(235,183,171))
    elif v in '123456789#XK':
     im.rect(px+2,py+2,cell-5,cell-5,(35,92,177)if v in '123456789#'else(187,66,49));im.text(px+max(3,cell//2-3),py+max(3,cell//2-4),v,(255,255,255),scale=1)
    elif v in 'o%':im.circle(px+cell//2,py+cell//2,max(2,cell//5),(185,143,25)if v=='o'else(213,74,145))
  for y in range(H+1):
   for x in range(W):
    if maps['initialHEdges'].get(str(y*W+x))==1:im.rect(x0+x*cell,y0+y*cell-1,cell+1,3,(39,49,64))
  for y in range(H):
   for x in range(W+1):
    if maps['initialVEdges'].get(str(y*(W+1)+x))==1:im.rect(x0+x*cell-1,y0+y*cell,3,cell+1,(39,49,64))
  for pair in M['portals']:
   for edge in pair:
    x=edge['x']+(edge['side']=='E');y=edge['y']+(edge['side']=='S')
    if edge['side']in['N','S']:im.rect(x0+x*cell,y0+y*cell-1,cell,3,(174,42,188))
    else:im.rect(x0+x*cell-1,y0+y*cell,3,cell,(174,42,188))
  if turn and j<len(turn['snapshots'])and turn['snapshots'][j].get('actor'):
   x,y=turn['snapshots'][j]['actor']['head'];px=x0+x*cell;py=y0+y*cell;col=(237,156,20)
   im.rect(px-1,py-1,cell+1,2,col);im.rect(px-1,py+cell-2,cell+1,2,col);im.rect(px-1,py-1,2,cell+1,col);im.rect(px+cell-2,py-1,2,cell+1,col)
  for x in range(W):
   if x%2==0:im.text(x0+x*cell+3,y0-11,str(x),scale=1)
  for y in range(H):
   if y%2==0:im.text(x0-18,y0+y*cell+3,str(y),scale=1)
 im.save(O/(slug+'.png'));return {'slug':slug,'png':str(O/(slug+'.png')),'width':im.w,'height':im.h,'snapshotN':len(matches)}
if __name__=='__main__':
 for slug in sys.argv[1:]:print(render(slug))
