from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodyx'
source = root / 'versions/v1.8/bot'
spec = json.loads((task / 'spec.json').read_text())
keys = set()
counts = {}
for lane in spec:
    assert (root / lane['bot'] / 'bot.toml').is_file()
    assert lane['cpu'] is True
    for opp in lane['opps']:
        assert (root / (opp if '/' in opp else 'bots/' + opp) / 'bot.toml').is_file()
        for m in lane['only']:
            assert (root / lane['maps'] / (m + '.map')).is_file()
            for side in lane['sides']:
                for seed in lane['seeds']:
                    k = (lane['out'], Path(opp).name, m, side, seed)
                    assert k not in keys
                    keys.add(k)
                    counts[lane['out']] = counts.get(lane['out'], 0) + 1
assert len(keys) == 192 and len(keys) <= 200
assert counts == {'exp/bodyx/on':84, 'exp/bodyx/off':84, 'exp/bodyx/id-off':12, 'exp/bodyx/id-base':12}
assert {p.name for p in source.iterdir() if p.is_file()} == {p.name for p in (task / 'bot-off').iterdir() if p.is_file()}
for p in source.iterdir():
    if not p.is_file(): continue
    assert p.read_bytes() == (task / 'bot-off' / p.name).read_bytes(), p.name
    want = p.read_bytes()
    if p.name == 'params.hpp': want = want.replace(b'BODYX_ON = false', b'BODYX_ON = true')
    assert want == (task / 'bot-on' / p.name).read_bytes(), p.name
old = (task / 'bot-base/params.hpp').read_text()
now = (source / 'params.hpp').read_text()
new_line = 'constexpr bool   BODYX_ON = false;       // Exact candidate bodies; movement prices stay unchanged.\n'
assert now.replace(new_line, '') == old
compile_check = json.loads((task / 'compile-check.json').read_text())
assert compile_check['off_equals_original_v18_wasm']
fixtures = json.loads((task / 'fixture-check.json').read_text())
assert fixtures['rejectedOn'] == fixtures['acceptedOff'] == 10
assert fixtures['drift'] == fixtures['priceChanges'] == 0
smoke = json.loads((task / 'analysis-smoke.json').read_text())
assert not smoke['oracleDrift'] and not smoke['stepDrift'] and not any(smoke['checks'].values())
manifest = {}
for variant in ['base','off','on']:
    manifest[variant] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((task / ('bot-' + variant)).iterdir()) if p.is_file()}
report = {'games':len(keys),'counts':counts,'pairs':84,'identityKeys':12,'sourceCopiesExact':True,
          'otherSwitchesPreserved':True,'wasmIdentity':True,'fixtures':fixtures['cases'],'censusRejected':10,
          'existingReplaySmoke':{'completedMulti':smoke['completed'],'oracleDrift':0,'stepDrift':0},'sourceHashes':manifest}
(task / 'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'sourceHashes'}))
