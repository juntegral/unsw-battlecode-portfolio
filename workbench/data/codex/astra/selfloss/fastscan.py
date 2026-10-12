import os, sys
sys.dont_write_bytecode=True
from pathlib import Path
import analyze
sys.path.insert(0,str(Path(__file__).resolve().parent))
from concurrent.futures import ProcessPoolExecutor
if __name__=='__main__':
    (analyze.OUT/'fast.pid').write_text(str(os.getpid()))
    inv=analyze.inventory()
    analyze.OUT.joinpath('inventory-latest.json').write_text(analyze.json.dumps({a:{k:str(v) for k,v in fs.items()} for a,fs in inv.items()},indent=2))
    order=['mR08_vb','mR05_vb','mDone8','mJo5_vb','mDone7','mH62_vb','mHzr_vb']
    jobs=[(a,k,p) for a in order for k,p in sorted(inv[a].items()) if not (analyze.OUT/f'{a}--{k}.json').exists()]
    with ProcessPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(analyze.scan_one,*args) for args in jobs]
        for f in fs:f.result()
