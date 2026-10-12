"""Full-population statistics, paired/team/seat consistency, and transparent Ward clustering.

No external packages; no network; caches are study-owned. An unobserved checkpoint is
missing, never an imputed final value. Every rate retains numerator and denominator.
"""
import pathlib,json,math,statistics as st,collections,hashlib,itertools,time
R=pathlib.Path(__file__).resolve().parents[2];O=R/'exp/map-atlas/cache'
WAVE=['cand-merge2-online','cand-merge2-online-r2','cand-merge2-online-r3']+[f'cand-stack{i}-online' for i in range(1,7)]+['cand-stack6-online-r2']+[f'cand-stack{i}-online' for i in range(7,12)]
WN=['W0a','W0b','W0c']+[f'W{i}' for i in range(1,13)]
PH=['0–49','50–99','100–249','250–349','350–449','450–499']
ROUNDS=[10,25,50,100,150,250,350]
MK={'csplit':'csplit','lsplit':'lsplit','frag':'frag','F':'fguard','cl':'cl','cov':'cov','cov30':'covw','conv':'conv','feed':'feed','g':'gather','grab':'grab','tg':'tg','escape-split':'escsplit','esc-split':'escsplit2','no-exit':'noexit','esc':'esc','portal':'portal','floor':'floor','kcap':'kcap','bsp':'bsplit','lnt veto':'lntv','pf':'pf'}
def jl(p):
    with p.open() as f:
        for l in f:
            if l.strip():yield json.loads(l)
def avg(a):return sum(a)/len(a) if a else None
def stat(a):
    a=[x for x in a if x is not None]
    return {'n':len(a),'mean':avg(a),'median':st.median(a) if a else None,'sd':st.stdev(a) if len(a)>1 else None,
            'q25':quantile(a,.25),'q75':quantile(a,.75)}
def quantile(a,q):
    if not a:return None
    a=sorted(a);p=(len(a)-1)*q;i=int(p);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(p-i)
def frac(n,d):return {'num':n,'den':d,'value':n/d if d else None}
def wilson(n,d):
    if not d:return [None,None]
    z=1.96;p=n/d;b=1+z*z/d;c=(p+z*z/(2*d))/b;h=z*math.sqrt(p*(1-p)/d+z*z/(4*d*d))/b;return[c-h,c+h]
def corr(a,b):
    if len(a)<3 or len(set(a))<2 or len(set(b))<2:return None
    ma,mb=avg(a),avg(b);va=sum((x-ma)**2 for x in a);vb=sum((x-mb)**2 for x in b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)
def cp(g,tm,r,field='heads'):return g[tm]['cp'].get(str(r),{}).get(field)
def onset(g,tm,f=.2):
    rows=sorted([a for a in g[tm]['sac'] if a[0]>=200]);total=sum(a[1] for a in rows)
    if total<10:return None
    run=0
    for a in rows:
        run+=a[1]
        if run>=total*f:return a[0]
