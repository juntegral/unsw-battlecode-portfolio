import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import local
name=sys.argv[1]
for a in sys.argv[2:]:
    g=local.rows(a).get(name)
    if not g:print(a,'no game');continue
    E=[e['r'] for e in g['eats'] if e['side']==0]
    ids=sorted({t['id'] for t in g['turns'] if t['side']==0 and t['r']<=1})
    print(a,g['result'][:70],'| our first eats',E[:5],'| their first eats',[e['r'] for e in g['eats'] if e['side']==1][:3])
    for i in ids[:3]:
        tr=[t for t in g['turns'] if t['id']==i and t['r']<=48]
        print('   id',i,' '.join('%d:%d,%d'%(t['r'],t['h'][0],t['h'][1]) for t in tr[::3]))
