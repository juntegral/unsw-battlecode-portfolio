"""watch19-opus: wait until cache.json exists or N seconds pass."""
import sys, time, os
end = time.time() + int(sys.argv[1])
while time.time() < end and not os.path.exists('data/codex/astra/watch19-opus/cache.json'):
    time.sleep(5)
print(os.path.exists('data/codex/astra/watch19-opus/cache.json'), time.strftime('%H:%M:%S'))
