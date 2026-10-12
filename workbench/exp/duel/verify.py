"""Independent streaming table recount. No JS aggregator code is imported."""
import gzip,json,collections,pathlib,datetime,subprocess,os
OUT=pathlib.Path(__file__).resolve().parent
def guard():
    text=subprocess.check_output(['memory_pressure','-Q'],text=True)
    import re
    m=re.search(r'System-wide memory free percentage:\s*(\d+)%',text)
    st=os.statvfs(OUT)
    if not m or int(m[1])<10 or st.f_bavail*st.f_frsize<21*2**30:raise RuntimeError('RESOURCE PAUSE')
def labels(e,tm):
    role=('winner' if e.get('winner')==tm else 'loser') if e.get('winner') else 'draw'
    ls=[]
    if any(s in ('top','elite') for s in e['sources']) and not e.get('stall'):
        ls.append('population/'+role)
        if e['strict']: ls.append('strict/'+role)
        rank=e.get('rankA' if tm=='A' else 'rankB')
        if isinstance(rank,(int,float)) and 1<=rank<=10:ls.append('elite/'+role)
    if e.get('us')==tm:ls.extend(['ours','ours/'+('custom' if e['custom'] else 'known')])
    if e.get('under')==tm:
        ls.append('under/'+('custom' if e['custom'] else 'known'))
        if e.get('underAutoscrim'):ls.append('under/known_autoscrim')
    if e['custom']:ls.append('sprint_custom/'+role)
    return ls
def run():
    guard()
    T=json.loads((OUT/'tables.json').read_text());counts=collections.defaultdict(collections.Counter);patterns=collections.defaultdict(collections.Counter);features=collections.defaultdict(collections.Counter);N=0;roundStartFeatures=collections.defaultdict(collections.Counter);reasons=collections.defaultdict(collections.Counter)
    for line in gzip.open(OUT/'episodes.jsonl.gz','rt'):
        e=json.loads(line);N+=1
        if N%100000==0:guard()
        for i in e['ids']:
            tm=e['teamById'][str(i)];out=e['outcome']
            if out=='kill':out='kill' if e['detail']['killer']==i else 'killed'
            for label in labels(e,tm):
                if out in ('kill','killed'):reasons[(label,out)][e['detail']['reason']]+=1
                for k in (label,label+'|map='+e['map'],label+'|phase='+e['phase'],label+'|map='+e['map']+'|phase='+e['phase']):counts[k][out]+=1
                if e['attempts'] or e['flags']:
                    for p in ('cut_off','sprint_cut','wall_pin','coil','head_bait','pearl_bait'):
                        c=patterns[(label,p)];n=e['attempts'].get(p+':'+str(i),0)
                        c['attemptEpisodes']+=n>0;c['attemptEvents']+=n
                        c['killAfterAttempt']+=bool(n) and out=='kill';c['tradeAfterAttempt']+=bool(n) and out=='trade'
                        c['deathAfterAttempt']+=bool(n) and out in ('killed','other_death')
                        c['fatalFlag']+=bool(e['flags'].get(p));c['killExclusive']+=out=='kill' and e['detail'].get('pattern')==p
                a=e['startFeatures'].get(str(i));b=e['startFeatures'].get(str(next(x for x in e['ids'] if x!=i)))
                if a and b and not a.get('contestedAtEntry'):
                    diff=a['space']-b['space'];v={'lengthDifference':'shorter' if a['len']<b['len'] else 'longer' if a['len']>b['len'] else 'equal','order':'earlier' if a['firstInRound'] else 'later','spaceDifference':'low' if diff < -4 else 'high' if diff>4 else 'mid','sprintBudget':'0' if a['budget']==0 else '1' if a['budget']==1 else '2+','nearPearls':'0' if a['visiblePearls']==0 else '1-2' if a['visiblePearls']<=2 else '3+','nearAllies':'0' if a['ally8']==0 else '1' if a['ally8']==1 else '2+'}
                    for f,bin in v.items():
                        features[(label,f,bin)][out]+=1
                        if e['entryTiming']=='round_start':roundStartFeatures[(label,f,bin)][out]+=1
    mismatches=[]
    for k,c in counts.items():
        a=dict(c);b=T['groups'][k]['outcomes']
        if a!=b:mismatches.append({'group':k,'primary':b,'independent':a})
    if N!=T['population']['episodeN']:mismatches.append({'episodes':[T['population']['episodeN'],N]})
    for (label,out),c in reasons.items():
        primary=T['groups'][label]['killReasons' if out=='kill' else 'killedReasons']
        if dict(c)!=primary:mismatches.append({'killReason':label+'/'+out,'primary':primary,'independent':dict(c)})
    pattern_results={}
    for (label,p),c in patterns.items():
        primary=T['groups'][label]['patterns'][p];other={f:c[f] for f in primary}
        pattern_results[label+'/'+p]={'primary':primary,'independent':other}
        if primary!=other:mismatches.append({'pattern':label+'/'+p,'primary':primary,'independent':other})
    feature_checks=0
    for (label,f,b),c in features.items():
        a=T['groups'][label]['features'][f][b];feature_checks+=1
        if dict(c)!=a['outcomes'] or sum(c.values())!=a['N']:mismatches.append({'feature':label+'/'+f+'/'+b,'primary':a,'independent':dict(c)})
    tactical=None
    if (OUT/'tactical-tables.json').exists():
        TT=json.loads((OUT/'tactical-tables.json').read_text());tc=collections.defaultdict(collections.Counter);TN=0;heads=0
        for line in gzip.open(OUT/'contacts.jsonl.gz','rt'):
            e=json.loads(line);TN+=1;heads+=e['reason']=='H'
            if TN%100000==0:guard()
            for tm in ('A','B'):
                for label in labels(e,tm):
                    c=tc[label];c['N']+=1;c['headContacts']+=e['reason']=='H'
                    c['bodyKills']+=e['reason']=='O' and e['teamById'].get(str(e['killer']))==tm
                    c['bodyDeaths']+=e['reason']=='O' and e['teamById'].get(str(e['victim']))==tm
                    c['nearWallSelf']+=e['reason'] in ('W','S') and e['teamById'].get(str(e['victim']))==tm
        tactical={'primaryN':TT['N_records'],'independentN':TN,'headContactPrimary':T['verification']['primary']['enemyContacts'],'headContactIndependent':heads,'groups':{}}
        if heads!=T['verification']['primary']['enemyContacts']:mismatches.append({'directHeadContacts':[T['verification']['primary']['enemyContacts'],heads]})
        if TN!=TT['N_records']:mismatches.append({'tacticalN':[TT['N_records'],TN]})
        for k,c in tc.items():
            primary={f:TT['groups'][k][f] for f in ('N','headContacts','bodyKills','bodyDeaths','nearWallSelf')};other={f:c[f] for f in primary};tactical['groups'][k]={'primary':primary,'independent':other}
            if primary!=other:mismatches.append({'tacticalGroup':k,'primary':primary,'independent':other})
    result={'at':datetime.datetime.now().astimezone().isoformat(),'primaryEpisodeN':T['population']['episodeN'],'independentEpisodeN':N,'groups':{k:{'primary':T['groups'][k]['outcomes'],'independent':dict(v)} for k,v in counts.items()},'patterns':pattern_results,'featureCellsChecked':feature_checks,'tactical':tactical,'mismatches':mismatches}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('RECOUNT',N,'groups',len(counts),'mismatches',len(mismatches))
    if mismatches:raise SystemExit(1)
if __name__=='__main__':run()
