#!/usr/bin/env python3
"""Full-population independent classification audit, including reverse membership."""
import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
p={z['key']:z for z in (json.loads(l) for l in open(C/'primary-extra.jsonl') if l.strip())}
r={z['key']:z for z in (json.loads(l) for l in open(C/'independent-v2.jsonl') if l.strip())}
assert set(p)==set(r)
m=[];n=0
for key in p:
    for tm in ['A','B']:
        a={(z['id'],z['r']):(z['len'],z['cause']) for z in p[key]['teams'][tm]['kingDeaths']}
        b={(z['id'],z['r']):(z['len'],z['cause']) for z in r[key]['teams'][tm]['kd']}
        n+=len(a)
        for k in set(a)|set(b):
            if a.get(k)!=b.get(k):m.append({'key':key,'team':tm,'dragonRound':k,'primary':a.get(k),'independent':b.get(k)})
old=json.load(open(C/'extra-checks.json'))
out={'gameN':len(p),'kingDeathN':n,'initialCauseDifferences':old['causeDifferenceCount'],'initialPairs':dict((str(k),v) for k,v in collections.Counter((z['primary'],z['independent']) for z in old['causeDifferences']).items()),'correctedMismatchCount':len(m),'correctedMismatches':m}
with open(C/'corrected-cause-checks.json','x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out if len(m)<3 else {**out,'correctedMismatches':m[:3]}))
if m:raise SystemExit('Classification mismatch remains')
