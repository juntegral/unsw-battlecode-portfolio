"""opp-ballers: wait for a new battle folder holding team 1149 (not b1507592). Usage: poll.py <HHMM stop> [min replays]"""
import sys, glob, json, time, os
stop = int(sys.argv[1])
need = int(sys.argv[2]) if len(sys.argv) > 2 else 5
while True:
    hit = {}
    for f in glob.glob('data/online/live-one1/b*/game-*.json'):
        if 'b1507592' in f:
            continue
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if 1149 in (j.get('teamAId'), j.get('teamBId')):
            d = os.path.dirname(f)
            hit[d] = (len(glob.glob(d + '/game-*.json')), len(glob.glob(d + '/M*.replay')))
    if hit and all(v[1] >= min(need, v[0]) for v in hit.values()):
        print('NEW', hit, time.strftime('%H:%M:%S'))
        break
    if int(time.strftime('%H%M')) >= stop:
        print('TIME', hit, time.strftime('%H:%M:%S'))
        break
    time.sleep(15)
