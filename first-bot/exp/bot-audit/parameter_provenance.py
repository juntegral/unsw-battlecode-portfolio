#!/usr/bin/env python3
"""Conservative provenance labels; D/J means informed choice, never an estimated optimum."""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[1]
parameters = json.loads((OUT/'parameters.json').read_text())
versions = [('merge2-before-W1', ROOT/'bot/params.hpp')]
versions += [(f'cand-stack{i}', ROOT/f'exp/cand-stack{i}/bot/params.hpp') for i in range(1, 12)]


def declarations(path):
    result = {}
    for line in path.read_text().splitlines():
        m = re.search(r'constexpr\s+(bool|int|double|long long)\s+(.+);', line)
        if not m:
            continue
        for item in re.finditer(r'(\w+)\s*=\s*(.*?)(?=,\s*\w+\s*=|$)', m[2]):
            result[item[1]] = item[2].strip()
    return result


history = [(name, declarations(path)) for name, path in versions]
observed_families = ('CONV_', 'FRAG_', 'GRAB_', 'KS_', 'KS2_', 'TG_', 'ESC_SPLIT_', 'PX_', 'GX_',
                     'SPLIT_TAIL_', 'CSPLIT_', 'FG_', 'FG2_', 'BSPLIT_', 'FLOOR_', 'KCAP_',
                     'CLAIM_', 'PX2_', 'LSPLIT_', 'LNT_', 'UTAB_', 'GH_', 'KX_', 'LWK_', 'GATHER_')
numeric_judgement_suffix = ('_W', '_VALUE', '_PENALTY', '_MULT', '_CONTEST')
wave = {'merge2-before-W1': 'before W1', 'cand-stack1': 'W1', 'cand-stack2': 'W2', 'cand-stack3': 'W3',
        'cand-stack4': 'W4', 'cand-stack5': 'W5', 'cand-stack6': 'W6 (same upload repeated W7)',
        'cand-stack7': 'W8', 'cand-stack8': 'W9', 'cand-stack9': 'W10', 'cand-stack10': 'W11', 'cand-stack11': 'W12'}
rows = []
for p in parameters:
    name = p['name']
    if p['type'] == 'bool':
        basis, note = 'CONFIG', 'Current build setting, not a fitted or measured parameter'
    elif name.startswith(observed_families) and not name.endswith(numeric_judgement_suffix):
        basis, note = 'D/J', 'Observation-informed gate/class/time choice; exact threshold not an estimated optimum'
    else:
        basis, note = 'J', 'Design/budget/confidence/score choice; no calibration or optimum measurement established'
    first = next((version for version, d in history if name in d), 'not found')
    h = [f'{version}:{d[name]}' for version, d in history if name in d]
    transitions = []
    previous = None
    for version, d in history:
        if name in d and d[name] != previous:
            transitions.append(f'{version}:{d[name]}')
            previous = d[name]
    rows.append(dict(p, basis=basis, basisNote=note, firstCandidate=first, firstWave=wave.get(first, 'unknown'), transitions=transitions))
(OUT/'parameter-provenance.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
header = ['name','value','params_line','basis','first_candidate','first_wave','value_transitions','basis_note','uses']
data = ['\t'.join(header)]
for r in rows:
    data.append('\t'.join([r['name'],r['value'],str(r['line']),r['basis'],r['firstCandidate'],r['firstWave'],
                           '; '.join(r['transitions']),r['basisNote'],'; '.join(r['uses'])]))
(OUT/'parameter-provenance.tsv').write_text('\n'.join(data)+'\n')
print(json.dumps(dict(parameters=len(rows), bases={b:sum(r['basis']==b for r in rows) for b in ['CONFIG','D/J','J']},
                      missingHistory=[r['name'] for r in rows if r['firstCandidate']=='not found']), indent=2))
