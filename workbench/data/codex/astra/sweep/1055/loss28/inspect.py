import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier')
from count_dossier import Geo
P=Path(__file__).resolve().parent
for gid in (1507915,1507916,1507917):
 g=json.loads((P/f'detail-{gid}.json').read_text());w,h=g['w'],g['h'];geo=Geo(w,h,g['edges']);q=g['queens'][0];xy=lambda c:(c%w,c//w)
 print('\nGAME',gid,w,h)
 for t in [t for t in g['queen_turns'] if t['id']==q][-3:]:
  hd=t['body'][0];occ={c:int(i) for i,b in t['bodies'].items() for c in b};print('TURN',t['r'],xy(hd),'len',len(t['body']),'act',t['action'])
  for d,(kind,dst) in enumerate(geo.moves[hd]):print('NESW'[d],kind,xy(dst),'owner',occ.get(dst),'pearl',dst in t['pearls'])
  for i,b in t['bodies'].items():
   if g['teams'][i]!=0 and geo.visible(hd,b[0]):print('ENEMY',i,'len',len(b),'head',xy(b[0]),'d',geo.distances(hd)[b[0]])
 d=next(d for d in g['deaths'] if d['id']==q)
 print('DEATH',d['r'],d['reason'],d['actor'],'ACTOR',d['turn']['id'],[xy(c) for c in d['turn']['body']],d['turn']['action'],'steps',[xy(c) for c in d['turn']['steps']])
 print('CORRELATED',[{k:v for k,v in x.items() if k!='turn'} for x in g['deaths'] if x['r']==d['r'] and x['actor']==d['actor']])
 print('NEAR',[(t['r'],t['id'],t['eq']['d'],len(t['body']),xy(t['body'][0]),xy(t['eq']['head']),t['eq']['visible'],t['action'],[xy(c) for c in t['steps']]) for t in g['near'][:6]])
 print('LAST NONLOSS Q',max((int(r) for r,s in g['snapshots'].items() if s[0]['queen']>=s[1]['queen']),default=None))
 print('TOTAL LAST NONLOSS',max((int(r) for r,s in g['snapshots'].items() if s[0]['total']>=s[1]['total']),default=None))
