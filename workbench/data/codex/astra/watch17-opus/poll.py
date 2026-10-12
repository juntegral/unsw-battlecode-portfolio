"""watch17-opus: wait for a new one17 set or a new ranked battle. Usage (from ROOT): python3 -B .../poll.py [max seconds]"""
import sys, json, glob, time, os
from pathlib import Path
C = json.loads(Path('data/codex/astra/watch17-opus/cache.json').read_text())
end = time.time() + (int(sys.argv[1]) if len(sys.argv) > 1 else 480)
while time.time() < end:
    hit = []
    for lab in ('one17-s1', 'one17-p1', 'one18-c1', 'one18-s1', 'one18-p1', 'one18-w1'):
        fs = glob.glob('data/online/smoke/%s-old/game-*.json' % lab)
        if os.path.exists('data/online/smoke/%s-finished' % lab) and any(Path(f).stem.split('-')[1] not in C for f in fs):
            hit.append(lab)
    for d in sorted(glob.glob('data/online/live-one1/b*'), key=os.path.getmtime)[-6:]:
        for f in glob.glob(d + '/game-*.json'):
            if Path(f).stem.split('-')[1] not in C:
                j = json.load(open(f))
                if (j.get('completedAt') or '') >= '2026-10-09T04:31' and 1119 in (j['teamAId'], j['teamBId']):
                    hit.append(d)
                    break
    if hit:
        time.sleep(8)
        print('NEW', hit, time.strftime('%H:%M:%S'))
        sys.exit(0)
    time.sleep(20)
print('none', time.strftime('%H:%M:%S'))
