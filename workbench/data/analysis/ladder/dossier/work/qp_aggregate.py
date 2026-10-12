import json,statistics
from pathlib import Path
from collections import defaultdict,Counter
D=Path('data/analysis/ladder/dossier');W=D/'work';games=[json.loads(s) for f in sorted(W.glob('qp_games_*.jsonl')) for s in f.open()]
assert len(games)==1097 and len({(g['who'],g['game']) for g in games})==1097
screens={(r['who'],r['game']):r['screen'] for f in sorted(W.glob('qp_screen_*.jsonl')) for s in f.open() for r in [json.loads(s)]}
assert len(screens)==1097
for g in games:
 for t,s in g['snaps'].items():
  if 'prox' in s:s['prox'][5]=screens[g['who'],g['game']].get(t)
layouts=sorted({g['layout'] for g in games if g['who']=='O'}&{g['layout'] for g in games if g['who']=='R'});assert len(layouts)==19
by=defaultdict(list)
for g in games:by[g['who'],g['layout']].append(g)
metrics=['alive','centre','path','nearer','length','n3','n5','n8','none5','nearest','friend_first','enemy5','other_nearest','other_none5']
detail={}
def values(s):
 out={k:s.get(k) for k in ['alive','centre','path','nearer','length']}
 if 'prox' in s:
  for k,v in zip(['n3','n5','n8','none5','nearest','friend_first','enemy5'],s['prox']):out[k]=v
  for k,idx in [('other_nearest',4),('other_none5',3)]:
   vv=[p[idx] for p in s['other_prox'] if p[idx] is not None];out[k]=statistics.mean(vv) if vv else None
 return out
def agg(lays,times):
 acc={};rec={}
 for k in metrics:
  per={who:{} for who in ['O','R']}
  for who in ['O','R']:
   for l in lays:
    vals=[values(g['snaps'][str(t)]).get(k) for g in by[who,l] for t in times if str(t) in g['snaps']];vv=[v for v in vals if v is not None]
    per[who][l]={'sum':sum(vv),'n':len(vv),'mean':statistics.mean(vv) if vv else None}
  valid=[l for l in lays if all(per[w][l]['mean'] is not None for w in ['O','R'])]
  acc[k]=[statistics.mean(per[w][l]['mean'] for l in valid) if valid else None for w in ['O','R']];rec[k]={'layouts':valid,'per_layout':per}
 return acc,rec
def moves(lays,wins):
 acc={};rec={}
 for cls in ['Q','D']:
  for metric,num,den in [('toward',1,0),('away',3,2),('near',5,6),('none',7,4)]:
   per={w:{} for w in ['O','R']}
   for w in ['O','R']:
    for l in lays:
     vv=[g['turns'].get(win+'|'+cls,[0]*8) for g in by[w,l] for win in wins];n=sum(v[num] for v in vv);d=sum(v[den] for v in vv);per[w][l]={'n':n,'d':d,'value':n/d if d else None}
   valid=[l for l in lays if all(per[w][l]['value'] is not None for w in ['O','R'])];acc[cls+'_'+metric]=[statistics.mean(per[w][l]['value'] for l in valid) if valid else None for w in ['O','R']];rec[cls+'_'+metric]={'layouts':valid,'per_layout':per}
 return acc,rec
def pair(v,scale=1):return '/'.join('NA' if x is None else f'{x*scale:.1f}' for x in v)
def span(t):return '0-30' if t<=30 else '31-60' if t<=60 else '61-150'
lines=['| Round | Centre % O/R | Start path steps O/R | Nearer than r0 % O/R | Length O/R | Alive % O/R | Live n O/R; ended-live excluded O/R |','|---|---:|---:|---:|---:|---:|---|']
for t in [0,10,20,30,40,60,80,100,150]:
 a,r=agg(layouts,[t]);detail['r'+str(t)]=r;counts=[];missing=[]
 for w in ['O','R']:
  gs=[g for g in games if g['who']==w];counts.append(sum(g['snaps'].get(str(t),{}).get('alive',0) for g in gs));missing.append(sum(str(t) not in g['snaps'] for g in gs))
 lines.append(f"| {t} | {pair(a['centre'],100)} | {pair(a['path'])} | {pair(a['nearer'],100)} | {pair(a['length'])} | {pair(a['alive'],100)} | {'/'.join(map(str,counts))}; {'/'.join(map(str,missing))} |")
