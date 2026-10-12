import json, glob, os
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
base = 'data/online/smoke'
out = []
for d in sorted(glob.glob(base + '/*-old')):
    for f in sorted(glob.glob(d + '/game-*.json')):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if j.get('mapName') == 'Trophy':
            out.append((os.path.basename(d), f))
for d in sorted(glob.glob('data/online/live-one1/b*')):
    for f in sorted(glob.glob(d + '/game-*.json')):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if j.get('mapName') == 'Trophy':
            out.append((d, f))
for o in out:
    print(*o)
f = glob.glob(base + '/one11-c1-old/game-*.json')[0]
j = json.load(open(f))
print({k: (v if not isinstance(v, (dict, list)) else type(v).__name__) for k, v in j.items()})
print(sorted(os.listdir(base + '/one11-c1-old'))[:40])
