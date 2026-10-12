from pathlib import Path
import hashlib
import json
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem'
source = root / 'versions/v1.8/bot'
spec = json.loads((task / 'spec.json').read_text())
keys = set(); counts = {}
for lane in spec:
    assert (root / lane['bot'] / 'bot.toml').is_file()
    assert lane['cpu'] is True
    for opp in lane['opps']:
        assert (root / (opp if '/' in opp else 'bots/' + opp) / 'bot.toml').is_file()
        for m in lane['only']:
            assert (root / lane['maps'] / (m + '.map')).is_file()
            for side in lane['sides']:
                for seed in lane['seeds']:
                    key = (lane['out'], Path(opp).name, m, side, seed)
                    assert key not in keys; keys.add(key)
                    counts[lane['out']] = counts.get(lane['out'], 0) + 1
assert len(keys) == 192 <= 200
assert counts == {'exp/bodymem/on':84, 'exp/bodymem/off':84, 'exp/bodymem/id-off':12, 'exp/bodymem/id-base':12}
source_files = {p.name for p in source.iterdir() if p.is_file()}
for variant in ['on', 'off']:
    assert source_files == {p.name for p in (task / ('bot-' + variant)).iterdir() if p.is_file()}
for p in source.iterdir():
    if not p.is_file(): continue
    assert p.read_bytes() == (task / 'bot-off' / p.name).read_bytes()
    want = p.read_bytes()
    if p.name == 'params.hpp': want = want.replace(b'BODYMEM_ON = false', b'BODYMEM_ON = true')
    assert want == (task / 'bot-on' / p.name).read_bytes(), p.name
now = (source / 'params.hpp').read_text()
old = (task / 'bot-base/params.hpp').read_text()
assert now.replace('constexpr bool   BODYMEM_ON = false;\n', '') == old
for name in ['BODYX_ON = true', 'FREECOST_ON = false']: assert name in now
compile_check = json.loads((task / 'compile-check.json').read_text())
assert compile_check['off_equals_original_v18_wasm']
fixtures = json.loads((task / 'fixture-check.json').read_text())
assert fixtures['on']['resyncDrift'] == 0 and fixtures['on']['memoryCases'] == fixtures['off']['memoryCases']
assert fixtures['on']['priceChanges'] == fixtures['off']['priceChanges'] == 0
smoke = json.loads((task / 'analysis-smoke.json').read_text())
assert not smoke['oracleDrift'] and not smoke['stepDrift'] and not any(smoke['checks'].values())
replay = json.loads((task / 'replay-smoke.json').read_text())
assert not any(replay['checks'].values()) and not any(replay['uncertain'].values())
fatal = next(x for x in replay['changed'] if x['id'] == 14 and x['round'] == 188)
assert fatal['off'] == 'NW' and fatal['on'] == 'N' and fatal['offOracle']['reason'] == 'A' and fatal['onOracle']['survived']
manifest = {v:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((task / ('bot-' + v)).iterdir()) if p.is_file()} for v in ['base','off','on']}
report = {'games':len(keys),'counts':counts,'pairs':84,'identityKeys':12,'sourceCopiesExact':True,'otherSwitchesPreserved':True,
          'wasmIdentity':True,'fixtures':fixtures,'existingReplaySmoke':{'completedMulti':smoke['completed'],'oracleDrift':0,'stepDrift':0,
          'paymentCandidate':fatal,'nativeOnly':True},'gamesRun':0,'networkUsed':False,'committed':False,'sourceHashes':manifest}
(task / 'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'sourceHashes'},ensure_ascii=False))
