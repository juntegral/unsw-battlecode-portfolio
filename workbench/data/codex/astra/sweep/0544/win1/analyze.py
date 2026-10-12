import sys
sys.dont_write_bytecode = True
import json, gzip, importlib.util
from pathlib import Path
sys.path.insert(0,'tools')
sys.path.insert(0,'data/analysis/ladder/dossier/work')
import ladder_replay as lr
import o1_scan
spec=importlib.util.spec_from_file_location('prior_win_detail','data/codex/astra/sweep/0519/win1/analyze.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
OUT=Path(__file__).parent
for gid in (1493877,1493885,1493887,1493889):
    path=Path(f'data/online/smoke/one8-c2-old/M{gid}.replay')
    meta=json.loads((path.parent/f'game-{gid}.json').read_text())
    base=lr.scan(path,meta,str(path.parent),set());base.pop('intervals');base.pop('text')
    ledger=o1_scan.scan('win1',path,meta)
    detail=prior.detail(path)
    assert base['bots']['A']=='21126' and base['winner']=='A' and base['ours']=='A'
    assert [base['final'][s]['total'] for s in ('us','them')]==[x[1] for x in ledger['ends']]
    assert [base['final'][s]['total'] for s in ('us','them')]==[x['total'] for x in detail['rounds'][base['last_round']]]
    (OUT/f'{gid}.json.gz').write_bytes(gzip.compress(json.dumps(dict(base=base,ledger=ledger,detail=detail),ensure_ascii=False).encode(),compresslevel=5))
    print(json.dumps(dict(gid=gid,map=meta['mapName'],end=base['last_round'],final=base['final'],ahead=detail['permanent_ahead'],queens=detail['queens'],queen_deaths=[x for x in base['deaths'] if x['id'] in base['queens'].values()],logs=detail['logs']),ensure_ascii=False))
