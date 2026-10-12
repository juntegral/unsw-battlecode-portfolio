import json,gzip,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
O=Path(__file__).parent
def roles(g,t):
    if g['src']=='top':return ['elite-top10','elite-winner' if str(g['winner']).upper()==t else 'elite-loser']
    if g['src']=='local':return ['local-'+g['set'].split('-')[1],'local-v12']
    return ['ours-online','ours-v1' if g['set'].startswith('v1-') else 'ours-W0-W12']
def verify():
    T=json.loads((O/'tables.json').read_text());groups=defaultdict(list);keys=set();checks=Counter()
    for line in gzip.open(O/'games.jsonl.gz','rt'):
        g=json.loads(line);assert g['key'] not in keys;keys.add(g['key']);checks.update(g['checks'])
        for t in g['eligible']:
            for role in roles(g,t):groups[('global',role)].append((g,t));groups[(g['map']+'/'+g['layout'],role)].append((g,t))
    errors=[];count=0;independent={}
    def check(label,want,got):
        nonlocal count
        count+=1
        equal=want==got if want is None or isinstance(want,int) else got is not None and math.isclose(want,got,rel_tol=1e-10,abs_tol=1e-10)
        if not equal:errors.append({'label':label,'expected':want,'actual':got})
    for (m,role),rs in groups.items():
        b=T['globalCohorts'][role] if m=='global' else T['maps'][m]['cohorts'][role];check(f'{m} {role} N',len(rs),b['N']);independent.setdefault(m,{})[role]={'N':len(rs),'rounds':{}}
        for r in [5,10,20,25,30,50,100,200]:
            c=b['checkpoints'][str(r)];vs=[(g,t,g['cp'][str(r)]['teams'][t]) for g,t in rs]
            cov=[v['seen']/g['area'] for g,t,v in vs];mean=statistics.fmean(cov);check(f'{m} {role} r{r} coverage',mean,c['coverage']['mean'])
            for name,field,den in [('spawnCoverage','spawnSeen','spawnTiles'),('fountainCoverage','fountainSeen','fountainTiles')]:
                vals=[v[field]/g['truth'][den] for g,t,v in vs if g['truth'][den]>0];check(f'{m} {role} r{r} {name} N',len(vals),c[name]['N']);check(f'{m} {role} r{r} {name}',statistics.fmean(vals) if vals else None,c[name]['mean'])
            decision=sum(v['mask'] in (1,2,4) for g,t,v in vs);check(f'{m} {role} r{r} decided',decision,c['symmetry']['decidedN'])
            pp=[(g,p) for g,t,v in vs for p in g['cp'][str(r)]['processes'] if p['team']==t];check(f'{m} {role} r{r} process N',len(pp),c['process']['N'])
            process={}
            for mode in ['own','inherited','patch','summary']:
                vals=[p[mode]['seen']/g['area'] for g,p in pp];ds=c['process']['all'][mode]['coverage'];check(f'{m} {role} r{r} {mode} N',len(vals),ds['N']);check(f'{m} {role} r{r} {mode} mean',statistics.fmean(vals) if vals else None,ds['mean']);process[mode]=statistics.fmean(vals) if vals else None
            po={};fr={}
            for region in ['raw','mirrored']:
                for mode in ['optimistic','pessimistic','literalOptimistic']:
                    q=[v['geometry'][region][mode] for g,t,v in vs];ss={k:sum(v[k] for v in q) for k in ['tp','fp','fn']}
                    for k,n in ss.items():check(f'{m} {role} r{r} pocket {region} {mode} {k}',n,c['pockets'][region][mode][k])
                    po[region+'/'+mode]=ss
                correct=sum(v['geometry'][region]['frontier']['correct'] for g,t,v in vs);n=sum(v['geometry'][region]['frontier']['N'] for g,t,v in vs);check(f'{m} {role} r{r} frontier {region} correct',correct,c['frontier'][region]['correct']);check(f'{m} {role} r{r} frontier {region} N',n,c['frontier'][region]['N']);fr[region]={'correct':correct,'N':n}
            rates={}
            for gate in ['1','2','4','8']:
                rr=[v['rates'][gate] for g,t,v in vs if v['rates'] is not None];s={k:sum(v[k] for v in rr) for k in ['tp','fp','fn','rateN','resetSamples','orbitSamples','rateRelativeAbsoluteSum']}
                for k,n in s.items():check(f'{m} {role} r{r} rates {gate} {k}',n,c['rates'][gate][k])
                rates[gate]=s
            independent[m][role]['rounds'][r]={'coverageMean':mean,'decidedN':decision,'processN':len(pp),'processCoverage':process,'pockets':po,'frontier':fr,'rates':rates}
    check('games',len(keys),T['population']['games'])
    for k,v in checks.items():check('checks '+k,v,T['checks'][k])
    with gzip.open(O/'key-independent.json.gz','wt',encoding='utf8') as f:f.write(json.dumps(independent,ensure_ascii=False,indent=1)+'\n')
    (O/'verification-aggregate.json').write_text(json.dumps({'method':'independent streaming grouping, statistics.fmean, raw integer numerators and denominators; all cohorts/maps/rounds; no aggregate.py imports','games':len(keys),'comparisonN':count,'mismatchN':len(errors),'mismatches':errors[:100]},ensure_ascii=False,indent=1)+'\n')
    print('independent aggregate comparisons',count,'mismatches',len(errors))
if __name__=='__main__':verify()
