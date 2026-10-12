#!/usr/bin/env python3
"""Read-only replay counts. Run, manually check raw-checks.json, then --report."""
import sys
sys.dont_write_bytecode=True
import csv,json,os
from pathlib import Path
from collections import defaultdict,deque,Counter
from multiprocessing import Pool
from statistics import median
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'data/analysis/top1'))
import lib
rp=lib.rp
SIZES=['up to 600','601–1,200','1,201–2,400','over 2,400']
TAGS=['ours','top three','other']
def size(n):return SIZES[0 if n<=600 else 1 if n<=1200 else 2 if n<=2400 else 3]
def inputs():
 rows=list(csv.DictReader((REPO/'data/analysis/top1/games.csv').open()))
 for r in rows:r['source']='ladder/top1'
 for folder,n in [('qh31b-test-old',30),('qh31b-dev1-old',15)]:
  ps=sorted((REPO/'data/online/smoke'/folder).glob('game-*.json'));assert len(ps)==n
  for p in ps:
   j=json.loads(p.read_text());assert j['status']=='completed'
   rows.append(dict(game_id=str(j['id']),source=folder,map=j['mapName'],replay_path=str(p.parent/f"M{j['id']}.replay"),**{f'team{s}{k}':j[f'team{s}{k}'] for s in 'AB' for k in ['Id','Name']}))
 assert len(rows)==2388 and len({r['game_id'] for r in rows})==2388
 return rows

