import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('won_reader', OUT.parents[1] / '0410/win1/analyze.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
reader.OUT = OUT
IDS = (1489831, 1489832, 1489833, 1489834, 1489835, 1489837,
       1489838, 1489839, 1489840, 1489841, 1489842, 1489843)

def main():
    rows = []
    for gid in IDS:
        path = OUT / f'{gid}.json'
        r = json.loads(path.read_text()) if path.exists() else reader.scan(gid, 'data/online/smoke/one10-k1-old')
        assert int(r['bot']) == 21200
        assert r['meta']['teamAId'] == 1119 and r['meta']['teamBId'] == 989
        result = reader.replay.load(r['path']).root().pointer(4)
        assert result.bit(0) and result.u16(4) == 1 and result.u16(6) == 0
        for s in (0, 1):
            st = result.pointer(s)
            assert r['ledger']['ends'][s][:4] == [st.i32(0), st.i32(8), st.i32(4), st.i32(12)]
        rows.append(dict(gid=r['gid'], bot=int(r['bot']), map=r['meta']['mapName'],
                         how=r['ledger']['how'], last=r['ledger']['last'], ends=r['ledger']['ends'],
                         ahead=r['ahead_for_good'], queenDeaths=r['queenDeaths'],
                         risks=r['risks'], logs=r['logs'], signatures=r['signatureCounts']))
    (OUT / 'summary.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')

if __name__ == '__main__':
    main()
