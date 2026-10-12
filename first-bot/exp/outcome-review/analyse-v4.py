#!/usr/bin/env python3
"""Census statistics, map/opponent-adjusted logistic models, and frozen selection.
Standard library only. New outputs are exclusive-created. No network or sampling.
"""
import collections, json, math, os, statistics as S, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.cache/outcome-review'
EXP=ROOT/'exp/outcome-review'
if '--allow-inherited-10' not in sys.argv:
    raise SystemExit('Heavy execution awaits explicit resource exception')
mem=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
import re
free=int(re.search(r'System-wide memory free percentage:\s*(\d+)%',mem)[1])
disk=int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])
if free<10 or disk<20: raise SystemExit('PAUSE resource threshold')

last_guard=0
def guard():
    global last_guard
    if time.monotonic()-last_guard<20:return
    last_guard=time.monotonic()
    m=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
    f=int(re.search(r'System-wide memory free percentage:\s*(\d+)%',m)[1])
    d=int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])
    if f<10 or d<20:raise SystemExit('PAUSE resource threshold')

def write(p,value):
    with open(p,'x',encoding='utf-8') as f:
        if isinstance(value,str):f.write(value)
        else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def readl(p):
    with open(p) as f:return [json.loads(l) for l in f if l.strip()]

def wilson(k,n):
    if not n:return [None,None]
    z=1.959963984540054;p=k/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]

def tcrit(df):
    ts=[0,12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042]
    if df<1:return None
    if df<=30:return ts[df]
    return 1.95996398454+(1.95996398454**3+1.95996398454)/(4*df)

def quantile(a,p):
    if not a:return None
    a=sorted(a);x=(len(a)-1)*p;j=int(x)
    return a[j]+(a[min(j+1,len(a)-1)]-a[j])*(x-j)

def dist(values):
    a=[x for x in values if x is not None and math.isfinite(x)]
    n=len(a)
    if not n:return {'n':0,'mean':None,'ci':[None,None],'median':None,'q1':None,'q3':None}
    m=S.mean(a);sd=S.stdev(a) if n>1 else None
    h=tcrit(n-1)*sd/math.sqrt(n) if sd is not None else None
    return {'n':n,'mean':m,'sd':sd,'ci':[m-h,m+h] if h is not None else [None,None],
            'median':quantile(a,.5),'q1':quantile(a,.25),'q3':quantile(a,.75),'min':min(a),'max':max(a)}

def ledger(rows):
    n=len(rows);c=collections.Counter(x['outcome'] for x in rows)
    e=sum(x['ourEliminated'] for x in rows);ee=sum(x['theirEliminated'] for x in rows)
    dom=sum(x['ourFinal']>x['theirFinal'] for x in rows)
    return {'n':n,**{o:c[o] for o in ['W','D','L']},'eliminated':e,'opponentEliminated':ee,
            'winCI':wilson(c['W'],n),'drawCI':wilson(c['D'],n),'lossCI':wilson(c['L'],n),
            'elimCI':wilson(e,n),'oppElimCI':wilson(ee,n),'dominance':dom,'dominanceCI':wilson(dom,n),
            'ownFinal':dist(x['ourFinal'] for x in rows),'enemyFinal':dist(x['theirFinal'] for x in rows),
            'pairedFinalDifference':dist(x['ourFinal']-x['theirFinal'] for x in rows)}

