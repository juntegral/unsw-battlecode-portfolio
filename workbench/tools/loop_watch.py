"""Wake-up watcher: exits with a short reason when the loop needs a look. No model.
Optional third argument quiet skips finished steps and building/testing state wakes.
"""
import json, os, re, subprocess, sys, time, datetime
OUT = os.path.expanduser('~/meow-loop-out')
SWARM = "~/01. Project/개인 프로젝트/unsw-swarm"
MIRROR = SWARM + "/data/discord/900000000000000004.md"
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 7200
LATE_AFTER = time.time() + 60 * float(sys.argv[2]) if len(sys.argv) > 2 else 0
QUIET = len(sys.argv) > 3 and sys.argv[3] == 'quiet'
def status():
    try: return json.load(open(OUT + '/status.json'))
    except Exception: return {}
def states(s): return {k: (c.get('state'), c.get('step')) for k, c in (s.get('cards') or {}).items() if isinstance(c, dict)}
def humans():
    # Wake for: anyone mentioning the bot; a teammate replying to the bot without addressing someone else;
    # a card answer relayed by the bot; a typed command the bot does not handle itself (it takes /meow and /answer).
    BOT = r'(<@!?900000000000000001>|@meowbot)'
    other = re.compile(r'<@!?(?!900000000000000001)\d+>')
    head = re.compile(r'^- \d\d-\d\d \d\d:\d\d \*\*([^*]+)\*\*: (.*)')
    out = []
    try: lines = open(MIRROR, encoding='utf-8').readlines()
    except Exception: return out
    for l in lines:
        m = head.match(l)
        if not m: continue
        who, text = m.group(1), m.group(2)
        if who.startswith('meowbot'):
            if re.match(r'💬 (Zhe|QWQ|jun|준싱) answered', text) or text.startswith('via /meow by'): out.append(l)
            continue
        if re.search(BOT, text) or (text.startswith('/') and not re.match(r'(?i)/(?:meow\s|answer(?:\s|$))', text)): out.append(l)
        elif text.startswith('↪ meowbot') and not other.search(text): out.append(l)
    return out
def alive(pat): return subprocess.run(['pgrep', '-f', pat], capture_output=True).returncode == 0
ev0 = sum(1 for _ in open(OUT + '/events.jsonl'))
st0 = {k: v[0] for k, v in states(status()).items()}
hm0 = len(humans())
t0 = time.time()
why = None
gone_n = 0
while not why and time.time() - t0 < LIMIT:
    time.sleep(60)
    subprocess.run(['python3', SWARM + '/tools/team_watch.py'], cwd=SWARM, capture_output=True)
    s = status(); now = time.time()
    rows = [json.loads(l) for l in list(open(OUT + '/events.jsonl'))[ev0:]]
    failed = [r for r in rows if r.get('event') == 'failed']
    built = [r for r in rows if r.get('event') == 'done' and r.get('step') in ('build', 'look', 'outcome', 'verdict')]
    if built and not QUIET: why = why or 'step finished: ' + '; '.join(f"#{r['card']} {r['step']}" for r in built)
    if failed: why = 'FAILED step: ' + '; '.join(f"#{r['card']} {r['step']}: {(r.get('note') or '')[:120]}" for r in failed)
    cur = states(s)
    for k, (state, step) in cur.items():
        if 'needs attention' in (step or '') or 'failed' in (step or ''): why = why or f'#{k} needs attention: {step[:160]}'
        if k in st0 and st0.get(k) != state:
            if QUIET and state in ('building', 'testing'): st0[k] = state
            else: why = why or f'#{k} moved {st0.get(k)} -> {state}: {step[:120]}'
        if QUIET and k not in st0 and state in ('needs-look', 'needs-info'): why = why or f'#{k} entered {state}: {step[:120]}'
    gone = [k for k in st0 if k not in cur]
    new = [k for k in cur if k not in st0]
    for k in new: st0[k] = cur[k][0]
    gone_n = (gone_n + 1) if gone else 0
    if gone_n >= 4: why = why or f'card left the loop list for 4 checks (tested, candidate or closed?): {gone}'
    for k, c in (s.get('cards') or {}).items():
        if not isinstance(c, dict) or c.get('queue') or not c.get('step_started') or not c.get('eta_minutes'): continue
        if not re.search(r'running|started', c.get('step') or ''): continue
        ran = (now - datetime.datetime.fromisoformat(c['step_started']).timestamp()) / 60
        if now > LATE_AFTER and ran > 1.5 * c['eta_minutes'] and ran - c['eta_minutes'] > 10: why = why or f"#{k} {c.get('step_kind')} is late: {ran:.0f}m, planned {c['eta_minutes']:.0f}m; {(c.get('reason') or '')[:140]}"
    try:
        upd = datetime.datetime.fromisoformat(s.get('updated')).timestamp()
        if now - upd > 900: why = why or f'status.json not updated for {(now-upd)/60:.0f} min'
    except Exception: pass
    if not alive('work/loop/runner.py --game-env'): why = why or 'runner process is gone'
    if not alive('tools/meowbot.py'): why = why or 'meowbot process is gone'
    if len(humans()) > hm0:
        last = humans()[-1]
        why = why or 'someone mentioned or replied to the bot, or answered a card: ' + last[:200].strip()
        if '**meowbot' not in last[:40]:  # a person is waiting for an answer: show that it is being worked on
            subprocess.run(['python3', SWARM + '/tools/meow_think.py', 'start'], cwd=SWARM, capture_output=True)
print(datetime.datetime.now().strftime('%H:%M'), 'WAKE:', why or f'heartbeat after {LIMIT/60:.0f} min, nothing flagged')
s = status()
for k, c in (s.get('cards') or {}).items():
    if isinstance(c, dict): print(f"#{k} {c.get('name')} | {c.get('state')} | {c.get('step')} | eta {(c.get('new_eta_at') or c.get('eta_at') or '')[11:16]}")
for r in [json.loads(l) for l in list(open(OUT + '/events.jsonl'))[ev0:]][-8:]:
    print(' ', r['time'][11:16], f"#{r['card']}", r['step'], r['event'], round(r.get('minutes') or 0, 1), (r.get('note') or '')[:100])
