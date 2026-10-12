"""Secret scan of the files git would commit. Usage: scan.py <repo root> [--staged | --worktree]
--staged: files in the index that differ from HEAD; --worktree: modified + untracked (not ignored). Prints names only."""
import os, re, subprocess, sys
S = '~/01. Project/개인 프로젝트/unsw-swarm'
root, mode = sys.argv[1], sys.argv[2]
if mode == '--staged':
    out = subprocess.run(['git', '-C', root, 'diff', '--cached', '--name-only', '-z'], capture_output=True).stdout
else:
    out = subprocess.run(['git', '-C', root, 'ls-files', '-z', '-m', '-o', '--exclude-standard'], capture_output=True).stdout
files = [f for f in out.decode().split('\0') if f]
sec = set()
for f in ('docs/api.txt', 'docs/discord.txt'):
    for tok in re.split(r'[\s=:"\',]+', open(os.path.join(S, f)).read()):
        if len(tok) >= 20:
            sec.add(tok)
PAT = {'discord-token': re.compile(r'[MNO][A-Za-z\d_-]{23,25}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,}'),
       'webhook': re.compile(r'discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}'),
       'github-token': re.compile(r'\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}'),
       'sk-key': re.compile(r'\bsk-[A-Za-z0-9_-]{24,}'),
       'bearer': re.compile(r'Bearer\s+[A-Za-z0-9._-]{24,}'),
       'aws': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
       'private-key': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')}
n = big = hit = 0
for f in files:
    p = os.path.join(root, f)
    if not os.path.isfile(p) or os.path.islink(p):
        continue
    n += 1
    sz = os.path.getsize(p)
    if sz > 40e6:
        big += 1
        print('BIG', f, int(sz / 1e6), 'MB')
    t = open(p, errors='ignore').read()
    bad = 'known-key' if any(s in t for s in sec) else next((k for k, rx in PAT.items() if rx.search(t)), None)
    if bad:
        hit += 1
        print('SECRET HIT', bad, f)
    if os.path.basename(f) in ('api.txt', 'discord.txt', '.env'):
        hit += 1
        print('KEY FILE NAME', f)
print(f'{mode}: {n} files scanned, {hit} hits, {big} over 40MB, total {sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.isfile(os.path.join(root, f)))/1e6:.1f}MB')
