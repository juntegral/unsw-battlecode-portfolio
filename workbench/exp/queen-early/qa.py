#!/usr/bin/env python3
import json,pathlib,re,struct,datetime,os,hashlib
O=pathlib.Path(__file__).resolve().parent;ROOT=O.parent.parent
read=lambda f:json.loads((O/f).read_text())
T=read('tables.json');A=T['aggregate'];L=read('local.json');OLD=read('old.json');V={x:read('verify-'+x+'.json') for x in ['elite','local','old']};D=read('decoder-qa.json');S=read('deep-selection.json');checks=[]
def check(name,cond):
 if not cond:raise AssertionError(name)
 checks.append(name)
check('264 unique online replay keys',len(T['games'])==len(set((g['battleId'],g['gameId']) for g in T['games']))==264)
check('all primary reconciliation checks zero',all(not any(g['checks'].values()) for g in T['games']+L['games']+OLD['games']))
check('all independent reconstruction checks zero',all(not any(v for k,v in z['checks'].items() if k!='games') and not z['diff'] for z in V.values()))
check('same N in primary and independent',V['elite']['checks']['games']==len(T['games']) and V['local']['checks']['games']==len(L['games']) and V['old']['checks']['games']==len(OLD['games']))
check('queen fate counts independently match',V['elite']['fates']==A['fates']=={'both_dead':240,'winner_only':24})
check('death causes independently match',V['elite']['reasons']==A['deathReasons'] and sum(A['deathReasons'].values())==504)
check('score independent queen6 longest119 elimination139',V['elite']['deciders']=={'queen':6,'longestDragon':119,'elimination':139})
check('wrong identity exactly reproduces 8/16',V['elite']['rawWrong']=={'winnerAlive':8,'loserAlive':16})
check('decoder comparison all zero, exact event N',D['N']==12 and all(x['bad']==0 for x in D['comparisons']) and sum(x['events'] for x in D['comparisons'])==941248)
check('deep selection contains all six survivors',set(x['gameId'] for x in A['survivors']).issubset(set(x.get('gameId') for x in S['games'])))
check('16 deep replay reads',S['N']==len(S['games'])==16)
g=read('game-815034.json');q=g['queens']['B'];attack=next(s for s in g['snapshots'] if s.get('stage')=='before attacker #726')
check('same-round newborn attack sequence',q['death']['round']==q['attackerBirth']['round']==308 and q['death']['moverId']==726 and q['attackerBirth']['parent']==347 and any(d['id']==726 for d in attack['dragons']) and any(d['id']==1 and d['body'][0]=={'x':35,'y':2} for d in attack['dragons']) and not any(d['id']==1 for s in g['snapshots'] if s['round']==309 for d in s['dragons']))
g=next(g for g in L['games'] if g['cohort']=='exp/v16/q1/q1-sprint2' and g['map']=='australia' and g['side']=='B');q=g['queens']['B']
check('local feed trap precedes escape split',[(x[0],x[1],x[8]) for x in q['turns'] if 411<=x[0]<=414]==[(411,19,2),(412,19,1),(413,19,0),(414,2,0)])
g=next(g for g in T['games'] if g['gameId']==814547);q=g['queens']['B'];t=[x for x in q['turns'] if x[0]>=400]
check('fandagong exact late head period4 and L2',len(t)==100 and all(x[1]==2 for x in t) and all(t[i][2:4]==t[i-4][2:4] for i in range(4,len(t))))
check('free exposure denominators',A['reach']['enemyTurnsWithinFreeReach']==149 and A['reach']['enemyTurns']==523813 and A['reach']['exposureQueenRounds']==149)
check('requested free multi count',sum(v['multiWithinFree'] for k,v in A['steps'].items() if k!='2-4')==6316 and sum(v['moves'] for k,v in A['steps'].items() if k!='2-4')==422318)
R=ROOT/'research/observations/queen-early.md';md=R.read_text();links=re.findall(r'\]\(([^)]+)\)',md);missing=[]
for l in links:
 if not l.startswith(('http:','https:','#')) and not (R.parent/l).exists():missing.append(l)
check('all report artifact links exist',not missing)
pics=list(O.glob('*.png'))
check('9 valid PNG board pictures',len(pics)==9 and all(p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',p.read_bytes()[16:24])[0]>0 for p in pics))
check('reports facts and interpretations marked',md.count('[사실]')>=30 and md.count('[해석]')>=10)
check('report corrected counts', 'N=941,248' in md and 'N=149여왕-라운드' in md and '분열하기 전에 이미 막혔다' in md)
disk=os.statvfs(O);free=disk.f_bavail*disk.f_frsize;check('disk at least 21GiB',free>=21*1024**3)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':len(checks),'checks':checks,'Ns':{'elite':264,'local':771,'old':277,'deep':16,'decoder':12,'pictures':9},'freeDiskBytes':free,'reportLines':len(md.splitlines()),'reportSha256':hashlib.sha256(R.read_bytes()).hexdigest(),'scope':'exp/queen-early/**; research/observations/queen-early.md','noNetwork':True,'noGames':True,'noUploads':True,'noCommits':True,'niceRequested':10,'niceApplied':False,'niceReason':'sandbox setpriority Operation not permitted','workerCap':2}
(O/'qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