def teamstats(gs,side,full=False):
    pairs=[(g,side(g)) for g in gs if side(g) in ['A','B']];N=len(pairs)
    t={'n':N,'curve':{},'cp':{},'phase':[],'sac':{},'kills':{},'exposure':[],'line':{}}
    for rr in ROUNDS+[300,400,500]:
        t['cp'][str(rr)]={f:stat([cp(g,s,rr,f) for g,s in pairs]) for f in ['heads','king','total','vor','enemyNear','raid']}
        if rr in ROUNDS:t['curve'][str(rr)]=t['cp'][str(rr)]['heads']
    for p in range(6):
        ps=[g[s]['phase'][p] for g,s in pairs if g[s]['phase'][p]['rounds']>0]
        sums={k:sum(a[k] for a in ps) for k in ['rounds','headRounds','eligibleHR','eligibleTurns','splits','birthsSmall','births22','nat','sacN','sacLen','sacDrops','raidHR']}
        sums['games']=len(ps);sums['splitSpeed']=frac(sums['splits'],sums['eligibleHR']);sums['splitTurnSpeed']=frac(sums['splits'],sums['eligibleTurns'])
        sums['naturalRate']=frac(sums['nat'],sums['rounds']);sums['raidShare']=frac(sums['raidHR'],sums['headRounds']);t['phase'].append(sums)
    t['eliminated']=sum(g[s]['cp']['500']['heads']==0 for g,s in pairs);t['eliminationRate']=frac(t['eliminated'],N)
    t['fullGames']=sum(g['rounds']==500 for g,s in pairs)
    t['elimRound']=stat([g['rounds']-1 for g,s in pairs if g[s]['cp']['500']['heads']==0])
    t['endingRound']=stat([g['rounds'] for g,s in pairs])
    for start in [0,250,300,350,450]:
        sacrifices=[a for g,s in pairs for a in g[s]['sac'] if a[0]>=start]
        t['sac'][str(start)]={'events':len(sacrifices),'length':sum(a[1] for a in sacrifices),'drops':sum(math.ceil(a[1]/2) for a in sacrifices),
          'toOwn':sum(a[2] for a in sacrifices),'toEnemy':sum(a[3] for a in sacrifices),'toLine':sum(a[4] for a in sacrifices),
          'nearAlly':stat([a[5] for a in sacrifices if a[5]!=999]),'nearLonger':stat([a[6] for a in sacrifices if a[6]!=999]),'nearLonger3':frac(sum(a[6]<=3 for a in sacrifices),len(sacrifices)),
          'games':sum(any(a[0]>=start for a in g[s]['sac']) for g,s in pairs)}
    t['sac']['first200']=stat([min([a[0] for a in g[s]['sac'] if a[0]>=200],default=None) for g,s in pairs])
    t['sac']['onset20']=stat([onset(g,s,.2) for g,s in pairs]);t['sac']['onset50']=stat([onset(g,s,.5) for g,s in pairs])
    for late in [False,True]:
        kills=[k for g,s in pairs for k in g[s]['kd'] if not late or k[0]>=300]
        out={'events':len(kills),'length':sum(k[1] for k in kills),'round':stat([k[0] for k in kills]),'causes':{}}
        for c in sorted({k[2] for k in kills}):
            ks=[k for k in kills if k[2]==c];out['causes'][c]={'n':len(ks),'r':stat([k[0] for k in ks]),'len':stat([k[1] for k in ks]),'killerLen':stat([k[3] for k in ks if k[3]>0]),'victim':sum(k[4]==0 for k in ks)}
        t['kills']['late' if late else 'all']=out
    for p in range(2):
        ex=[g[s]['exposure'][p] for g,s in pairs];v=[sum(a[k] for a in ex) for k in range(4)]
        t['exposure'].append({'games':sum(a[0]>0 for a in ex),'rounds':v[0],'near3':frac(v[1],v[0]),'near6':frac(v[2],v[0]),'distanceCapped30':frac(v[3],v[0])})
    fullpairs=[(g,s) for g,s in pairs if g['rounds']==500]
    t['line']['fullN']=len(fullpairs)
    for rr in [300,400]:
        t['line']['current'+str(rr)]=stat([cp(g,s,rr,'king') for g,s in fullpairs])
        t['line']['ancestor'+str(rr)]=stat([g[s]['line']['lens'].get(str(rr)) for g,s in fullpairs])
    t['line']['final']=stat([cp(g,s,500,'king') for g,s in fullpairs]);t['line']['sac300']=stat([g[s]['line']['lateEat'][1] for g,s in fullpairs])
    t['line']['natural300']=stat([g[s]['line']['lateEat'][0] for g,s in fullpairs])
    t['line']['growth300']=stat([(cp(g,s,500,'king')-cp(g,s,300,'king'))/200 for g,s in fullpairs])
    t['line']['ancestorGrowth300']=stat([(cp(g,s,500,'king')-g[s]['line']['lens']['300'])/200 for g,s in fullpairs if g[s]['line']['lens'].get('300') is not None])
    t['line']['growth400']=stat([(cp(g,s,500,'king')-cp(g,s,400,'king'))/100 for g,s in fullpairs])
    t['lateBirths']=stat([sum(p['birthsSmall'] for p in g[s]['phase'][3:]) for g,s in pairs if g['rounds']>250])
    t['late22']=stat([sum(p['births22'] for p in g[s]['phase'][3:]) for g,s in pairs if g['rounds']>250])
    return t
