"""Wrap-up inventory 2, read-only: what the ignored data folders hold, by folder and file type, and how well replays compress."""
import os, sys, collections, subprocess, gzip
S = '~/01. Project/개인 프로젝트/unsw-swarm'
R = os.path.expanduser('~/meow-redteam')
TEXT = {'.md', '.txt', '.py', '.tsv', '.csv', '.json', '.zsh', '.sh', '.toml', '.cpp', '.hpp', '.js', '.map', '.switches', '.yml', '.yaml', ''}


def walk(root, depth):
    by = collections.defaultdict(lambda: [0, 0])
    ext = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    small = collections.defaultdict(lambda: [0, 0])
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '.git']
        rel = os.path.relpath(dp, root).split(os.sep)
        key = '/'.join(rel[:depth])
        for f in fn:
            p = os.path.join(dp, f)
            try:
                if os.path.islink(p):
                    continue
                n = os.path.getsize(p)
            except OSError:
                continue
            e = os.path.splitext(f)[1].lower()
            by[key][0] += 1; by[key][1] += n
            ext[key][e][0] += 1; ext[key][e][1] += n
            if e in TEXT and n < 1_000_000:
                small[key][0] += 1; small[key][1] += n
    return by, ext, small


def show(title, root, depth, top=28):
    by, ext, small = walk(root, depth)
    print('===', title)
    for k, (c, n) in sorted(by.items(), key=lambda kv: -kv[1][1])[:top]:
        es = sorted(ext[k].items(), key=lambda kv: -kv[1][1])[:4]
        print(f'{n/1e6:9.0f}MB {c:7d} files  small-text {small[k][0]:6d}/{small[k][1]/1e6:6.1f}MB  {k:42s} ' + ' '.join(f'{e or "(none)"}:{v[0]}/{v[1]/1e6:.0f}MB' for e, v in es))


show('unsw-swarm/data', S + '/data', 2)
show('meow-redteam (without solo/runs)', R, 2, top=30)
# sample replay compression
import glob
smp = sorted(glob.glob(S + '/data/online/live-one1/b1532570/*'))[:6]
for p in smp:
    raw = open(p, 'rb').read()
    print(os.path.basename(p), len(raw), 'gz', len(gzip.compress(raw, 6)), 'head', raw[:16])
