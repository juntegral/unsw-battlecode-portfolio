import json, math, hashlib
from pathlib import Path
from collections import Counter
p=Path('data/analysis/ladder/dossier')
a=json.loads((p/'fingerprint.json').read_text())
rows=[json.loads(s) for s in (p/'per-game.jsonl').read_text().splitlines()]
assert a['source_sha256']==hashlib.sha256((p/'per-game.jsonl').read_bytes()).hexdigest()
assert a['rating_band_games']=={'<1900':215,'1900-2099':215,'2100+':70}
rates=a['rates']; assert len({(r['name'],r['window']) for r in rates})==len(rates)
assert len((p/'fingerprint.md').read_text().splitlines())<=80
ranked=sorted((r for r in rates if not r['context']),key=lambda r:(not r['consistent'],-r['relative_gap'],r['name'],r['window']))
assert all(r['rank']==i for i,r in enumerate(ranked,1))
assert a['top30']==[{'name':r['name'],'window':r['window']} for r in ranked[:30]]
for r in rates:
    for group in [r['pooled'],*r['rating_bands'].values(),*r['layouts'].values()]:
        for v in group.values():
            assert v['denominator']>=0
            assert v['value']==(v['numerator_scaled']/v['denominator'] if v['denominator'] else None)
    x,y=[r['pooled'][s]['value'] for s in ('us','them')]
    sg=None if x is None or y is None else (y>x)-(y<x)
    signs=[]
    for g in r['layouts'].values():
        x,y=[g[s]['value'] for s in ('us','them')]
        signs.append(None if x is None or y is None else (y>x)-(y<x))
    assert r['layouts_theirs_higher']==signs.count(1)
    assert r['layouts_theirs_lower']==signs.count(-1)
    assert r['layouts_tied']==signs.count(0)
    assert r['layouts_missing']==signs.count(None)
    bands=[]
    for g in r['rating_bands'].values():
        x,y=[g[s]['value'] for s in ('us','them')]
        bands.append(None if x is None or y is None else (y>x)-(y<x))
    assert r['consistent']==bool(sg and signs.count(sg)>=15 and all(s==sg for s in bands))
    wl=r['won_lost_layout_demeaned']
    residual_sum=sum(v['mean']*v['valid_games'] for v in wl.values() if v['mean'] is not None)
    assert abs(residual_sum)<1e-7,(r['name'],r['window'],residual_sum)
# Independent numerator/denominator and residual calculations for representative families.
for w in ('0-100','101-300'):
    tests=[('Blind direction kept',lambda r:(100*r['ranges'][w]['keeps'],r['ranges'][w]['keeps_eligible'])),('Death: wall',lambda r:(1000*r['ranges'][w]['deaths']['wall'],r['ranges'][w]['turns'])),('Splits per eaten pearl',lambda r:(r['ranges'][w]['splits'],r['ranges'][w]['pearls_eaten'])),('Portal-required birth-cohort harvest',lambda r:(100*r['ranges'][w]['portal_required_eaten'][r['relation']],r['ranges'][w]['portal_required_births']))]
    for name,fn in tests:
        out=next(r for r in rates if r['name']==name and r['window']==w)
        for s in ('us','them'):
            valid=[r for r in rows if r['relation']==s and fn(r)[1]]
            v=out['pooled'][s]
            assert v['numerator_scaled']==sum(fn(r)[0] for r in valid)
            assert v['denominator']==sum(fn(r)[1] for r in valid)
        valid=[r for r in rows if r['relation']=='us' and r['our_result'] in ('win','loss') and fn(r)[1]]
        means={l:sum(fn(r)[0]/fn(r)[1] for r in valid if r['layout_key']==l)/sum(r['layout_key']==l for r in valid) for l in {r['layout_key'] for r in valid}}
        for result in ('win','loss'):
            subset=[r for r in valid if r['our_result']==result]
            expected=sum(fn(r)[0]/fn(r)[1]-means[r['layout_key']] for r in subset)/len(subset)
            assert math.isclose(out['won_lost_layout_demeaned'][result]['mean'],expected,abs_tol=1e-10)
cache=json.loads((p/'work/fp_recount.json').read_text())
assert len(cache['games'])==500
for r in rows:
    c=cache['games'][str(r['game'])][r['relation']]
    assert c['game'].get('eaten',0)==r['game_counts']['pearls_eaten']
    for w in ('0-100','101-300'):
        assert c[w].get('eaten',0)==r['ranges'][w]['pearls_eaten']
        assert c[w].get('turns',0)==r['ranges'][w]['turns']
        assert 0<=c[w].get('drop_eaten',0)<=c[w].get('eaten',0)
print('PASS:',len(rates),'entries;',len(ranked),'ranked rates; 500 recounts; 30 table rows;',len((p/'fingerprint.md').read_text().splitlines()),'lines')