P=readl(CACHE/'primary.jsonl');raw={x['key']:x for x in readl(CACHE/'independent-v2.jsonl')}
checks=json.load(open(CACHE/'recount-checks-v2.json'))
extra={x['key']:x for x in readl(CACHE/'primary-extra.jsonl')}
extra_checks=json.load(open(CACHE/'extra-checks.json'))
if extra_checks['mismatchCount']:raise SystemExit('Primary-extra mismatches must be resolved')
if checks['mismatchCount']:raise SystemExit('Independent reconstruction has mismatches; resolve before analysis')
assert len(raw)==len(P)
for r in P:
    z=raw[r['key']];a=z['teams'][r['ourSide']];b=z['teams']['B' if r['ourSide']=='A' else 'A']
    for name,t in [('our',a),('their',b)]:
        r[name+'LatePieces']=t['births250'];r[name+'Births250to299']=t['births250']-t['births300']
        r[name+'LineSacAll']=t['lineSacAll'];r[name+'RawKingDeaths']=extra[r['key']]['teams'][r['ourSide'] if name=='our' else ('B' if r['ourSide']=='A' else 'A')]['kingDeaths']
        r[name+'Exposure']=t['exposure'];r[name+'ExposureTurns']=t['exposureTurns']
        den,num=t['turnExposure200'];r[name+'Exposure200']=num/den if den else None
    r['layout']=z['layout']
    r['earlyLogNaturalRatio']=math.log((r['ourNatural100']+1)/(r['theirNatural100']+1))
    r['fullLogNaturalRatio']=math.log((r['ourNatural']+1)/(r['theirNatural']+1))
    for t in [10,50,100,250]:
        a0,b0=r['ourHeads'+str(t)],r['theirHeads'+str(t)]
        r['headLogRatio'+str(t)]=math.log((a0+1)/(b0+1)) if a0 is not None and b0 is not None else None
    r['currentKingDifference300']=(r['ourKing300']-r['theirKing300'])/5 if r['ourKing300'] is not None else None
    r['lineageDifference300']=(r['ourLineage300']-r['theirLineage300'])/5 if r['ourLineage300'] is not None and r['theirLineage300'] is not None else None
    r['sacrificeLogRatio']=math.log((r['ourSacrifices']+1)/(r['theirSacrifices']+1))
    r['sacrificeLogRatio300']=math.log((r['ourSacrifices300']+1)/(r['theirSacrifices300']+1))
    r['birthLogRatio']=math.log((r['ourLatePieces']+1)/(r['theirLatePieces']+1))
    r['birthLogRatio300']=math.log((r['ourBirths250to299']+1)/(r['theirBirths250to299']+1))
    r['lineSacDifference']=(r['ourLineSac300']-r['theirLineSac300'])/10 if r['ourLineSac300'] is not None and r['theirLineSac300'] is not None else None
    r['exposureDifference']=(r['ourExposure']-r['theirExposure'])/.2 if r['ourExposure'] is not None and r['theirExposure'] is not None else None
    r['exposureDifference200']=(r['ourExposure200']-r['theirExposure200'])/.2 if r['ourExposure200'] is not None and r['theirExposure200'] is not None else None
    r['waveTrend']=r['waveOrder'];r['eraFlag']=int(r['era']=='waves')

waves=[r for r in P if r['era']=='waves'];history=[r for r in P if r['era']=='history']
top6=[r for r in waves if r['opponent']!=545];dev=[r for r in waves if r['opponent']==545]
wg=collections.defaultdict(list)
for r in waves:wg[r['wave']].append(r)
waveNames=sorted(wg,key=lambda x:(wg[x][0]['waveOrder'],min(r['id'] for r in wg[x])))

out={'population':{'all':ledger(P),'waves':ledger(waves),'top6':ledger(top6),'dev':ledger(dev),'history':ledger(history)},
     'waveNames':waveNames,'waveLedger':{},'byMap':{},'byOpponent':{},'waveFamily':{},'waveMap':{},'waveOpponent':{},'historySets':{},'distributions':{},'classes':{},'models':{},'trend':{},'power':{},'stratified':{},'mapLayout':{}}
for w in waveNames:
    rr=wg[w];out['waveLedger'][w]={k:ledger([r for r in rr if (r['opponent']!=545)==(k=='top6')]) for k in ['top6','DEV']}
    out['waveFamily'][w]={k:{f:ledger([r for r in rr if (r['opponent']!=545)==(k=='top6') and r['family']==f]) for f in ['r500','elim']} for k in ['top6','DEV']}
    out['waveMap'][w]={m:{k:ledger([r for r in rr if r['map']==m and (r['opponent']!=545)==(k=='top6')]) for k in ['top6','DEV']} for m in sorted(set(r['map'] for r in rr))}
    out['waveOpponent'][w]={str(o):ledger([r for r in rr if r['opponent']==o]) for o in sorted(set(r['opponent'] for r in rr))}
