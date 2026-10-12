"""Stream inherited caches, independently reconcile numbers, and retain useful diagnostics.

All joins use the frozen replay key. Caches have different collection cutoffs: they are
never treated as an additional game population. Side/checkpoint denominators are explicit.
"""
import pathlib,json,gzip,collections,math,time,subprocess
R=pathlib.Path(__file__).resolve().parents[2];O=R/'exp/map-atlas/cache'
def jl(p):
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:
        for l in f:
            if l.strip():yield json.loads(l)
def resources():
    import re
    m=subprocess.check_output(['memory_pressure'],text=True)
    d=subprocess.check_output(['df','-g','/'],text=True).splitlines()[-1].split()
    free=int(re.search(r'System-wide memory free percentage:\s*(\d+)%',m)[1])
    if free<10 or int(d[3])<20:raise SystemExit('PAUSED: resources')
def main():
    resources();raw={r['key']:r for r in jl(O/'raw.jsonl')};fi=json.loads((O/'ledger-fields.json').read_text())
    sets={r['set'] for r in raw.values() if r['src']=='online'}
    audits={};coverage={};extra={};trade={};errors=[];start=time.time()
    def compare(family,g,tm,metric,old,new):
        if old is None or new is None:return
        layout=g['map']+'/'+g['layout'];pop=g['src']
        if pop=='top':
            if g['stall']:return
            pop+='-W' if tm==g['winner'] else '-L' if g['winner'] else '-draw'
        elif g['src']=='online':pop='W12-ours' if g['set']=='cand-stack11-online' and tm==g['us'] else 'online-other'
        key='|'.join([family,layout,pop,metric]);v=audits.setdefault(key,{'n':0,'old':0.,'new':0.,'mismatch':0,'maxDiff':0.,'examples':[]})
        v['n']+=1;v['old']+=old;v['new']+=new;diff=abs(old-new)
        if diff>1e-6:
            v['mismatch']+=1;v['maxDiff']=max(v['maxDiff'],diff)
            if len(v['examples'])<3:v['examples'].append([g['key'],tm,old,new])
    for family in ['mass-ledger','intake-gap','endgame-king','supply-chain','econ-principles','conv-chain']:
        base=R/'.cache'/family
        names={'mass-ledger':['top-sample.jsonl'],'intake-gap':['top-p0.jsonl','top-p1.jsonl','top-p2.jsonl'],
               'endgame-king':['top.jsonl'],'supply-chain':['top-all.jsonl.gz'],
               'econ-principles':['top-all.jsonl'],'conv-chain':['top.jsonl','top2.jsonl']}[family]
        files=[base/n for n in names if (base/n).exists()]
        files += [f for s in sorted(sets) for f in [base/f'online-{s}.jsonl',base/f'online-{s}.jsonl.gz'] if f.exists()]
        seen=set();cov={'files':[str(f.relative_to(R)) for f in files],'rows':0,'unique':0,'matched':0,'topRetained':0,'online':0,'missing':0,'duplicates':0,'checks':collections.Counter()}
        for file in files:
            prefix=file.name.removeprefix('online-').removesuffix('.gz').removesuffix('.jsonl') if file.name.startswith('online-') else None
            for c in jl(file):
                cov['rows']+=1;k=str(c['key'])
                if k not in raw and prefix:k=prefix+':'+k
                if k in seen:cov['duplicates']+=1;continue
                seen.add(k);cov['unique']+=1
                if k not in raw:cov['missing']+=1;continue
                g=raw[k];cov['matched']+=1
                if g['src']=='top' and not g['stall']:cov['topRetained']+=1
                if g['src']=='online':cov['online']+=1
                for ck,value in c.get('chk',{}).items():
                    if isinstance(value,(float,int)):cov['checks'][ck]+=value
                e=extra.setdefault(k,{'A':{},'B':{}})
                for tm in ['A','B']:
                    t=c[tm];u=g[tm];x=e[tm]
                    if family=='mass-ledger':
                        for rr in [10,50,100,150,250,300,350,400]:
                            if str(rr) not in u['cp']:continue
                            for field,cf in [('heads','units'),('king','king')]:compare(family,g,tm,f'{field}{rr}',t['st'][cf][rr//10],u['cp'][str(rr)][field])
                        compare(family,g,tm,'finalKing',t['st']['king'][50],u['cp']['500']['king'])
                        compare(family,g,tm,'natural',sum(t['fl'][fi['eat_nat']]),sum(p['nat'] for p in u['phase']))
                        compare(family,g,tm,'splits',sum(t['fl'][fi['split_n']]),u['splits'])
                        compare(family,g,tm,'sacrificeLength',sum(t['fl'][fi['dl_sac']]),sum(p['sacLen'] for p in u['phase']))
                        li=t.get('lin')
                        if li and li.get('cp',{}).get('300'):
                            compare(family,g,tm,'lineSac300',li['cp']['300']['eat'][1],u['line']['lateEat'][1])
                            compare(family,g,tm,'lineLength300',li['cp']['300']['Lt'],u['line']['lens'].get('300'))
                        x['naturalOwnTerr']=sum(t['fl'][fi['nat_own']]);x['naturalEnemyTerr']=sum(t['fl'][fi['nat_enemy']])
                        x['deaths']={};x['deathLengths']={}
                        for cause in ['sac','trap','rammed','ram','enemyBody','allyHead','fault','sprintDeath']:
                            x['deaths'][cause]=sum(t['fl'][fi['dn_'+cause]])
                            x['deathLengths'][cause]=sum(t['fl'][fi['dl_'+cause]])
                    elif family=='intake-gap':
                        ti=0 if tm=='A' else 1
                        for p,(a,b) in enumerate([(0,5),(5,10),(10,25),(25,35),(35,45),(45,50)]):
                            compare(family,g,tm,f'eligibleHR{p}',sum(sum(h[a:b]) for h in c['HR'][ti][2:]),u['phase'][p]['eligibleHR'])
                            compare(family,g,tm,f'headRounds{p}',sum(sum(h[a:b]) for h in c['HR'][ti]),u['phase'][p]['headRounds'])
                        compare(family,g,tm,'natural',sum(t['eatNat']),sum(p['nat'] for p in u['phase']))
                        compare(family,g,tm,'splits',sum(t['splitN']),u['splits'])
                        # Capacity occupancy is theoretical attempted supply, not actual blocked spawns.
                        nph=6;ob=c.get('OB',[]);capr=c.get('CAPR',[])
                        if ob and capr:
                            x['bodyBlockedCapacity']=sum(ob[(ti*nph*3*3*2):((ti+1)*nph*3*3*2)])
                            x['totalCapacityExposure']=sum(capr)
                    elif family=='endgame-king':
                        for rr in ['300','350','400','450']:compare(family,g,tm,'lineLength'+rr,t.get('Lt',{}).get(rr),u['line']['lens'].get(rr))
                        compare(family,g,tm,'lineSac300',sum(v[1] for v in t['dec'][1:]),u['line']['lateEat'][1])
                        x['finalLineEnv']=t['env'];x['finalLineDec']=t['dec'];x['lineSacProximity']=t['lineSac'];x['generation']=t['gen']
                    elif family=='supply-chain':
                        ti=0 if tm=='A' else 1;pieces=[p for p in c['P'] if p[0]==ti and p[1]>=250]
                        compare(family,g,tm,'lateBirths',len(pieces),sum(p['birthsSmall'] for p in u['phase'][3:]))
                        compare(family,g,tm,'late22',sum(p[2]==2 and p[3]==4 for p in pieces),sum(p['births22'] for p in u['phase'][3:]))
                        x['latePieceLife']={'n':len(pieces),'alive30':sum(p[28] for p in pieces),'nat30':sum(p[27] for p in pieces),
                          'toOwn':sum(p[30] for p in pieces),'toBig':sum(p[31] for p in pieces),'toEnemy':sum(p[32] for p in pieces)}
                    elif family=='econ-principles':
                        x['econOccupation']=c['OCC'][(0 if tm=='A' else 9):(9 if tm=='A' else 18)]
                    elif family=='conv-chain':
                        old=sum(v for name,v in t.get('lineSac',{}).items() if name.startswith('sac|'))
                        compare(family,g,tm,'lineSac350',old,sum(u['line']['eat'][p][1] for p in [4,5]))
                        x['convChain']={'lineSac350':old,'generation':t['gen'],'lateSacDrops':sum(v[2] for name,v in t['agg'].items() if name.startswith('sac|') and not name.startswith('sac|p0|') and not name.startswith('sac|p250|'))}
                if family=='econ-principles' and (g['src']!='top' or not g['stall']):
                    layout=g['map']+'/'+g['layout']
                    for contact in c['C']:
                        # Two actors excluded from the local support counts.
                        own,enemy=contact[29],contact[32];d8=contact[18]-contact[19]
                        bucket='advantage' if d8>=3 else 'disadvantage' if d8<=-3 else 'balanced'
                        v=trade.setdefault(layout+'|'+g['src']+'|'+bucket,{'n':0,'own20':0,'enemy20':0,'net':0,'kingMover':0,'r':0,'Lm':0,'Lv':0,'LmSmall':0})
                        v['n']+=1;v['own20']+=own;v['enemy20']+=enemy;v['net']+=contact[3]-contact[2]+own-enemy
                        v['kingMover']+=contact[4];v['r']+=contact[0];v['Lm']+=contact[2];v['Lv']+=contact[3];v['LmSmall']+=contact[2]<=4
                if cov['matched']%1000==0:resources()
        cov['checks']=dict(cov['checks']);coverage[family]=cov
        print(family,{k:cov[k] for k in ['unique','matched','topRetained','online','missing','duplicates']},'seconds',round(time.time()-start),flush=True)
    for k,v in audits.items():v['oldMean']=v['old']/v['n'];v['newMean']=v['new']/v['n']
    (O/'cache-audit.json').write_text(json.dumps({'coverage':coverage,'metrics':audits,'trade':trade},ensure_ascii=False,indent=2))
    (O/'supplement.jsonl').write_text(''.join(json.dumps({'key':k,**v},ensure_ascii=False)+'\n' for k,v in extra.items()))
    print('DONE',sum(v['mismatch'] for v in audits.values()),'metric mismatches',flush=True)
if __name__=='__main__':main()
