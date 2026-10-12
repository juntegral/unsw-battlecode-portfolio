import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from concurrent.futures import ProcessPoolExecutor
import analyze
sys.path.insert(0,str(Path(__file__).resolve().parent))

def one(args):
    arm,key,folder=args;target=analyze.OUT/f'{arm}--{key}.json'
    if target.exists():return
    root=analyze.replay.load(folder/'game.replay').root();fin=root.pointer(4);own=int(key[-1]);winner=fin.u16(6) if fin.u16(4)==1 else None
    ends=[]
    for s in [own,1-own]:
        p=fin.pointer(s);ends.append([p.i32(0),p.i32(8),p.i32(4),p.i32(12)])
    how='elim' if not all(e[0] for e in ends) else 'queen' if ends[0][3]!=ends[1][3] else 'longest' if ends[0][2]!=ends[1][2] else 'total'
    W,H=map(int,root.text(0).splitlines()[0].split()[1:3])
    g=dict(src=arm,folder=key,path=str(folder/'game.replay'),result='draw' if winner is None else 'win' if winner==own else 'loss',how=how,ends=ends,cells=W*H,bot=root.text(own+1),final_only=True,result_txt=(folder/'result.txt').read_text().strip(),initial=hashlib.sha256(root.text(0).encode()).hexdigest())
    tmp=target.with_suffix('.census-tmp');tmp.write_text(json.dumps(g));tmp.replace(target)
    print(arm,key,g['result'],flush=True)

if __name__=='__main__':
    inv=json.loads((analyze.OUT/'inventory-latest.json').read_text())
    jobs=[(a,k,Path(p)) for a in ['mDone7','mH62_vb','mHzr_vb'] for k,p in sorted(inv[a].items())]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for x in pool.map(one,jobs):pass
