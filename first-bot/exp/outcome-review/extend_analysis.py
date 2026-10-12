#!/usr/bin/env python3
"""Additional census estimates for readable conclusions. No sampled games."""
import json,math,statistics as S,collections,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
A=json.load(open(C/'analysis.json'));G=[json.loads(l) for l in open(C/'games.jsonl') if l.strip()]
def wilson(k,n):
    if not n:return [None,None]
    z=1.95996398454;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]
def tcrit(df):
    vals=[0,12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042]
    return vals[df] if df<=30 else 1.96+(1.96**3+1.96)/(4*df)
def dist(a):
    a=[x for x in a if x is not None];n=len(a)
    if not n:return {'n':0,'mean':None,'ci':[None,None]}
    m=S.mean(a);h=tcrit(n-1)*S.stdev(a)/math.sqrt(n) if n>1 else None
    return {'n':n,'mean':m,'ci':[m-h,m+h] if h is not None else [None,None]}
def cf(a,b,x):
    qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap;d=1/(d if abs(d)>1e-300 else 1e-300);h=d
    for m in range(1,201):
        aa=m*(b-m)*x/((qam+2*m)*(a+2*m));d=1+aa*d;d=d if abs(d)>1e-300 else 1e-300;c=1+aa/c;c=c if abs(c)>1e-300 else 1e-300;d=1/d;h*=d*c
        aa=-(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m));d=1+aa*d;d=d if abs(d)>1e-300 else 1e-300;c=1+aa/c;c=c if abs(c)>1e-300 else 1e-300;d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<3e-14:break
    return h
def ibeta(a,b,x):
    if x<=0:return 0.
    if x>=1:return 1.
    bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    return bt*cf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-bt*cf(b,a,1-x)/b
def pvalue(t,df):return ibeta(df/2,.5,df/(df+t*t))
def write(p,x):
    with open(p,'x')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
features=['ourHeads10','ourHeads50','ourHeads100','ourHeads250','naturalRatio','ourFinal','ourLineage300','ourSacrifices','ourLineSac300','ourLineSacAll','ourLatePieces','ourExposure','eliminationRound']
trends={}
for f in features:
    points=[]
    for w in A['waveNames']:
        rs=[r for r in G if r['wave']==w and r[f] is not None]
        if rs:points.append((rs[0]['waveOrder'],S.mean(r[f] for r in rs),len(rs)))
    n=len(points);xbar=S.mean(x for x,y,k in points);ybar=S.mean(y for x,y,k in points);xx=sum((x-xbar)**2 for x,y,k in points)
    b=sum((x-xbar)*(y-ybar) for x,y,k in points)/xx;a=ybar-b*xbar
    sd=math.sqrt(sum((y-a-b*x)**2 for x,y,k in points)/(n-2));se=sd/math.sqrt(xx);h=tcrit(n-2)*se;t=b/se if se else 0
    trends[f]={'waveN':n,'gameN':sum(k for x,y,k in points),'slopePerWave':b,'slopeCI':[b-h,b+h],'p':pvalue(t,n-2),'points':points}
ordered=sorted(trends,key=lambda k:trends[k]['p']);q=1.
for rank in range(len(ordered),0,-1):
    k=ordered[rank-1];q=min(q,trends[k]['p']*len(ordered)/rank);trends[k]['BHq']=q
classes={}
for k,z in A['classes'].items():
    if k.startswith('win:'):den=A['population']['all']['W']
    elif k.startswith('near:'):den=sum(r['outcome']=='L' and r['theirFinal']>0 and r['ourFinal']>0 for r in G)
    else:den=sum(r['outcome']=='L' and r.get('leadClass') is not None for r in G)
    classes[k]={'n':z['n'],'denominator':den,'share':z['n']/den,'CI':wilson(z['n'],den)}
latest=A['waveNames'][-1];position={}
fields=features+['ourNatural','theirNatural','ourKing300','theirKing300','theirHeads100','theirHeads250','theirFinal','theirLineage300','theirLineSac300','theirLatePieces','theirExposure']
for group in ['top6','DEV','top7']:
    for family in ['all','r500','elim']:
        rr=[r for r in G if r['wave']==latest and (group=='top7' or (r['opponent']!=545)==(group=='top6')) and (family=='all' or r['family']==family)]
        position[group+'-'+family]={'n':len(rr),'indicators':{f:dist(r[f] for r in rr) for f in fields}}
near={}
for era in ['waves','history','all']:
    rr=[r for r in G if (era=='all' or r['era']==era) and r['outcome']=='L' and r.get('nearClass')]
    positive=[r for r in G if (era=='all' or r['era']==era) and r['outcome']=='L' and r['ourFinal']>0 and r['theirFinal']>0]
    terms=sorted({k for r in rr for k in r.get('gapTerms',{})})
    near[era]={'n':len(rr),'positiveLongestLossN':len(positive),'shareCI':wilson(len(rr),len(positive)),'terms':{k:dist(r['gapTerms'][k] for r in rr if k in r.get('gapTerms',{})) for k in terms},'gap':dist(r['theirFinal']-r['ourFinal'] for r in rr)}
lever=[]
for label,f,scale in [('r100 heads +1 ratio x2','headLogRatio100',math.log(2)),('Natural intake +1 ratio x2','fullLogNaturalRatio',math.log(2)),('Current king lead +5 at r300','currentKingDifference300',1),('Final-line own sacrifice lead +10 pearls','lineSacDifference',1),('Late pieces +1 ratio x2','birthLogRatio',math.log(2)),('Final-line exposure difference -20pp','exposureDifference',-1)]:
    m=A['models'].get('single-adjusted:'+f,{})
    if m.get('coefficients'):
        z=m['coefficients'][0];b=z['beta']*scale;c=sorted(t*scale for t in z['betaCI']);lever.append({'label':label,'feature':f,'OR':math.exp(b),'CI':[math.exp(t) for t in c],'N':m['informativeN'],'strata':m['strata'],'clusters':m['clusters'],'completeN':m['completeN']})
out={'featureWaveTrends':trends,'classProportions':classes,'latestWave':latest,'latestPosition':position,'nearMissAccounting':near,'leverScaledOR':lever}
write(C/'extensions.json',out)
print(json.dumps({'trends':{k:{a:z[a] for a in ['slopePerWave','slopeCI','BHq']} for k,z in trends.items()},'leverScaledOR':lever},ensure_ascii=False))
