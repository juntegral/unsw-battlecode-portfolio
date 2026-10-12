import sys
sys.dont_write_bytecode = True
import json, importlib.util
from pathlib import Path
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
import ladder_replay as lr
spec=importlib.util.spec_from_file_location('prior_win_trace','data/codex/astra/sweep/0559/win1/analyze.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
OUT=Path(__file__).resolve().parent
JOBS=[(1501017,'data/online/live-one1/b1501017',21269,'B'),(1501018,'data/online/live-one1/b1501017',21269,'B'),(1501021,'data/online/live-one1/b1501017',21269,'B'),(1501671,'data/online/smoke/one12-c1-old',21330,'A'),(1501673,'data/online/smoke/one12-c1-old',21330,'A'),(1503501,'data/online/smoke/one12-p1-old',21330,'A'),(1503505,'data/online/smoke/one12-p1-old',21330,'A'),(1503507,'data/online/smoke/one12-p1-old',21330,'A'),(1503511,'data/online/smoke/one12-p1-old',21330,'A'),(1503361,'data/online/live-one1/b1503361',21330,'B'),(1504480,'data/online/smoke/one12-k1-old',21330,'A'),(1504481,'data/online/smoke/one12-k1-old',21330,'A')]
def score(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
def main():
    rows=[]
    for gid,folder,bot,side in JOBS:
        folder=Path(folder); rp=folder/f'M{gid}.replay'
        meta=json.loads((folder/f'game-{gid}.json').read_text())
        root=lr.replay.load(rp).root()
        assert int(root.text(1 if side=='A' else 2))==bot
        assert meta['team'+side+'Id']==1119
        original=lr.replay.load
        lr.replay.load=lambda _:type('Loaded',(),{'root':lambda _:root})()
        try: basic=lr.scan(rp,meta,str(folder),set())
        finally: lr.replay.load=original
        detail=prior.trace(root,gid)
        nonlead=[r for r,s in basic['snapshots'].items() if score(s['us'])<=score(s['them'])]
        lead=max(nonlead)+1 if nonlead else min(basic['snapshots'])
        assert all(score(s['us'])>score(s['them']) for r,s in basic['snapshots'].items() if r>=lead)
        qd=[d for d in basic['deaths'] if d['id'] in basic['queens'].values()]
        for d in qd:
            if d['reason']==3:d['cause']='head-on mover' if d['id']==d['actor'] else 'head-on hit'
        final=basic['final'];u,v=final['us'],final['them']
        dec='elimination' if not v['alive'] else 'queen' if u['queen_length']!=v['queen_length'] else 'longest' if u['longest']!=v['longest'] else 'total'
        row=dict(gid=gid,map=meta['mapName'],bot=bot,side=side,last=basic['last_round'],final=final,decided=dec,lead_forever_round_end=lead,last_nonleading=basic['snapshots'].get(max(nonlead)) if nonlead else None,qdeaths=qd,anomalies=basic['anomalies'],event_counts=detail['event_counts'])
        rows.append(row)
        basic['intervals']={str(k):v for k,v in basic['intervals'].items()}
        (OUT/f'{gid}-base.json').write_text(json.dumps(basic,ensure_ascii=False))
        (OUT/f'{gid}-trace.json').write_text(json.dumps(detail,ensure_ascii=False))
        print(json.dumps(row,ensure_ascii=False),flush=True)
        (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')

if __name__ == "__main__": main()