def features(g,tm):
    p=g[tm]['phase'];sumx=lambda k,a,b:sum(v[k] for v in p[a:b])
    d={'heads25':cp(g,tm,25),'heads50':cp(g,tm,50),'heads100':cp(g,tm,100),'heads250':cp(g,tm,250),
       'vor100':cp(g,tm,100,'vor'),'enemyNear100':cp(g,tm,100,'enemyNear'),
       'split0':p[0]['splits']/p[0]['eligibleHR'] if p[0]['eligibleHR'] and g['rounds']>=50 else None,
       'nat100':sumx('nat',0,2) if g['rounds']>=100 else None,
       'raid100':sumx('raidHR',0,2)/sumx('headRounds',0,2) if g['rounds']>=100 and sumx('headRounds',0,2) else None,
       'lateBirths':sumx('birthsSmall',3,6) if g['rounds']==500 else None,
       'lineSac300':g[tm]['line']['lateEat'][1] if g['rounds']==500 else None,
       'sac300Len':sum(a[1] for a in g[tm]['sac'] if a[0]>=300) if g['rounds']==500 else None,
       'king500':cp(g,tm,500,'king'),'onset20':onset(g,tm),
       'exposure6':sum(a[2] for a in g[tm]['exposure'])/sum(a[0] for a in g[tm]['exposure']) if sum(a[0] for a in g[tm]['exposure']) else None}
    return d
def paired(gs,metric):
    pairs=[];own=collections.defaultdict(lambda:[[],[]])
    for g in gs:
        if not g['winner']:continue
        w=g['winner'];l='B' if w=='A' else 'A';a,b=features(g,w).get(metric),features(g,l).get(metric)
        if a is not None and b is not None:pairs.append((g,a,b))
        for s in ['A','B']:
            x=features(g,s).get(metric)
            if x is not None:own[g['team'+s]][0 if s==w else 1].append(x)
    ds=[a-b for g,a,b in pairs];D=avg(ds);clusters=collections.defaultdict(list)
    for g,a,b in pairs:clusters[str(g.get('battleId',g['key']))].append(a-b)
    nc=len(clusters);se=math.sqrt(nc/(nc-1)*sum((sum(v)-len(v)*D)**2 for v in clusters.values())/len(ds)**2) if nc>1 else None
    eligible=[(team,avg(a)-avg(b),len(a),len(b)) for team,(a,b) in own.items() if len(a)>=5 and len(b)>=5]
    same=sum((v[1]>=0 if D>=0 else v[1]<=0) for v in eligible) if D is not None else 0
    sd=st.stdev(ds) if len(ds)>1 else None
    return {'n':len(pairs),'winner':avg([a for g,a,b in pairs]),'loser':avg([b for g,a,b in pairs]),'delta':D,
     'standardized':D/sd if sd else None,'positive':frac(sum(x>0 for x in ds),len(ds)),'battleClusters':nc,
     'ci95':[D-1.96*se,D+1.96*se] if se is not None else [None,None],
     'seatA':stat([a-b for g,a,b in pairs if g['winner']=='A']),'seatB':stat([a-b for g,a,b in pairs if g['winner']=='B']),
     'teamAgreement':frac(same,len(eligible)),'teamDeltas':eligible}
