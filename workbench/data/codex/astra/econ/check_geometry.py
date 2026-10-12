import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/approach')
from scan import Board
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
out=[]
for p in sorted(O.glob('game-*.json')):
    g=json.loads(p.read_text());b=Board(g['path'])
    bad=sum(c not in b.adj[n] for c,ns in b.adj.items() for n in ns if n is not None)
    assert bad==0,(g['gid'],bad)
    out.append(dict(gid=g['gid'],map=g['map'],width=b.W,height=b.H,asymmetric_edges=bad))
(O/'graph-symmetry.json').write_text(json.dumps(out,indent=2))
print('symmetric graphs:',len(out))
