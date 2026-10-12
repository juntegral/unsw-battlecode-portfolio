#!/usr/bin/env python3
"""Validate generated audit evidence without executing games or changing any input."""
import ast
import collections
import csv
import gzip
import hashlib
import json
import pathlib
import re
import subprocess

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[1]
REPORT = ROOT/'research/observations/bot-architecture-audit.md'
errors = []
checks = {}


def require(ok, label, detail=None):
    if not ok:
        errors.append(dict(check=label, detail=detail))


mem = subprocess.check_output(['memory_pressure'], text=True)
disk = subprocess.check_output(['df', '-g', '/'], text=True).splitlines()[-1].split()
free = int(re.search(r'free percentage:\s*(\d+)%', mem)[1])
if free < 10 or int(disk[3]) < 20:
    raise SystemExit('PAUSE: resource floor reached')
checks['resources'] = dict(freeMemoryPct=free, freeDiskGB=int(disk[3]))

changed = []
snapshots = json.loads((OUT/'source-manifest.json').read_text())
supplemental = json.loads((OUT/'replay-input-manifest.json').read_text())
for item in snapshots + supplemental:
    path = pathlib.Path(item['path'])
    if not path.is_absolute():
        path = ROOT/path
    if not path.is_file():
        changed.append(dict(path=item['path'], reason='missing'))
        continue
    if 'sha256' in item:
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            changed.append(dict(path=item['path'], reason='hash'))
    else:
        st = path.stat()
        if st.st_size != item['bytes'] or st.st_mtime_ns != item['mtimeNs']:
            changed.append(dict(path=item['path'], reason='size/mtime'))
require(not changed, 'input_snapshot_unchanged', changed)
checks['inputSnapshot'] = dict(hashed=len(snapshots)+sum('sha256' in x for x in supplemental),
                               replayMetadata=sum('sha256' not in x for x in supplemental), changed=changed)

syntax = []
for path in sorted(OUT.glob('*.py')):
    try:
        ast.parse(path.read_text(), filename=str(path))
        syntax.append(dict(file=path.name, ok=True))
    except SyntaxError as e:
        syntax.append(dict(file=path.name, ok=False, error=str(e)))
        require(False, 'python_syntax', str(e))
for path in sorted(OUT.glob('*.js')):
    p = subprocess.run(['nice','-n','15','node','--check',str(path)], capture_output=True, text=True)
    syntax.append(dict(file=path.name, ok=p.returncode==0, stderr=p.stderr.strip()))
    require(p.returncode==0, 'node_syntax', path.name)
checks['scriptSyntax'] = syntax

text = REPORT.read_text()
require('<!-- AUDIT_' not in text, 'no_assembly_placeholders')
require(len(re.findall(r'^```', text, re.M)) % 2 == 0, 'balanced_fences')
for n in range(9):
    require(bool(re.search(r'^## '+str(n)+r'\.', text, re.M)), 'required_report_section', n)
expected = None
table_errors = []
for n,line in enumerate(text.splitlines(),1):
    if line.startswith('|'):
        columns = len(line.split('|'))-2
        if expected is not None and columns != expected:
            table_errors.append(dict(line=n, columns=columns, expected=expected))
        expected = columns if expected is None else expected
    else:
        expected = None
require(not table_errors, 'table_columns', table_errors)
broken = []
for target in re.findall(r'\]\(([^)]+)\)', text):
    if '://' in target or target.startswith('#'):
        continue
    target = target.split('#',1)[0].strip('<>')
    if not (REPORT.parent/target).is_file():
        broken.append(target)
require(not broken, 'report_file_links', broken)

abbreviations = {'P':'plan.cpp','H':'params.hpp','W':'world.cpp','WH':'world.hpp','M':'mapid.cpp','MAIN':'main.cpp'}
line_bounds = {k:len((ROOT/'exp/cand-stack11/bot'/f).read_text().splitlines()) for k,f in abbreviations.items()}
bad_pointers = []
for match in re.finditer(r'\b(P|H|W|WH|M|MAIN):(\d+)(?:[–-](\d+))?', text):
    key,first,last = match.groups()
    if not 1 <= int(first) <= int(last or first) <= line_bounds[key]:
        bad_pointers.append(match[0])
