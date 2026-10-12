import json,gzip,base64,hashlib,collections,math,subprocess,time,re
from pathlib import Path
O=Path(__file__).parent
def guard():
    d=subprocess.check_output(['df','-k','.'],text=True).strip().splitlines()[-1].split();m=re.search(r'System-wide memory free percentage:\s*(\d+)%',subprocess.check_output(['memory_pressure','-Q'],text=True));return int(d[3])/1048576>=21 and m and int(m[1])>=10
def main():
    P=json.loads((O/'population.json').read_text());local=[t for t in P['tasks'] if t['src']=='local'];errors=[];cmpN=0;sampleEvents=0;scheduleN=0;unique=set();calendarErrors=[];symN=0
    def check(label,x,y):
        nonlocal cmpN
        cmpN+=1
        if isinstance(x,float):good=math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-10)
        else:good=x==y
        if not good:errors.append({'label':label,'expected':x,'actual':y})
    for t in local:
        while not guard():print('RESOURCE PAUSE',flush=True);time.sleep(30)
        a=json.load(gzip.open(O/'raw'/(hashlib.sha256(t['key'].encode()).hexdigest()[:20]+'.json.gz'),'rt'));W,H=a['M']['width'],a['M']['height'];N=W*H;gaps=a['gap'];spawn=[g[1]>0 for g in gaps];fount=[g[1]>0 and sum(g)/2<=12 for g in gaps];schedule=collections.defaultdict(list)
        expiry=[-2147483647]*N
        for r,k,c in a['trace']['countdowns']:
            ex=max(r,-1)+c
            if r>=0 and spawn[k]:
                scheduleN+=1
                if expiry[k]!=r:calendarErrors.append([t['key'],r,k,expiry[k],c])
            expiry[k]=ex;schedule[r].append((k,ex))
        expiry=[-2147483647]*N
        for k,e in schedule[-1]:expiry[k]=e
        def fresh():return {'last':[-9]*N,'ex':[-2147483647]*N,'n':[0]*N,'sum':[0]*N,'seen':[0]*N,'mask':7,'first':None}
        team={tm:fresh() for tm in 'AB'};state={};turns=a['trace']['turns'];rnow=-1
        def mirror(k,h):return (H-1-k//W if h in (1,2) else k//W)*W+(W-1-k%W if h in (0,2) else k%W)
        def observation(C,k,r):
            nonlocal sampleEvents
            old=C['ex'][k];ex=expiry[k];C['seen'][k]=1
            if spawn[k]:
                if C['last'][k]==r-1 and old==r and ex>old:
                    C['n'][k]+=1;C['sum'][k]+=ex-r;sampleEvents+=1
                    if C is team[t['us']]:unique.add((t['mapFile'],t['seed'],r,min(k,mirror(k,{'x':1,'y':0,'xy':2}[a['M']['symmetry']]))))
                C['last'][k]=r;C['ex'][k]=ex
        def estimate(C,gate):
            tp=fp=classified=rn=0;rel=0.0;samples=0;seen=0;fs=0;tr=er=0.0
            for k in range(N):
                if not C['seen'][k] or not spawn[k]:continue
                seen+=1;fs+=fount[k];samples+=C['n'][k];mu=sum(gaps[k])/2;tr+=1/mu;n=C['n'][k]
                if n>=gate:
                    classified+=1;mean=C['sum'][k]/n;tp+=mean<=12 and fount[k];fp+=mean<=12 and not fount[k];rn+=1;rel+=abs(mu/mean-1);er+=1/mean
            return {'tp':tp,'fp':fp,'fn':sum(fount)-tp,'classified':classified,'spawnSeen':seen,'fountainSeen':fs,'resetSamples':samples,'rateN':rn,'rateRelativeAbsoluteSum':rel,'trueSeenRate':tr,'estimatedRate':er}
        def snapshot(r):
            c=a['cp'][str(r)]
            for tm in 'AB':
                for gate in (1,2,4,8):
                    calc=estimate(team[tm],gate);ref=c['teams'][tm]['rates'][str(gate)]
                    for k,v in calc.items():check(f"{t['key']} r{r} {tm} gate{gate} {k}",v,ref[k])
            for p in c['processes']:
                C=state[p['id']]
                for gate in (2,4):
                    calc=estimate(C,gate);ref=p['rates'][str(gate)]
                    for k,v in calc.items():check(f"{t['key']} r{r} process{p['id']} gate{gate} {k}",v,ref[k])
        for r,id,tm,k in turns:
            if r!=rnow:
                if rnow in (0,5,10,20,25,30,50,100,200):snapshot(rnow)
                rnow=r
                if r>200:break
                for v,e in schedule[r]:expiry[v]=e
            if id not in state:state[id]=fresh()
            C=state[id];x,y=k%W,k//W
            for yy in range(y-3,y+4):
                for xx in range(x-3,x+4):v=yy%H*W+xx%W;observation(C,v,r);observation(team[tm],v,r)
        if rnow in (0,5,10,20,25,30,50,100,200):snapshot(rnow)
        for r in (0,5,10,20,25,30,50,100,200):
            if r>rnow and a['cp'][str(r)]['censored']:snapshot(r)
    out={'method':'independent per-round replay countdown calendar, independent modular windows and contiguous-reset sample estimator, all W1 games and both seats/processes','games':len(local),'comparisonN':cmpN,'mismatchN':len(errors),'mismatches':errors[:100],'resetCalendarEventN':scheduleN,'resetCalendarMismatchN':len(calendarErrors),'calendarMismatches':calendarErrors[:20],'sampleEventsIncludingBothSeatsAndProcesses':sampleEvents,'uniqueOurObservedOrbitResetsAcrossRepeatedSeedRunsBy200':len(unique),'seedMapConditionN':len({(t['mapFile'],t['seed']) for t in local})};(O/'verification-rates.json').write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n');print(out)
if __name__=='__main__':main()
