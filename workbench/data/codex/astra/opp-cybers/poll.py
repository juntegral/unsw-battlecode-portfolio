"""opp-cybers: wait (up to argv[1] seconds) for a battle folder against 1148 that is not b1512747 and has all replays."""
import sys, json, glob, time, os
t0 = time.time()
lim = int(sys.argv[1])
while True:
    hit = {}
    for f in glob.glob('data/online/live-one1/b153*/game-*.json') + glob.glob('data/online/smoke/*-old/game-153*.json'):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if 1148 in (j.get('teamAId'), j.get('teamBId')):
            d = os.path.dirname(f)
            hit.setdefault(d, []).append((j['id'], j.get('status'), j.get('winner'), j.get('mapName'), os.path.exists('%s/M%d.replay' % (d, j['id']))))
    if hit and all(all(g[4] for g in v) for v in hit.values()):
        for d, v in hit.items():
            print(d, sorted(v))
        break
    if time.time() - t0 > lim:
        print('none yet', hit)
        break
    time.sleep(10)
