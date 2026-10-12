import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
OUT=Path(__file__).resolve().parent
for gid in (1512561,1512562,1512563):
 d=json.loads((OUT/f'{gid}-details.json').read_text());base=json.loads((OUT/f'{gid}-scan.json').read_text());qid=base['queens']['us'];qd=next(x for x in base['deaths'] if x['id']==qid)
 attacker=qd['actor'] if qd['actor']!=qid else next(x['id'] for x in base['deaths'] if x['collision']==qd['collision'] and x['id']!=qid)
 w,h=d['W'],d['H']; raw=[tuple(map(int,l.split()[1:])) for l in base['text'].splitlines() if l.startswith('EDGE ')]; g=Geo(w,h,raw)
 print('\nGAME',gid,'attacker',attacker)
 for t in d['turns']:
  if t['id'] in (qid,attacker) and qd['round']-4<=t['round']<=qd['round']:
   print({k:v for k,v in t.items() if k not in ('board','pearls')})
   if 'board' not in t:continue
   x,y=t['body'][0];occ={tuple(c):(int(i),n) for i,body in t['board'].items() for n,c in enumerate(body)}
   print('neighbors',[(k,(dst%w,dst//w),occ.get((dst%w,dst//w))) for k,dst in g.moves[y*w+x]])
   for dy in range(-3,4):
    line=[]
    for dx in range(-3,4):
     xy=((x+dx)%w,(y+dy)%h);i,n=occ.get(xy,(-1,-1))
     sym='Q' if i==qid and n==0 else 'q' if i==qid else 'X' if i==attacker and n==0 else 'x' if i==attacker else ('A' if n==0 else 'a') if i>=0 and d['teams'][str(i)]==0 else ('E' if n==0 else 'e') if i>=0 else '*' if list(xy) in t['pearls'] else '.'
     line.append(sym)
    print(''.join(line))
   print('nearby',[(i,b[:6]) for i,b in t['board'].items() if min(abs(b[0][0]-x),w-abs(b[0][0]-x))<=3 and min(abs(b[0][1]-y),h-abs(b[0][1]-y))<=3])
 print('last deaths',[(x['id'],x['round'],x['length'],x['cause'],x['actor']) for x in base['deaths'] if x['side']=='us'][-8:])
