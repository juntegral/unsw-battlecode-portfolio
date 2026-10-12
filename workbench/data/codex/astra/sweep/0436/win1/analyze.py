import sys
sys.dont_write_bytecode = True
import importlib.util, json
from pathlib import Path
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prior_won_reader', OUT.parents[1]/'0410/win1/analyze.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
reader.OUT = OUT
JOBS = [(1486055, 'data/online/live-one1/b1486051'), *[(i,'data/online/smoke/one9-k1-old') for i in (1487475,1487476,1487477,1487480,1487481,1487482,1487483,1487484,1487485,1487487)],(1488287,'data/online/live-one1/b1488287')]
rows = [json.loads((OUT/f'{gid}.json').read_text()) if (OUT/f'{gid}.json').is_file() else reader.scan(gid,folder) for gid,folder in JOBS]
for r in rows:
    expected = 21126 if r['gid'] == 1486055 else 21165
    assert int(r['bot']) == expected
    end = r['ledger']['ends']
    root = reader.replay.load(r['path']).root()
    result = root.pointer(4)
    assert result.bit(0)
    for s in (0,1):
        st = result.pointer(s)
        assert end[s][:4] == [st.i32(0),st.i32(8),st.i32(4),st.i32(12)]
(OUT/'summary.json').write_text(json.dumps([dict(gid=r['gid'], bot=json.loads(r['bot']), map=r['meta']['mapName'],how=r['ledger']['how'],last=r['ledger']['last'],ends=r['ledger']['ends'],ahead=r['ahead_for_good'],queenDeaths=r['queenDeaths'],risks=r['risks'],logs=r['logs'],signatures=r['signatureCounts']) for r in rows], ensure_ascii=False,indent=2)+'\n')
