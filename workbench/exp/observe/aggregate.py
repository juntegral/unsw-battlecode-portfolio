import json,gzip,math,statistics,datetime
from pathlib import Path
from collections import defaultdict,Counter
O=Path(__file__).parent
CPS=[0,5,10,20,25,30,50,100,200]
def dist(a):
    a=sorted(v for v in a if v is not None and math.isfinite(v))
    if not a:return {'N':0,'mean':None,'p10':None,'p50':None,'p90':None}
    def q(p):
        i=(len(a)-1)*p;j=int(i);return a[j]+(a[min(j+1,len(a)-1)]-a[j])*(i-j)
    return {'N':len(a),'mean':sum(a)/len(a),'sd':statistics.pstdev(a),'p10':q(.1),'p50':q(.5),'p90':q(.9),'min':a[0],'max':a[-1]}
def ratio(a,b):return a/b if b else None
def cohorts(row,t):
    if row['src']=='top':
        return ['elite-top10']+(['elite-winner'] if str(row['winner']).upper()==t else ['elite-loser'])
    if row['src']=='local':return ['local-'+row['set'].split('-')[1],'local-v12']
    return ['ours-online', 'ours-v1' if row['set'].startswith('v1-') else 'ours-W0-W12']
class Bucket:
    def __init__(self):self.rows=[]
    def result(self):
        rows=self.rows;out={'N':len(rows),'uniqueGames':len(set(r['key'] for r,t in rows)),'checkpoints':{}}
        for r in CPS:
            observations=[(g,t,g['cp'][str(r)]['teams'][t]) for g,t in rows]
            a={'N':len(observations),'endedBeforeRoundN':sum(g['cp'][str(r)]['censored'] for g,t,v in observations)}
            for name,fun in {
              'coverage':lambda g,v:v['coverage'],'mirroredCoverage':lambda g,v:v['mirroredSeen']/g['area'],
              'spawnCoverage':lambda g,v:ratio(v['spawnSeen'],g['truth']['spawnTiles']),
              'fountainCoverage':lambda g,v:ratio(v['fountainSeen'],g['truth']['fountainTiles']),
              'spawnMirroredCoverage':lambda g,v:ratio(v['spawnMirrored'],g['truth']['spawnTiles']),
              'fountainMirroredCoverage':lambda g,v:ratio(v['fountainMirrored'],g['truth']['fountainTiles']),
              'dynamicMirroredCoverage':lambda g,v:ratio(v.get('dynamicMirroredSeen'),g['area']) if v.get('dynamicMirroredSeen') is not None else None,
            }.items():a[name]=dist([fun(g,v) for g,t,v in observations])
            a['symmetry']={'decidedN':sum(v['candidates']==1 for g,t,v in observations),'maskCounts':dict(Counter(v['mask'] for g,t,v in observations)),
                'firstRound':dist([v['first'] for g,t,v in observations if v['first'] is not None and v['first']<=r]),
                'dynamicN':sum(g['exactCountdowns'] for g,t,v in observations),
                'dynamicDecidedN':sum(v['dynamicMask'] in [1,2,4] for g,t,v in observations if g['exactCountdowns']),
                'dynamicFirstRound':dist([v['dynamicFirst'] for g,t,v in observations if v['dynamicFirst'] is not None and v['dynamicFirst']<=r])}
            a['pockets']={};a['frontier']={}
            for region in ['raw','mirrored']:
                a['pockets'][region]={}
                for mode in ['optimistic','pessimistic','literalOptimistic']:
                    rs=[v['geometry'][region][mode] for g,t,v in observations];s={k:sum(q[k] for q in rs) for k in ['tp','fp','fn','predicted','evaluated']}
                    s.update(N=len(rs),precision=ratio(s['tp'],s['tp']+s['fp']),recall=ratio(s['tp'],s['tp']+s['fn']),nonzeroTruthGameN=sum(g['truth']['pocketTiles']>0 for g,t,v in observations),macroPrecision=dist([ratio(q['tp'],q['tp']+q['fp']) for q in rs]),macroRecall=dist([ratio(q['tp'],q['tp']+q['fn']) for q in rs]))
                    a['pockets'][region][mode]=s
                rs=[v['geometry'][region]['frontier'] for g,t,v in observations];s={k:sum(q[k] for q in rs) for k in ['correct','oracleEnemyCorrect','bodyReferenceCorrect','N','spawnN','spawnCorrect','fountainN','fountainCorrect','reachableN','reachableCorrect']}
                s.update(gameN=len(rs),accuracy=ratio(s['correct'],s['N']),oracleEnemyAccuracy=ratio(s['oracleEnemyCorrect'],s['N']),bodyReferenceAccuracy=ratio(s['bodyReferenceCorrect'],s['N']),macroAccuracy=dist([ratio(q['correct'],q['N']) for q in rs]),enemyStartCorrectN=sum(q['enemyStartCorrect'] for q in rs),decidedN=sum(q['decided'] for q in rs),unresolvedPortalDirections=sum(v['geometry'][region]['unresolvedPortalDirections'] for g,t,v in observations),matrix=[[sum(q['matrix'][i][j] for q in rs) for j in range(6)] for i in range(6)])
                a['frontier'][region]=s
                s.update(spawnAccuracy=ratio(s['spawnCorrect'],s['spawnN']),fountainAccuracy=ratio(s['fountainCorrect'],s['fountainN']),reachableAccuracy=ratio(s['reachableCorrect'],s['reachableN']))
            dynamic=[v['dynamicGeometry'] for g,t,v in observations if 'dynamicGeometry' in v]
            a['dynamicGeometry']={'N':len(dynamic),'pockets':{},'frontier':{}}
            for mode in ['optimistic','pessimistic','literalOptimistic']:
                ss={k:sum(v[mode][k] for v in dynamic) for k in ['tp','fp','fn','predicted','evaluated']};ss.update(precision=ratio(ss['tp'],ss['tp']+ss['fp']),recall=ratio(ss['tp'],ss['tp']+ss['fn']));a['dynamicGeometry']['pockets'][mode]=ss
            ss={k:sum(v['frontier'][k] for v in dynamic) for k in ['correct','N','spawnN','spawnCorrect','fountainN','fountainCorrect']};ss.update(accuracy=ratio(ss['correct'],ss['N']),spawnAccuracy=ratio(ss['spawnCorrect'],ss['spawnN']),fountainAccuracy=ratio(ss['fountainCorrect'],ss['fountainN']));a['dynamicGeometry']['frontier']=ss
            processes=[(g,p) for g,t,v in observations for p in g['cp'][str(r)]['processes'] if p['team']==t]
            a['process']={'N':len(processes),'liveTeamGameN':sum(any(p['team']==t for p in g['cp'][str(r)]['processes']) for g,t,v in observations)}
            for role,pr in [('all',processes),('roots',[(g,p) for g,p in processes if p['born']==0 and p['id']==p['root']]),('children',[(g,p) for g,p in processes if p['id']!=p['root']])]:
                b={'N':len(pr),'age':dist([p['age'] for g,p in pr])}
                for mode in ['own','inherited','patch','summary','dynamic','block']:
                    pp=[(g,p) for g,p in pr if mode in p]
                    b[mode]={'coverage':dist([p[mode]['seen']/g['area'] for g,p in pp]),'mirroredCoverage':dist([p[mode]['mirroredSeen']/g['area'] for g,p in pp]),'decidedN':sum(p[mode]['candidates']==1 for g,p in pp),'N':len(pp)}
                b['inheritanceGain']=dist([(p['inherited']['seen']-p['own']['seen'])/g['area'] for g,p in pr]);b['patchGain']=dist([(p['patch']['seen']-p['own']['seen'])/g['area'] for g,p in pr]);b['summaryMirroringGain']=dist([(p['summary']['mirroredSeen']-p['own']['mirroredSeen'])/g['area'] for g,p in pr]);b['blockGain']=dist([(p['block']['seen']-p['own']['seen'])/g['area'] for g,p in pr if 'block' in p]);b['bitmap']={'knownTileCoverage':dist([p['bitmap']['seen']/g['area'] for g,p in pr if 'bitmap' in p]),'spawnCoverage':dist([p['bitmap']['spawnCoverage'] for g,p in pr if 'bitmap' in p])}
                a['process'][role]=b
            # Equal game-seat weights make population growth less dominant than pooled process quantiles.
            a['process']['seatMeanOwnCoverage']=dist([sum(p['own']['seen']/g['area'] for p in g['cp'][str(r)]['processes'] if p['team']==t)/sum(p['team']==t for p in g['cp'][str(r)]['processes']) for g,t,v in observations if any(p['team']==t for p in g['cp'][str(r)]['processes'])])
            exact=[(g,t,v) for g,t,v in observations if g['exactCountdowns']];a['rates']={}
            for gate in [1,2,4,8]:
                rs=[v['rates'][str(gate)] for g,t,v in exact];ks=['tp','fp','fn','classified','spawnSeen','fountainSeen','resetSamples','orbitSamples','rateN','rateRelativeAbsoluteSum','rateRelativeSquaredSum','trueSeenRate','estimatedRate'];s={k:sum(q[k] for q in rs) for k in ks};s.update(N=len(rs),precision=ratio(s['tp'],s['tp']+s['fp']),recall=ratio(s['tp'],s['tp']+s['fn']),seenFountainRecall=ratio(s['tp'],s['fountainSeen']),classifiedSpawnerShare=ratio(s['classified'],s['spawnSeen']),rateRelativeMAE=ratio(s['rateRelativeAbsoluteSum'],s['rateN']),rateRelativeRMSE=math.sqrt(s['rateRelativeSquaredSum']/s['rateN']) if s['rateN'] else None,estimatedToSeenTrueRate=ratio(s['estimatedRate'],s['trueSeenRate']))
                a['rates'][gate]=s
            old={'tp':sum(v.get('oldFountain',{}).get('tp',0) for g,t,v in exact),'fp':sum(v.get('oldFountain',{}).get('fp',0) for g,t,v in exact),'fountainN':sum(g['truth']['fountainTiles'] for g,t,v in exact),'N':len(exact)};old.update(precision=ratio(old['tp'],old['tp']+old['fp']),recall=ratio(old['tp'],old['fountainN']));a['oldFountain']=old
            out['checkpoints'][r]=a
        lifetimes=[(g,q) for g,t in rows for q in g['lifetimes'] if q['team']==t]
        out['lifetimes']={'N':len(lifetimes),'born':dist([q['born'] for g,q in lifetimes]),'deadN':sum(q['death'] is not None for g,q in lifetimes)}
        for mode in ['own','inherited','patch','summary','dynamic']:
            ls=[(g,q) for g,q in lifetimes if mode!='dynamic' or g['exactCountdowns']];d=[q[mode+'First'] for g,q in ls if q[mode+'First'] is not None]
            out['lifetimes'][mode]={'N':len(ls),'decidedN':len(d),'firstRound':dist(d),'delayFromBirth':dist([q[mode+'First']-q['born'] for g,q in ls if q[mode+'First'] is not None])}
        out['sonar']={k:sum(g['sonar'][t][k] for g,t in rows) for k in ['sent','delivered','self','enemy','lost']}
        return out
