#!/usr/bin/env python3
import json,statistics,collections,datetime,pathlib
OUT=pathlib.Path(__file__).resolve().parent
def read(f): return json.loads((OUT/f).read_text())
def stats(a):
 a=sorted(x for x in a if x is not None)
 return dict(N=len(a),min=a[0] if a else None,median=statistics.median(a) if a else None,p25=a[int((len(a)-1)*.25)] if a else None,p75=a[int((len(a)-1)*.75)] if a else None,max=a[-1] if a else None)
def count(a,key): return dict(collections.Counter(key(x) for x in a))
def queens(G): return [dict(game=g,side=t,name=g['team'+t],q=g['queens'][t]) for g in G for t in ['A','B']]
def deathkind(x):
 d=x['q']['death'];t=x['side']
 if d['reason']=='H':return ('enemy_' if d['other']['team']!=t else 'ally_')+d['role']
 if d['reason']=='O':return 'ally_body' if d['other']['team']==t else 'enemy_body'
 return {'W':'wall','S':'self','A':'no_valid_action'}[d['reason']]
def bins(G,role=None):
 out={}
 for g in G:
  for t in ['A','B']:
   for k,v in g['actions'][t].items():
    b,phase,r=k.split('/')
    if role and role!=r:continue
    z=out.setdefault(b,dict(turns=0,moves=0,splits=0,requested={},executedSteps=0,paidSteps=0,freeBudgetSum=0,withinFree=0,multiWithinFree=0))
    for f in z:
     if f=='requested':
      for n,m in v[f].items():z[f][n]=z[f].get(n,0)+m
     else:z[f]+=v[f]
 for z in out.values():
  z['requestedSteps']=sum(int(n)*m for n,m in z['requested'].items())
  z['meanRequested']=z['requestedSteps']/z['moves'] if z['moves'] else None
  z['meanExecuted']=z['executedSteps']/z['moves'] if z['moves'] else None
 return out
def profiles(G):
 out={}
 for x in queens(G):
  n=x['name'];out.setdefault(n,[]).append(x)
 result={}
 for n,a in out.items():
  qq=[x['q'] for x in a]; late=[q for q in qq if any(t[0]>=300 for t in q['turns'])];surv=[q for q in qq if q['aliveAt500']]
  result[n]=dict(N=len(a),maps=count(a,lambda x:x['game']['map']),aliveEnd=sum(q['aliveEnd'] for q in qq),alive500=sum(q['aliveAt500'] for q in qq),roundLimit=sum(x['game']['rounds']==500 for x in a),splitQueens=sum(bool(q['splits']) for q in qq),queenSplits=sum(len(q['splits']) for q in qq),deathRounds=stats([q['death']['round'] for q in qq if q['death']]),lateAliveN=len(late),lateSplits=sum(sum(s['round']>=300 for s in q['splits']) for q in qq),lateEndLengths=stats([q['endLength'] for q in surv]),queenLongEarly=sum(any(t[0]<100 and t[1]>=9 for t in q['turns']) for q in qq))
 return result
