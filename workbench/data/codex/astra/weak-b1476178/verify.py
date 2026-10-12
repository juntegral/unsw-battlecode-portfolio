import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from collections import Counter
OUT=Path(__file__).resolve().parent
inv=json.loads((OUT/'inventory.json').read_text())['games'];radius=json.loads((OUT/'radius.json').read_text());rows=[];counts={}
for job in inv:
 x=json.loads((OUT/f"set-{job['gid']}.json").read_text());g=x['scan'];d=x['detail'];res=[]
 assert g['bot']=='21033'
 for s in (0,1):
  start=sum(z['length'] for z in d['initial'] if z['side']==s);eat=sum(z[1]==s for z in g['eats']);dead=sum(z[2] for z in g['deaths'] if z[1]==s);paid=sum(z[3] for z in g['paids'] if z[1]==s)
  resid=start+eat-dead-paid-g['ends'][s][1];assert resid==0;res.append(resid)
 for r,snap in g['snaps'].items():assert [z[:4] for z in snap]==d['all_snapshots'][r]
 rows.append(dict(gid=job['gid'],ledger_residual=res))
for label in sorted({j['label'] for j in inv}):
 xs=[json.loads((OUT/f"set-{j['gid']}.json").read_text()) for j in inv if j['label']==label]
 rr=[x for x in radius if x['label']==label];ii=[r for x in rr for r in x['rows'] if r['newly_marked']]
 counts[label]=dict(games=len(xs),short_rammed=sum(z[1]==0 and not z[6] and z[2]<=4 and z[4]=='rammed' for x in xs for z in x['scan']['deaths']),marked=len(ii),marked_games=sum(any(r['newly_marked'] for r in x['rows']) for x in rr),alternative=sum(bool(r['safe']) for r in ii),alternative_games=sum(any(r['newly_marked'] and r['safe'] for r in x['rows']) for x in rr))
src=Path('data/online/smoke/one6-bot/main.cpp').read_text();candidate=(OUT/'candidate/main.cpp').read_text();assert candidate==src.replace('constexpr bool SMALL_SPRINT_THREAT = false;','constexpr bool SMALL_SPRINT_THREAT = true;');assert (OUT/'candidate/bot').is_file();ET.parse(OUT/'queen-last-three.svg')
(OUT/'verification.json').write_text(json.dumps(dict(games=len(rows),rows=rows,counts=counts,candidate_only_constant_changed=True,candidate_compiled=True,behavioral_tests=0,svg_xml_valid=True,source_sha256=hashlib.sha256(src.encode()).hexdigest()),indent=2))
print(json.dumps(counts,indent=2))