require(not bad_pointers, 'source_pointer_bounds', bad_pointers)
parameters = json.loads((OUT/'parameters.json').read_text())
bools = {x['name']:x['value'] for x in parameters if x['type']=='bool'}
for name,value in re.findall(r'\b([A-Z][A-Z0-9_]+)=(true|false)\b', text):
    if name in bools:
        require(bools[name]==value, 'inline_toggle_matches_source', name)
provenance = json.loads((OUT/'parameter-provenance.json').read_text())
require(len(parameters)==len(provenance)==246 and len(bools)==41, 'parameter_coverage')
checks['report'] = dict(lines=len(text.splitlines()), bytes=REPORT.stat().st_size,
                        tableErrors=table_errors, brokenLinks=broken, badSourcePointers=bad_pointers,
                        bools=len(bools), constants=len(parameters), sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest())

sets = []
for wave,folder in [('W11',OUT),('W12',OUT/'w12')]:
    total = json.loads((folder/'counts.json').read_text())
    games = [json.loads(s) for s in (folder/'per-game.jsonl').read_text().splitlines()]
    require(len(games)==total['games']==70, 'games_'+wave)
    for key in ['turns','labelled','move','wins']:
        value = sum(g['winner']==g['us'] for g in games) if key=='wins' else sum(g[key] for g in games)
        require(value==total[key], wave+'_game_sum_'+key)
    for key in ['tags','kinds','splits','splitActual','explicitGoals']:
        summed = collections.Counter()
        for g in games:
            summed.update(g[key])
        require(dict(summed)==total[key], wave+'_game_sum_'+key)
    require(total['splits']==total['splitActual'], wave+'_split_event_matches_labels')
    require(total['turns']==total['labelled'], wave+'_all_turns_labelled')
    require(sum(total['explicitGoals'].get(k,0) for k in ['F','g','K','none'])==total['move'], wave+'_goal_partition')
    require(total['explicitGoals']['early_action']==total['turns']-total['move'], wave+'_early_partition')
    require(not total['unexpected'] and all(v==0 for v in total['checks'].values()), wave+'_ledger_checks')
    for key in ['missingLabels','duplicates','labelActionMismatch','faults','over80M']:
        require(total[key]==0, wave+'_'+key)
    tags = collections.Counter()
    kinds = collections.Counter()
    goals = collections.Counter()
    rows = 0
    with gzip.open(folder/'turn-tags.tsv.gz','rt') as handle:
        for row in csv.DictReader(handle,delimiter='\t'):
            rows += 1
            kinds.update([row['kind']])
            goals.update([row['explicitGoal']])
            tags.update(filter(None,row['tags'].split(',')))
    require(rows==total['turns'] and dict(tags)==total['tags'] and dict(kinds)==total['kinds'] and dict(goals)==total['explicitGoals'],
            wave+'_full_turn_tsv_recount')
    with (folder/'per-game-tags.tsv').open() as handle:
        csvrows = list(csv.DictReader(handle,delimiter='\t'))
    require(len(csvrows)==70, wave+'_per_game_tsv_count')
    for key,number in total['tags'].items():
        require(sum(int(r[key]) for r in csvrows)==number, wave+'_per_game_tsv_'+key)
    sets.append(dict(wave=wave,games=70,turns=rows,splits=sum(total['splits'].values()),
                     nonEscapeSplits=total['nonEscapeSplits'], wins=total['wins'],maxInstructions=total['maxInstr']))
checks['counts'] = sets
raw = json.loads((OUT/'raw-verification.json').read_text())
require(len(raw['games'])==140 and all(not g['mismatch'] for g in raw['games']), 'raw_140_games')
require(all(s['mismatches']==0 and s['directIdMismatchLow8']==0 and s['missingSonar64']==0 for s in raw['summary']), 'raw_sonar_verification')
checks['rawSummary'] = raw['summary']
checks['complete'] = not errors
checks['errors'] = errors
(OUT/'final-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(complete=not errors,errors=errors,report=checks['report'],counts=sets,
                     inputChanged=len(changed),resources=checks['resources']), ensure_ascii=False,indent=2))
if errors:
    raise SystemExit(1)
