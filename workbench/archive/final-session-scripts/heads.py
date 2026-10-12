import sys, os, glob
d = sys.argv[1]; pats = sys.argv[2].split(','); n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
W = int(sys.argv[4]) if len(sys.argv) > 4 else 300
fs = sorted(set(f for p in pats for f in glob.glob(os.path.join(d, p))))
for f in fs:
    try: L = open(f, encoding='utf-8', errors='replace').read().splitlines()
    except Exception as e: continue
    keep = [l.strip() for l in L[:14] if l.strip() and not l.startswith('#!') and not l.startswith('import ') and not l.startswith('from ') and not l.startswith('sys.') and l.strip() != 'set -eu'][:n]
    print('%s (%d): %s' % (os.path.basename(f), len(L), ' | '.join(keep)[:W]))