for pop,rr in [('waves',waves),('all',P),('history',history)]:
    out['byMap'][pop]={m:{k:ledger([r for r in rr if r['map']==m and (r['opponent']!=545)==(k=='top6')]) for k in ['top6','DEV']} for m in sorted(set(r['map'] for r in rr))}
    out['byOpponent'][pop]={str(o):ledger([r for r in rr if r['opponent']==o]) for o in sorted(set(r['opponent'] for r in rr))}
for s in sorted(set(r['set'] for r in history)):
    out['historySets'][s]={k:ledger([r for r in history if r['set']==s and (r['opponent']!=545)==(k=='top6')]) for k in ['top6','DEV']}

indicators=['ourHeads10','ourHeads50','ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLineSacAll','ourLatePieces','ourExposure','eliminationRound']
for w in waveNames:
    out['distributions'][w]={k:dist(r[k] for r in wg[w]) for k in indicators}
    out['distributions'][w]['enemy']={k:dist(r.get(k.replace('our','their')) for r in wg[w]) for k in indicators if k.startswith('our')}
    out['distributions'][w]['byGroup']={g:{k:dist(r[k] for r in wg[w] if (r['opponent']!=545)==(g=='top6')) for k in indicators} for g in ['top6','DEV']}
    out['distributions'][w]['alive']={str(t):{'n':len(wg[w]),'reached':sum(r['rounds']>t for r in wg[w]),'ownAliveAbsorbing':sum(r['ourAbsorbedHeads'+str(t)]>0 for r in wg[w]),'aliveCI':wilson(sum(r['ourAbsorbedHeads'+str(t)]>0 for r in wg[w]),len(wg[w]))} for t in [10,50,100,250,300,400]}

# Full-population, exclusive win classes and two overlapping loss populations.
def winclass(r):
    if r['theirEliminated']:return 'opponent-elimination'
    if any(x['r']>=300 for x in r['theirRawKingDeaths']):return 'opponent-late-king-loss'
    return 'length-race'

def mechanism(r):
    if r['ourLineage300'] is None or r['theirLineage300'] is None:return 'no-r300-decomposition'
    terms=[('initial-lineage',r['theirLineage300']-r['ourLineage300']),('natural-intake',r['theirLineNatural300']-r['ourLineNatural300']),('sacrifice-to-line',r['theirLineSac300']-r['ourLineSac300']),('other-own-drops',r['theirLineOwnOther300']-r['ourLineOwnOther300']),('enemy-drops',r['theirLineEnemy300']-r['ourLineEnemy300']),('sprint-loss',r['ourLineSprint300']-r['theirLineSprint300']),('split-loss',r['ourLineSplit300']-r['theirLineSplit300'])]
    r['gapTerms']=dict(terms)
    assert sum(v for k,v in terms)==r['theirFinal']-r['ourFinal']
    return max(terms,key=lambda x:x[1])[0]

classes=collections.defaultdict(list)
for r in P:
    if r['outcome']=='W':r['winClass']=winclass(r);classes['win:'+r['winClass']].append(r)
    if r['outcome']=='L' and r['finalRatio'] is not None and r['finalRatio']>=.8:
        r['nearClass']=mechanism(r);classes['near:'+r['nearClass']].append(r)
    lead300=r['ourKing300'] is not None and r['ourKing300']>r['theirKing300']
    lead400=r['ourKing400'] is not None and r['ourKing400']>r['theirKing400']
    r['led300']=lead300;r['led400']=lead400
    if r['outcome']=='L' and (lead300 or lead400):
        t=300 if lead300 else 400
        if any(x['r']>=t for x in r['ourRawKingDeaths']):lc='our-late-king-loss'
        elif r['theirLineSac300'] is not None and r['ourLineSac300'] is not None and r['theirLineSac300']>r['ourLineSac300']:lc='opponent-sacrifice-growth'
        else:lc='other-growth'
        r['leadClass']=lc;classes['lead:'+lc].append(r)

