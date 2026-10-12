from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2];T=R/'exp/q1c';B=R/'versions/v1.8/bot'
errors=[]
flags={'off':set(),'b':{'Q1B_BACKUP_ON'},'c':{'Q1C_SIGHT_ON'},'on':{'Q1B_BACKUP_ON','Q1C_SIGHT_ON'}}
for variant,on in flags.items():
 D=T/f'bot-{variant}'
 if {p.name for p in B.iterdir() if p.is_file()}!={p.name for p in D.iterdir() if p.is_file()}:errors.append(f'file list {variant}')
 for p in B.iterdir():
  if not p.is_file():continue
  expected=p.read_bytes()
  if p.name=='params.hpp':
   s=expected.decode()
   for f in on:s=s.replace(f'{f} = false;',f'{f} = true;')
   expected=s.encode()
  if expected!=(D/p.name).read_bytes():errors.append(f'copy drift {variant}/{p.name}')
base=(T/'bot-base/params.hpp').read_text();current=(B/'params.hpp').read_text()
for line in ['constexpr bool   Q1B_BACKUP_ON = false;\n','constexpr bool   Q1C_SIGHT_ON = false;\n','constexpr int    Q1C_SIGHT_MEMORY = 50;\n']:current=current.replace(line,'')
if base!=current:errors.append('other parameter/default changed')
spec=json.loads((T/'spec.json').read_text());counts={};allkeys=set();identity=set()
for lane in spec:
 for bot in [lane['bot'],*lane['opps']]:
  directory=R/bot if '/' in bot else R/'bots'/bot
  if not (directory/'bot.toml').is_file():errors.append(f'bot missing {bot}')
 for mapname in lane['only']:
  if not (R/lane['maps']/(mapname+'.map')).is_file():errors.append(f'map missing {mapname}')
  for opp in lane['opps']:
   for side in lane['sides']:
    for seed in lane['seeds']:
     key=(lane['out'],Path(opp).name,mapname,side,seed)
     if key in allkeys:errors.append(f'duplicate {key}')
     allkeys.add(key);counts[lane['out']]=counts.get(lane['out'],0)+1
     if lane['out'].endswith('id-off'):identity.add(key[1:])
if len(allkeys)!=196 or len(identity)!=6:errors.append('game count/identity count')
check=json.loads((T/'compile-check.json').read_text())
if not check['off_equals_original_v18_wasm']:errors.append('off WASM mismatch')
for v in ['base','off','b','c','on']:
 blob=(T/f'compiled/{v}.wasm').read_bytes()
 if check[v]['sha256']!=hashlib.sha256(blob).hexdigest():errors.append(f'wasm hash {v}')
 if not (T/f'fixtures-{v}.txt').exists() and v!='base':errors.append(f'missing fixtures {v}')
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for D in [B,*[T/f'bot-{v}' for v in ['base','off','b','c','on']]] for p in D.iterdir() if p.is_file()}
result={'games':len(allkeys),'identity_keys':len(identity),'counts':counts,'errors':errors,'source_manifest':manifest}
(T/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='source_manifest'},indent=2))
assert not errors
