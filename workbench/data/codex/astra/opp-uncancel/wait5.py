"""opp-uncancel: wait until folder argv[1] holds argv[2] replays (max argv[3] s)."""
import glob, sys, time
sys.dont_write_bytecode = True
end = time.time() + int(sys.argv[3])
while time.time() < end:
    n = len(glob.glob('data/online/live-one1/%s/M*.replay' % sys.argv[1]))
    if n >= int(sys.argv[2]):
        time.sleep(4)
        break
    time.sleep(3)
print(sys.argv[1], 'replays', len(glob.glob('data/online/live-one1/%s/M*.replay' % sys.argv[1])), time.strftime('%H:%M:%S'))
