import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).resolve().parent
for p in P.glob('m*--*.json'):
    if p.stat().st_size<500000:continue
    try:g=json.loads(p.read_text())
    except ValueError:continue
    if g.get('compacted'):continue
    d=g.get('detail',{})
    for key in ['all_dragons','leaders']:
        for v in d.get(key,{}).values():v.pop('lineage',None)
    g['compacted']=True
    tmp=p.with_suffix('.compact');tmp.write_text(json.dumps(g,separators=(',',':')));tmp.replace(p)
