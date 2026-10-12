import sys,json,statistics
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summarize import *
assert len(D)==8 and all(len(v)==15 for v in D.values())
whq=['one'+v+'-w1' for v in '2345'];dev=['one'+v+'-d1' for v in '1345']
rows=[]
for ks in (whq,dev):
 for k in ks:
  z=summ(D[k]); rows.append([k,z['n'],f"{z['qmean']:.2f}",z['fe'],f"{z['alone']}/{z['turns']} ({z['alone_pct']:.1f}%)",f"{z['p300']:.1f}"])

def table(headers,rows):return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def permap(ks):
 out=[]
 for m in sorted(G[ks[0]],key=lambda m:G[ks[0]][m]['map_id']):
  row=[m]
  for k in ks:
   g=G[k][m];row.append(f"{g['game']}: {g['queen_pearls']} / {g['death']['round'] if g['death'] else '생존@'+str(g['last'])} / {g['feeder_eat']}")
  out.append(row)
 return table(['[M] 지도; 경기: Q / 사망 r / FE']+[k for k in ks],out)

cmp=compare('one3-w1','one4-w1','one5-w1');cmpd=compare('one3-d1','one4-d1','one5-d1')
comp=[]
for s,c in [('WHQ',cmp),('dev',cmpd)]:
 for key,name in [('q','여왕 섭취↓'),('feed','FE↓'),('alone','고립률↑'),('p300','팀 섭취 r300↓')]:
  x=c[key];comp.append([s,name,len(x['worse']),len(x['better']),x['eligible'],', '.join(x['worse']) or '없음'])
check=[]
for m in sorted(G['one3-w1'],key=lambda m:G['one3-w1'][m]['map_id']):
 for r in (12,30,60,100):
  row=[m,r]
  for v in '35':
   q=G['one'+v+'-w1'][m]['snaps'][str(r)]['queen']
   if not q['alive']:txt=f"사망; Q={q['pearls']}"
   else:txt=f"{','.join(map(str,q['head']))}; {q['nearest_mate']}/{q['mates5']}; {q['pearls']}/{q['length']}; {q['pearl_path'] if q['pearl_path'] is not None else '∞'}"
   row.append(txt)
  check.append(row)

bands=[]
for k in whq+dev:
 counts=Counter()
 for g in D[k]:
  for e in g['eats']:
   if e['queen']:counts['early' if e['round']<=100 else 'mid' if e['round']<=300 else 'late']+=1
 bands.append([k,counts['early'],counts['mid'],counts['late']])

paired=[]
for s in ('w1','d1'):
 for r in (12,30,60,100):
  pairs=[(G['one3-'+s][m]['snaps'][str(r)]['queen'],G['one5-'+s][m]['snaps'][str(r)]['queen']) for m in G['one3-'+s]]
  pairs=[(a,b) for a,b in pairs if a['alive'] and b['alive']]
  z=[s,r,len(pairs)]
  for key in ('nearest_mate','mates5','pearls','length'):
   z.append(' / '.join(f'{statistics.mean(p[i][key] for p in pairs if p[i][key] is not None):.2f}' + (f'(∞{sum(p[i][key] is None for p in pairs)})' if any(p[i][key] is None for p in pairs) else '') for i in (0,1)))
  z.append(sum(a['mates5']>0 and b['mates5']==0 for a,b in pairs));z.append(sum(a['mates5']==0 and b['mates5']>0 for a,b in pairs));paired.append(z)

extras={}
for s in ('w1','d1'):
 a,b=G['one3-'+s],G['one5-'+s]
 extras[s]=dict(same_full_map_text=sum(a[m]['map_hash']==b[m]['map_hash'] for m in a),same_api_team_side=sum(a[m]['own']==b[m]['own'] for m in a),
                same_unaligned_natural_births_to30=sum(a[m]['births']==b[m]['births'] for m in a),
                same_unaligned_actions_to11=sum([x for x in a[m]['actions'] if x[0]<=11]==[x for x in b[m]['actions'] if x[0]<=11] for m in a))

def competition(g):return sum(e['side']==0 and not e['queen'] and e['queen_adjacent'] for e in g['eats'] if e['round']<=100)
extra_tables=[]
for k in whq+dev:
 extra_tables.append([k,sum(competition(g) for g in D[k]),sum(e['side']==0 and not e['queen'] and e['queen_distance'] is not None and e['queen_distance']<=e['actor_distance'] for g in D[k] for e in g['eats'] if e['round']<=100)])

OUT.joinpath('summary.json').write_text(json.dumps(dict(aggregates={k:summ(v) for k,v in D.items()},whq=cmp,dev=cmpd,paired=paired,bands=bands,provenance=extras,competition=extra_tables),ensure_ascii=False,indent=2))
OUT.joinpath('tables.md').write_text('\n\n'.join([
 table(['[M] 라벨','판','Q/판','FE 합계','고립 턴/생존 턴 r51–300','팀 진주/판 ≤r300'],rows),
 permap(whq),permap(dev),
 table(['[M] 표본','one3 대비 방향','one4·5 모두 해당','둘 다 반대','비교 가능 지도','해당 지도'],comp),
 table(['[M] 라벨','Q ≤r100','Q r101–300','Q r301+'],bands),
 table(['[M] 표본','r','양쪽 생존 지도','최근접 아군 거리 3/5','5칸 내 아군 3/5','Q 3/5','길이 3/5','유→무','무→유'],paired),
 table(['[M] 라벨','r0–100 아군이 여왕 인접 진주 섭취','아군 섭취 중 여왕 거리≤섭취자 거리'],extra_tables),
 table(['[M] 지도','r 종료','one3: 위치; 거리/아군수; Q/L; 진주 경로거리','one5: 동일'],check)
])+'\n')
print(json.dumps(json.loads(OUT.joinpath('summary.json').read_text()),ensure_ascii=False,indent=2))
