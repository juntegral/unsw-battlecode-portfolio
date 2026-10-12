from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[2];T=ROOT/'exp/qsight'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((T/'manifest.json').read_text())
for p,h in manifest['files'].items():assert sha(ROOT/p)==h,p
bot=ROOT/'versions/v1.8/bot';off=T/'bot-off';on=T/'bot-on';base=T/'bot-base'
assert sorted(p.name for p in bot.iterdir())==sorted(p.name for p in off.iterdir())==sorted(p.name for p in on.iterdir())
for p in bot.iterdir():
 assert p.read_bytes()==(off/p.name).read_bytes(),p
 expected=p.read_text().replace('Q2SIGHT_ON = false','Q2SIGHT_ON = true') if p.name=='params.hpp' else p.read_text()
 assert (on/p.name).read_text()==expected,p
old=dict(re.findall(r'constexpr bool\s+(\w+)\s*=\s*(true|false)',(base/'params.hpp').read_text()))
new=dict(re.findall(r'constexpr bool\s+(\w+)\s*=\s*(true|false)',(off/'params.hpp').read_text()))
assert all(new[k]==v for k,v in old.items()) and new['Q2SIGHT_ON']=='false'
spec=json.loads((T/'spec.json').read_text());count=0;keys=set();identity=set()
for s in spec:
 assert s['cpu'] and s['seeds']==[1]
 assert (ROOT/s['bot']).is_dir()
 maps=[p for p in (ROOT/s['maps']).glob('*.map') if 'only' not in s or p.stem in s['only']]
 assert maps
 if 'only' in s:assert len(maps)==len(s['only'])
 for opp in s['opps']:
  assert (ROOT/opp if '/' in opp else ROOT/'bots'/opp).is_dir()
  for p in maps:
   for side in s['sides']:
    for seed in s['seeds']:
     key=(s['out'],Path(opp).name,p.stem,side,seed);assert key not in keys,key
     keys.add(key);count+=1
     if s['out']=='exp/qsight/id-off':identity.add(key[1:])
assert count==196 and len(identity)==6
assert manifest['map_sets']=={'online':10,'sprint':7,'bundled':5}
check=json.loads((T/'compile-check.json').read_text())
for v in ['base','off','on']:
 p=T/'compiled'/f'{v}.wasm';assert sha(p)==check[v]['sha256'] and p.stat().st_size==check[v]['bytes']
assert (T/'compiled/base.wasm').read_bytes()==(T/'compiled/off.wasm').read_bytes()
assert len((T/'BUILD.txt').read_text().splitlines())==5
print('PASS: frozen sources/maps, copies/defaults, 196 games, 6 identity keys, official WASM identity, BUILD 5 lines')
