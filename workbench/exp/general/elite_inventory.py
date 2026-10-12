"""Read local collector indexes only; no collection, requests or uploads."""
import json,pathlib,collections,datetime
O=pathlib.Path(__file__).resolve().parent;R=O.parents[1]
known={'Autarky','Default','Devil','Portals','Prisoners Dilemma','Queen Of Spades','Schooltime','Slithery Fight','Trauma','Trophy'}
p=R/'data/elite/index.jsonl';rows=[]
if p.exists():
 for l in open(p):
  if l.strip():rows.append(json.loads(l))
unique={str(r['battleId'])+':'+str(r['gameId']):r for r in rows};unknown=[r for r in unique.values() if r['map'] not in known]
json.dump({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'indexRows':len(rows),'uniqueN':len(unique),'mapCounts':dict(collections.Counter(r['map'] for r in unique.values())),'unknownN':len(unknown),'unknown':unknown,'knownMaps':sorted(known),'appendixPlan':['freeze new map games with collector metadata, deduplicate against top snapshot','do not infer hidden min/max from online replay: preserve successful-spawn support lower bounds','reconstruct heads/frontier/splits/provenance using ML hooks and separate replay bodies; same stall filter','evaluate frozen pre-sprint model before any refit; rank<=10 own behavior separated from winner/loser vs variable opponents','score MAE, signed bias and prediction interval coverage by new map and by team; disclose game and battle N','audit r0-30 observable estimates separately; report portal/symmetry uncertainty instead of using whole unseen map features','select class medoids after full counts and classes; trace r0-50 opening and r250-499 conversion','record all missing replays and incomplete maps; never merge these into 15-layout fitting population']},open(O/'elite-inventory.json','w'),ensure_ascii=False,indent=1)
print('ELITE LOCAL',len(rows),'unique',len(unique),'unknown',len(unknown))
