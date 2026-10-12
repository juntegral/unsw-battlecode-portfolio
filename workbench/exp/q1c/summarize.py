import json, statistics, re
from pathlib import Path
P=Path(__file__).parent
A=json.loads((P/'analysis.json').read_text())
def med(a): return statistics.median(a) if a else None
def metric(ts, field):
    tp=sum(t[field] and t['truth'] for t in ts); fp=sum(t[field] and not t['truth'] for t in ts)
    fn=sum(not t[field] and t['truth'] for t in ts); tn=len(ts)-tp-fp-fn
    return dict(N=len(ts),TP=tp,FP=fp,FN=fn,TN=tn,accuracy=(tp+tn)/len(ts) if ts else None,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
def crowd(gs, lo, hi):
    xs=[x['n'] for g in gs for x in g['crowd'] if lo<=x['r']<=hi]
    return dict(N=len(xs),median=med(xs),ge2=sum(x>=2 for x in xs),share=sum(x>=2 for x in xs)/len(xs) if xs else None)
S=dict(games={s:len(gs) for s,gs in A['sets'].items()},missing=A['missing'],historyErrors=A['historyErrors'],identity=A['identity'],groups={},backup={},safety={})
for s,gs in A['sets'].items():
    values=list(gs.values()); S['groups'][s]=dict(errors=[dict(key=g['key'],**e) for g in values for e in g['errors']],checks={k:sum(g['checks'].get(k,0) for g in values) for k in values[0]['checks']},violations=[dict(key=g['key'],**e) for g in values for e in g['mergeViolations']],cpuMissing=[],cpu=[],traps=[dict(key=g['key'],**t) for g in values for t in g['traps']])
    z=S['groups'][s]
    for g in values:
        side=g['key'].split(':')[2]; lines=[l for l in g['cpu'] if l.startswith('team '+side+' ')]
        if not lines:z['cpuMissing'].append(g['key'])
        for l in lines:z['cpu'].append(float(re.search(r'max ([\d.]+)M',l)[1]))
    z['cpuMax']=max(z['cpu'],default=None)
    if s not in ['c','on','self']:continue
    for population in ['primary','flip']:
        gv=[g for g in values if ('_flip:' in g['key'])==(population=='flip')]
        ts=[t for g in gv for t in g['sightTurns']]; rays=[t for g in gv for t in g['signalTurns']]
        send=[t for g in gv for t in { (t['r'],t['id']):t for t in g['signalTurns'] }.values()]
        p=[p for g in gv for p in g['propagation']]
        z[population]=dict(games=len(gv),belief=metric(ts,'belief'),rays=metric(rays,'bit'),senderTurns=metric(send,'bit'),relay=sum(t['relay'] for t in rays),directTrue=sum(t['direct'] for t in ts),visible=sum(t['visible'] for t in ts),receivedOnly=sum(t['belief'] and not t['direct'] for t in ts),propagation=dict(N=len(p),set=sum(t['set'] for t in p),delayMax=max((t['delay'] for t in p),default=None)),feeds=len([f for g in gv for f in g['feeds']]),queenFeeds=sum(f['toQueen'] for g in gv for f in g['feeds']),staleFeeds=[dict(key=g['key'],**f) for g in gv for f in g['feeds'] if f['toQueen'] and not f['enemyAlive']])
    table=[]
    for grouping in ['map','side','opp','period']:
        groups={}
        for g in values:
            opp,m,side,seed=g['key'].split(':')
            for t in g['sightTurns']:
                key={'map':m,'side':side,'opp':opp,'period':'0-299' if t['r']<300 else '300-429' if t['r']<430 else '430+'}[grouping]
                groups.setdefault(key,[]).append(t)
        table.extend(dict(grouping=grouping,key=k,**metric(v,'belief')) for k,v in groups.items())
    z['beliefTable']=table
    z['signalTable']=[]
    for grouping in ['map','side','opp','period']:
        groups={}
        for g in values:
            opp,m,side,seed=g['key'].split(':')
            for t in {(t['r'],t['id']):t for t in g['signalTurns']}.values():
                key={'map':m,'side':side,'opp':opp,'period':'0-299' if t['r']<300 else '300-429' if t['r']<430 else '430+'}[grouping]
                groups.setdefault(key,[]).append(t)
        z['signalTable'].extend(dict(grouping=grouping,key=k,**metric(v,'bit')) for k,v in groups.items())
    z['decay']=dict(turns=len([t for g in values for t in g['sightTurns']]),expired=sum(t['r']-max(t['seen'],t['heard'])>50 for g in values for t in g['sightTurns']),expiredTrue=sum(t['belief'] and t['r']-max(t['seen'],t['heard'])>50 for g in values for t in g['sightTurns']),noDirectTrue=sum(t['bit'] and not t['direct'] for g in values for t in g['signalTurns']))
    for population in ['primary','flip']:
        for comparison in ['off/b','off/c','b/on']:
            pairs=[p for p in A['pairs'] if p['comparison']==comparison and ('_flip:' in p['key'])==(population=='flip')]
            l,r=comparison.split('/'); common=[p for p in pairs if p['bothQueenAlive430']]
            ck=[p['key'] for p in common]
            z2=dict(N=len(pairs),commonN=len(common),keys=ck,checkpoints={},oneSidedAlive=[],crowd={},newTraps=[],queenDeaths=[])
            for cp in ['350','400','430']:
                ds=[p['backupDelta'][cp] for p in common if p['backupDelta'][cp] is not None]
                z2['checkpoints'][cp]=dict(N=len(ds),null=len(common)-len(ds),medianDelta=med(ds),positive=sum(x>0 for x in ds),zero=sum(x==0 for x in ds),negative=sum(x<0 for x in ds),raw=[dict(key=k,off=A['sets'][l][k]['backup'].get(cp),on=A['sets'][r][k]['backup'].get(cp)) for k in ck])
            for p in pairs:
                ga,gb=[A['sets'][s][p['key']] for s in [l,r]]
                alive=lambda g:not g['qDeath'] or g['qDeath']['r']>=430
                if alive(ga)!=alive(gb):z2['oneSidedAlive'].append(dict(key=p['key'],off=ga['qDeath'],on=gb['qDeath']))
                for t in gb['traps']:
                    if t['r'] not in [q['r'] for q in ga['traps']]:z2['newTraps'].append(dict(key=p['key'],**t))
                if ga['qDeath']!=gb['qDeath']:z2['queenDeaths'].append(dict(key=p['key'],off=ga['qDeath'],on=gb['qDeath']))
            for lo,hi in [(340,429),(430,480)]:
                ca=[A['sets'][l][p['key']] for p in pairs];cb=[A['sets'][r][p['key']] for p in pairs]
                matched=[(p['key'],x['r'],x['n'],y['n']) for p in pairs for x in A['sets'][l][p['key']]['crowd'] for y in A['sets'][r][p['key']]['crowd'] if x['r']==y['r'] and lo<=x['r']<=hi]
                z2['crowd'][str(lo)]=dict(off=crowd(ca,lo,hi),on=crowd(cb,lo,hi),matchedN=len(matched),increased=sum(y>x for k,rr,x,y in matched),decreased=sum(y<x for k,rr,x,y in matched),increaseKeys=sorted(set(k for k,rr,x,y in matched if y>x)))
            S['backup'][population+'/'+comparison]=z2
(P/'summary.json').write_text(json.dumps(S,indent=2)+'\n')
print(json.dumps({k:v for k,v in S.items() if k not in ['groups','backup']},indent=2))
for s,z in S['groups'].items():
    print(s, 'errors',len(z['errors']),'checks',z['checks'],'CPU',z['cpuMax'],'cpuMissing',len(z['cpuMissing']),'violations',len(z['violations']),'traps',z['traps'])
    for pop in ['primary','flip']:
        if pop in z:print(s,pop,json.dumps({k:v for k,v in z[pop].items() if k!='staleFeeds'}),'staleFeeds',len(z[pop]['staleFeeds']))
for k,z in S['backup'].items():
    print(k,json.dumps({f:v for f,v in z.items() if f not in ['checkpoints','queenDeaths','keys']}))
    for cp,x in z['checkpoints'].items():print(cp,{k:v for k,v in x.items() if k!='raw'})