for k,rr in sorted(classes.items()):
    comp=[]
    if k.startswith('win:'):
        cells={(r['map'],r['opponent']) for r in rr}
        comp=[r for r in P if r['outcome']=='L' and (r['map'],r['opponent']) in cells]
    out['classes'][k]={'n':len(rr),'wavesN':sum(r['era']=='waves' for r in rr),'historyN':sum(r['era']=='history' for r in rr),'mapCounts':dict(collections.Counter(r['map'] for r in rr)),'opponentCounts':dict(collections.Counter(str(r['opponent']) for r in rr)),
       'ids':[r['key'] for r in rr],'indicators':{f:dist(r[f] for r in rr) for f in indicators},'sameCellsLossN':len(comp),'sameCellsLossIndicators':{f:dist(r[f] for r in comp) for f in indicators}}
    # Same map/opponent loss means matched to the empirical distribution of this class.
    matched={}
    for f in indicators:
        dif=[]
        for r in rr:
            if r[f] is None:continue
            a=[z[f] for z in comp if z['map']==r['map'] and z['opponent']==r['opponent'] and z[f] is not None]
            if a:dif.append(r[f]-S.mean(a))
        matched[f]=dist(dif)
    out['classes'][k]['matchedWinMinusLoss']=matched

selection={}
for k,rr in sorted(classes.items()):
    for r in sorted(rr,key=lambda x:x['id'])[:2]:selection.setdefault(r['key'],{'key':r['key'],'id':r['id'],'file':r['file'],'reasons':[]})['reasons'].append(k)
for key,sel in list(selection.items()):
    r=next(z for z in P if z['key']==key)
    if r['outcome']!='W':continue
    candidates=[z for z in P if z['outcome']=='L' and z['map']==r['map'] and z['opponent']==r['opponent']]
    same=[z for z in candidates if z['era']==r['era']]
    if same:candidates=same
    if candidates:
        z=min(candidates,key=lambda x:x['id']);selection.setdefault(z['key'],{'key':z['key'],'id':z['id'],'file':z['file'],'reasons':[]})['reasons'].append('same-map-opponent-loss-for:'+key)
out['selected']=sorted(selection.values(),key=lambda x:x['id'])
write(CACHE/'selection.json',{'method':'METHOD.md','classes':{k:len(v) for k,v in classes.items()},'games':out['selected']})
write(CACHE/'games.jsonl',''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in P))

# Descriptive stratification uses prespecified raw thresholds, explicit missing classes.
bins={
 'ourHeads10':[0,2,4,8,math.inf], 'ourHeads50':[0,4,8,16,math.inf],
 'ourHeads100':[0,4,8,16,math.inf], 'ourHeads250':[0,4,8,16,math.inf],
 'naturalRatio':[0,.2,.4,.8,math.inf], 'ourFinal':[0,8,16,32,math.inf],
 'ourLineage300':[0,4,8,16,math.inf], 'ourSacrifices':[0,10,30,100,math.inf],
 'ourLineSac300':[0,5,10,20,math.inf], 'ourLatePieces':[0,5,20,100,math.inf],
 'ourExposure':[0,.2,.4,.6,math.inf], 'eliminationRound':[0,100,250,400,math.inf]}
for f,edges in bins.items():
    tab=[]
    for pop,rr in [('waves-top7',waves),('waves-top6',top6),('all-top7',P)]:
        for i in range(len(edges)-1):
            sel=[r for r in rr if r[f] is not None and edges[i]<=r[f]<edges[i+1]]
            tab.append({'population':pop,'range':[edges[i],None if math.isinf(edges[i+1]) else edges[i+1]],**ledger(sel)})
        tab.append({'population':pop,'range':'missing',**ledger([r for r in rr if r[f] is None])})
    out['stratified'][f]=tab
    # Keep every map x opponent x bin row, including zero outcomes, in the machine output.
    fine=[]
    for cell in sorted({(r['map'],r['opponent']) for r in waves}):
        rr=[r for r in waves if (r['map'],r['opponent'])==cell]
        for i in range(len(edges)-1):
            q=[r for r in rr if r[f] is not None and edges[i]<=r[f]<edges[i+1]]
            if q:fine.append({'map':cell[0],'opponent':cell[1],'range':[edges[i],None if math.isinf(edges[i+1]) else edges[i+1]],**ledger(q)})
        q=[r for r in rr if r[f] is None]
        if q:fine.append({'map':cell[0],'opponent':cell[1],'range':'missing',**ledger(q)})
    out['stratified'][f+'-map-opponent']=fine

