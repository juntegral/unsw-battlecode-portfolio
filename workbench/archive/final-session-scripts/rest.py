"""Wrap-up: in a repo, stage the remaining untracked (not ignored) files that are text and under 2 MB; report the rest.
Usage: rest.py <repo root>"""
import os, subprocess, sys, collections
root = sys.argv[1]
out = subprocess.run(['git', '-C', root, 'ls-files', '-z', '-o', '--exclude-standard'], capture_output=True).stdout
files = [f for f in out.decode().split('\0') if f]
add, skip = [], collections.defaultdict(lambda: [0, 0, []])
for f in files:
    p = os.path.join(root, f)
    if os.path.islink(p) or not os.path.isfile(p):
        skip['link-or-special'][0] += 1; skip['link-or-special'][2].append(f); continue
    n = os.path.getsize(p)
    b = open(p, 'rb').read(8192)
    if b'\0' in b or n > 2e6:
        k = f.split('/')[0] + ('/' + f.split('/')[1] if '/' in f else '')
        skip[k][0] += 1; skip[k][1] += n; skip[k][2].append(f)
    else:
        add.append(f)
if add:
    subprocess.run(['git', '-C', root, 'add', '--pathspec-from-file=-', '--pathspec-file-nul'], input='\0'.join(add).encode(), check=True)
print('added', len(add), 'e.g.', add[:8])
for k, (c, n, ex) in sorted(skip.items(), key=lambda kv: -kv[1][1]):
    print(f'left out {c:5d} files {n/1e6:8.1f}MB  {k}  e.g. {ex[:2]}')