T=read('tables.json');G=T['games'];Z=queens(G);D=[x for x in Z if x['q']['death']];limits=[g for g in G if g['rounds']==500];tie=[g for g in limits if g['fate']=='both_dead'];surv=[x for x in Z if x['q']['aliveAt500']]
H=[x for x in D if x['q']['death']['category']=='rammed'];nonqueen=[x for x in H if not x['q']['death']['other']['queen']];multi=[x for x in nonqueen if x['q']['death']['fate']['step']>=1]
A={
 'N':len(G),'battles':len(set(g['battleId'] for g in G)),'maps':count(G,lambda g:g['map']),'teamNames':len(set(x['name'] for x in Z)),
 'timeRange':[min(g['at'] for g in G),max(g['at'] for g in G)],'fates':count(G,lambda g:g['fate']),
 'endReasons':count(G,lambda g:g['endReason']),'limitFates':count(limits,lambda g:g['fate']),
 'queenN':len(Z),'aliveEnd':sum(x['q']['aliveEnd'] for x in Z),'alive500':len(surv),
 'deathReasons':count(D,lambda x:x['q']['death']['reason']),'deathKinds':count(D,deathkind),'deathCategories':count(D,lambda x:x['q']['death']['category']),
 'deathRounds':stats([x['q']['death']['round'] for x in D]),'deathPeriod':count(D,lambda x:'0-49' if x['q']['death']['round']<50 else '50-99' if x['q']['death']['round']<100 else '100-299' if x['q']['death']['round']<300 else '300-499'),
 'deathLengths':stats([x['q']['death']['length'] for x in D]),
 'noValidActions':count([x for x in D if x['q']['death']['reason']=='A'],lambda x:x['q']['death']['category']+'/'+str((x['q']['death']['ownHistory'][-1]['action'] or {}).get('kind'))),
 'queenSplitting':dict(N=len(Z),splitQueens=sum(bool(x['q']['splits']) for x in Z),splits=sum(len(x['q']['splits']) for x in Z),keptAtMost3=sum(s['kept']<=3 for x in Z for s in x['q']['splits']),lateSplits=sum(s['round']>=300 for x in Z for s in x['q']['splits'])),
 'reach':dict(queenTurns=sum(len(x['q']['turns']) for x in Z),queenTurnsWithinEnemyFreeReach=sum(x['q']['freeReachTurns'] for x in Z),enemyTurns=sum(x['q']['enemyTurnOpportunities'] for x in Z),enemyTurnsWithinFreeReach=sum(x['q']['enemyFreeReach'] for x in Z),exposedQueens=sum(x['q']['enemyFreeReach']>0 for x in Z),exposedGames=sum(g['queens']['A']['enemyFreeReach']+g['queens']['B']['enemyFreeReach']>0 for g in G),exposureQueenRounds=sum(len(x['q']['exposureRounds']) for x in Z)),
 'assassination':dict(targetDeaths=len(H),nonQueenAttackers=len(nonqueen),multiStepNonQueenKills=len(multi),multiStepFreeKills=sum(x['q']['death']['fate']['step']+1<=-(-x['q']['death']['otherHistory'][-1]['length']//4) for x in multi),multiStepRecords=[dict(gameId=x['game']['gameId'],battleId=x['game']['battleId'],map=x['game']['map'],victim=x['name'],queenId=x['q']['id'],round=x['q']['death']['round'],victimLength=x['q']['death']['length'],attackerId=x['q']['death']['other']['id'],attackerStartLength=x['q']['death']['otherHistory'][-1]['length'],path=''.join(x['q']['death']['otherHistory'][-1]['action']['steps'])) for x in multi]),
 'steps':bins(G),'queenSteps':bins(G,'queen'),'otherSteps':bins(G,'other'),
 'earlyLong':dict(teamN=2*len(G),teamsAtLeast9Before100=sum(v is not None and v['round']<100 for g in G for v in g['firstLong'].values()),queenN=len(Z),queensAtLeast9Before100=sum(any(t[0]<100 and t[1]>=9 for t in x['q']['turns']) for x in Z)),
 'ties':dict(N=len(tie),winnerLongest=stats([g['result']['team'+g['winner']]['longestDragon'] for g in tie]),loserLongest=stats([g['result']['team'+('A' if g['winner']=='B' else 'B')]['longestDragon'] for g in tie]),winnerLongestByMap={m:stats([g['result']['team'+g['winner']]['longestDragon'] for g in tie if g['map']==m]) for m in sorted(set(g['map'] for g in tie))},games=[dict(gameId=g['gameId'],battleId=g['battleId'],map=g['map'],winner=g['winner'],winnerTeam=g['team'+g['winner']],longestA=g['result']['teamA']['longestDragon'],longestB=g['result']['teamB']['longestDragon'],totalA=g['result']['teamA']['totalLength'],totalB=g['result']['teamB']['totalLength']) for g in tie]),
 'profiles':profiles(G),
 'survivors':[],'curves':{}
}
A['assassination']['enemyHeadContacts']=len(set((x['game']['gameId'],x['q']['death']['round'],x['q']['death']['moverId']) for x in D if x['q']['death']['reason']=='H' and x['q']['death']['other']['team']!=x['side']))
A['assassination']['queenOnQueenContacts']=sum(x['q']['death']['other']['queen'] for x in H)
A['assassination']['nonQueenVictimLengths']=stats([x['q']['death']['length'] for x in nonqueen])
A['assassination']['longQueenNonQueenKills']=sum(x['q']['death']['length']>=8 for x in nonqueen)
A['trapBlockers']=dict(N=sum(x['q']['death']['category']=='trap' for x in D),onlySelfAndWall=sum(x['q']['death']['category']=='trap' and not any(n['kind'] in ['ally','enemy'] for n in x['q']['death']['neighbours']) for x in D),allyPresent=sum(x['q']['death']['category']=='trap' and any(n['kind']=='ally' for n in x['q']['death']['neighbours']) for x in D),enemyPresent=sum(x['q']['death']['category']=='trap' and any(n['kind']=='enemy' for n in x['q']['death']['neighbours']) for x in D))
for r in [0,25,50,100,150,200,250,300,350,400,450,499]:
 v=[x['q']['curve'][str(r)] for x in Z if str(r) in x['q']['curve']]
 live=[x for x in v if x>0]
 A['curves'][r]=dict(atRiskGames=sum(g['rounds']>r for g in G),queenN=len(v),aliveN=len(live),liveLengths=stats(live))
for x in surv:
 q=x['q'];late=[t for t in q['turns'] if t[0]>=300];end=[t for t in q['turns'] if t[0]>=400];period=None
 for p in range(2,41):
  if len(end)>=p*3 and all(end[i][2:4]==end[i-p][2:4] for i in range(p,len(end))):period=p;break
 A['survivors'].append(dict(gameId=x['game']['gameId'],battleId=x['game']['battleId'],team=x['name'],side=x['side'],queen=q['id'],map=x['game']['map'],length=q['endLength'],curve=q['curve'],splits=q['splits'],enemyDistance=stats([t[4] for t in late]),torusDistance=stats([t[5] for t in late]),alliesWithin3=stats([t[6] for t in late]),allyPresentTurns=sum(t[6]>0 for t in late),lateMotion=q['lateMotion'],endPeriod=period,eats=q['eats'],roomAt400=x['game']['checkpoints']['400'][x['side']]['room'],endRoom=q['endRoom'],endHead=q['endHead'],freeReachEnemyTurns=q['enemyFreeReach']))
L=read('local.json');local={}
for c in sorted(set(g['cohort'] for g in L['games'])):
 gg=[g for g in L['games'] if g['cohort']==c];qq=[g['queens'][g['side']] for g in gg];dd=[q for q in qq if q['death']];feeds=[f for q in qq for f in q['feeds'] if f['round']>=300];liveFeeds=[f for f in feeds if f['queenAlive']];qfeeds=[f for f in liveFeeds if f['toQueen']]
 local[c]=dict(N=len(gg),aliveEnd=sum(q['aliveEnd'] for q in qq),alive500=sum(q['aliveAt500'] for q in qq),roundLimit=sum(g['rounds']==500 for g in gg),deathRounds=stats([q['death']['round'] for q in dd]),deathCategories=count(dd,lambda q:q['death']['category']),deathReasons=count(dd,lambda q:q['death']['reason']),queenEndLengths=stats([q['endLength'] for q in qq if q['aliveAt500']]),feeds=dict(N=len(feeds),whileQueenAlive=len(liveFeeds),toQueen=len(qfeeds),drops=sum(f['drops'] for f in qfeeds),byQueen=sum(f['byQueen'] for f in qfeeds),byOwn=sum(f['byOwn'] for f in qfeeds),byEnemy=sum(f['byEnemy'] for f in qfeeds)))
A['local']={'N':len(L['games']),'inventory':L['inventory'],'cohorts':local,'snapshotAt':L['createdAt']}
O=read('old.json');OG=[g for g in O['games'] if not any(g['checks'].values())];oldprofiles=profiles(OG)
# Rebalance comparison: only same name + map cells, at most 3 newest games in each cohort/cell.
oldcells=collections.defaultdict(list);newcells=collections.defaultdict(list)
for x in queens(OG):oldcells[(x['name'],x['game']['map'])].append(x)
for x in Z:newcells[(x['name'],x['game']['map'])].append(x)
matched={}
for n in sorted(set(x['name'] for x in Z)):
 cells=[k for k in newcells if k[0]==n and k in oldcells]
 if not cells:continue
 def metrics(a):
  qq=[x['q'] for x in a];longMoves=multi=0
  for x in a:
   for k,v in x['game']['actions'][x['side']].items():
    if k.split('/')[0]!='2-4':longMoves+=v['moves'];multi+=sum(m for s,m in v['requested'].items() if int(s)>=2)
  return dict(N=len(a),aliveEnd=sum(q['aliveEnd'] for q in qq),alive500=sum(q['aliveAt500'] for q in qq),roundLimit=sum(x['game']['rounds']==500 for x in a),splitQueens=sum(bool(q['splits']) for q in qq),queenSplitMean=sum(len(q['splits']) for q in qq)/len(a),deathRounds=stats([q['death']['round'] for q in qq if q['death']]),longMoves=longMoves,longMultiMoves=multi)
 matched[n]=dict(maps=[k[1] for k in cells],old=metrics([x for k in cells for x in sorted(oldcells[k],key=lambda x:x['game']['at'],reverse=True)[:3]]),new=metrics([x for k in cells for x in sorted(newcells[k],key=lambda x:x['game']['at'],reverse=True)[:3]]))
A['oldComparison']=dict(N=len(O['games']),cleanN=len(OG),failedN=len(O['games'])-len(OG),cutoff=O['cutoff'],selection=O['selection'],profiles=oldprofiles,matched=matched,oldChecks={k:sum(g['checks'][k] for g in O['games']) for k in O['games'][0]['checks']})
A['checks']={k:sum(g['checks'][k] for g in G) for k in G[0]['checks']}
A['createdAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
T['aggregate']=A;T['status']='aggregated; see verify-*.json for independent reconstruction checks';T['method']=dict(rules='123',queenIdentity='id 0/1 mapped through initialDragons.team; never assume team A=id 0',turnColumns=['round','length','headX','headY','nearestEnemyKelpPortalDistance','nearestEnemyWrappedManhattan','alliesWithinWrappedManhattan3','enemyHeadsWithinConservativeFreeReach','freeNeighbours','nearestEnemyId'],room='queen-head flood area while all current bodies stay blocked; includes head tile, not a permanent geometric room',freeReach='body-blocked BFS at each enemy turn, goal queen head allowed; fixed ceil(attacker start length/4); conservative because future tail vacating ignored',aliveAt500='only rounds=500 and no queen dragonDeath; early elimination survivors counted only aliveEnd',localSnapshot=L['createdAt'],noIntentInference='multi-step kill is a behavior proxy, not proof of queen-specific targeting')
(OUT/'tables.json').write_text(json.dumps(T,ensure_ascii=False,indent=2)+'\n')
(OUT/'aggregate.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(eliteN=A['N'],localN=A['local']['N'],oldN=A['oldComparison']['N'],oldFailures=A['oldComparison']['failedN'],fates=A['fates'],survivors=len(A['survivors'])),ensure_ascii=False))
