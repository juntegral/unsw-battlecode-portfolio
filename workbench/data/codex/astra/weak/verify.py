import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
ROOT=Path.cwd();OUT=ROOT/'data/codex/astra/weak'
sys.path.insert(0,str(OUT));import analyze
rows=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')]
checks=[]
for g in rows:
 for s in (0,1):
  start=sum(x['length'] for x in g['detail']['initial'] if x['side']==s)
  eat=sum(e[1]==s for e in g['eats']); dead=sum(d[2] for d in g['deaths'] if d[1]==s);paid=sum(p[3] for p in g['paids'] if p[1]==s)
  assert start+eat-dead-paid==g['ends'][s][1],(g['gid'],s,start,eat,dead,paid)
  assert g['ends'][s][:4]==g['detail']['all_snapshots'][str(g['last'])][s]
 checks.append({'id':g['gid'],'ledger_ok':True,'snapshot_ok':True})
for gid in (1460076,1460077,1460078,1471965,1471966,1471967):
 g=next(g for g in rows if g['gid']==gid);p=next((ROOT/'data/online/live-one1').glob(f'b*/M{gid}.replay'));root=analyze.replay.load(p).root();own=int(g['meta']['teamAId']!=1119)
 for s in (0,1):
  st=root.pointer(4).pointer(own if s==0 else 1-own)
  assert [st.i32(0),st.i32(8),st.i32(4),st.i32(12)]==g['ends'][s][:4]
result={'games':len(rows),'checks':checks,'six_final_replay_results_verified':True,'source_hash':hashlib.sha256((ROOT/'data/online/smoke/one5-bot/main.cpp').read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print('verified',len(rows),'games; both-side mass ledgers, independent snapshots, six replay result records')
