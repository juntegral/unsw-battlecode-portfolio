from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem2'
source = root / 'versions/v1.8/bot'
spec = json.loads((task / 'spec.json').read_text())
original_spec = json.loads((root / 'exp/bodymem/spec.json').read_text())
assert json.dumps(spec).replace('exp/bodymem2/', 'exp/bodymem/') == json.dumps(original_spec)
keys = set()
counts = {}
map_hashes = {}
for lane in spec:
    assert (root / lane['bot'] / 'bot.toml').is_file()
    assert lane['cpu'] is True
    for opp in lane['opps']:
        assert (root / (opp if '/' in opp else 'bots/' + opp) / 'bot.toml').is_file()
        for name in lane['only']:
            m = root / lane['maps'] / (name + '.map')
            assert m.is_file()
            map_hashes[str(m.relative_to(root))] = hashlib.sha256(m.read_bytes()).hexdigest()
            for side in lane['sides']:
                for seed in lane['seeds']:
                    key = (lane['out'], Path(opp).name, name, side, seed)
                    assert key not in keys
                    keys.add(key)
                    counts[lane['out']] = counts.get(lane['out'], 0) + 1
assert len(keys) == 192 <= 200
assert counts == {'exp/bodymem2/on':84, 'exp/bodymem2/off':84, 'exp/bodymem2/id-off':12, 'exp/bodymem2/id-base':12}
source_files = {p.name for p in source.iterdir() if p.is_file()}
for variant in ['on', 'off', 'base']:
    assert source_files == {p.name for p in (task / ('bot-' + variant)).iterdir() if p.is_file()}
changed = []
for p in source.iterdir():
    if not p.is_file():
        continue
    assert p.read_bytes() == (task / 'bot-off' / p.name).read_bytes()
    want = p.read_bytes()
    if p.name == 'params.hpp':
        want = want.replace(b'BODYMEM2_ON = false', b'BODYMEM2_ON = true')
    assert want == (task / 'bot-on' / p.name).read_bytes(), p.name
    if p.read_bytes() != (task / 'bot-base' / p.name).read_bytes():
        changed.append(p.name)
assert sorted(changed) == ['main.cpp', 'params.hpp', 'plan.cpp', 'world.cpp', 'world.hpp']
params = (source / 'params.hpp').read_text()
assert params.replace('constexpr bool   BODYMEM2_ON = false;\n', '') == (task / 'bot-base/params.hpp').read_text()
assert 'BODYMEM_ON = false' in params and 'BODYX_ON = true' in params and 'FREECOST_ON = false' in params

def between(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]

w = (source / 'world.cpp').read_text()
b = (task / 'bot-base/world.cpp').read_text()
assert between(w, 'void World::ingestDragons(', 'void World::predictOwnMove(') == between(b, 'void World::ingestDragons(', 'void World::predictOwnMove(')
assert w[w.index('void World::buildOccupancy('):] == b[b.index('void World::buildOccupancy('):]
m = (source / 'main.cpp').read_text()
bm = (task / 'bot-base/main.cpp').read_text()
assert between(m, '        if (P::SEND_SONAR', '        if constexpr (P::BODYMEM_ON) {\n            if (a.kind') == between(bm, '        if (P::SEND_SONAR', '        if constexpr (P::BODYMEM_ON) {\n            if (a.kind')
compile_check = json.loads((task / 'compile-check.json').read_text())
assert compile_check['off_equals_original_v18_wasm']
assert (task / 'compiled/base.wasm').read_bytes() == (task / 'compiled/off.wasm').read_bytes()
fixtures = json.loads((task / 'fixture-check.json').read_text())
assert fixtures['on']['resyncDrift'] == 0
assert fixtures['on']['memoryCases'] == fixtures['off']['memoryCases']
assert fixtures['on']['allySnapshot'] == fixtures['off']['allySnapshot']
assert fixtures['on']['priceChanges'] == fixtures['off']['priceChanges'] == 0
smoke = json.loads((task / 'audit/default-original.json').read_text())
assert not any(smoke['checks'].values()) and not any(smoke['uncertain'].values())
fatal = next(x for x in smoke['changed'] if x['id'] == 14 and x['round'] == 188)
assert fatal['off'] == 'NW' and fatal['on'] == 'N'
assert fatal['offOracle']['reason'] == 'A' and fatal['onOracle']['survived']
analysis_smoke = json.loads((task / 'analysis-smoke.json').read_text())
assert not analysis_smoke['oracleDrift'] and not analysis_smoke['stepDrift']
assert analysis_smoke['predicted'] + len(analysis_smoke['missingTags']) == analysis_smoke['multi']
manifest = {v:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((task / ('bot-' + v)).iterdir()) if p.is_file()} for v in ['base', 'off', 'on']}
report = {'games':len(keys), 'counts':counts, 'pairs':84, 'identityKeys':12,
          'sameKeysAsBodymem':True, 'sourceCopiesExact':True, 'otherSwitchesPreserved':True,
          'legacyAllyAndSonarCodeUnchanged':True, 'allySnapshotsIdentical':True,
          'wasmIdentity':True, 'compile':compile_check,
          'fixtures':{v:{k:x for k,x in f.items() if k != 'allySnapshot'} for v,f in fixtures.items()},
          'existingReplaySmoke':{'paymentChoice':fatal, 'nativeOnly':True, 'realGameCausalGateMeasured':False},
          'gamesRun':0, 'networkUsed':False, 'committed':False,
          'unmeasured':['real-game body drift', 'firstdiv causal gates/harm explanations', 'payment deaths', 'event/sonar identity', 'CPU'],
          'specHash':hashlib.sha256((task / 'spec.json').read_bytes()).hexdigest(),
          'sourceHashes':manifest, 'mapHashes':map_hashes}
(task / 'validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['sourceHashes', 'mapHashes']}, ensure_ascii=False, indent=2))
