import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path('data/codex/astra/kraken')
games=[json.loads(p.read_text()) for p in OUT.glob('M*.json')]
ranked=[g for g in games if g['ledger']['src'].startswith('b')]
f=open(OUT/'verification.txt','w')
for g in ranked:
 d,l=g['detail'],g['ledger'];q=d['queens'][0]
 death=next((x for x in d['deaths'] if x['id']==q),None)
 if not death:continue
 r=death['r'];root=lr.replay.load(Path('data/online/live-one1')/l['src']/f"M{l['gid']}.replay").root()
 present={};rnd=-1;actor=None;pearlbefore={};eats=[]
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==1:
   actor=p.i32(0)
   if actor==q and r-3<=rnd<=r:pearlbefore[rnd]=list(present)
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):present[c]=(rnd,actor)
   else:
    if rnd==r and actor==death['actor']:eats.append((c,present[c]))
    del present[c]
 print(l['gid'],l['map'],'q death',r,'attacker',death['actor'],'eats (xy, spawned round/actor)',eats,file=f)
 if death['actor']!=q:
  t=d['qt'][0][-1];x,y=t['body'][0];w,h=d['w'],d['h']
  def visible(c):return min(abs(c[0]-x),w-abs(c[0]-x))<=3 and min(abs(c[1]-y),h-abs(c[1]-y))<=3
  before=pearlbefore[t['r']]
  print('pearls existed and visible at q turn',[(c,c in before,visible(c)) for c,_ in eats],file=f)
 print('final turns',l['last'],'q length reductions',[(t['r'],t['L'],len(t['end']),t['dirs']) for t in d['qt'][0] if t['end'] and len(t['end'])<t['L']],file=f)
f.close()

sys.path.insert(0,str(OUT))
import summarize as s
shared=set.intersection(*[{g['ledger']['map'] for g in games if g['ledger']['src']==label} for label in ('one7-w1-old','one7-c1-old','one8-w1-old')])
groups={}
for label in ('one7-w1-old','one7-c1-old','one8-w1-old'):
 groups[label]=s.stats([g for g in games if g['ledger']['src']==label and g['ledger']['map'] in shared])
# One ranked sample per shared map; one7 maps matched to one7, one8 maps to one8 when possible.
groups['kraken7']=s.stats([g for g in ranked if g['ledger']['map'] in shared and g['ledger']['gid']!=1483343])
(OUT/'matched.json').write_text(json.dumps(groups,indent=2))
with open(OUT/'matched.md','w') as f:
 print('[M] 공통 7지도: '+', '.join(sorted(shared))+'. kraken Maze는 one7 M1482057만 포함; 버전/진영/시드는 통제하지 않음.\n',file=f)
 print('|상대 표본|r0–30 분열|진주|첫 진주 r 중앙값|방문 머리칸/판|r30 머리/판|능동 램|2걸음 이상|유료 램|우리 여왕 피격|r401+ 열린칸 정지사|최종 머리/판|',file=f)
 print('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',file=f)
 import statistics
 for label,p in groups.items():
  v=p[1];steps=v['ram_steps'];n=v['rams']
  print('|'+ '|'.join(map(str,[label,v['splits30'],v['pearls30'],statistics.median(v['first']),v['spread'],v['head30'],f"{n}/{n+v['rammed']}",sum(num for k,num in steps.items() if k>=2),v['ram_paid'],v['ram_queens'],v['late_stops'],v['final_heads']]))+'|',file=f)
