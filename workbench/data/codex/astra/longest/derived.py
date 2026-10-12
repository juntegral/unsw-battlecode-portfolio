from collections import Counter
from lineage import major_lineage

def candidate(d):
    return d['cause'] in ('stop','own body') and d['free']>0 and bool(d['near_longer']) and not (d.get('action') or {}).get('timeout')

def annotate(g):
    ds={d['id']:d for d in g['deaths']}
    deliveries=[]
    for e in g['eats']:
        d=ds.get(e['source'])
        if d and e['origin']=='own_drop' and candidate(d) and e['id'] in d['near_longer']:
            deliveries.append(dict(e,cause=d['cause']))
    g['deliveries']=deliveries
    for rr,ss in g['snapshots'].items():
        for side,x in enumerate(ss):
            if x['id'] is None:continue
            anc=major_lineage(g['all_dragons'][str(x['id'])]['lineage'])
            direct=[e for e in deliveries if e['id']==x['id'] and e['round']<=int(rr)]
            inherited=any(e['id']==a['id'] and e['round']<=a['round'] for a in anc for e in deliveries)
            x['feed_proxy_pearls']=len(direct)
            x['role']='queen' if x['id']==g['queens'][side] else 'fed' if direct else 'inherited-fed' if inherited else 'ordinary'
    for d in g['all_dragons'].values():
        d['feed_proxy_pearls']=sum(e['id']==d['id'] for e in deliveries)
    return g
