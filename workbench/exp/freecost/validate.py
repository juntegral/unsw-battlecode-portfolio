from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[2]
task=root/'exp/freecost';base=task/'bot-base';off=task/'bot-off';on=task/'bot-on';live=root/'versions/v1.8/bot'
assert {p.name for p in live.iterdir()}=={p.name for p in off.iterdir()}=={p.name for p in on.iterdir()}
for p in live.iterdir():
 assert p.read_bytes()==(off/p.name).read_bytes(),p.name
 expected=p.read_text().replace('FREECOST_ON = false','FREECOST_ON = true') if p.name=='params.hpp' else p.read_text()
 assert expected==(on/p.name).read_text(),p.name
old=dict(re.findall(r'constexpr bool\s+(\w+)\s*=\s*(true|false)',(base/'params.hpp').read_text()))
new=dict(re.findall(r'constexpr bool\s+(\w+)\s*=\s*(true|false)',(off/'params.hpp').read_text()))
assert {k:v for k,v in new.items() if k!='FREECOST_ON'}==old
assert new['FREECOST_ON']=='false' and new['Q2D_FREESTEP_ON']=='false' and new['Q2DQ_ON']=='false'
spec=json.loads((task/'spec.json').read_text());sets={};lanes={}
for s in spec:
 assert (root/s['bot']/'bot.toml').is_file(),s['bot']
 keys=sets.setdefault(s['out'],set());n=0
 for opp in s['opps']:
  p=root/opp if '/' in opp else root/'bots'/opp
  assert (p/'bot.toml').is_file(),p
  for m in s['only']:
   assert (root/s['maps']/(m+'.map')).is_file(),m
   for side in s['sides']:
    for seed in s['seeds']:
     k=(Path(opp).name,m,side,seed)
     assert k not in keys,(s['out'],k)
     keys.add(k);n+=1
 lanes[s['name']]=n
count=sum(map(len,sets.values()));assert count==160 and count<=200
assert len(sets['exp/freecost/id-off'])==12
assert sets['exp/freecost/on']==sets['exp/freecost/off']
assert sets['exp/freecost/id-off']==sets['exp/freecost/id-base']
compile_check=json.loads((task/'compile-check.json').read_text());assert compile_check['off_equals_original_v18_wasm']
for variant in ['base','off','on']:
 blob=(task/'compiled'/(variant+'.wasm')).read_bytes()
 assert hashlib.sha256(blob).hexdigest()==compile_check[variant]['sha256']
report={'game_count':count,'identity_keys':12,'on_off_pairs':68,'lanes':lanes,'copies_match':True,'existing_defaults_unchanged':True,'off_wasm_identical':True,'games_run_in_BUILD':0}
(task/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
