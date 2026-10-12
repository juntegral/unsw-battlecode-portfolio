#!/usr/bin/env python3
"""Team catch-up: new #meow Discord messages + new GitHub activity on the team repo.

usage: python3 tools/team_watch.py [--prs --wait SECONDS]
  no flag: one check at the start of a turn, prints what is new since the last run (Discord + GitHub)
  --prs --wait: background mode, GitHub PR activity only (no Discord); polls every 30 s and exits on the
                first new PR event. Uses its own state file so it never eats the turn-start check.
Repository-feed events from our own account (juntegral) are skipped. PR list changes show the author.
State: data/github/ (git-ignored).
"""
from member_names import member_name
import argparse, json, os, subprocess, sys, time
from pr_poll import pr_activity, pr_list_args

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'forrest-gan2005/battlecode'
ME = 'juntegral'
STATE = os.path.join(ROOT, 'data', 'github', 'last_event.txt')
PR_STATE = os.path.join(ROOT, 'data', 'github', 'last_pr_event.txt')
PR_KINDS = ('PullRequestEvent', 'PullRequestReviewEvent', 'PullRequestReviewCommentEvent')


def discord():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'discord_sync.py')],
                       capture_output=True, text=True, cwd=ROOT)
    lines = (r.stdout + r.stderr).strip().splitlines()
    new = [l for l in lines[1:] if l.strip()]
    return new, (lines[0] if lines else 'discord: 출력 없음')


def short(text, n=160):
    text = ' '.join((text or '').split())
    return text if len(text) <= n else text[:n] + '…'


def render(e):
    p, who, kind = e.get('payload', {}), e['actor']['login'], e['type']
    when = e['created_at'][5:16].replace('T', ' ') + 'Z'
    if kind == 'IssuesEvent':
        i = p['issue']
        lab = f" {p['label']['name']}" if p.get('label') else ''
        what = f"issue #{i['number']} {p['action']}{lab}: {i['title']}"
    elif kind == 'IssueCommentEvent':
        i = p['issue']
        what = f"comment on #{i['number']} ({i['title']}): {short(p['comment']['body'])}"
    elif kind == 'PullRequestEvent':
        pr = p['pull_request']
        act = 'merged' if p['action'] == 'closed' and pr.get('merged') else p['action']
        what = f"PR #{pr['number']} {act}: {pr['title']}"
    elif kind in ('PullRequestReviewEvent', 'PullRequestReviewCommentEvent'):
        body = (p.get('review') or p.get('comment') or {}).get('body')
        what = f"review on PR #{p['pull_request']['number']}: {short(body) or (p.get('review') or {}).get('state', '')}"
    elif kind == 'PushEvent':
        msgs = [short(c['message'].splitlines()[0], 80) for c in p.get('commits', [])]
        what = f"push to {p.get('ref', '').replace('refs/heads/', '')}" + (': ' + ' | '.join(msgs) if msgs else '')
    elif kind in ('CreateEvent', 'DeleteEvent'):
        what = f"{kind[:-5].lower()} {p.get('ref_type')} {p.get('ref') or ''}".strip()
    else:
        what = kind
    return f'- {when} {who}: {what}'


def is_pr(e):
    return e['type'] in PR_KINDS or (e['type'] == 'IssueCommentEvent' and 'pull_request' in e['payload'].get('issue', {}))


def github(state=STATE, prs=False):
    lines = []
    snapshot_file = state + '.prs.json'
    r = subprocess.run(['gh'] + pr_list_args(REPO), capture_output=True, text=True)
    if r.returncode:
        lines.append(f'(GitHub PR 조회 실패: {short(r.stderr, 120)})')
    else:
        try:
            with open(snapshot_file) as f:
                st = json.load(f)
        except (OSError, ValueError):
            st = {}
        for pr, action in pr_activity(st, json.loads(r.stdout), head_changes=True):
            who = member_name(pr['author']['login'])
            when = (pr.get('mergedAt') if action == 'merged' else pr.get('closedAt') if action == 'closed' else None) or pr['updatedAt']
            when = when[5:16].replace('T', ' ') + 'Z'
            lines.append(f"- {when} {who}: PR #{pr['number']} {action}: {pr['title']}")
        os.makedirs(os.path.dirname(snapshot_file), exist_ok=True)
        with open(snapshot_file + '.tmp', 'w') as f:
            json.dump(st, f)
        os.replace(snapshot_file + '.tmp', snapshot_file)
    r = subprocess.run(['gh', 'api', f'repos/{REPO}/events?per_page=50'], capture_output=True, text=True)
    if r.returncode:
        return lines + [f'(GitHub 조회 실패: {short(r.stderr, 120)})']
    events = json.loads(r.stdout)
    try:
        with open(state) as f:
            last = int(f.read().strip())
    except (OSError, ValueError):
        last = None
    if events:
        os.makedirs(os.path.dirname(state), exist_ok=True)
        with open(state, 'w') as f:
            f.write(str(max(int(e['id']) for e in events)) + '\n')
    fresh = [e for e in events if last is None or int(e['id']) > last]
    if last is None:
        fresh = [] if prs else fresh[:10]
    return lines + [render(e) for e in reversed(fresh) if e['type'] != 'PullRequestEvent'
                    and e['actor']['login'] != ME and (not prs or is_pr(e))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--wait', type=int, default=0)
    ap.add_argument('--prs', action='store_true')
    args = ap.parse_args()
    if args.prs:
        deadline = time.time() + args.wait
        while True:
            new = [l for l in github(PR_STATE, prs=True) if not l.startswith('(GitHub')]
            if new or time.time() >= deadline:
                break
            time.sleep(30)
        print(f'[GitHub PR] 새 PR 활동 {len(new)}건')
        for l in new:
            print(l)
        return
    deadline = time.time() + args.wait
    while True:
        d_new, d_head = discord()
        g_new = github()
        if d_new or g_new or time.time() >= deadline:
            break
        time.sleep(20)
    print(f'[Discord] {d_head}')
    for l in d_new:
        print(l)
    print(f'[GitHub {REPO}] 새 활동 {len(g_new)}건')
    for l in g_new:
        print(l)


if __name__ == '__main__':
    main()