def ourstats(gs):
    t=teamstats(gs,lambda g:g['us']);N=len(gs);wins=sum(g['winner']==g['us'] for g in gs)
    nat=sum(sum(p['nat'] for p in g[g['us']]['phase']) for g in gs);enemy=sum(sum(p['nat'] for p in g['B' if g['us']=='A' else 'A']['phase']) for g in gs)
    t.update({'wins':wins,'winRate':frac(wins,N),'winCI':wilson(wins,N),'natural':nat,'enemyNatural':enemy,'intakeShare':frac(nat,nat+enemy),'intakeRatio':frac(nat,enemy),
      'seats':{s:{'n':sum(g['us']==s for g in gs),'wins':sum(g['us']==s and g['winner']==s for g in gs)} for s in ['A','B']},
      'opponents':{str(o):{'n':sum(g['oppId']==o for g in gs),'wins':sum(g['oppId']==o and g['winner']==g['us'] for g in gs)} for o in sorted({g['oppId'] for g in gs},key=str)}})
    return t
def mechanisms(gs,mc):
    result={};totalTurns=sum(g[g['us']]['turns'] for g in gs);pairs=[(g,mc[g['key']]) for g in gs if g['key'] in mc]
    for label,k in MK.items():
        v={f:0 for f in ['n','ex','okN','ok','sitN','sit','nat30','alive30N','alive30']};rawfire=0;rawapp=0;xs=[];ys=[];final=[];fireGames=0
        for g,c in pairs:
            a=c['by'].get(k,{})
            for f in v:v[f]+=a.get(f,0)
            b=g[g['us']]['mech'].get(label,{})
            rawfire+=b.get('n',0);rawapp+=b.get('applied',0)
            n=a.get('n',0);fireGames+=n>0;xs.append(n/max(1,g[g['us']]['turns'])*1000);ys.append(+(g['winner']==g['us']));final.append(cp(g,g['us'],500,'king'))
        v.update({'games':len(pairs),'fireGames':fireGames,'turns':totalTurns,'rawTagTurns':rawfire,'rawEnacted':rawapp,
          'per1000Turns':frac(v['n']*1000,totalTurns),'enactRate':frac(v['ex'],v['n']),'successRate':frac(v['ok'],v['okN']),
          'winCorrelation':corr(xs,ys),'kingCorrelation':corr(xs,final),'winCorrN':len(xs),
          'winFireRate':stat([x for x,y in zip(xs,ys) if y]),'lossFireRate':stat([x for x,y in zip(xs,ys) if not y])})
        # Opponent x wave strata remove the broad opponent/wave mean, not survival or opportunity confounding.
        strata=collections.defaultdict(list)
        for i,(g,c) in enumerate(pairs):strata[(g.get('wave'),g.get('oppId'))].append(i)
        ax=[];ay=[]
        for ix in strata.values():
            if len(ix)<2:continue
            mx=avg([xs[i] for i in ix]);my=avg([ys[i] for i in ix])
            ax += [xs[i]-mx for i in ix];ay += [ys[i]-my for i in ix]
        v['stratifiedWinCorrelation']=corr(ax,ay);v['stratifiedN']=len(ax)
        # Additive wave and opponent fixed effects are estimable although joint cells have one game.
        rx=xs[:];ry=ys[:]
        for _ in range(8):
            for field in ['wave','oppId']:
                groups=collections.defaultdict(list)
                for i,(g,c) in enumerate(pairs):groups[g.get(field)].append(i)
                for ix in groups.values():
                    mx=avg([rx[i] for i in ix]);my=avg([ry[i] for i in ix])
                    for i in ix:rx[i]-=mx;ry[i]-=my
        v['adjustedWinCorrelation']=corr(rx,ry);result[label]=v
    v={'games':len(pairs),'n':0,'okN':0,'ok':0,'rawTagTurns':0,'rawEnacted':0}
    for g,c in pairs:
        a=c['by'].get('fguard',{});v['n']+=a.get('f2N',0);v['okN']+=a.get('f2OkN',0);v['ok']+=a.get('f2Ok',0)
        a=g[g['us']]['mech'].get('F2',{});v['rawTagTurns']+=a.get('n',0);v['rawEnacted']+=a.get('applied',0)
    v['successRate']=frac(v['ok'],v['okN']);result['F2']=v;return result
