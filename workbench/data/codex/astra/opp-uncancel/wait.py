"""opp-uncancel: wait (max N seconds) for a new battle folder holding team 899 games with replays."""
import glob, json, os, sys, time
sys.dont_write_bytecode = True
known = set(sys.argv[2:])
end = time.time() + int(sys.argv[1])
while time.time() < end:
    for d in glob.glob('data/online/live-one1/b*'):
        b = os.path.basename(d)
        if b in known:
            continue
        gs = glob.glob(d + '/game-*.json')
        if not gs:
            continue
        try:
            j = json.load(open(gs[0]))
        except Exception:
            continue
        if 899 in (j.get('teamAId'), j.get('teamBId')):
            n = len(glob.glob(d + '/M*.replay'))
            if n == len(gs):
                time.sleep(3)
                print('NEW', b, 'games', len(gs), 'replays', n)
                sys.exit(0)
    time.sleep(5)
print('TIMEOUT', time.strftime('%H:%M:%S'))
