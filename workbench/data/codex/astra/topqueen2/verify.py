import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/work')
from o1_scan import scan
P=Path('data/codex/astra/topqueen2')
games=[json.loads(l) for l in (P/'games.jsonl').read_text().splitlines()]
want=[1444028,1451983,1430379,1458946,1482056,1483343,1483347,1487485]
want += [g['gid'] for g in games if g['version']==10][:3]
prior=json.loads((P/'verification.json').read_text()) if (P/'verification.json').exists() else {}
rows=prior.get('checks',[])
already={r['gid'] for r in rows}
for gid in want:
 if gid in already:continue
 hits=[g for g in games if g['gid']==gid]
 if not hits:continue
 g=hits[0];meta=json.loads(Path(g['meta']).read_text());v=scan('topqueen2-verify',Path(g['path']),meta,team=g['teams'][0])
 for s in (0,1):
  assert v['ends'][s][:4]==[g['final'][s][1],g['final'][s][3],g['final'][s][2],g['final'][s][0]],gid
  origins={'n':'natural','own':'mate','foe':'enemy'}
  for x,y in origins.items():assert sum(e[1]==s and e[2]=='q' and e[3]==x for e in v['eats'])==sum(e['origin']==y for e in g['eats'][s]),(gid,s,x)
  assert sum(e[1]==s and e[6] for e in v['deaths'])==int(g['fates'][s] is not None)
 rows.append(dict(gid=gid,final_and_queen_origin_match=True))
 print('verified',gid,flush=True)
assert len(games)==len({g['gid'] for g in games})
(P/'verification.json').write_text(json.dumps(dict(games_unique=len(games),checks=rows,convergence_crosscheck=prior.get('convergence_crosscheck')),indent=2))
