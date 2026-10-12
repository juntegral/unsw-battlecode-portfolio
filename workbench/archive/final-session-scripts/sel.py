"""Wrap-up: choose which files of an ignored / non-repo tree go to git, and scan them for secrets.
Usage: sel.py swarm|redteam  -> writes tmp/add-<name>.txt (paths relative to the root), prints totals and any secret hit.
Selection: text-like files under a size cap; bulk caches (folders with many small json/csv/jsonl), replays, binaries,
compiled bots and big logs stay out (replays go to release archives instead)."""
import os, re, sys, collections
T = '~/.claude/jobs/e2109d93/tmp'
S = '~/01. Project/개인 프로젝트/unsw-swarm'
R = os.path.expanduser('~/meow-redteam')
which = sys.argv[1]
ALWAYS = {'.md': 5e6, '.txt': 2e6, '.py': 1e6, '.sh': 1e6, '.zsh': 1e6, '.tsv': 2e6, '.switches': 1e6, '.toml': 1e6,
          '.html': 1e6, '.cpp': 1e6, '.hpp': 1e6, '.js': 1e6, '.map': 8e6, '.yml': 1e6, '.yaml': 1e6, '.fixture': 1e6}
DATA = {'.json': 1e5, '.csv': 3e5, '.jsonl': 1e5, '.log': 1e5}
SKIPDIR = {'.git', '__pycache__', 'node_modules', '.unswbc-build', 'build'}


def is_text(p):
    try:
        b = open(p, 'rb').read(4096)
    except OSError:
        return False
    return b'\0' not in b


def select(root, sub, skip_prefix=(), keep_prefix_data=()):
    out = []
    base = os.path.join(root, sub) if sub else root
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in SKIPDIR]
        rel = os.path.relpath(dp, root)
        if any(rel == s or rel.startswith(s + '/') for s in skip_prefix):
            dn[:] = []
            continue
        nd = sum(1 for f in fn if os.path.splitext(f)[1].lower() in DATA)
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.islink(p) or f in ('.DS_Store', 'api.txt', 'discord.txt') or f.endswith('.pyc'):
                continue
            e = os.path.splitext(f)[1].lower()
            n = os.path.getsize(p)
            ok = False
            if e in ALWAYS and n <= ALWAYS[e]:
                ok = True
            elif e in DATA and n <= DATA[e] and (nd <= 60 or any(rel.startswith(k) for k in keep_prefix_data)):
                ok = True
            elif e == '' and n <= 2e5 and is_text(p):
                ok = True
            if ok:
                out.append((os.path.relpath(p, root), n))
    return out


if which == 'swarm':
    root = S
    files = select(S, 'data', skip_prefix=('data/retro-work',))
    # online folders: keep only the uploaded bot folders and small top-level records, never the per-game files
    keep = []
    for rel, n in files:
        if rel.startswith('data/online/'):
            parts = rel.split('/')
            if len(parts) == 3 or (parts[2] == 'smoke' and (len(parts) == 4 or parts[3].endswith('-bot'))) or parts[2] == 'park':
                if not re.match(r'game-\d+\.json$', parts[-1]):
                    keep.append((rel, n))
            continue
        if rel.startswith('data/analysis/top1/') and rel.endswith('.json'):
            continue
        keep.append((rel, n))
    files = keep
else:
    root = R
    files = select(R, '', skip_prefix=('solo/runs', 'runs', 'proof'))
    files += [(r, n) for r, n in select(R, 'runs') + select(R, 'proof') if not r.endswith('.log')]

by = collections.defaultdict(lambda: [0, 0])
for rel, n in files:
    k = '/'.join(rel.split('/')[:3 if which == 'swarm' else 2])
    by[k][0] += 1; by[k][1] += n
for k, (c, n) in sorted(by.items(), key=lambda kv: -kv[1][1])[:45]:
    print(f'{n/1e6:8.1f}MB {c:6d}  {k}')
print('TOTAL', len(files), f'{sum(n for _, n in files)/1e6:.1f}MB', 'largest', sorted(files, key=lambda x: -x[1])[:3])

# secrets
sec = set()
for f in ('docs/api.txt', 'docs/discord.txt'):
    try:
        for tok in re.split(r'[\s=:"\',]+', open(os.path.join(S, f)).read()):
            if len(tok) >= 20:
                sec.add(tok)
    except OSError:
        pass
PAT = {'discord-token': re.compile(r'[MNO][A-Za-z\d_-]{23,25}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,}'),
       'webhook': re.compile(r'discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}'),
       'github-token': re.compile(r'\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}'),
       'sk-key': re.compile(r'\bsk-[A-Za-z0-9_-]{24,}'),
       'bearer': re.compile(r'Bearer\s+[A-Za-z0-9._-]{24,}'),
       'aws': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
       'private-key': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')}
hits = collections.defaultdict(list)
clean = []
for rel, n in files:
    try:
        t = open(os.path.join(root, rel), errors='ignore').read()
    except OSError:
        continue
    bad = None
    for s in sec:
        if s in t:
            bad = 'known-key'
            break
    if not bad:
        for name, rx in PAT.items():
            if rx.search(t):
                bad = name
                break
    if bad:
        hits[bad].append(rel)
    else:
        clean.append(rel)
print('known key strings loaded:', len(sec))
for k, v in hits.items():
    print('SECRET HIT', k, len(v), v[:12])
open(f'{T}/add-{which}.txt', 'w').write('\n'.join(clean) + '\n')
print('written', len(clean), 'clean paths')