for m in sorted({r['map'] for r in P}):
    rr=[r for r in P if r['map']==m];variants={json.dumps(r['layout'],sort_keys=True) for r in rr}
    out['mapLayout'][m]={'layouts':[json.loads(x) for x in sorted(variants)],'all':ledger(rr),'waves':ledger([r for r in rr if r['era']=='waves'])}

# Logistic slopes with a distinct profiled intercept for each map x opponent.
def sigmoid(x):
    if x>=0:return 1/(1+math.exp(-min(x,700)))
    e=math.exp(max(x,-700));return e/(1+e)

def inverse(A):
    n=len(A);z=[a[:]+[float(i==j) for j in range(n)] for i,a in enumerate(A)]
    for i in range(n):
        k=max(range(i,n),key=lambda k:abs(z[k][i]));z[i],z[k]=z[k],z[i]
        if abs(z[i][i])<1e-10:raise ArithmeticError('Singular observed information')
        a=z[i][i];z[i]=[v/a for v in z[i]]
        for j in range(n):
            if j!=i:
                b=z[j][i]
                if b:z[j]=[v-b*w for v,w in zip(z[j],z[i])]
    return [r[n:] for r in z]

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def matmul(A,B):return [[sum(a[k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for a in A]

def model(rows,fields):
    rr=[r for r in rows if r['outcome']!='D' and all(r.get(f) is not None and math.isfinite(r[f]) for f in fields)]
    groups=collections.defaultdict(list)
    for r in rr:groups[(r['map'],r['opponent'],r['layout']['initialHeadsA'])].append(r)
    informative={k:a for k,a in groups.items() if 0<sum(r['outcome']=='W' for r in a)<len(a)}
    data=[a for a in informative.values()];p=len(fields)
    base={'candidateN':len(rows),'completeN':len(rr),'drawExcluded':sum(r['outcome']=='D' for r in rows),'informativeN':sum(map(len,data)),'strata':len(data),'uninformativeStrata':len(groups)-len(data),'wins':sum(r['outcome']=='W' for a in data for r in a),'fields':fields}
    if not data:return {**base,'error':'No outcome variation'}
    arrays=[[(r,[float(r[f]) for f in fields],int(r['outcome']=='W')) for r in a] for a in data]
    def evaluate(beta,need=True):
        ll=0;grad=[0.]*p;H=[[0.]*p for _ in range(p)];cluster=collections.defaultdict(lambda:[0.]*p)
        for a in arrays:
            eta=[dot(x,beta) for r,x,y in a];wins=sum(y for r,x,y in a)
            lo=-40-max(eta);hi=40-min(eta)
            for _ in range(50):
                al=(lo+hi)/2
                if sum(sigmoid(al+e) for e in eta)>wins:hi=al
                else:lo=al
            al=(lo+hi)/2;prob=[sigmoid(al+e) for e in eta]
            for (_,x,y),q in zip(a,prob):ll+=y*math.log(max(q,1e-300))+(1-y)*math.log(max(1-q,1e-300))
            if not need:continue
            weights=[q*(1-q) for q in prob];sw=sum(weights)
            sx=[sum(w*x[j] for w,(_,x,y) in zip(weights,a)) for j in range(p)]
            xm=[v/sw for v in sx]
            for (r,x,y),q,w in zip(a,prob,weights):
                v=y-q
                for j in range(p):
                    grad[j]+=x[j]*v;cluster[r['set']][j]+=(x[j]-xm[j])*v
                    for k in range(p):H[j][k]+=w*(x[j]-xm[j])*(x[k]-xm[k])
        return ll,grad,H,cluster
    beta=[0.]*p;converged=False
    try:
        for iteration in range(80):
            guard()
            ll,gr,H,cl=evaluate(beta);bread=inverse(H);step=[dot(a,gr) for a in bread]
            if max(map(abs,step),default=0)<1e-7:converged=True;break
            fac=min(1,5/max(map(abs,step)))
            while fac>1e-8:
                candidate=[b+fac*s for b,s in zip(beta,step)]
                if evaluate(candidate,False)[0]>=ll-1e-10:break
                fac/=2
            beta=candidate
        ll,gr,H,cl=evaluate(beta);bread=inverse(H);G=len(cl)
        meat=[[sum(a[j]*a[k] for a in cl.values())*G/(G-1) for k in range(p)] for j in range(p)] if G>1 else H
        V=matmul(matmul(bread,meat),bread);tc=tcrit(G-1) or 1.96
        coef=[]
        for j,f in enumerate(fields):
            se=math.sqrt(max(0,V[j][j]));c=[beta[j]-tc*se,beta[j]+tc*se]
            coef.append({'feature':f,'beta':beta[j],'clusterSE':se,'betaCI':c,'OR':math.exp(min(700,beta[j])),'ORCI':[math.exp(max(-700,min(700,x))) for x in c],'modelSE':math.sqrt(max(0,bread[j][j]))})
        return {**base,'converged':converged,'iterations':iteration+1,'clusters':G,'clusterDF':G-1,'logLikelihood':ll,'coefficients':coef}
    except (ArithmeticError,OverflowError,ZeroDivisionError) as e:return {**base,'error':str(e)}

early=['headLogRatio10','headLogRatio50','headLogRatio100','earlyLogNaturalRatio','waveTrend']
landmark=['headLogRatio250','earlyLogNaturalRatio','currentKingDifference300','sacrificeLogRatio300','birthLogRatio300','waveTrend']
late=['headLogRatio100','headLogRatio250','fullLogNaturalRatio','lineageDifference300','sacrificeLogRatio','lineSacDifference','birthLogRatio','exposureDifference']
out['models']['early-waves-top7']=model(waves,early)
out['models']['early-waves-top6']=model(top6,early)
out['models']['early-all-top7']=model(P,early[:-1]+['eraFlag'])
out['models']['landmark300-top7']=model([r for r in waves if r['rounds']>300],landmark)
out['models']['landmark300-exposure']=model([r for r in waves if r['rounds']>300],['currentKingDifference300','exposureDifference200','headLogRatio250','waveTrend'])
out['models']['late-retrospective-top7']=model(waves,late)
for f in ['headLogRatio10','headLogRatio50','headLogRatio100','headLogRatio250','earlyLogNaturalRatio','fullLogNaturalRatio','currentKingDifference300','lineageDifference300','sacrificeLogRatio','lineSacDifference','birthLogRatio','exposureDifference']:
    out['models']['single-adjusted:'+f]=model(waves,[f])
# Layout has no main effect after map fixed intercepts; interaction remains identifiable.
for r in waves:r['head100ByPortals']=r['headLogRatio100']*int(r['layout']['portalPairs']>0) if r['headLogRatio100'] is not None else None
out['models']['layout-interaction']=model(waves,['headLogRatio100','head100ByPortals','earlyLogNaturalRatio','waveTrend'])

out['trend']['top6-logistic']=model(top6,['waveTrend'])
out['trend']['elimination-logistic']=model([{**r,'outcome':'W' if r['ourEliminated'] else 'L'} for r in top6],['waveTrend'])
old=[r for r in waves if r['bot']=='merge2'];new=[r for r in waves if r['waveOrder']>=9]
out['trend']['endpointGroups']={'oldN':len(old),'newN':len(new),'oldTop6':ledger([r for r in old if r['opponent']!=545]),'newTop6':ledger([r for r in new if r['opponent']!=545])}
for f in indicators:
    a=dist(r[f] for r in old);b=dist(r[f] for r in new)
    if a['n']>1 and b['n']>1:
        se=math.sqrt(a['sd']**2/a['n']+b['sd']**2/b['n']);delta=b['mean']-a['mean'];ci=[delta-1.96*se,delta+1.96*se]
    else:delta=None;ci=[None,None]
    out['trend'][f]={'merge2':a,'latestStack8to11':b,'difference':delta,'differenceCI':ci}

# Replicate noise: same bot, fixed 60 map/opponent cells, varying seeds.
rep={b:[(w,out['waveLedger'][w]['top6']) for w in waveNames if wg[w][0]['bot']==b] for b in ['merge2','stack6']}
chi=0;df=0
for b,rr in rep.items():
    ws=[x['W'] for w,x in rr];p=sum(ws)/(60*len(ws));v=60*p*(1-p)
    chi+=sum((x-S.mean(ws))**2/v for x in ws);df+=len(ws)-1
    rep[b]={'waves':[w for w,x in rr],'N':60*len(ws),'wins':sum(ws),'winCounts':ws,'winCI':wilson(sum(ws),60*len(ws)),'winCountSD':S.stdev(ws),'discordantPairs':[]}
    for i in range(len(rr)):
        for j in range(i+1,len(rr)):
            a={(r['map'],r['opponent']):r['outcome']=='W' for r in wg[rr[i][0]] if r['opponent']!=545}
            z={(r['map'],r['opponent']):r['outcome']=='W' for r in wg[rr[j][0]] if r['opponent']!=545}
            discord=sum(a[k]!=z[k] for k in a);rep[b]['discordantPairs'].append({'pair':[rr[i][0],rr[j][0]],'discordant':discord,'n':60})
# chi-square df=3 quantiles are tabulated constants; no network/library dependency.
assert df==3
phi=chi/df;phiCI=[chi/9.3484036045,chi/.2157952826]
p0=out['population']['top6']['W']/len(top6)
power=[]
for plus in [3,5,10]:
    delta=plus/60;p1=p0+delta;pm=(p0+p1)/2
    for target,zbeta in [(.8,.84162123357),(.9,1.28155156554)]:
        unrounded=(1.95996398454*math.sqrt(2*pm*(1-pm))+zbeta*math.sqrt(p0*(1-p0)+p1*(1-p1)))**2/delta**2
        for label,inflation in [('binomial-floor',1),('measured-with-floor',max(1,phi)),('dispersion-upper95',max(1,phiCI[1]))]:
            n=math.ceil(unrounded*inflation);power.append({'plusWinsPer60':plus,'power':target,'noise':label,'gamesPerArm':n,'totalGames':2*n,'wavesPerArm':math.ceil(n/60),'totalWaves':2*math.ceil(n/60),'p0':p0,'p1':p1,'inflation':inflation})
out['power']={'replicates':rep,'residualDF':df,'pearsonChi':chi,'dispersion':phi,'dispersionCI':phiCI,'assumptions':'two-sided alpha=.05; equal independent old/new arms; census map/opponent mix; normal approximation','table':power}

# Every top-vs-top cached game is read, including inactive/faulty teams, without sampling.
top=collections.defaultdict(lambda:{'n':0,'winFinal':[],'loseFinal':[],'winHeads100':[],'loseHeads100':[],'winLineSac':[],'loseLineSac':[],'draws':0,'faultGames':0})
topfile=ROOT/'.cache/mass-ledger/top-sample.jsonl'
with open(topfile) as f:
    for line in f:
        guard()
        if not line.strip():continue
        r=json.loads(line);t=top[r['kind']];t['n']+=1
        t['faultGames']+=int(any(sum(r[s]['fl'][46])>0 for s in ['A','B']))
        if r['winner'] not in ['A','B']:t['draws']+=1;continue
        w=r['winner'];l='A' if w=='B' else 'B'
        if r['rounds']==500:
            for pre,s in [('win',w),('lose',l)]:
                t[pre+'Final'].append(r[s]['st']['king'][50]);t[pre+'Heads100'].append(r[s]['st']['units'][10])
                q=r[s]['lin'];
                if q and q.get('cp',{}).get('300'):t[pre+'LineSac'].append(q['cp']['300']['eat'][1])
out['topVsTop']={k:{**{a:v for a,v in z.items() if not isinstance(v,list)},**{a:dist(v) for a,v in z.items() if isinstance(v,list)}} for k,z in top.items()}
write(CACHE/'analysis.json',out)
# games.jsonl and selection.json were frozen before modeling.
print(json.dumps({'population':out['population'],'classes':{k:len(v) for k,v in classes.items()},'selectedN':len(selection),'trend':out['trend']['top6-logistic'],'dispersion':phi,'dispersionCI':phiCI},ensure_ascii=False))
