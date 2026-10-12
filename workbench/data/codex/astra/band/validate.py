import json,collections,datetime
from pathlib import Path
O=Path('data/codex/astra/band');I=json.loads((O/'inventory.json').read_text());G=list(map(json.loads,(O/'games.jsonl').read_text().splitlines()))
assert len(G)==len({g['gid'] for g in G})==I['count']
assert {g['gid'] for g in G}=={j['meta']['id'] for j in I['games']}
J={j['meta']['id']:j for j in I['games']}
checks=collections.Counter()
for g in G:
 j=J[g['gid']]['meta'];ours='a' if j['teamAId']==1119 else 'b'
 expected='draw' if j['winner'] not in ('a','b') else 'win' if j['winner']==ours else 'loss'
 assert g['result']==expected,(g['gid'],'metadata winner')
 assert g['audit']==dict(anomalies={},residual=[],final_match=True),g['gid']
 for s in (0,1):
  assert sum(d[1]==s and d[4]=='rams' for d in g['deaths'])==sum(d[1]!=s and d[4]=='rammed' for d in g['deaths'])
 assert len(g['qfeeds'])==sum(e[1]==1 and e[2]=='q' and e[3]!='n' for e in g['eats'])
 assert int(g['bot'])>=21126 and g['start']>=I['cutoff'].removesuffix('Z')
 checks['games_checked']+=1
 checks['ranked']+=g['ranked']
 checks['queen_drop_pearls_checked']+=len(g['qfeeds'])
assert sum('one8-p1-old' in p for j in I['games'] for p in [j['path']]+j['copies'])==15
checks['duplicates_removed']=I['duplicates'];checks['one8_p1_included']=15
out=dict(timestamp=datetime.datetime.now().astimezone().isoformat(),checks=checks,all_pass=True)
(O/'validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