def supplementstats(gs,side,supp):
    out={}
    for name in ['naturalEnemyTerr','bodyBlockedCapacity','generation']:
        out[name]=stat([supp.get(g['key'],{}).get(side(g),{}).get(name) for g in gs if side(g)])
    envs=[supp.get(g['key'],{}).get(side(g),{}).get('finalLineEnv') for g in gs if side(g)]
    envs=[e for e in envs if e];E=[sum(row[j] for e in envs for row in e) for j in range(9)]
    out['finalLineExposure']={'games':len(envs),'turns':E[0],'near3':frac(E[1],E[0]),'near6':frac(E[2],E[0]),'distance':frac(E[3],E[0])}
    return out
def decisionstats(gs,side,dec):
    rows=[dec[g['key']][side(g)] for g in gs if g['key'] in dec and side(g)]
    s={k:sum(r[k] for r in rows) for k in rows[0]} if rows else {};s['games']=len(rows)
    for name,num,den in [('splitEligible','split','eligibleW'),('safeSplitRate','safeSplit','safeEligibleW'),('lowExitSplitRate','lowExitSplitN','lowExitEligibleN'),('lowHeadsSplitRate','lowHeadsSplit','lowHeadsEligibleW'),('kingExposure6','kingNear6N','kingLateN'),('approachFamily30','approachF30','approachN'),('avoidFamily30','avoidF30','avoidN'),('B3Rate','adjacentLongestB3Taken','adjacentLongestB3N')]:s[name]=frac(s.get(num,0),s.get(den,0))
    return s
def clustering(atlas):
    labels=sorted(atlas);names=['heads100','heads250','earlySplit','earlyNatRate','lateBirths','sac300Len','onset20','finalKing500','elimination','raid100','exposure6']
    features0=[];ns=[]
    for label in labels:
        x=atlas[label];w=x['elite']['W'];p=w['phase'];v=[w['cp']['100']['heads']['mean'],w['cp']['250']['heads']['mean'],
          (p[0]['splits']+p[1]['splits'])/(p[0]['eligibleHR']+p[1]['eligibleHR']),
          (p[0]['nat']+p[1]['nat'])/(p[0]['rounds']+p[1]['rounds']),w['lateBirths']['mean'],
          w['sac']['300']['length']/max(1,w['n']),w['sac']['onset20']['mean'],w['line']['final']['mean'],
          x['eliminationRate']['value'],(p[0]['raidHR']+p[1]['raidHR'])/(p[0]['headRounds']+p[1]['headRounds']),
          (w['exposure'][0]['near6']['num']+w['exposure'][1]['near6']['num'])/max(1,w['exposure'][0]['near6']['den']+w['exposure'][1]['near6']['den'])]
        features0.append(v);ns.append([w['cp']['100']['heads']['n'],w['cp']['250']['heads']['n'],w['n'],w['n'],w['lateBirths']['n'],w['n'],w['sac']['onset20']['n'],w['line']['fullN'],x['n'],w['n'],sum(a['rounds'] for a in w['exposure'])])
    means=[avg([v[j] for v in features0 if v[j] is not None]) for j in range(len(names))]
    sds=[st.pstdev([v[j] for v in features0 if v[j] is not None]) or 1 for j in range(len(names))]
    X=[[(v[j]-means[j])/sds[j] if v[j] is not None else 0 for j in range(len(names))] for v in features0]
    distance=lambda a,b:math.sqrt(sum((x-y)**2 for x,y in zip(a,b))/len(names))
    D=[[distance(a,b) for b in X] for a in X]
    groups=[[i] for i in range(len(labels))];cuts={len(groups):[g[:] for g in groups]};merges=[]
    centroid=lambda g:[avg([X[i][j] for i in g]) for j in range(len(names))]
    while len(groups)>1:
        costs=[]
        for i,j in itertools.combinations(range(len(groups)),2):
            a,b=groups[i],groups[j];cost=len(a)*len(b)/(len(a)+len(b))*sum((x-y)**2 for x,y in zip(centroid(a),centroid(b)))
            costs.append((cost,i,j))
        cost,i,j=min(costs);a,b=groups[i],groups[j];merges.append({'a':[labels[v] for v in a],'b':[labels[v] for v in b],'wardCost':cost})
        groups=[g for k,g in enumerate(groups) if k not in [i,j]]+[sorted(a+b)];cuts[len(groups)]=[g[:] for g in groups]
    silhouettes={}
    for k in range(2,7):
        gs=cuts[k];v=[]
        for i in range(len(labels)):
            own=next(g for g in gs if i in g)
            if len(own)==1:v.append(0);continue
            a=avg([D[i][j] for j in own if i!=j]);b=min(avg([D[i][j] for j in g]) for g in gs if g!=own);v.append((b-a)/max(a,b))
        silhouettes[k]=avg(v)
    best=max(silhouettes,key=silhouettes.get)
    return {'labels':labels,'features':names,'rawFeatures':features0,'featureN':ns,'means':means,'sds':sds,'standardized':X,'distances':D,
      'cuts':{k:[[labels[i] for i in g] for g in gs] for k,gs in cuts.items() if 2<=k<=6},'merges':merges,'silhouettes':silhouettes,'bestK':best}
