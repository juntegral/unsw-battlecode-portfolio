import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
from analyze import OUT, IDS

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    threat = module('threat_reader', 'data/codex/astra/audit-threat/audit.py')
    hunt = module('hunt_reader', 'data/codex/astra/audit-hunt/analyze.py')
    threat.OUT = OUT
    for gid in IDS:
        rp = Path(f'data/online/smoke/one10-k1-old/M{gid}.replay')
        meta = json.loads(rp.with_name(f'game-{gid}.json').read_text())
        job = dict(gid=gid, path=str(rp), meta=meta, bot='21200', version=10)
        threat_path = OUT / f'g{gid}.json'
        if not threat_path.exists():
            t = threat.scan(job)
            print('threat', gid, t['qfinal'], flush=True)
        hunt_path = OUT / f'hunt-{gid}.json'
        if not hunt_path.exists():
            job['version'] = 'one10'
            h = hunt.trace(job)
            hunt_path.write_text(json.dumps(h, ensure_ascii=False, separators=(',', ':')) + '\n')
            print('hunt', gid, len(h['reach']), h['checks'], flush=True)

if __name__ == '__main__':
    main()
