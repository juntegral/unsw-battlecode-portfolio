"""watch19-opus: wait until a new battle folder holds a finished game with its replay that is not in cache.json.
Usage (from ROOT): python3 -B .../poll19.py [max seconds]"""
import sys, json, glob, time, os
from pathlib import Path
cp = Path('data/codex/astra/watch19-opus/cache.json')
end = time.time() + (int(sys.argv[1]) if len(sys.argv) > 1 else 55)
while True:
    C = json.loads(cp.read_text()) if cp.exists() else {}
    hit = []
    for d in sorted(glob.glob('data/online/live-one1/b*'), key=os.path.getmtime)[-8:]:
        for f in glob.glob(d + '/game-*.json'):
            gid = Path(f).stem.split('-')[1]
            if gid not in C and os.path.exists('%s/M%s.replay' % (d, gid)):
                j = json.load(open(f))
                if (j.get('completedAt') or '') >= '2026-10-09T04:25' and 1119 in (j['teamAId'], j['teamBId']):
                    hit.append(os.path.basename(d))
                    break
    if hit or time.time() >= end:
        break
    time.sleep(10)
print('NEW' if hit else 'none', hit, time.strftime('%H:%M:%S'))
