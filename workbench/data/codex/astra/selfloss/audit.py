import sys,json,re,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
from summarize import readall,flow,first,write_tsv
P=Path(__file__).resolve().parent
data=readall();n=0;bad=[];results=[];ledger=[]
for arm,gs in data.items():
    for key,g in gs.items():
        n+=1;s=int(key[-1]);m=re.search(r'winner=(\S+)',g['result_txt']);winner=m[1];expected='draw' if winner=='draw' else 'win' if int(winner)==s else 'loss'
        if expected!=g['result']:bad.append(['winner',arm,key])
        m=re.search(r'final_lengths=(\d+),(\d+)',g['result_txt']);raw=list(map(int,m.groups()))
        if [g['ends'][0][1],g['ends'][1][1]]!=[raw[s],raw[1-s]]:bad.append(['total',arm,key])
        results.append(dict(arm=arm,key=key,result=g['result'],how=g['how'],cells=g['cells'],our_n=g['ends'][0][0],our_T=g['ends'][0][1],our_L=g['ends'][0][2],our_Q=g['ends'][0][3],opp_n=g['ends'][1][0],opp_T=g['ends'][1][1],opp_L=g['ends'][1][2],opp_Q=g['ends'][1][3]))
        if g.get('final_only'):continue
        prev=0
        for r in sorted(map(int,g['snaps'])):
            if r==0:continue
            for sd in (0,1):
                c=flow(g,prev,r,sd);a=g['snaps'][str(prev)][sd];b=g['snaps'][str(r)][sd]
                resid=b[1]-a[1]-sum(c['eat_'+z] for z in ['n','own','foe'])+c['death']+c['paid']
                nr=b[0]-a[0]-c['split']+c['ndeath']
                ledger.append(dict(arm=arm,key=key,side=sd,lo=prev,hi=r,resid=resid,unit_resid=nr))
                if resid or nr:bad.append(['ledger',arm,key,sd,prev,r,resid,nr])
            prev=r
write_tsv(P/'game-results.tsv',results);write_tsv(P/'audit-ledger.tsv',ledger)
build={x:hashlib.sha256((P/f'build-check/{x}/bot').read_bytes()).hexdigest() for x in ['one8-off','r08','one5-on','r05']}
out=dict(games=n,by_arm={a:len(g) for a,g in data.items()},ledger_intervals=len(ledger),failures=bad,build_sha256=build)
(P/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert not bad;assert build['one8-off']==build['r08'];assert build['one5-on']==build['r05']
