import json
from pathlib import Path

P=Path(__file__).resolve().parent
out={}
for gid in (1496851,1496852,1496857):
    d=json.loads((P/f'{gid}-detail.json').read_text())
    s=json.loads((P/f'{gid}-scan.json').read_text())
    assert s['bots']['A']=='21269'
    assert not s['anomalies']
    final={}
    for side,name in ((0,'us'),(1,'them')):
        bs={int(i):v['body'] for i,v in d['snaps'][str(s['last_round'])].items() if v['side']==side}
        final[name]=dict(alive=len(bs),total=sum(map(len,bs.values())),longest=max(map(len,bs.values()),default=0),queen_length=len(bs.get(d['queens'][side],[])))
        assert all(s['final'][name][k]==v for k,v in final[name].items())
    windows={}
    for lo,hi in ((0,100),(101,300),(301,499)):
        windows[f'{lo}-{hi}']={}
        for side,name in ((0,'us'),(1,'them')):
            ts=[t for t in d['turns'] if t['side']==side and lo<=t['r']<=hi]
            drop=sum(p['eater']==name and p['eat_round'] is not None and lo<=p['eat_round']<=hi for p in s['pearls'])
            empty=[t for t in ts if t['moves'] and not t['eats']]
            windows[f'{lo}-{hi}'][name]=dict(turns=len(ts),natural=sum(len(t['eats']) for t in ts)-drop,drop=drop,splits=sum(t['split'] for t in ts),empty_moves=len(empty),empty_no_adjacent_plain_pearl=sum(not t['adjacent_plain_pearls'] for t in empty))
    out[gid]=dict(final=final,windows=windows,queen_deaths=[{k:x[k] for k in ('id','round','cause','actor')} for x in s['deaths'] if x['id'] in d['queens']])
    if gid==1496851:
        ts=[t for t in d['turns'] if t['id']==1123]
        assert len(ts)==69 and sum(bool(t['eats']) for t in ts)==3
        assert sum(len(t['eats']) for t in ts)==3
        assert sum(p['eater_id']==1123 for p in s['pearls'])==3
        assert s['snapshots']['498']['us']['longest']==s['snapshots']['498']['them']['longest']==33
    if gid==1496857:
        assert all(v['us']['queen_length']<v['them']['queen_length'] for r,v in s['snapshots'].items() if int(r)>=437)
        assert s['snapshots']['436']['us']['queen_length']==s['snapshots']['436']['them']['queen_length']==30
        ts=[t for t in d['turns'] if t['id']==1 and t['r']>=395]
        assert len(ts)==105 and sum(len(t['eats']) for t in ts)==6
        assert not any(p['eater_id']==1 and p['eat_round']>=395 for p in s['pearls'])
(P/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS: replay bot IDs, terminal state, accounting, decisive rounds and report counts')
