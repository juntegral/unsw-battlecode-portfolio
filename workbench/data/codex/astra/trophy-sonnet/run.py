import sys, os, json, glob
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/trophy-sonnet')
import scan2

vers = {}
for line in open('data/online/smoke/versions.tsv'):
    p = line.split()
    if len(p) >= 2:
        vers[p[0]] = p[1]
seen = {}
folders = sorted(glob.glob('data/online/smoke/*-old')) + sorted(glob.glob('data/online/live-one1/b*'))
for fo in folders:
    for f in sorted(glob.glob(fo + '/game-*.json')):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if j.get('mapName') != 'Trophy' or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        rp = '%s/M%d.replay' % (fo, j['id'])
        if j['id'] in seen or not os.path.exists(rp):
            continue
        seen[j['id']] = (fo, rp, j)
out = []
for gid, (fo, rp, j) in sorted(seen.items()):
    try:
        r = scan2.scan(os.path.basename(fo), rp, j)
    except Exception as e:
        print('FAIL', gid, fo, e)
        continue
    r['bot_name'] = vers.get(str(r['bot']), '?')
    r['ranked'] = j.get('ranked')
    r['elo'] = [j.get('teamAElo'), j.get('teamBElo')]
    r['seat'] = 'A' if j['teamAId'] == 1119 else 'B'
    out.append(r)
json.dump(out, open('data/codex/astra/trophy-sonnet/trophy.json', 'w'))
print(len(out))
