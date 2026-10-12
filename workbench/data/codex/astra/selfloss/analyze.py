import sys
sys.dont_write_bytecode = True
import json, re, hashlib, csv, importlib.util
from pathlib import Path
from collections import Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/analysis/ladder/dossier/online', 'data/codex/astra/longest']
import o1_scan
from ladder_replay import replay
spec = importlib.util.spec_from_file_location('longest_detail', 'data/codex/astra/longest/analyze.py')
detailmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detailmod)
OUT = Path('data/codex/astra/selfloss')
RUNS = Path.home() / 'meow-redteam/solo/runs'
ARMS = ['mJo5_vb','mDone8','mDone7','mH62_vb','mHzr_vb','mR08_vb','mR05_vb']

def inventory():
    found = {}
    for arm in ARMS:
        found[arm] = {p.parent.name: p.parent for p in (RUNS/arm).glob('*/result.txt') if (p.parent/'game.replay').exists()}
    keep = set(found['mDone7']) & (set(found['mH62_vb']) | set(found['mHzr_vb']))
    for arm in ['mH62_vb','mHzr_vb']:
        found[arm] = {k:v for k,v in found[arm].items() if k in keep}
    return found

def signature(path):
    root = replay.load(path).root()
    rounds, actions, physical = {}, [], []
    r = -1; actor = None
    def save():
        if r >= 0:
            rounds[r] = dict(actions=actions[:], physical=hashlib.sha256(repr(physical).encode()).hexdigest())
    for ev in root.pointer(3):
        k = ev.u16(0); p = ev.pointer(0)
        if k == 0:
            save(); r=p.i32(0); actions=[]; physical=[]
        elif k == 1: actor=p.i32(0)
        elif k == 4:
            a=p.pointer(0)
            actions.append([actor, a.u16(0) if a else None, list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [], a.i32(4) if a else 0])
        elif k == 3: physical.append((k,p.u32(0),replay.point(p.pointer(0))))
        elif k == 9: physical.append((k,p.i32(0),replay.point(p.pointer(0)),replay.point(p.pointer(1))))
        elif k == 10: physical.append((k,p.i32(0),p.i32(4),tuple(replay.point(c) for c in p.pointer(0)),tuple(replay.point(c) for c in p.pointer(1))))
        elif k == 11: physical.append((k,p.i32(0),p.u16(4)))
    save()
    return dict(initial=hashlib.sha256(root.text(0).encode()).hexdigest(), rounds=rounds)

def scan_one(arm,key,folder):
    target=OUT/f'{arm}--{key}.json'
    if target.exists(): return
    side=int(key[-1]); j=dict(id=0,teamAId=1119 if side==0 else 1,teamBId=1 if side==0 else 1119,mapName=key.rsplit('-seed',1)[0],teamAName='A',teamBName='B')
    path=folder/'game.replay'
    loader=replay.load
    loaded=loader(path)
    replay.load=lambda p:loaded
    try:
        g=o1_scan.scan(arm,path,j)
        g['folder']=key;g['path']=str(path);g['result_txt']=(folder/'result.txt').read_text().strip()
        if arm not in ['mDone7','mH62_vb','mHzr_vb'] and g['last']>=200:g['detail']=detailmod.detail(path,j,g)
        g['signature']=signature(path)
    finally:replay.load=loader
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(g,separators=(',',':')));tmp.replace(target)
    print(arm,key,g['result'],flush=True)

def main():
    inv=inventory(); (OUT/'inventory.json').write_text(json.dumps({a:{k:str(v) for k,v in fs.items()} for a,fs in inv.items()},indent=2))
    for arm,fs in inv.items():
        for n,(key,folder) in enumerate(sorted(fs.items())):
            target=OUT/f'{arm}--{key}.json'
            if target.exists(): continue
            side=int(key[-1]); j=dict(id=0,teamAId=1119 if side==0 else 1,teamBId=1 if side==0 else 1119,mapName=key.rsplit('-seed',1)[0],teamAName='A',teamBName='B')
            path=folder/'game.replay'; g=o1_scan.scan(arm,path,j)
            g['folder']=key; g['path']=str(path); g['result_txt']=(folder/'result.txt').read_text().strip()
            if arm not in ['mDone7','mH62_vb','mHzr_vb']:
                g['detail']=detailmod.detail(path,j,g)
            g['signature']=signature(path)
            target.write_text(json.dumps(g,separators=(',',':')))
            print(arm,n+1,len(fs),key,g['result'],flush=True)
    print('DONE',flush=True)

if __name__=='__main__':main()