def count(row):
 portal=None
 try:
  root=rp.load(row['replay_path']).root();b=lib.Board(root.text(0));labels=defaultdict(list);wx=wy=False
  for line in root.text(0).splitlines():
   p=line.split()
   if not p or p[0]!='EDGE':continue
   er,x=divmod(int(p[1]),b.w+1);y=er//2;k=int(p[2])
   if k==0:wx|=er%2==1 and x==0;wy|=er==0
   if k==2:
    cells=[(x,y%b.h),(x,(y-1)%b.h)] if er%2==0 else [(x%b.w,y),((x-1)%b.w,y)]
    labels[int(p[3])].append((int(p[1]),cells))
  portal=bool(labels)
  if not portal:return dict(skip=True,game_id=row['game_id'],source=row['source'],map=row['map'],w=b.w,h=b.h,group=size(b.w*b.h),elimination=root.pointer(4).u16(2)==0)
  links={}
  for label,es in labels.items():
   assert len(es)==2,(label,es)
   for e,a in es:
    for f,c in es:
     if e!=f:
      for u in a:
       for v in c:links.setdefault((u,v),[]).append((label,e,f))
  def dist(a,c):
   dx,dy=abs(a[0]-c[0]),abs(a[1]-c[1])
   return (min(dx,b.w-dx) if wx else dx)+(min(dy,b.h-dy) if wy else dy)
  bodies,teams=b.bodies,b.teams;assert set(b.queen.values())=={0,1}
  qs={}
  for s in 'AB':
   tid=int(row[f'team{s}Id']);qs[s]=dict(side=s,id=b.queen[s],team=tid,name=row[f'team{s}Name'],tag='ours' if tid==1119 else 'top three' if tid in (306,91,264) else 'other',jumps=[],death=None,alive100=False)
  rnd,actor,dirs,used,seq=-1,None,[],0,0;raw=[]
  for idx,ev in enumerate(root.pointer(3)):
   k,p=ev.u16(0),ev.pointer(0);rec=None
   if k==0:
    rnd=p.i32(0)
    if rnd==100:
     for q in qs.values():q['alive100']=q['id'] in bodies
   elif k==1:actor,dirs,used=p.i32(0),[],0;seq+=1
   elif k==4:
    actor=p.i32(0);a=p.pointer(0);ak=a.u16(0) if a else None
    dirs=list(a.pointer(0)) if ak==0 and a.pointer(0) is not None else [];used=0
    rec=dict(kind='dragonAction',id=actor,action=ak,dirs=dirs)
   elif k==9:
    did=p.i32(0);head,tail=rp.point(p.pointer(0)),rp.point(p.pointer(1));body=bodies[did];old=body[0]
    if did in (0,1) and old!=head and dist(old,head)>1:
     assert (old,head) in links,(idx,rnd,did,old,head)
     s=teams[did];en=[(d,v[0],dist(head,v[0])) for d,v in bodies.items() if teams[d]!=s];near=min(en,key=lambda v:v[2]) if en else None;distance=near[2] if near else None
     mine,theirs=b.starts[did],b.starts[1-did]
     qs[s]['jumps'].append(dict(event=idx,seq=seq,round=rnd,id=did,from_cell=old,landing=head,links=links[(old,head)],distance=distance,nearest=near,distance_bin='not seen' if distance is None or distance>15 else '0–3' if distance<=3 else '4–8' if distance<=8 else '9+',own_start_distance=dist(head,mine),enemy_start_distance=dist(head,theirs),other_side=dist(head,theirs)<dist(head,mine)))
    if old!=head:body.appendleft(head)
    while len(body)>1 and body[-1]!=tail:body.pop()
    if did==actor:used+=1
    rec=dict(kind='dragonUpdate',id=did,old=old,head=head,tail=tail)
   elif k==10:
    for did,j in [(p.i32(0),0),(p.i32(4),1)]:bodies[did]=deque(rp.point(v) for v in p.pointer(j));teams[did]='AB'[p.u16(8)]
   elif k==11:
    did,reason=p.i32(0),p.u16(4);body=bodies[did];cause,target,owners='other',None,[]
    if reason==0:cause='wall'
    elif reason==1:cause='own body'
    elif reason==2 and actor==did and used<len(dirs):
     target=b.step(body[0],dirs[used]);owners=[d for d,v in bodies.items() if d!=did and target in v]
     if owners and all(teams[d]==teams[did] for d in owners):cause='team body'
    elif reason==3 and actor!=did and actor in teams and teams[actor]!=teams[did]:cause='rammed by enemy'
    if did in (0,1):qs[teams[did]]['death']=dict(round=rnd,event=idx,reason=lib.REASONS[reason] if reason<5 else 'other',cause=cause,actor=actor,target=target,owners=owners,head=body[0])
    rec=dict(kind='dragonDeath',id=did,reason=reason,actor=actor,cause=cause,target=target,owners=owners);bodies.pop(did)
   if rec:raw.append(dict(event=idx,seq=seq,round=rnd,**rec))
  result=root.pointer(4);winner='AB'[result.u16(6)] if result.u16(4)==1 else None;final={}
  for i,s in enumerate('AB'):
   ls=[len(v) for d,v in bodies.items() if teams[d]==s];st=result.pointer(i)
   assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
   q=qs[s];q['alive_end']=q['id'] in bodies;q['win']=winner==s
   final[s]=dict(units=len(ls),queen=len(bodies[q['id']]) if q['alive_end'] else 0,longest=max(ls,default=0),total=sum(ls))
  if result.u16(2)==0:end='elimination'
  elif result.u16(2)==1:
   end='draw'
   for metric,label in [('queen','queen rule'),('longest','longest dragon'),('total','total length')]:
    if final['A'][metric]!=final['B'][metric]:
     end=label;assert winner==('A' if final['A'][metric]>final['B'][metric] else 'B');break
  else:end='unknown'
  samples=[]
  for s,q in qs.items():
   for j in q['jumps']:
    delta=q['death']['round']-j['round'] if q['death'] else None;j['death_delta']=delta
    j['death10']=delta is not None and 0<=delta<=10;j['death30']=delta is not None and 0<=delta<=30
    if len(samples)<6 and (q['tag'] in ('ours','top three') or j['death10']):samples.append(dict(side=s,tag=q['tag'],jump=j,raw=[v for v in raw if v['seq']==j['seq']],death=q['death']))
  return dict(game_id=row['game_id'],source=row['source'],replay_path=row['replay_path'],map=row['map'],w=b.w,h=b.h,cells=b.w*b.h,group=size(b.w*b.h),portals=len(labels),wrap_x=wx,wrap_y=wy,rounds=rnd+1,winner=winner,end=end,queens=qs,samples=samples)
 except Exception as e:return dict(game_id=row['game_id'],source=row['source'],map=row['map'],portal=portal,error=f'{type(e).__name__}: {e}')

