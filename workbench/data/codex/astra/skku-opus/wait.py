import glob, time, subprocess, sys
t0 = time.time()
while time.time() - t0 < 200:
    n = len(glob.glob('data/online/live-one1/b1536232/M*.replay')); m = len(glob.glob('data/online/live-one1/b1536232/game-*.json'))
    if n >= 5 and m >= 5: break
    time.sleep(5)
print('replays', n, 'json', m, 'waited', round(time.time() - t0), flush=True)
time.sleep(2)
subprocess.run([sys.executable, '-B', 'data/codex/astra/skku-opus/last.py'])
