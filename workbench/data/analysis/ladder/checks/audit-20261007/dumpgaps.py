import sys, json
sys.dont_write_bytecode = True
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
sys.path.insert(0, ROOT + 'tools')
import ladder_rows as lr
from ladder_replay import base
obs = json.load(open(ROOT + 'data/analysis/ladder/map-observations.json'))
out = {}
seen = {}
for gid, o in obs.items():
    key = (o['map'], o['text'])
    if key in seen: continue
    h = base.header(o['text']); ranges, src = lr.local_ranges(o['map'], h)
    seen[key] = 1
    if ranges:
        out.setdefault(o['map'], {'source': src, 'gaps': {f'{x},{y}': v for (x, y), v in ranges.items() if v[1] > 0}})
json.dump(out, open('gaps.json', 'w'))
print({k: (len(v['gaps']), v['source'].split('/')[-1]) for k, v in out.items()})
