"""Wrap-up: put each worktree's uncommitted work on GitHub as a commit on an archive branch, without touching the
worktree, its index or its branch (a temporary index file is used and the commit is made with commit-tree).
Text files under 2 MB only; anything else is listed as left out. Usage: wtarch.py [--push]"""
import os, re, subprocess, sys
T = '~/.claude/jobs/e2109d93/tmp'
S = '~/01. Project/개인 프로젝트/unsw-swarm'
H = os.path.expanduser('~')
WT = [(H + '/meow-bigmap', 'exp-bigmap-state'), (H + '/meow-dev', 'dev-pool'), (H + '/meow-dev2', 'dev-fair'),
      (H + '/meow-dev3', 'dev-latefix'), (H + '/meow-loop', 'loop-overnight-1003'), (H + '/meow-queen', 'exp-zhe-queen')]
push = '--push' in sys.argv
sec = set()
for f in ('docs/api.txt', 'docs/discord.txt'):
    for tok in re.split(r'[\s=:"\',]+', open(os.path.join(S, f)).read()):
        if len(tok) >= 20:
            sec.add(tok)
RX = re.compile(r'[MNO][A-Za-z\d_-]{23,25}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,}|discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}|\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}|\bsk-[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9._-]{24,}|BEGIN [A-Z ]*PRIVATE KEY')


def git(w, *a, env=None, inp=None):
    r = subprocess.run(['git', '-C', w, *a], capture_output=True, env=env, input=inp)
    if r.returncode:
        raise SystemExit(f'git {a} failed in {w}: {r.stderr.decode()[:300]}')
    return r.stdout.decode()


for w, name in WT:
    branch = git(w, 'branch', '--show-current').strip()
    head = git(w, 'rev-parse', 'HEAD').strip()
    files = [f for f in git(w, 'ls-files', '-z', '-m', '-o', '-d', '--exclude-standard').split('\0') if f]
    add, out, hits = [], [], []
    for f in sorted(set(files)):
        p = os.path.join(w, f)
        if not os.path.exists(p):
            add.append(f)  # deleted in the worktree
            continue
        if os.path.islink(p) or not os.path.isfile(p):
            out.append(f); continue
        n = os.path.getsize(p)
        b = open(p, 'rb').read()
        if n > 2e6 or b'\0' in b[:8192]:
            out.append(f); continue
        t = b.decode(errors='ignore')
        if any(s in t for s in sec) or RX.search(t):
            hits.append(f); continue
        add.append(f)
    osz = sum(os.path.getsize(os.path.join(w, f)) for f in out if os.path.isfile(os.path.join(w, f)))
    print(f'{name}: branch {branch} head {head[:7]}  to commit {len(add)}  left out {len(out)} ({osz/1e6:.0f}MB)  secret hits {hits}')
    exts = {}
    for f in out:
        e = os.path.splitext(f)[1] or '(none)'
        exts[e] = exts.get(e, 0) + 1
    if out:
        print('   left out by type:', exts)
    if not push:
        continue
    env = dict(os.environ, GIT_INDEX_FILE=f'{T}/idx-{name}')
    if os.path.exists(env['GIT_INDEX_FILE']):
        os.remove(env['GIT_INDEX_FILE'])
    git(w, 'read-tree', 'HEAD', env=env)
    git(w, 'add', '-A', '--pathspec-from-file=-', '--pathspec-file-nul', env=env, inp='\0'.join(add).encode())
    tree = git(w, 'write-tree', env=env).strip()
    msg = (f'Archive: uncommitted local work on {branch} at contest wrap-up (2026-10-10)\n\n'
           f'Snapshot of a local worktree so that nothing is left only on one machine.\n'
           f'Not for merge. {len(add)} files; replays and other bulk or binary files are not included.\n\n'
           f'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n')
    commit = git(w, 'commit-tree', tree, '-p', head, '-m', msg).strip()
    r = subprocess.run(['git', '-C', w, 'push', 'origin', f'{commit}:refs/heads/archive/local-1010/{name}'], capture_output=True)
    print('   pushed' if r.returncode == 0 else '   PUSH FAILED', commit[:7], r.stderr.decode().strip().splitlines()[-1][:120])
    os.remove(env['GIT_INDEX_FILE'])
