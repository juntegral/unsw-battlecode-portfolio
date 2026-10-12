from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
task = root / 'exp/freecost2'
def files(directory):
    return {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob('*') if p.is_file()}
def sha(blob):
    return hashlib.sha256(blob).hexdigest()
base, off, on, current = [files(p) for p in [task/'bot-base', task/'bot-off', task/'bot-on', root/'versions/v1.8/bot']]
assert off == current
assert set(base) == set(off) == set(on)
assert {k for k in base if base[k] != off[k]} == {'params.hpp', 'plan.hpp', 'plan.cpp'}
for name in off:
    want = off[name].replace(b'constexpr bool   FREECOST2_ON = false;', b'constexpr bool   FREECOST2_ON = true;') if name == 'params.hpp' else off[name]
    assert on[name] == want, name
assert off['params.hpp'].replace(b'constexpr bool   FREECOST2_ON = false;\n', b'') == base['params.hpp']
helper = b'''    int pricedPaidSteps(int x) const {
        if constexpr (P::FREECOST2_ON) return P::paidSteps123(w_.myLen, x);
        else return paidSteps(x);
    }
'''
assert off['plan.hpp'].replace(helper, b'') == base['plan.hpp']
s = off['plan.cpp'].decode()
s = s.replace('        if constexpr (P::FREECOST2_ON) maxSteps = std::min(P::STRIKE_MAX_STEPS, P::reach123(w_.myLen));\n', '')
assert s.count('pricedPaidSteps(2) * P::SPRINT_COST') == 4
assert s.count('pricedPaidSteps(3) * P::SPRINT_COST') == 1
assert s.count('pricedPaidSteps((int)dirs.size()) * P::SPRINT_COST') == 2
s = s.replace('pricedPaidSteps(2) * P::SPRINT_COST', 'paid2 * P::SPRINT_COST', 3)
s = s.replace('pricedPaidSteps(', 'paidSteps(')
assert s.encode() == base['plan.cpp']
for name in base.keys()-{'params.hpp','plan.hpp','plan.cpp'}:
    assert base[name] == off[name], name
spec = json.loads((task/'spec.json').read_text())
original = json.loads((root/'exp/freecost/spec.json').read_text())
def keys(lanes):
    result = {}
    for lane in lanes:
        assert lane['cpu']
        assert (root/lane['bot']/'bot.toml').is_file()
        for opp in lane['opps']:
            opponent = root/opp if '/' in opp else root/'bots'/opp
            assert (opponent/'bot.toml').is_file()
            for m in lane['only']:
                assert (root/lane['maps']/(m+'.map')).is_file()
                for side in lane['sides']:
                    for seed in lane['seeds']:
                        key = ':'.join([Path(opp).name,m,side,str(seed)])
                        result.setdefault(Path(lane['out']).name,set())
                        assert key not in result[Path(lane['out']).name]
                        result[Path(lane['out']).name].add(key)
    return result
newKeys, oldKeys = keys(spec), keys(original)
assert newKeys == oldKeys
assert len(newKeys['on']) == len(newKeys['off']) == 68
assert len(newKeys['id-off']) == len(newKeys['id-base']) == 12
assert sum(map(len,newKeys.values())) == 160
assert all(s['bot']=='versions/v1.8/bot' for s in spec if s['name'].startswith('identity-base'))
mapPaths = {root/s['maps']/(m+'.map') for s in spec for m in s['only']}
manifest = {'sources': {name:{k:sha(v) for k,v in data.items()} for name,data in zip(['base','off','on','current'],[base,off,on,current])},
            'maps':{str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(mapPaths)},'specSha256':sha((task/'spec.json').read_bytes())}
manifestFile = task/'source-manifest.json'
if '--record' in sys.argv:
    assert not manifestFile.exists(), 'do not replace the frozen manifest'
    manifestFile.write_text(json.dumps(manifest,indent=2)+'\n')
else:
    assert json.loads(manifestFile.read_text()) == manifest, 'source/map/spec changed since BUILD'
for name in ['runq.js','analyze.js','replay-audit.js']:
    subprocess.run(['node','--check',str(task/name)],check=True)
compileReport=json.loads((task/'compile-check.json').read_text())
assert compileReport['off_equals_original_v18_wasm']
for arm in ['base','off','on']:
    blob=(task/'compiled'/(arm+'.wasm')).read_bytes()
    assert sha(blob) == compileReport[arm]['sha256']
    assert len(blob) == compileReport[arm]['bytes']
subprocess.run(['git','diff','--check','--','versions/v1.8/bot','versions/v1.8/VERSION.md'],cwd=root,check=True)
report={'games':160,'onOffPairs':68,'identityKeys':12,'exactFreecostMapSet':True,'otherDefaultsPreserved':True,
        'oldFreecostAndBodyCodePreserved':True,'candidateGenerationPreserved':True,'offEqualsCurrentSources':True,
        'offEqualsOriginalWasm':True,'gameResults':'UNMEASURED','cpu':'UNMEASURED','sourceManifest':'exp/freecost2/source-manifest.json'}
(task/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
