"""Wrap-up: save every report the analysts sent to the lead during the last session. Several analysts (opponent
studies, watchers) reported only by message, so the session transcript is the only place their text exists.
Reads the transcript, writes archive/final-session-agent-reports/<agent>.md (messages in order, duplicates dropped)."""
import json, os, re, collections, hashlib
TR = '~/.claude/projects/-Users-jun-01--Project---------battlecode--claude-worktrees-one13-into-main/e2109d93-03be-427c-b332-75e8d0f32a2d.jsonl'
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/archive/final-session-agent-reports'
RX = re.compile(r'<teammate-message teammate_id="([^"]+)"[^>]*?(?:summary="([^"]*)")?>\n?(.*?)</teammate-message>', re.S)
by = collections.defaultdict(list)
seen = set()


def texts(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from texts(x)
    elif isinstance(o, dict):
        for k in ('text', 'content'):
            if k in o:
                yield from texts(o[k])


n = 0
with open(TR, errors='ignore') as f:
    for line in f:
        if '<teammate-message' not in line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('type') != 'user':
            continue
        ts = row.get('timestamp', '')
        for t in texts(row.get('message', {})):
            for who, summ, body in RX.findall(t):
                body = body.strip()
                if body.startswith('{'):
                    try:
                        j = json.loads(body)
                        if j.get('type') != 'idle_notification' or not j.get('result'):
                            continue
                        body, summ = j['result'], 'closing summary'
                    except ValueError:
                        pass
                h = hashlib.sha1((who + body).encode()).hexdigest()
                if h in seen or len(body) < 80:
                    continue
                seen.add(h)
                by[who].append((ts, summ, body))
                n += 1
os.makedirs(OUT, exist_ok=True)
for who, rows in by.items():
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', who)
    with open(os.path.join(OUT, name + '.md'), 'w') as f:
        f.write(f'# Reports sent to the lead by {who}\n\nTaken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).\n')
        for ts, summ, body in rows:
            f.write(f'\n---\n\n## {ts[:19].replace("T", " ")}' + (f' — {summ}' if summ else '') + f'\n\n{body}\n')
print(n, 'messages from', len(by), 'agents ->', OUT)
print(sorted((len(v), k) for k, v in by.items())[-12:])