def main():
    population=json.loads((O/'population.json').read_text());rows=[json.loads(l) for l in gzip.open(O/'games.jsonl.gz','rt')];assert len(rows)==len({r['key'] for r in rows})
    maps=defaultdict(lambda:defaultdict(Bucket));global_=defaultdict(Bucket);checks=Counter();inventory=Counter()
    for g in rows:
        checks.update(g['checks']);inventory[g['src']]+=1
        for t in g['eligible']:
            for c in cohorts(g,t):maps[g['map']+'/'+g['layout']][c].rows.append((g,t));global_[c].rows.append((g,t))
    prior=json.loads((O/'tables.json').read_text());prior.update(status='complete' if len(rows)==len(population['tasks']) else 'partial',computedAt=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),population={'games':len(rows),'expectedGames':len(population['tasks']),'sources':dict(inventory),'selection':population['selection'],'localSets':dict(Counter(g.get('set') for g in rows if g['src']=='local')),'onlineSets':dict(Counter(g.get('set') for g in rows if g['src']=='online')),'maxProcessIdBy200':max(q['id'] for g in rows for q in g['lifetimes'] if q['born']<=200),'localSeedMapConditions':len({(g['mapFile'],g['seed']) for g in rows if g['src']=='local'})},checks=dict(checks),globalCohorts={k:b.result() for k,b in global_.items()},maps={})
    for m,co in sorted(maps.items()):
        sample=co[next(iter(co))].rows[0][0];prior['maps'][m]={'truth':sample['truth'],'area':sample['area'],'W':sample['W'],'H':sample['H'],'mapFile':sample['mapFile'],'cohorts':{k:b.result() for k,b in co.items()}}
    prior['mapBalanced']={}
    for c in ['local-F','local-S','ours-online','ours-v1','elite-top10','elite-winner']:
        prior['mapBalanced'][c]={}
        for r in CPS:
            bs=[m['cohorts'][c]['checkpoints'][r] for m in prior['maps'].values() if c in m['cohorts']]
            prior['mapBalanced'][c][r]={k:dist([b[k]['mean'] for b in bs]) for k in ['coverage','mirroredCoverage','spawnCoverage','fountainCoverage']}
    (O/'tables.json').write_text(json.dumps(prior,ensure_ascii=False,indent=1)+'\n')
    print(json.dumps({'status':prior['status'],'games':len(rows),'inventory':dict(inventory),'checks':dict(checks)},ensure_ascii=False))
if __name__=='__main__':main()