def main():
    start=time.time();raw=list(jl(O/'raw.jsonl'));by={r['key']:r for r in raw};mc={r['key']:r for r in jl(O/'mechanisms.jsonl')};supp={r['key']:r for r in jl(O/'supplement.jsonl')}
    dec={r['key']:r for f in [O/'decision-rows.jsonl',O/'decision-rows-online.jsonl'] for r in jl(f)}
    top=[r for r in raw if r['src']=='top'];valid=[r for r in top if not r['stall']];waves=[r for r in raw if r['src']=='online' and r['wave'] is not None];early=[r for r in raw if r['src']=='online' and r['wave'] is None]
    top6=[r for r in waves if r['oppId']!=545];dev=[r for r in waves if r['oppId']==545]
    loc=list(jl(O/'local-tasks.jsonl'));hashes={r['key']:hashlib.sha256(pathlib.Path(r['file']).read_bytes()).hexdigest() for r in loc};unique={}
    for r in loc:unique.setdefault(hashes[r['key']],r)
    local=[by[r['key']] for r in unique.values()]
    geo=json.loads((O/'geometry.json').read_text());atlas={}
    for key in sorted(geo):
        m,lay=key.rsplit('/',1);gs=[r for r in valid if r['map']==m and r['layout']==lay];ours=[r for r in top6 if r['map']==m and r['layout']==lay];ours7=[r for r in waves if r['map']==m and r['layout']==lay];olds=[r for r in early if r['map']==m and r['layout']==lay];win=[r for r in gs if r['winner']];elim=sum(r['endReason']=='teamEliminated' for r in gs)
        x={'geometry':geo[key],'n':len(gs),'topBefore':sum(r['map']==m and r['layout']==lay for r in top),'excluded':sum(r['map']==m and r['layout']==lay and bool(r['stall']) for r in top),'draws':len(gs)-len(win),
          'eliminations':elim,'eliminationRate':frac(elim,len(gs)),'full':sum(r['rounds']==500 for r in gs),
          'winnerSeats':{s:sum(r['winner']==s for r in gs) for s in ['A','B']},'teamN':len({r['team'+s] for r in gs for s in ['A','B']}),'battleN':len({r['battleId'] for r in gs})}
        x['elite']={s:teamstats(win,lambda g,s=s:g['winner'] if s=='W' else ('B' if g['winner']=='A' else 'A')) for s in ['W','L']}
        x['paired']={metric:paired(gs,metric) for metric in features(gs[0],'A')} if gs else {}
        x['supplement']={s:supplementstats(win,lambda g,s=s:g['winner'] if s=='W' else ('B' if g['winner']=='A' else 'A'),supp) for s in ['W','L']}
        x['decisions']={s:decisionstats(win,lambda g,s=s:g['winner'] if s=='W' else ('B' if g['winner']=='A' else 'A'),dec) for s in ['W','L']}
        x['ours']=ourstats(ours);x['oursAll7']=ourstats(ours7);x['dev']=ourstats([r for r in ours7 if r['oppId']==545]);x['early']=ourstats(olds)
        x['waves']={WN[i]:ourstats([r for r in ours if r['wave']==i]) for i in range(len(WAVE))}
        x['earlySets']={s:ourstats([r for r in olds if r['set']==s]) for s in sorted({r['set'] for r in early})}
        x['mechanisms']=mechanisms(ours7,mc);x['mechanismsTop6']=mechanisms(ours,mc);x['mechanismsW12']=mechanisms([r for r in ours7 if r['wave']==14],mc)
        x['decisionOurs']=decisionstats(ours,lambda g:g['us'],dec)
        locals0=[r for r in local if r['map']==m and r['layout']==lay];on=[r for r in locals0 if r['pfOn']];off=[r for r in locals0 if not r['pfOn']]
        x['local']={'n':len(locals0),'on':ourstats(on),'off':ourstats(off),'mechOn':mechanisms(on,mc),'indexedN':sum(r['map']==m and r['layout']==lay for r in raw if r['src']=='local')}
        # Choose the explicit full 42/42 matched population; variants, side, seed, opponent are identical.
        aa={r['key'].split(':',1)[1]:r for r in raw if r['src']=='local' and r['map']==m and r['layout']==lay and r['set']=='stack12-pf-ab'}
        bb={r['key'].split(':',1)[1]:r for r in raw if r['src']=='local' and r['map']==m and r['layout']==lay and r['set']=='stack12off-pf-ab'}
        pp=[(aa[k],bb[k]) for k in sorted(aa.keys()&bb.keys())]
        x['local']['matched']={'n':len(pp),'onWin':sum(a['winner']==a['us'] for a,b in pp),'offWin':sum(b['winner']==b['us'] for a,b in pp),
          'onElim':sum(cp(a,a['us'],500)==0 for a,b in pp),'offElim':sum(cp(b,b['us'],500)==0 for a,b in pp),
          'head100Delta':stat([cp(a,a['us'],100)-cp(b,b['us'],100) for a,b in pp if cp(a,a['us'],100) is not None and cp(b,b['us'],100) is not None]),
          'kingDelta':stat([cp(a,a['us'],500,'king')-cp(b,b['us'],500,'king') for a,b in pp]),
          'winDiscordant':[sum(a['winner']==a['us'] and b['winner']!=b['us'] for a,b in pp),sum(a['winner']!=a['us'] and b['winner']==b['us'] for a,b in pp)]}
        atlas[key]=x;print(key,'top',len(gs),'ours',x['ours']['wins'],len(ours),flush=True)
    pop={'raw':len(raw),'topIndex':len(top),'topUnique':len({r['key'] for r in top}),'topExcluded':len(top)-len(valid),'topRetained':len(valid),
      'topUnclassified':[{k:r.get(k) for k in ['key','map','rounds','layoutEvidence']} for r in valid if r['layout']=='?'],
      'topTeams':len({r['team'+s] for r in valid for s in ['A','B']}),'topBattles':len({r['battleId'] for r in valid}),
      'topDates':[min(r['at'] for r in top),max(r['at'] for r in top)],'waves':ourstats(waves),'top6':ourstats(top6),'dev':ourstats(dev),'early':ourstats(early),
      'waveSets':WAVE,'waveNames':WN,'mechanisms':len(mc),'mechanismChecks':dict(collections.Counter({k:sum(r['checks'].get(k,0) for r in mc.values()) for k in next(iter(mc.values()))['checks']})),
      'localIndexed':len(loc),'localUnique':len(local),'decisionsGames':len(dec),'decisionRows':sum(r['actualRows'] for r in dec.values()),
      'decisionMismatchGames':sum(r['actualRows']!=r['expectedRows'] for r in dec.values()),'rawFinalMismatch':sum(r['chk']['final'] for r in raw)}
    result={'population':pop,'atlas':atlas,'cluster':clustering(atlas)}
    (O/'stats.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));(O/'local-dedup.json').write_text(json.dumps({'indexed':len(loc),'unique':len(local),'hashByKey':hashes},indent=2))
    print('DONE seconds',round(time.time()-start),flush=True)
if __name__=='__main__':main()
