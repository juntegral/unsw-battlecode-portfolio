import sys
sys.dont_write_bytecode=True
import analyze as a
import json
old=json.loads((a.R/'data/codex/astra/audit-threat/inventory.json').read_text())
for j in old['games']:
 if j['version'] not in (8,9,10):continue
 j['v']=j['version'];f=a.O/f'g{j["gid"]}.json'
 if f.exists():continue
 x=a.scan(j);f.write_text(json.dumps(x,ensure_ascii=False));print(j['gid'],j['v'],x['death'] and (x['death']['r'],x['death']['reason']),x['selected'],flush=True)
