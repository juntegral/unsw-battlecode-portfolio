#!/usr/bin/env python3
"""Summarise only the newly written per-game audit; never modify inputs."""
import collections
import hashlib
import json
import math
import pathlib
import subprocess
import re

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def resource_check():
    mem = subprocess.check_output(['memory_pressure'], text=True)
    disk = subprocess.check_output(['df', '-g', '/'], text=True).splitlines()[-1].split()
    free = int(re.search(r'free percentage:\s*(\d+)%', mem)[1])
    if free < 10 or int(disk[3]) < 20:
        raise SystemExit('PAUSE: resource floor reached')


def wilson(k, n):
    z = 1.96
    p = k / n
    den = 1 + z*z/n
    mid = (p + z*z/(2*n)) / den
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return [100*(mid-half), 100*(mid+half)]


def group(rows, key):
    out = []
    by = collections.defaultdict(list)
    for row in rows:
        by[str(row[key])].append(row)
    for name, rr in sorted(by.items()):
        wins = sum(r['winner'] == r['us'] for r in rr)
        x = dict(name=name, games=len(rr), wins=wins, turns=sum(r['turns'] for r in rr))
        for tag in ['csplit', 'lsplit', 'frag', 'floor', 'kcap', 'bsplit', 'F', 'g', 'gh', 'kx']:
            x[tag] = sum(r['tags'].get(tag, 0) for r in rr)
        out.append(x)
    return out


resource_check()
result = {}
md = ['# Population checks', '', 'These are descriptive counts, not treatment effects.', '']
supplemental_inputs = []
for wave, setname, folder in [('W11', 'cand-stack10-online', OUT), ('W12', 'cand-stack11-online', OUT/'w12')]:
    rows = [json.loads(s) for s in (folder/'per-game.jsonl').read_text().splitlines()]
    wins = sum(r['winner'] == r['us'] for r in rows)
    result[wave] = dict(games=len(rows), wins=wins, winWilson95Pct=wilson(wins, len(rows)),
                       maps=group(rows, 'map'), opponents=group(rows, 'opp'))
    md += [f'## {wave} maps', '', '| Map | Games | Wins | Own turns | csplit | lsplit | frag | bsp | floor | kcap | F turns | g turns | gh | kx |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for x in result[wave]['maps']:
        md.append('| '+' | '.join(str(x[k]) for k in ['name','games','wins','turns','csplit','lsplit','frag','bsplit','floor','kcap','F','g','gh','kx'])+' |')
    md += ['']
    index = ROOT/'data/online'/setname/'index.json'
    data = index.read_bytes()
    ix = json.loads(data)
    supplemental_inputs.append(dict(path=str(index.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
    for row in ix['games']:
        p = index.parent/f'M{row["gameId"]}.replay'
        st = p.stat()
        supplemental_inputs.append(dict(path=str(p.relative_to(ROOT)), bytes=st.st_size, mtimeNs=st.st_mtime_ns,
                                        checksum='Not hashed; both loaders read this exact path'))
for name in ['mech-cand-stack10.md', 'mech-cand-stack11.md']:
    p = ROOT/'research/experiments'/name
    data = p.read_bytes()
    supplemental_inputs.append(dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
(OUT/'population-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
(OUT/'population-tables.md').write_text('\n'.join(md)+'\n')
(OUT/'replay-input-manifest.json').write_text(json.dumps(supplemental_inputs, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:{'games':v['games'],'wins':v['wins'],'Wilson95Pct':v['winWilson95Pct']} for k,v in result.items()}, indent=2))
