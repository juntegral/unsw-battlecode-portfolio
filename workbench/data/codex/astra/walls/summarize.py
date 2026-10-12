import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent

def classify(d):
    c=d['closure'];t=d['history'][-1] if d['history'] else None
    tags=[];alternatives=[];distance=None
    if d['startfree']:
        # This certifies an alternative immediate action, not long-term survival.
        alternatives=[o for o in t['options'] if o['exits'] and o['seen'] and not o['portal']]
        tags.append('free_start')
        if not t['moves'] and alternatives:tags.append('legal_veto')
    if c and c['by']==d['id'] and c.get('step'):
        st=c['step'];alternatives=[o for o in st['options'] if o['exits'] and o['seen'] and not o['portal'] and o['n']!=st['dest']]
        if alternatives:tags.append('self_pocket_alternative')
        chosen=next((o for o in st['options'] if o['n']==st['dest']),None)
        if chosen and chosen['portal']:tags.append('portal_entry')
        if st['eat']:tags.append('pearl_entry')
        if st['L']>=4:tags.append('entry_length4plus')
        if (alternatives and chosen and chosen['portal'] and not chosen['seen'] and
            st['L']+int(st['eat'])<4 and not d['startfree'] and not d['queen'] and
            not (d['lastsplit'] and d['lastsplit']['event']>c['event'])):
            tags.append('portal_last_card')
    if c and c['by']!=d['id'] and c['by_side']==d['side'] and c.get('step') and c.get('actor_turn'):
        t=c['actor_turn'];st=c['step'];last={tuple(z) for z in c['last_cells']}
        distance=next((m['distance'] for m in t['mates'] if m['id']==d['id']),None)
        if t['moves'] and t['moves'][0]['event']==st['event']:
            alternatives=[]
            for o in t['options']:
                b=[o['n']]+t['body'] if o['eat'] else [o['n']]+t['body'][:-1]
                if last-{tuple(z) for z in b} and o['exits'] and o['seen'] and not o['portal']:
                    alternatives.append(o)
            if alternatives:
                tags.append('mate_closure_alternative')
                if distance==3:tags.append('mate_radius3')
    return dict(tags=tags,alternatives=alternatives,distance=distance)

def main():
    G=[json.loads(p.read_text()) for p in sorted(OUT.glob('game-*.json'))]
    verification=json.loads((OUT/'verification.json').read_text())
    qchecks={(c['gid'],c['id'],c['r']):c for g in verification['one11'] for c in g['chosen']}
    out={};flat=[]
    for g in G:
        for d in g['deaths']:
            a=classify(d);d['audit']=a
            qc=qchecks.get((g['gid'],d['id'],d['r']))
            if g['version']=='one11' and 'legal_veto' in a['tags']:
                assert qc is not None
                if not qc['safe_alternatives']:
                    a['tags'].remove('legal_veto');a['tags'].append('queen_protection_unresolved')
            flat.append(dict(gid=g['gid'],version=g['version'],opp=g['opp'],r=d['r'],id=d['id'],side=d['side'],L=d['L'],queen=d['queen'],
                             reason=d['reason'],classification=d['classification'],startfree=d['startfree'],blocked_for=d['blocked_for'],
                             closure_kind=d['closure']['kind'] if d['closure'] else '',
                             closer=d['closure']['by'] if d['closure'] else '',
                             tags=';'.join(a['tags']),alternatives=json.dumps(a['alternatives'],separators=(',',':')),
                             last_free_round=d['lastfree']['r'] if d['lastfree'] else '',
                             last_free_own_turn=max((h['r'] for h in d['history'] if h['options']),default=''),
                             closure_round=d['closure']['r'] if d['closure'] else '',
                             closure_cells=json.dumps(d['closure']['last_cells']) if d['closure'] else '',
                             blockers=json.dumps(d['closure']['blockers']) if d['closure'] else ''))
    for v in ('one8','one10','one11','all'):
        gs=[g for g in G if v=='all' or g['version']==v];row={'games':len(gs),'sides':[]}
        for s in (0,1):
            ds=[d for g in gs for d in g['deaths'] if d['side']==s];den=sum(g['turns'][s] for g in gs)
            counts=Counter(d['classification'] for d in ds);tags=Counter(t for d in ds for t in d['audit']['tags'])
            forced=[d for d in ds if not d['startfree']]
            who=Counter('none' if not d['closure'] else 'birth' if d['closure']['kind'] in ('initial','split') else 'self' if d['closure']['by']==d['id'] else 'mate' if d['closure']['by_side']==s else 'enemy' for d in forced)
            delays=Counter(str(d['blocked_for']) for d in forced)
            row['sides'].append(dict(turns=den,deaths=len(ds),wall=sum(d['reason']==0 for d in ds),body=sum(d['reason']==1 for d in ds),classes=dict(counts),rates={k:1000*n/den for k,n in counts.items()} if den else {},tags=dict(tags),closers=dict(who),blocked_rounds=dict(delays)))
        out[v]=row
    with (OUT/'deaths.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]) if flat else []);w.writeheader();w.writerows(flat)
    (OUT/'summary.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
