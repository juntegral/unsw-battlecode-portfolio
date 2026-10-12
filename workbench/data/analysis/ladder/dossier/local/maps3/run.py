import sys,json,datetime
sys.dont_write_bytecode=True
from collections import defaultdict
from pathlib import Path
import analyze_fast as a
import analyze_complete as ac
import fit,renewal_fit,check,validate
OUT=a.OUT
if __name__=='__main__':
    inv=json.loads((OUT/'inventory.json').read_text());inv['examined_files']=len(list((a.ROOT/'data/online').rglob('*.replay')));inv['snapshot_local']=datetime.datetime.now().astimezone().isoformat();(OUT/'inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    a.extract()
    active=defaultdict(set)
    for l in (OUT/'observations-fast.jsonl').read_text().splitlines():
        r=json.loads(l);active[r['slug']].update(map(int,r['records']))
    (OUT/'active-orbits.json').write_text(json.dumps({s:sorted(v) for s,v in active.items()},indent=2)+'\n')
    ac.extract()
    fit.main()
    renewal_fit.main()
    validate.main()
    check.main()
