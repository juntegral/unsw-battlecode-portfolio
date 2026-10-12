import sys,json
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
LABELS={'one5-w1':'o5','one5-c1':'c5','one3-w1':'o3'}
allout={}
for label,short in LABELS.items():
    led=[json.loads(l) for l in (P/(label+'-ledger.jsonl')).read_text().splitlines()]
    mid={g['gid']:g for g in map(json.loads,Path('data/analysis/ladder/dossier/work/o1_mid-'+short+'.jsonl').read_text().splitlines())}
    extra={g['gid']:g for g in map(json.loads,(P/(label+'-scan-v2.jsonl')).read_text().splitlines())} if (P/(label+'-scan-v2.jsonl')).exists() else {}
    C=[Counter(),Counter()]; deaths=[Counter(),Counter()]; lens=[Counter(),Counter()]; bycause=Counter(); decomposition=Counter(); examples=[]
    for g in led:
        M=[Counter(),Counter()]
        for s,w,k,v in mid[g['gid']]['C']:
            if s<2 and w in (1,2): M[s][k]+=v
        for s in (0,1):
            a=g['snaps'].get('100',g['ends'])[s]; b=g['snaps'].get('300',g['ends'])[s]
            C[s].update(H100=a[0],H300=b[0],L100=a[1],L300=b[1],turns=M[s]['turns'])
            for e in g['eats']:
                if 101<=e[0]<=300 and e[1]==s: C[s]['eat_'+e[3]]+=1
            for d in g['deaths']:
                if 101<=d[0]<=300 and d[1]==s:
                    C[s]['deaths']+=1; C[s]['deadlen']+=d[2]; deaths[s][d[4]]+=1
                    lb=str(d[2]) if d[2]<5 else '5-9' if d[2]<10 else '10+'
                    lens[s][lb]+=1
                    if s==0: bycause[d[4],lb]+=1
                    C[s]['dead_age01']+=int(0<=d[7]<=1)
            for d in g['paids']:
                if 101<=d[0]<=300 and d[1]==s: C[s]['paid']+=d[3]
            C[s]['splits']+=sum(101<=d[0]<=300 and d[1]==s for d in g['splits'])
        t=[M[s]['turns'] for s in (0,1)]
        p=[M[s]['pearls nat'] for s in (0,1)]
        q=[p[s]/t[s] if t[s] else 0 for s in (0,1)]
        h=(t[1]-t[0])*(q[0]+q[1])/2
        eff=(q[1]-q[0])*(t[0]+t[1])/2
        assert abs(h+eff-(p[1]-p[0]))<1e-8
        decomposition['heads']+=h; decomposition['efficiency']+=eff
        if g['gid'] in extra:
            E=[Counter(),Counter()]
            for s,w,k,v in extra[g['gid']]['C']: E[s][k]+=v
            assert [E[s]['turns'] for s in (0,1)]==t,(label,g['gid'],'turns')
            for cl in ('blind','unreachable7','adjacent','reachable2+'):
                v=[E[s]['nat:'+cl]/t[s] if t[s] else 0 for s in (0,1)]
                decomposition['class '+cl]+=(v[1]-v[0])*(t[0]+t[1])/2
            for s in (0,1):
                assert sum(E[s]['nat:'+cl] for cl in ('blind','unreachable7','adjacent','reachable2+'))==p[s]
        examples.append(dict(gid=g['gid'],map=g['map'],start=g['snaps'].get('100',g['ends']),end=g['snaps'].get('300',g['ends']),heads=h,eff=eff,turns=t,nat=p))
    n=len(led)
    out={'games':n,'totals':C,'deaths':deaths,'dead_length_bins':lens,'our_cause_length':[[*k,v] for k,v in bycause.items()],
         'natural_decomp_per_game':{k:v/n for k,v in decomposition.items()},'games_ledger':examples}
    if extra:
        E=[Counter(),Counter()]; G=Counter(); G100=Counter(); G300=Counter(); misses=Counter(); blind=Counter()
        for g in extra.values():
            for s,w,k,v in g['C']: E[s][k]+=v
            for gr in g['ground']:
                if gr['r']>100:
                    for kind in ('spawn','pearls','natural'):
                        for k,v in gr[kind].items(): G[kind+':'+k]+=v
                for r,Cg in ((100,G100),(300,G300)):
                    if gr['r']==r:
                        for k,v in gr['spawn'].items(): Cg[k]+=v
        out.update(extra_games=len(extra),counts=E,ground=G,ground100=G100,ground300=G300)
    allout[label]=out
    print('\n',label,n,'extra',len(extra))
    for k in C[0].keys()|C[1].keys(): print(k, *(round(C[s][k]/n,3) for s in (0,1)))
    print('decomp',out['natural_decomp_per_game'])
    for k in sorted(deaths[0].keys()|deaths[1].keys()): print('death',k,*(round(100*deaths[s][k]/C[s]['turns'],4) for s in (0,1)))
    print('length bins',lens)
    if extra:
        print('ground',G,'r100',G100,'r300',G300)
        for k in sorted(E[0].keys()|E[1].keys()):
            if k.startswith(('D1','solo','class:','nat:')): print(k,*[E[s][k] for s in (0,1)])
(P/'summary.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2)+'\n')