lines+=['','| Round | Own heads ≤3 O/R | ≤5 O/R | ≤8 O/R | None ≤5 % O/R | Nearest mate O/R | Mate nearer nearest enemy % O/R | Enemy heads ≤5 O/R | Same-length others nearest O/R; none ≤5 % O/R |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
for t in [0,10,20,30,40,60,80,100,150]:
 a,_=agg(layouts,[t]);lines.append('| '+str(t)+' | '+' | '.join(pair(a[k],100 if k in ['none5','friend_first'] else 1) for k in ['n3','n5','n8','none5','nearest','friend_first','enemy5'])+' | '+pair(a['other_nearest'])+'; '+pair(a['other_none5'],100)+' |')
lines+=['','| Cells (layouts), rounds | Centre %; path; nearer % O/R | Own ≤3; ≤5; ≤8 O/R | None ≤5 %; nearest mate; mate nearer enemy % O/R | Enemy ≤5; length; alive % O/R | Toward centre % Q O/R; D O/R | Away from mate % Q O/R; D O/R | Turn-start nearest Q O/R; D O/R |','|---|---|---|---|---|---|---|---|']
summary={}
for group in ['all','≤700','701–1200','>1200']:
 lays=[l for l in layouts if group=='all' or (by['O',l][0]['cells']<=700 if group=='≤700' else 700<by['O',l][0]['cells']<=1200 if group=='701–1200' else by['O',l][0]['cells']>1200)]
 for win in ['0-30','31-60','61-150']:
  ts=[t for t in [0,10,20,30,40,60,80,100,150] if span(t)==win];a,r=agg(lays,ts);m,mr=moves(lays,[win]);detail[group+' '+win]={'snapshot':r,'moves':mr};summary[group+' '+win]={'snapshot':a,'moves':m}
  lines.append(f'| {group} ({len(lays)}), {win} | '+'; '.join(pair(a[k],100 if k in ['centre','nearer'] else 1) for k in ['centre','path','nearer'])+' | '+'; '.join(pair(a[k]) for k in ['n3','n5','n8'])+' | '+'; '.join(pair(a[k],100 if k in ['none5','friend_first'] else 1) for k in ['none5','nearest','friend_first'])+' | '+'; '.join(pair(a[k],100 if k=='alive' else 1) for k in ['enemy5','length','alive'])+' | '+pair(m['Q_toward'],100)+'; '+pair(m['D_toward'],100)+' | '+pair(m['Q_away'],100)+'; '+pair(m['D_away'],100)+' | '+pair(m['Q_near'])+'; '+pair(m['D_near'])+' |')
lines+=['','| Cells | Death ≤150 n O/R; equal-layout % O/R | Death rounds 0–30; 31–60; 61–150 n O/R | Mean death round O/R | Causes n O/R: wall; own body; other body; head-on hit; head-on mover; illegal split; other |','|---|---|---|---|---|']
death_summary={}
for group in ['≤700','701–1200','>1200']:
 lays=[l for l in layouts if (by['O',l][0]['cells']<=700 if group=='≤700' else 700<by['O',l][0]['cells']<=1200 if group=='701–1200' else by['O',l][0]['cells']>1200)]
 n=[];pct=[];windows=[[],[],[]];mean=[];causes=[[],[],[],[],[],[],[]]
 for w in ['O','R']:
  gs=[g for g in games if g['who']==w and g['layout'] in lays];ds=[g['death'] for g in gs if g['death']];n.append(len(ds));pct.append(statistics.mean(sum(bool(g['death']) for g in by[w,l])/len(by[w,l]) for l in lays));vl=[l for l in lays if all(any(g['death'] for g in by[who,l]) for who in ['O','R'])];mean.append(statistics.mean(statistics.mean(g['death']['round'] for g in by[w,l] if g['death']) for l in vl) if vl else None)
  for ix,win in enumerate(['0-30','31-60','61-150']):windows[ix].append(sum(span(d['round'])==win for d in ds))
  cc=Counter(d['cause'] for d in ds)
  for ix,c in enumerate(['wall','own body','another body','head-on hit','head-on mover','illegal split','other']):causes[ix].append(cc[c] if c!='other' else sum(v for k,v in cc.items() if k not in ['wall','own body','another body','head-on hit','head-on mover','illegal split']))
  death_summary[group+' '+w]={'games':len(gs),'deaths':len(ds),'causes':dict(cc),'rounds':[d['round'] for d in ds]}
 lines.append('| '+group+' | '+'/'.join(map(str,n))+'; '+pair(pct,100)+' | '+'; '.join('/'.join(map(str,v)) for v in windows)+' | '+pair(mean)+' | '+'; '.join('/'.join(map(str,v)) for v in causes)+' |')
(W/'qp_detail.json').write_text(json.dumps({'snapshots':detail,'summary':summary,'death':death_summary},indent=2)+'\n')
(W/'qp_tables.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines));print('TABLE LINES',len(lines))