def run():
 try:os.nice(10)
 except PermissionError:pass
 rows=inputs();out=[]
 with Pool(3) as pool:
  for i,v in enumerate(pool.imap(count,rows,chunksize=2),1):
   out.append(v)
   if i%100==0:print(f'{i}/{len(rows)}; errors={sum("error" in r for r in out)}',flush=True)
 (HERE/'games.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
 candidates=[(r,s) for r in out if 'queens' in r for s in r['samples']];checks=[];seen=set()
 for label,pred in [('ours',lambda s:s['tag']=='ours'),('top three',lambda s:s['tag']=='top three'),('death within 10',lambda s:s['jump']['death10'])]:
  found=next(((r,s) for r,s in candidates if pred(s) and (r['game_id'],s['jump']['event']) not in seen),None)
  if found:
   r,s=found;seen.add((r['game_id'],s['jump']['event']));checks.append(dict(check=label,game_id=r['game_id'],source=r['source'],map=r['map'],w=r['w'],h=r['h'],wrap_x=r['wrap_x'],wrap_y=r['wrap_y'],**s))
 (HERE/'raw-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
 print('Counts saved. Inspect raw-checks.json before --report.',flush=True)

def report():
 data=json.loads((HERE/'games.json').read_text());games=[r for r in data if 'queens' in r];errors=[r for r in data if 'error' in r];qrows=[dict(game=g,**q) for g in games for q in g['queens'].values()]
 lines=['# Queen portal counts','',f'Input: 2,343 ladder/top1 games and 45 live-bot games; {len(data)} unique games. Parsed portal-map games: {len(games)}; queen-games: {len(qrows)}. No network or game runs.','',
 'A queen-game is one team’s queen in one game; both teams are included. G = unique games, Q = queen-games, J = jumps. Ours = 1119 meow; top three = 306 Vibing++, 91 SSS, 264 forgot to mention; other = every remaining team. Each fraction states its sample size; the row’s G applies to each number in that row.','',
 'Detection reuses qh31b-analysis/count.py: a dragonUpdate head move longer than one normal step, with open-border wrapping on each axis, between cells touching different edges of the same portal label. No sonar-ping requirement. Updates are individual steps, so the threshold is one step, not a full action’s reach.','',
 'Distance = Manhattan cells, wrapping an axis only when its border has an open edge. Walls, bodies and portal shortcuts are ignored for distance. Enemy heads use full replay positions immediately before the landing update. “Not seen” means no enemy head within 15 cells, not actual bot visibility; 9+ means 9–15. Other-side means landing strictly nearer the enemy queen’s initial head than the own queen’s initial head.','',
 'Alive at round 100 means alive at the start of round 100; games ending earlier are excluded. Death windows include the jump round and the next 10 or 30 rounds. Repeated jumps may share a death. Queen-game death shares count a queen once if any selected jump meets the window.','']
 def table(h,rs):
  lines.extend(['| '+' | '.join(h)+' |','|'+'|'.join(['---']*len(h))+'|']);lines.extend('| '+' | '.join(str(v).replace('|','\\|') for v in r)+' |' for r in rs);lines.append('')
 def share(k,n):return f'{k}/{n} ({100*k/n:.1f}%)' if n else '0/0 (not measured)'
 def ns(qs):return f'Q={len(qs)}, G={len({q["game"]["game_id"] for q in qs})}'
 def chosen(q,mode):return [j for j in q['jumps'] if mode=='any' or j['other_side']]
 table(['Source','Parsed portal games','Queen-games'],[[source,f'G={sum(g["source"]==source for g in games)}',f'Q={2*sum(g["source"]==source for g in games)}, G={sum(g["source"]==source for g in games)}'] for source in ['ladder/top1','qh31b-test-old','qh31b-dev1-old']])
 maps={}
 for g in games:maps.setdefault((g['map'],g['w'],g['h'],g['portals']),[]).append(g)
 lines+=['## Maps','','Portals = paired labels (two edges each). Free cells were not separately counted: this format stores blocked edges, not blocked tiles.','']
 table(['Map','Width × height','Cells','Portal pairs (edges)','Size group','Games'],[[name,f'{w} × {h}',w*h,f'{p} ({2*p})',size(w*h),f'G={len(gs)}'] for (name,w,h,p),gs in sorted(maps.items())])
 for sz in SIZES:lines.append(f'- {sz}: '+', '.join(sorted({g['map'] for g in games if g['group']==sz}))+f" (G={sum(g['group']==sz for g in games)}).")
 lines+=['','## 1. Queen jumps',''];rs=[]
 for sz in SIZES:
  for tag in TAGS:
   qs=[q for q in qrows if q['game']['group']==sz and q['tag']==tag];yes=[q for q in qs if q['jumps']];J=sum(len(q['jumps']) for q in qs);first=[q['jumps'][0]['round'] for q in yes]
   rs.append([sz,tag,ns(qs),share(len(yes),len(qs)),f'{J/len(qs):.3f} (J={J}, {ns(qs)})' if qs else f'not measured (J=0, {ns(qs)})',f'{median(first):g} ({ns(yes)})' if first else f'not measured ({ns(yes)})'])
 table(['Size','Tag','Sample','At least one jump','Jumps per queen-game','First jump median round'],rs)
 lines+=['## 2. Game endings',''];rs=[]
 for sz in SIZES:
  for tag in TAGS:
   for yes in (True,False):
    qs=[q for q in qrows if q['game']['group']==sz and q['tag']==tag and bool(q['jumps'])==yes]
    rs.append([sz,tag,'jumped' if yes else 'never jumped',ns(qs)]+[share(sum(q['game']['end']==e for q in qs),len(qs)) for e in ['elimination','queen rule','longest dragon','total length','draw','unknown']])
 table(['Size','Tag','Queen','Sample','Elimination','Queen rule','Longest dragon','Total length','Draw','Unknown'],rs)
 def sections(mode):
  title='any jump' if mode=='any' else 'other-side jump'
  lines.extend([f'### Win rate: {title}',''])
  if mode!='any':lines.extend(['Comparison: queens with at least one other-side jump versus queens without an other-side jump (including queens that jumped only to their own side).',''])
  rs=[]
  for sz in SIZES:
   for tag in TAGS:
    for alive in (False,True):
     qs=[q for q in qrows if q['game']['group']==sz and q['tag']==tag and (not alive or q['alive100'])];a=[q for q in qs if chosen(q,mode)];z=[q for q in qs if not chosen(q,mode)]
     rs.append([sz,tag,'alive r100' if alive else 'all',share(sum(q['win'] for q in a),len(a))+f' ({ns(a)})',share(sum(q['win'] for q in z),len(z))+f' ({ns(z)})'])
  table(['Size','Tag','Subset','Wins with '+title,'Wins without '+title],rs)
  lines.extend([f'### Fate: {title}','']);rs=[]
  for sz in SIZES:
   for tag in TAGS:
    for yes in (True,False):
     qs=[q for q in qrows if q['game']['group']==sz and q['tag']==tag and bool(chosen(q,mode))==yes]
     rs.append([sz,tag,'with' if yes else 'without',ns(qs),share(sum(q['alive_end'] for q in qs),len(qs))]+[share(sum(any(j[f'death{n}'] for j in chosen(q,mode)) for q in qs),len(qs)) if yes else 'not applicable' for n in (10,30)])
  table(['Size','Tag',title,'Sample','Alive at end','Death within 10 (Q)','Death within 30 (Q)'],rs)
  lines.extend(['The next two tables count jumps. A later death may follow multiple jumps. Causes are exclusive. Other includes enemy body, an active queen’s head-on, allied head-on, suicide/no action, and unresolved collisions.','']);rs=[]
  for sz in SIZES:
   for tag in TAGS:
    pairs=[(q,j) for q in qrows if q['game']['group']==sz and q['tag']==tag for j in chosen(q,mode)]
    for n in (10,30):
     ds=[(q,j) for q,j in pairs if j[f'death{n}']]
     short=[(q,j) for q,j in pairs if not j[f'death{n}'] and q['game']['rounds']-1-j['round']<n]
     rs.append([sz,tag,n,f'J={len(pairs)}, G={len({q["game"]["game_id"] for q,j in pairs})}',share(len(ds),len(pairs))+f' (death G={len({q["game"]["game_id"] for q,j in ds})})']+[share(sum(q['death']['cause']==c for q,j in ds),len(ds)) for c in ['rammed by enemy','wall','own body','team body','other']]+[share(len(short),len(pairs))+f' (G={len({q["game"]["game_id"] for q,j in short})})'])
  table(['Size','Tag','Window rounds','All jumps','Followed by death','Rammed by enemy','Wall','Own body','Team body','Other','Game ended before full window, without death'],rs)
  rs=[]
  for sz in SIZES:
   for tag in TAGS:
    for bin in ['0–3','4–8','9+','not seen']:
     allp=[(q,j) for q in qrows if q['game']['group']==sz and q['tag']==tag for j in chosen(q,mode)];ps=[(q,j) for q,j in allp if j['distance_bin']==bin]
     rs.append([sz,tag,bin,share(len(ps),len(allp))+f' (G={len({q["game"]["game_id"] for q,j in ps})})']+[share(sum(j[f'death{n}'] for q,j in ps),len(ps))+f' (death G={len({q["game"]["game_id"] for q,j in ps if j[f"death{n}"]})})' for n in (10,30)])
  table(['Size','Tag','Landing distance','Share of jumps (J)','Death within 10 (J)','Death within 30 (J)'],rs)
 lines+=['## 3 and 4. Win rate and fate',''];sections('any')
 lines+=['## 5. Other-side jumps',''];rs=[]
 for sz in SIZES:
  for tag in TAGS:
   ps=[(q,j) for q in qrows if q['game']['group']==sz and q['tag']==tag for j in q['jumps']];cross=[(q,j) for q,j in ps if j['other_side']]
   rs.append([sz,tag,share(len(cross),len(ps))+f' (all G={len({q["game"]["game_id"] for q,j in ps})}, other-side G={len({q["game"]["game_id"] for q,j in cross})})'])
 table(['Size','Tag','Other-side share of jumps'],rs);sections('other-side')
 lines+=['## 6. Every game where our queen jumped','','Each row is G=1. Distances over 15 retain their numeric value and are labeled not seen. If the game ends before 30 further rounds, the shorter observation is stated.',''];rs=[]
 for q in qrows:
  if q['tag']!='ours' or not q['jumps']:continue
  g=q['game'];o=g['queens']['B' if q['side']=='A' else 'A'];js=[]
  for j in q['jumps']:
   if j['death30']:fate=f'died +{j["death_delta"]} rounds ({q["death"]["cause"]})'
   elif g['rounds']-1-j['round']<30:fate=f'alive through game end (+{g["rounds"]-1-j["round"]} rounds)' if q['alive_end'] else 'no death within 30 rounds'
   else:fate='alive after 30 rounds'
   js.append(f'r{j["round"]}: distance {j["distance"] if j["distance"] is not None else "none"} [{j["distance_bin"]}], '+('other-side, ' if j['other_side'] else '')+fate)
  rs.append([g['game_id'],g['source']+' / '+Path(g['replay_path']).parent.name,o['name'],g['map'],'; '.join(js),('win' if q['win'] else 'draw' if g['winner'] is None else 'loss')+' / '+g['end']])
 table(['Game (G=1)','Source','Opponent','Map','Each jump and next 30 rounds','Final result'],rs)
 lines+=['## 7. Elimination among all portal-map games','']
 table(['Size','Elimination share'],[[sz,share(sum(g['end']=='elimination' for g in games if g['group']==sz),sum(g['group']==sz for g in games))+f' (G={sum(g["group"]==sz for g in games)})'] for sz in SIZES])
 lines+=['The table above uses every included portal-map game, whether either queen jumped or not. For completeness, the following table uses all input games, including non-portal maps.','']
 allgames=[dict(group=g['group'],elimination=g['end']=='elimination') for g in games]
 original={r['game_id']:r for r in inputs()}
 for r in data:
  if not r.get('skip'):continue
  if 'group' not in r:
   # Compatibility with counts made before non-portal result fields were saved.
   row=original[r['game_id']]
   if row['source']=='ladder/top1':r=dict(r,group=size(int(row['cells'])),elimination=row['end_type']=='wipe-out')
   else:
    root=rp.load(row['replay_path']).root();b=lib.Board(root.text(0));r=dict(r,group=size(b.w*b.h),elimination=root.pointer(4).u16(2)==0)
  allgames.append(r)
 table(['Size','Elimination share, including non-portal games'],[[sz,share(sum(g['elimination'] for g in allgames if g['group']==sz),sum(g['group']==sz for g in allgames))+f' (G={sum(g["group"]==sz for g in allgames)})'] for sz in SIZES])
 lines+=['## Raw event hand-checks','',(HERE/'hand-checks.md').read_text().strip(),'','## Input checks and limits','',
 f'- Portal-map parse failures: {sum(r.get("portal") is True for r in errors)} games. Unknown portal status after load/header failure: {sum(r.get("portal") is None for r in errors)} games. Total errors: {len(errors)}.',
 f'- Non-portal games excluded: {sum(r.get("skip",False) for r in data)}. Final survivor count, longest length and total length match replay result fields in all {len(games)} counted games. Every counted queen is id 0 or 1. Every long queen move matches a paired portal label.',
 '- Independent comparison with existing top1 CSV and queen records: 1,911 ladder games / 3,822 queen-games checked; ending type, queen id, final queen survival, death round, and start-of-round-100 survival had 0 mismatches (validation.json). The 36 portal-map live games / 72 queen-games use the replay-result checks above.',
 '- Round-limit endings use final queen length, then longest dragon, then total length, and the inferred winner is checked against the replay. Draws have their own column and are not wins.',
 '- Portal crossings of ordinary distance one, and attempted portal entries ending in death before a landing update, are outside this detection definition. Intent and whether a portal was necessary were not measured.',
 '- Body deaths use the next requested direction and the map transition, including portals, to identify the body owner at event time. Enemy-body and unresolved collisions go in other. Rammed by enemy means the queen was the non-acting head-on victim of an enemy actor; a queen initiating head-on goes in other.',
 '- The round-100 subset uses eventual jump status, including jumps later than round 100. No matching by opponent, build, map or survival duration was done. These are counts, not controlled tests or causal estimates.',
 '- Death-window denominators include jumps with less than the full window before game end. Their shorter observation is counted separately; absence of a recorded death is not a claim of survival beyond game end.',
 '- Free-cell totals, actual bot visibility, and a usefulness threshold were not measured. No strategic interpretation is made.',
 '- Reproduce: python3 -B data/analysis/queen-portals/count.py; inspect raw-checks.json and record checks in hand-checks.md; then python3 -B data/analysis/queen-portals/count.py --report. games.json stores counts and failures; summary.md is written last.','']
 if errors:table(['Game','Source','Portal status','Error'],[[r['game_id'],r['source'],r['portal'],r['error']] for r in errors])
 (HERE/'summary.md').write_text('\n'.join(lines));print(f'summary.md written last: portal games={len(games)}, errors={len(errors)}')
if __name__=='__main__':report() if '--report' in sys.argv else run()
