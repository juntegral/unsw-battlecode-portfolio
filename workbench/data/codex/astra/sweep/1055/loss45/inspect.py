import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path(__file__).resolve().parent
for gid,qid,att,death in [(1509102,0,25,115),(1509107,1,159,191),(1509108,0,30,47)]:
 a=json.loads((OUT/f'{gid}-details.json').read_text());w=a['w'];h=a['h'];geo=Geo(w,h,a['edges']);xy=lambda c:(c%w,c//w)
 print('\nGAME',gid,'wh',w,h)
 for t in a['turns']:
  if (t['id'] in [qid,att] and death-4<=t['r']<=death) or (gid==1509107 and t['id']==170 and 194<=t['r']<=198):
   b=t['bodies'];head=b[str(t['id'])][0];occ={c:i for i,bb in b.items() for c in bb}
   print('TURN',t['r'],t['id'],'body',list(map(xy,b[str(t['id'])])),'action',t.get('action'),'steps',list(map(xy,t['steps'])),'eat',t['eats'],'split',t.get('split'))
   print('around',[(d,k,xy(dst),occ.get(dst),dst in t['pearls']) for d,(k,dst) in enumerate(geo.moves[head])])
   print('near bodies',[(i,list(map(xy,bb))) for i,bb in b.items() if min(abs(bb[0]%w-head%w),w-abs(bb[0]%w-head%w))<=5 and min(abs(bb[0]//w-head//w),h-abs(bb[0]//w-head//w))<=5])
 root=lr.replay.load(Path('data/online/smoke/one13-k1-old')/f'M{gid}.replay').root();rnd=-1;logs=[]
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==6 and death-4<=rnd<=death and p.i32(0)==qid:logs.append([rnd,p.i32(0),p.text(0)])
 print('LOGS',logs)
