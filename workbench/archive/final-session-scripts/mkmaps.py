"""Make local map files for the ladder maps we do not have yet, from the replays of the one14-c1 set."""
import json, glob, os, re, subprocess
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm'
OUT = os.path.expanduser('~/meow-redteam/maps/ladder')
os.chdir(ROOT)
have = set(os.listdir(OUT))
for j in sorted(glob.glob('data/online/smoke/one14-c1-old/game-*.json')):
    d = json.load(open(j))
    name = d.get('map') or d.get('mapName') or (d.get('game') or {}).get('map')
    if isinstance(name, dict):
        name = name.get('name')
    gid = re.search(r'game-(\d+)', j).group(1)
    rep = 'data/online/smoke/one14-c1-old/M%s.replay' % gid
    if not name or not os.path.exists(rep):
        print('skip', j, name)
        continue
    slug = 'ladder_' + re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_') + '_1.map'
    if slug in have:
        continue
    r = subprocess.run(['node', 'tools/replay2map.js', rep, os.path.join(OUT, slug)], capture_output=True, text=True)
    print(slug, 'rc', r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:140] if (r.stdout + r.stderr).strip() else '')
print(sorted(os.listdir(OUT)))
