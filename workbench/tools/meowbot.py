#!/usr/bin/env python3
"""meowbot: bridges the team repo and Discord #meow.

usage: python3 tools/meowbot.py                 run (posts PR/idea updates, candidate approvals, slash commands)
       python3 tools/meowbot.py --preview-pr N  print how PR N would be posted, then exit
       python3 tools/meowbot.py --preview-candidate FILE  print how a candidate manifest would be posted
       python3 tools/meowbot.py --preview-candidate-pr N  preview candidate cards from an open PR (read-only)
       python3 tools/meowbot.py --announce-file FILE [--dry-run]  post a one-off message via REST, then exit
/meow <message>: member-only threaded teammate; follow-ups resume a read-only Claude session.
Quick explanations use Sonnet medium; actions/analysis/judgment use Opus high. Each call refreshes data/meow/brain.md.
AI returns validated action plans; only meowbot executes them after requester confirmation.
Force is available to every member: one Confirm, with the member's own /meow message recorded as the reason;
the Force buttons ask for a one-line reason, and submitting it is the last step. Public/card audit either way.
tools/meow_offer.py leaves a ready-made plan in OFFER_DIR; the bot posts it with a Confirm only the named member can press.
A member's ordinary message in #meow that starts with "/meow " or "/answer " is handled as that command.
Keys, ranked requests, branch/issue deletion and team rules/memory edits are never forceable.
Runner controls use durable requests; forced bot merges queue a notification-only old-map identity check.
/meow queue and /status show unresolved requests. Requires Discord message-content intent for thread follow-ups.
Slash commands (team members only): /hypo, /hypo-max (AI analysis), /board (open ideas, only you see it), /board-edit <issue>.
/task [who=all] [share=false]: each person's next actions, private by default, without a model call.
/answer card:<issue number> text:<answer> is the card reply command: questions, replay checks and result decisions.
Replies are untranslated and visible on the open [Idea]/[Task] card and in #meow.
Use text:ship it / drop it / revise: … after results; /meow covers everything else.
State pings have no extra Force post; candidate buttons and /meow force #31 … remain available.
Ideas carry by:junsing/by:zhe/by:qwq/by:ai. /hypo, /hypo-max and /board-edit accept idea_by;
text may also contain an Idea by: <member> line. AI analysis preserves the human proposer.
Loops can use author_label("AI") and tag promoted AI cards: gh issue edit N --add-label by:ai.
Candidates: open PRs changing candidates/*.json (see CANDIDATE_FIELDS). Human ideas need an author OK + a non-author OK;
unknown authors need two distinct members; AI-only needs one member (AI promotion counts as the author's OK).
OKs persist on cancel and unchanged patch-id after rebase; changed patches reset OKs.
Approvals merge to main only and mark linked cards kept. /submit [ref=main] needs only the requesting member,
then confirmation submits the exact commit through UPLOAD_ENABLED (enabled).
Normal submissions freeze at 2026-10-08 20:00 KST; Force requires explicit responsibility and its own confirmation. Rollbacks are manual.
Candidate OKs never upload. Submit cards are pinned to exact commits.
Secrets: docs/discord.txt (bot token); the game key is read by tools/submit.js only. State: data/meowbot/ (git-ignored).
"""
import argparse, asyncio, base64, datetime, gzip, hashlib, io, json, os, re, ssl, subprocess, sys, tempfile, threading
from zoneinfo import ZoneInfo
import math
from contextlib import ExitStack
from urllib.parse import quote
from urllib.request import Request, urlopen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr_poll import pr_activity, pr_list_args
from replay_fix import strip_padding
from fair_queue import author as queue_author, order_cards, read_fair
from card_names import card_ref as format_card_ref, card_name, label_names, unique_slug, valid_slug
import snooze
from member_names import member_name, member_state
import tasks as task_lists
import decision_nudge as nudge
import meow_chat
from meow_ui import MeowUI

# python.org builds ship without a CA bundle; fall back to the macOS one
if not os.path.exists(ssl.get_default_verify_paths().openssl_cafile or "") and os.path.exists("/etc/ssl/cert.pem"):
    os.environ.setdefault("SSL_CERT_FILE", "/etc/ssl/cert.pem")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "forrest-gan2005/battlecode"
STATE = os.path.join(ROOT, "data", "meowbot", "state.json")
RELEASE_DIR = os.path.expanduser("~/meow-release")
LOOP_DIR = os.path.expanduser("~/meow-loop")
LOOK_DIR = os.path.expanduser("~/meow-loop-out")
OFFER_DIR = os.path.join(ROOT, "data", "meowbot", "offers")
LOOK_MAX_BYTES = 24 * 1024 * 1024
LOOK_INLINE_BYTES = 8 * 1024 * 1024
MEMBERS = {900000000000000005: "jun", 900000000000000002: "Zhe", 900000000000000003: "QWQ"}
AUTHOR_LABELS = {"jun": "by:junsing", "Zhe": "by:zhe", "QWQ": "by:qwq", "AI": "by:ai"}
UPLOAD_ENABLED = True
POLL_SECONDS = 60
TRANSLATE_MODEL = ("claude-sonnet-5-5", "medium")
ANALYSIS_MODEL = ("opus", "high")
ANALYSIS_TIMEOUT = 25 * 60
WORKFLOW = {1: "① Zhe's workflow", 2: "② Board loop", 3: "③ Full-AI workflow"}
AREAS = ["queen", "terrain", "late-game", "economy", "infra", "other"]
COLOR = {"opened": 0x2C64C4, "reopened": 0x2C64C4, "ready-for-review": 0x2C64C4, "merged": 0x8957E5, "closed": 0x6E7781, "idea": 0xA86400,
         "candidate": 0x1F7A50, "analysis": 0x0B6E78}
CARD = [("claim", "Claim"), ("evidence", "Evidence"), ("expected_signal", "Expected signal"), ("falsifier", "What would show it's wrong")]
EXTRA = [("code_pointers", "Code pointers"), ("prior_attempts", "Prior attempts"), ("ladder_evidence", "Ladder evidence"),
         ("overlap", "Overlap with owners"), ("toggle_sketch", "Toggle sketch"), ("test_plan", "Test plan"), ("risks", "Risks")]
CANDIDATE_FIELDS = ("version", "workflow", "changes", "results", "bot_dir", "issues", "pr")
FINAL_STATES = {"kept", "rejected", "inconclusive"}
_STATE_WRITE_LOCK = threading.Lock()


def clamp_embed(embed, field_pointer=""):
    embed = {**embed}
    parts = []

    def add(container, key, limit, pointer=""):
        if key in container:
            suffix = "\n" + pointer if pointer else ""
            text = container[key]
            parts.append((container, key, suffix))
            if len(text) > limit:
                container[key] = text[:limit - len(suffix) - 1] + "…" + suffix

    add(embed, "title", 256)
    add(embed, "description", 4096)
    for key, text_key, limit in (("footer", "text", 2048), ("author", "name", 256)):
        if key in embed:
            embed[key] = {**embed[key]}
            add(embed[key], text_key, limit)
    if "fields" in embed:
        embed["fields"] = [{**field} for field in embed["fields"][:25]]
        for field in embed["fields"]:
            add(field, "name", 256)
            add(field, "value", 1024, field_pointer)
    excess = sum(len(container[key]) for container, key, _ in parts) - 6000
    for container, key, suffix in sorted(parts, key=lambda part: len(part[0][part[1]]), reverse=True):
        if excess <= 0:
            break
        text = container[key]
        cut = min(excess, max(0, len(text) - len(suffix) - 1))
        if cut:
            limit = len(text) - cut
            container[key] = text[:limit - len(suffix) - 1] + "…" + suffix
            excess -= cut
    return embed


def gh(args):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    if not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return r.stdout.strip()


def card_ref(issue_or_number):
    if isinstance(issue_or_number, dict):
        return format_card_ref(issue_or_number)
    try:
        issue = gh(['issue', 'view', str(issue_or_number), '--repo', REPO,
                    '--json', 'number,title,labels'])
        if isinstance(issue, dict):
            return format_card_ref({**issue, 'number': issue_or_number})
    except RuntimeError:
        pass
    return f"#{issue_or_number}"


def name_label(title, suggested=None, exclude=None):
    cards = gh(['issue', 'list', '--repo', REPO, '--state', 'open', '--limit', '1000',
                '--json', 'number,title,labels']) or []
    used = [card_name(c) for c in cards if c['number'] != exclude]
    if suggested is None:
        try:
            result = claude_json('Return only JSON with a slug for this Battlecode card: 1–2 lowercase English words, '
                                 'hyphenated, at most 16 characters. Title: ' + title,
                                 *TRANSLATE_MODEL, cwd=ROOT, timeout=180, tools=False)
            suggested = result.get('slug')
        except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired):
            pass
    slug = unique_slug(title, used, suggested)
    label = 'name:' + slug
    existing = gh(['label', 'list', '--repo', REPO, '--search', label, '--limit', '1000', '--json', 'name']) or []
    if not any(row['name'] == label for row in existing):
        gh(['label', 'create', label, '--repo', REPO, '--color', 'bfd4f2', '--description', 'Short card name'])
    return label


def pr_card_refs(pr, cards=None):
    numbers = set(map(int, re.findall(r'(?<![\w/])#(\d+)\b', pr.get('title', '') + '\n' + (pr.get('body') or ''))))
    if not numbers:
        return []
    if cards is None:
        cards = gh(['issue', 'list', '--repo', REPO, '--state', 'all', '--limit', '1000',
                    '--json', 'number,title,labels,url']) or []
    return [card_ref(c) for c in cards if c.get('number', c.get('n')) in numbers
            and (is_board_card(c['title']) or 'n' in c)]


def pr_display(pr, cards=None):
    return ', '.join(pr_card_refs(pr, cards)) or pr['title']


def pr_line(pr, cards=None):
    refs = pr_card_refs(pr, cards)
    names = ', '.join(f'[{ref}](https://github.com/{REPO}/issues/{ref.split()[0][1:]})' for ref in refs)
    return (names or clean(pr['title'], 100)) + f" · [PR]({pr['url']})"


def load_state():
    try:
        with open(STATE) as f:
            return member_state(json.load(f))
    except (OSError, ValueError):
        return {}


def save_state(st):
    with _STATE_WRITE_LOCK:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        tmp = STATE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(member_state(st), f, indent=2, ensure_ascii=False)
        os.replace(tmp, STATE)


STEP_WORDS = {'clarify': 'clarifying', 'build': 'building', 'task': 'task build + check',
              'adopt': 'adopting', 'mechanism': 'quick behaviour check', 'look': 'reading behaviour',
              'outcome': 'local A/B', 'verdict': 'judging results', 'ladder': 'reading new ladder games',
              'decide': 'deciding', 'reply': 'reading reply'}


def eta_clock(value):
    stamp = datetime.datetime.fromisoformat(value)
    return ' / '.join(stamp.astimezone(ZoneInfo(zone)).strftime('%H:%M %Z')
                      for zone in ('Asia/Seoul', 'Europe/Stockholm', 'Australia/Sydney'))


def duration_words(minutes):
    hours, mins = divmod(max(1, math.ceil(minutes)), 60)
    return f'{hours}h {mins}m' if hours else f'{mins}m'


def loop_eta(info, now=None):
    if not info.get('eta_at'):
        return ''
    now = now or datetime.datetime.now(datetime.timezone.utc)
    started = info.get('step_started')
    elapsed = max(0, int((now - datetime.datetime.fromisoformat(started)).total_seconds() / 60)) if started else 0
    step = STEP_WORDS.get(info.get('step_kind'), info.get('step', '-'))
    queue = info.get('queue')
    progress = f"waiting on {queue} (~{math.ceil(info.get('wait_minutes', 0))}m wait)" if queue else f'{elapsed}m elapsed'
    if info.get('late'):
        return (f"⏳ late · {step} · {progress} · {late_activity(info)}"
                f" · {late_eta(info, waiting=bool(queue))}")
    return f"{step} · {progress} · ETA {eta_clock(info['eta_at'])}"


def notice_text(value):
    return clean(str(value), 300).replace('@', '@\u200b')


def late_eta(info, waiting=False):
    if not info.get('eta_known', True):
        return "no estimate yet, i'll post again in 15 min"
    stamp = info.get('new_start_at') if waiting else info.get('new_eta_at')
    if not stamp:
        return "no estimate yet, i'll post again in 15 min"
    return f"{'should start' if waiting else 'should be done'} ~{eta_clock(stamp)}"


def late_activity(event):
    clause = str(event.get('reason') or '').strip()
    if 'tool calls' in clause:
        latest = re.findall(r"'([^']+)'", clause.partition('last:')[2])
        clause = latest[-1] if latest else ''
    clause = re.sub(r';?\s*(?:unknown, checking again.*|no estimate yet.*)$', '', clause)
    clause = ' '.join(clause.split()).rstrip('…. ')[:90].rstrip('…. ')
    clause = clause[:1].lower() + clause[1:]
    if not clause:
        clause = {'build': 'still editing and checking the change',
                  'mechanism': 'running games and checking how it plays',
                  'outcome': 'running games and checking how it plays',
                  'ladder': 'still reading our new ladder games'}.get(event.get('step'), 'still working through this step')
    return notice_text(clause)


def late_card(event):
    if event.get('step') == 'ladder' or str(event.get('card', event.get('number'))) == '0':
        return 'the ladder review'
    return notice_text(card_ref(event))


def loop_event_line(event):
    step = STEP_WORDS.get(event.get('step'), event.get('step', 'step'))
    card = late_card(event) if event.get('step') == 'ladder' else card_ref({'card': event.get('card', '?'), 'name': event.get('name', ''), 'title': event.get('title', '')})
    if event.get('event') == 'late':
        if event.get('post') is False or (event.get('post') is not True and event.get('covered_by')):
            return None
        card = late_card(event)
        elapsed = duration_words(event.get('elapsed_minutes', 0))
        waiting = event.get('waiting') or bool(event.get('queue'))
        slot = 'game slot' if 'batch' in str(event.get('queue', '')) else 'AI slot'
        activity = late_activity(event)
        if waiting:
            message = f'⏳ {card}: waiting {elapsed} for the {slot}. {activity}. '
        else:
            if card == 'the ladder review':
                card += ' (AI reading our new ladder games)'
                step = ''
            else:
                card += ':'
                step += ' '
            activity_text = (f"it's still digging: {activity}" if event.get('step') == 'ladder' else
                             activity if event.get('step') in ('mechanism', 'outcome') else
                             f"it's still working: {activity}")
            message = (f"⏳ {card} {step}is running late: {elapsed} so far, "
                       f"planned {duration_words(event.get('planned_minutes', event.get('eta_minutes', 0)))}. "
                       f"{activity_text}. ")
        message += late_eta(event, waiting=waiting) + '.'
        waiters = dict.fromkeys(late_card(c) for c in event.get('waiters', []))
        if waiters:
            message += ' waiting behind it: ' + ', '.join(waiters)
        return message
    if event.get('event') == 'failed':
        note = clean(str(event.get('note') or 'unknown error'), 180)
        return f'⚠️ {card}: {step} failed: {note}; the loop retries or needs a look'
    if event.get('event') != 'start' or event.get('eta_minutes', 0) < 10:
        return None
    minutes = event['eta_minutes']
    end = datetime.datetime.fromisoformat(event['time']) + datetime.timedelta(minutes=minutes)
    return f"⏱ {card}: {step} started, about {duration_words(minutes)} (done ~{eta_clock(end.isoformat())})"


def tail_loop_events(st, path=None):
    path = path or os.path.join(LOOK_DIR, 'events.jsonl')
    try:
        stream = open(path, 'rb')
    except FileNotFoundError:
        st.setdefault('loop_events_offset', 0)
        return []
    with stream:
        size = os.fstat(stream.fileno()).st_size
        if 'loop_events_offset' not in st:
            st['loop_events_offset'] = size
            return []
        offset = st['loop_events_offset']
        stream.seek(offset if offset <= size else 0)
        rows = []
        while line := stream.readline():
            if not line.endswith(b'\n'):
                break
            try:
                event = json.loads(line)
                message = event
            except (ValueError, TypeError, AttributeError, KeyError, OverflowError):
                message = None
            rows.append((stream.tell(), message))
        try:
            with open(os.path.join(LOOK_DIR, 'status.json')) as status_file:
                cards = json.load(status_file).get('cards', {})
        except (OSError, ValueError):
            cards = {}
        late_jobs = {e.get('job') for _, e in rows if isinstance(e, dict)
                     and e.get('event') == 'late' and e.get('post') is not False and not e.get('waiting') and e.get('job')}
        late_jobs.update(c['job'] for c in cards.values() if c.get('late') and not c.get('queue') and c.get('job'))
        for _, event in rows:
            if not isinstance(event, dict) or event.get('event') != 'late':
                continue
            holders = event.get('holders', [])
            if any(h.get('job') in late_jobs for h in holders):
                event['covered_by'] = [h['job'] for h in holders if h.get('job') in late_jobs]
            if not event.get('waiting'):
                event['waiters'] = list(event.get('waiters', []))
                for number, info in cards.items():
                    if info.get('queue') and any(h.get('job') == event.get('job') for h in info.get('holders', [])):
                        event['waiters'].append({'card': number, 'name': info.get('name', ''), 'title': info.get('title', '')})
                for _, waiter in rows:
                    if isinstance(waiter, dict) and waiter.get('waiting') and any(
                            h.get('job') == event.get('job') for h in waiter.get('holders', [])):
                        event['waiters'].append(waiter)
        latest = {}
        for offset, event in rows:
            if isinstance(event, dict) and event.get('event') == 'late' and event.get('post') is not False:
                cause = (event.get('job') or (event.get('card'), event.get('step')),
                         bool(event.get('waiting')), event.get('started'))
                latest[cause] = offset
        rendered = []
        for offset, event in rows:
            try:
                message = loop_event_line(event) if isinstance(event, dict) else None
                if isinstance(event, dict) and event.get('event') == 'late':
                    cause = (event.get('job') or (event.get('card'), event.get('step')),
                             bool(event.get('waiting')), event.get('started'))
                    if event.get('post') is not False and latest[cause] != offset:
                        message = None
            except (ValueError, TypeError, AttributeError, KeyError, OverflowError):
                message = None
            rendered.append((offset, message))
        return rendered


def summarize(body, limit=380):
    lines = []
    for raw in (body or "").splitlines():
        s = raw.strip()
        if not s or s.startswith(("#", "<")) or "Generated with" in s:
            continue
        s = re.sub(r"\*\*|`", "", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        lines.append(s)
        if len(lines) >= 3 or sum(len(x) for x in lines) > limit:
            break
    text = "\n".join(lines)
    return text if len(text) <= limit else text[:limit - 1] + "…"


def non_english(*texts):
    return any(re.search(r"[ᄀ-ᇿ㄰-㆏가-힯぀-ヿ一-鿿]", t or "") for t in texts)


def first_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    return json.loads(m.group(0)) if m else {}


def claude_json(prompt, model, effort, cwd, timeout, tools=True):
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort, "--output-format", "json", "--no-session-persistence"]
    if tools:
        cmd += ["--permission-mode", "bypassPermissions", "--settings", os.path.join(LOOP_DIR, "loop", "settings.json"),
                "--disallowedTools", "Write", "Edit", "NotebookEdit", "Bash(git push:*)", "Bash(gh:*)"]
    else:
        cmd += ["--tools", ""]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, stdin=subprocess.DEVNULL)
    out = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
    if out.get("is_error") or not out.get("result"):
        raise RuntimeError((out.get("result") or r.stderr or "no output")[:300])
    return first_json(out["result"])


def translate(fields):
    payload = json.dumps(fields, ensure_ascii=False)
    prompt = ("Translate and tidy this idea card for a team GitHub board about a Battlecode bot (dragons, queen, pearls, "
              "portals, kelp, sonar, splitting, feeding). The input may be Korean, Chinese or English. Keep the author's "
              "meaning exactly: do not add facts, numbers or claims, and keep code identifiers unchanged. Write clear, plain "
              "English. Empty fields stay empty. Return only a JSON object with the same keys plus \"language\" (the input "
              f"language).\n\nInput:\n{payload}")
    out = claude_json(prompt, *TRANSLATE_MODEL, cwd=ROOT, timeout=180, tools=False)
    return {k: (out.get(k) or "").strip() for k in fields}, out.get("language", "")


def card_body(author, f, original=None, extra=None, via="meowbot"):
    author = author_name(author_label(author))
    parts = [f"**Idea by:** {author} (via {via})."]
    for key, head in CARD:
        parts.append(f"## {head}\n{f.get(key) or '-'}")
    for key, head in EXTRA:
        if extra and extra.get(key):
            parts.append(f"## {head}\n{extra[key]}")
    if original:
        lines = "\n\n".join(f"**{k}:** {v}" for k, v in original.items() if v)
        parts.append(f"<details><summary>Original text</summary>\n\n{lines}\n\n</details>")
    return "\n\n".join(parts) + "\n"


def parse_card(body):
    out, cur, buf = {}, None, []
    for line in (body or "").splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def replace_sections(body, new):
    heads = dict(CARD)
    lines, out, skip = (body or "").splitlines(), [], False
    for line in lines:
        m = re.match(r"^##\s+(.*)", line)
        if m:
            name = m.group(1).strip()
            key = next((k for k, h in CARD if h == name), None)
            if key is not None:
                out += [line, new.get(key) or "-", ""]
                skip = True
                continue
            skip = False
        if not skip:
            out.append(line)
    for key, head in CARD:
        if f"## {head}" not in body:
            out += [f"## {head}", new.get(key) or "-", ""]
    return "\n".join(out).rstrip() + "\n"


def wf_for(author):
    return 1 if author == "Zhe" else 2


def author_label(author):
    """Resolve a member/AI name or label; loops tag AI cards with gh issue edit N --add-label by:ai."""
    value = member_name(author or "").strip().casefold()
    for name, label in AUTHOR_LABELS.items():
        if value in (name.casefold(), label.casefold(), label[3:]):
            return label
    return None


def body_author(body):
    match = re.search(r"^\s*(?:\*\*)?Idea by:(?:\*\*)?\s*(.+?)\s*$", body or "", re.I | re.M)
    if match:
        return author_label(re.split(r"\s*\(via\b", match[1], flags=re.I)[0].rstrip(" ."))
    return None


def author_name(label):
    return next((name for name, value in AUTHOR_LABELS.items() if value == label), "Unknown human")


def clock():
    return datetime.datetime.now(datetime.timezone.utc)


def idea_mention(issue):
    """The card authors, tagged only in their waking hours (the hourly check tags them once they are up)."""
    labels = {l["name"] for l in issue.get("labels", [])}
    if "by:ai" in labels:
        return ""
    out = []
    for uid, name in MEMBERS.items():
        label = AUTHOR_LABELS[name]
        if label in labels:
            local = (clock() + datetime.timedelta(hours=nudge.PEOPLE[label][2])).hour
            out.append(f"<@{uid}>" if nudge.awake(name, local) else f"{name} (asleep there, no ping)")
    return " ".join(out)


def is_board_card(title):
    return title.lower().startswith(("[idea]", "[task]"))


def board_card_title(title):
    return re.sub(r"^\[(?:Idea|Task)\]\s*", "", title, flags=re.I)


def reply_hint(number):
    return f"reply to this message in your own words, or use /answer card:{number} text:…"


def state_message(number, extra):
    issue, status = extra["issue"], extra["status"]
    ref = card_ref({**issue, "number": number})
    if status == "candidate":
        return f"{ref} is a candidate, PR + OK buttons coming"
    mention = idea_mention(issue)
    prefix = mention + " " if mention else ""
    if status == "needs-info":
        return f"{prefix}the loop has a few questions before building {ref}: {issue['html_url']}\n{reply_hint(number)}"
    if status == "needs-look":
        if "by:ai" in label_names(issue):
            return (f"{ref} is built. this is an AI card, so nobody needs to answer; the loop moves on by itself. "
                    f"replays below if you're curious: {issue['html_url']}")
        return f"{prefix}{ref} is built, can you check 2–3 replays? {issue['html_url']}\n{reply_hint(number)}"
    icon = {"tested": "✅", "rejected": "❌", "inconclusive": "➖", "kept": "🚀"}[status]
    head = {"tested": "results are in", "rejected": "dropped", "inconclusive": "closed, not settled", "kept": "merged to main"}[status]
    line = outcome_line(number)
    return (f"{prefix if status == 'tested' else ''}{icon} **{ref}**: {head}"
            + (f"\n{line}" if line else "")
            + (f"\nship it, drop it, or say what to revise. {reply_hint(number)}" if status == "tested" else "")
            + f"\n{issue['html_url']}")


def outcome_line(number):
    """Latest "Did it work" line from the card's result comments, shortened for Discord."""
    try:
        data = gh(["issue", "view", str(number), "--repo", REPO, "--json", "comments"]) or {}
    except RuntimeError:
        return ""
    for c in reversed(data.get("comments") or []):
        m = re.search(r"^\W*Did it work\W*:\W*(.+)$", c.get("body") or "", re.I | re.M)
        if m:
            text = " ".join(m[1].split())
            return text if len(text) <= 280 else text[:279] + "…"
    return ""


def log(*a):
    print(datetime.datetime.now().isoformat(timespec="seconds"), *a, flush=True)


async def send_state_message(channel, number, extra, discord):
    message = state_message(number, extra)
    if extra["status"] != "needs-look":
        await channel.send(message)
        return
    directory = os.path.join(LOOK_DIR, f"card-{number}")
    try:
        with open(os.path.join(directory, "look.json")) as source:
            look = json.load(source)
        if not isinstance(look, dict):
            raise ValueError("look.json must be an object")
    except (OSError, ValueError):
        await channel.send(message)
        return
    note = " ".join(str(look.get("note") or "").split())
    if note:
        message += "\n" + (note if len(note) <= 300 else note[:299] + "…")
    message += "\nWatch: download the .replay, open https://game.battlecode.au/visualiser and choose the file."
    paths = look.get("replays", [])
    with ExitStack() as stack:
        files = []
        for path in paths if isinstance(paths, list) else []:
            if len(files) == 3:
                break
            if not isinstance(path, str) or not path:
                continue
            path = os.path.expanduser(path)
            if not os.path.isabs(path):
                path = os.path.join(directory, path)
            try:
                with open(path, "rb") as source:
                    raw = strip_padding(source.read())
            except OSError:
                continue
            name = os.path.basename(path)
            if len(raw) > LOOK_INLINE_BYTES:  # Discord rejects big files; replays shrink about 4x
                raw, name = gzip.compress(raw, 9), name + ".gz"
            if len(raw) > LOOK_INLINE_BYTES:
                continue
            files.append((raw, name))
        if any(name.endswith(".gz") for _, name in files):
            message += "\n(.gz files: unzip first, then open the .replay)"
        # The text goes first and each replay in its own message, so one big file cannot sink the ping.
        await channel.send(message)
        for raw, name in files:
            try:
                await channel.send(file=discord.File(io.BytesIO(raw), filename=name))
            except Exception as exc:
                log("look replay not sent:", name, type(exc).__name__)


def candidate_authors(c):
    labels = set()
    for number in dict.fromkeys(c.get("issues") or []):
        issue = gh(["issue", "view", str(number), "--repo", REPO, "--json", "labels,body"])
        by = [item["name"] for item in issue.get("labels", []) if item["name"].startswith("by:")]
        labels.update((author_label(label) or "by:unknown") for label in by)
        if not by:
            labels.add(body_author(issue.get("body")) or "by:unknown")
    return sorted(labels or {"by:unknown"})


def approval_ready(rec):
    labels = set(rec.get("author_labels") or ["by:unknown"])
    votes = set(rec.get("oks", [])) & {str(uid) for uid in MEMBERS}
    if labels == {"by:ai"}:
        return bool(votes)
    authors = {str(uid) for uid, name in MEMBERS.items() if AUTHOR_LABELS[name] in labels}
    if not authors:
        return len(votes) >= 2
    return bool(votes & authors) and bool(votes - authors)


def record_ok(rec, user_id):
    """Record a unique member vote; a repeated OK can reopen a cancelled confirmation."""
    if user_id not in MEMBERS:
        return False
    votes = rec.setdefault("oks", [])
    value = str(user_id)
    if value in votes:
        return False
    votes.append(value)
    return True


def candidate_patch_id(rec):
    base = gh(["api", f"repos/{REPO}/pulls/{rec['pr']}"])["base"]["sha"]
    r = subprocess.run(["gh", "api", f"repos/{REPO}/compare/{base}...{rec['head_sha']}", "-H", "Accept: application/vnd.github.diff"], capture_output=True, text=True, check=True)
    chunks = re.split(r"(?=^diff --git )", r.stdout, flags=re.M)
    diff = "".join(c for c in chunks if c.startswith("diff --git ") and not c.startswith("diff --git a/candidates/"))
    r = subprocess.run(["git", "patch-id", "--stable"], input=diff, capture_output=True, text=True, check=True)
    if not r.stdout.strip():
        raise RuntimeError("Cannot identify candidate changes; no approval carry-over is safe.")
    return r.stdout.split()[0]


def prepare_candidate(rec, seen):
    rec["author_labels"] = candidate_authors(rec["manifest"])
    rec["patch_id"] = candidate_patch_id(rec)
    rec["oks"] = []
    previous = [old for old in seen.values() if old.get("pr") == rec["pr"] and old.get("head_sha") != rec["head_sha"] and old.get("path") == rec.get("path")]
    if previous:
        old = previous[-1]
        if old.get("patch_id") == rec["patch_id"] and old.get("author_labels") == rec["author_labels"]:
            rec["oks"] = list(old.get("oks", []))
            rec["result"] = "Same patch-id after re-check; previous OKs carried over."
        else:
            rec["result"] = "PR changes changed. Previous OKs reset; this patch needs fresh OKs."


def candidate_current(rec):
    main = gh(["api", f"repos/{REPO}/commits/main"])["sha"]
    comparison = gh(["api", f"repos/{REPO}/compare/{main}...{rec['head_sha']}"])
    if comparison["behind_by"] == 0:
        return True
    # Reverse comparison lists changes on main since the common ancestor.
    incoming = gh(["api", f"repos/{REPO}/compare/{rec['head_sha']}...{main}"])
    return not any(f["filename"].startswith("mybot2/") or f.get("previous_filename", "").startswith("mybot2/")
                   for f in incoming["files"])


def request_rebase(rec):
    message = "main moved since this candidate was built; the loop is re-checking it on the new main"
    gh(["pr", "edit", str(rec["pr"]), "--repo", REPO, "--add-label", "needs:rebase"])
    gh_comment("pr", rec["pr"], message)
    return message


def gh_comment(kind, number, message):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", encoding="utf-8") as f:
        f.write(message); f.flush()
        subprocess.run(["gh", kind, "comment", str(number), "--repo", REPO, "--body-file", f.name], check=True, capture_output=True, text=True)


def keep_cards(issues, commit):
    for number in dict.fromkeys(issues):
        issue = gh(["issue", "view", str(number), "--repo", REPO, "--json", "labels"])
        args = ["issue", "edit", str(number), "--repo", REPO]
        for label in issue["labels"]:
            if label["name"].startswith("status:"):
                args += ["--remove-label", label["name"]]
        gh(args + ["--add-label", "status:kept"])
        gh_comment("issue", number, f"merged to main as {commit}; ships with the next /submit")


def idea_labels(area, wf, author=None):
    return ["status:untested", f"wf:{wf}"] + ([author_label(author)] if author_label(author) else []) + ([f"area:{area}"] if area in AREAS[:-1] else [])


def create_issue(title, body, area, wf, name=None):
    author = body_author(body)
    if not author:
        raise ValueError("Idea by must name a team member or AI.")
    labels = idea_labels(area, wf, author) + [name_label(title, name)]
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(body)
    args = ["issue", "create", "--repo", REPO, "--title", f"[Idea] {title}", "--body-file", fh.name]
    for l in labels:
        args += ["--label", l]
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    os.unlink(fh.name)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    url = r.stdout.strip().splitlines()[-1]
    return int(url.rstrip("/").split("/")[-1]), url


def board_state():
    issues = gh(["issue", "list", "--repo", REPO, "--state", "open", "--limit", "200", "--json", "number,title,labels,url,createdAt,updatedAt"]) or []
    ideas = []
    for i in issues:
        if not is_board_card(i["title"]):
            continue
        labels = [l["name"] for l in i["labels"]]
        ideas.append({
            "n": i["number"], "url": i["url"], "created": i["createdAt"],
            "updated": i.get("updatedAt", i["createdAt"]),
            "title": board_card_title(i["title"]), "name": card_name(i), "labels": i["labels"],
            "status": next((l.split(":", 1)[1] for l in labels if l.startswith("status:")), "untested"),
            "area": next((l.split(":", 1)[1] for l in labels if l.startswith("area:")), "-"),
            "wf": next((l.split(":", 1)[1] for l in labels if l.startswith("wf:")), "-"),
            "ready": "loop:ready" in labels, "running": "loop:running" in labels,
        })
    return sorted(ideas, key=lambda x: x["n"])


def open_ideas():
    return [(i["n"], i["area"], i["status"], i["title"], i["url"]) for i in board_state() if i["status"] in ("untested", "in-progress")]


async def reply_tasks(it, st, who="all", share=False):
    import discord
    if it.user.id not in MEMBERS:
        await it.response.send_message("Only team members can use meowbot commands.", ephemeral=True)
        return
    await it.response.defer(ephemeral=not share, thinking=True)
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        data = await asyncio.to_thread(task_lists.collect, now, state=st)
        message = task_lists.render(data, who=who, now=now, caller=MEMBERS[it.user.id])
    except Exception:
        message = "Could not read the task board. Try /task again later."
    await it.followup.send(message, ephemeral=not share, allowed_mentions=discord.AllowedMentions.none())


def loop_status():
    issues = gh(["issue", "list", "--repo", REPO, "--state", "open", "--search", "Loop status in:title", "--json", "number,title,body,url"]) or []
    loops, url = {}, None
    for i in issues:
        if i["title"].strip() == "Loop status":
            m = re.search(r"<!-- loops-json\s*(\{.*?\})\s*-->", i["body"] or "", re.S)
            loops, url = (json.loads(m.group(1)).get("loops", {}) if m else {}), i["url"]
            break
    try:
        with open(os.path.join(LOOK_DIR, 'status.json')) as stream:
            snapshot = json.load(stream)
        for number, info in snapshot.get('cards', {}).items():
            if not info.get('eta_at') or not (info.get('queue') or 'running' in info.get('step', '') or info.get('step', '').startswith('started ')):
                continue
            key = next((k for k, row in loops.items() if str(row.get('issue')) == number), f'card {card_ref(int(number))}')
            loops[key] = {**loops.get(key, {}), **info, 'issue': int(number), 'state': 'running'}
    except (OSError, ValueError, TypeError):
        pass
    return loops, url


def recent_results(limit=5, days=4):
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    comments = gh(["api", f"repos/{REPO}/issues/comments?since={since}&per_page=100"]) or []
    out = []
    for c in comments:
        b = (c.get("body") or "").lstrip()
        if b.startswith(("[test]", "[check]")):
            lines = [x.strip() for x in b.splitlines() if x.strip()]
            out.append({"n": int(c["issue_url"].rstrip("/").split("/")[-1]), "url": c["html_url"], "at": c["created_at"],
                        "head": lines[0][:140], "first": (lines[1] if len(lines) > 1 else "")[:200]})
    return sorted(out, key=lambda x: x["at"], reverse=True)[:limit]


def ladder_summary():
    def node(*args):
        r = subprocess.run(["node", os.path.join(ROOT, "tools", "online.js"), *args, "--json"], capture_output=True, text=True, cwd=ROOT)
        return json.loads(r.stdout) if r.stdout.strip().startswith(("{", "[")) else None
    team, subs = node("team"), node("submissions")
    active = next((s for s in (subs or []) if s.get("status") == "active"), None)
    if not team:
        return "ladder info unavailable"
    rec = team.get("record", {})
    sub = f"{active['name']} (uploaded {active['uploadedAt'][5:16].replace('T', ' ')} UTC)" if active else "none"
    return f"Active bot: {sub} · rating {team['team'].get('elo')} · rank #{team.get('rank')} · record {rec.get('wins')}-{rec.get('losses')}"


KST = datetime.timezone(datetime.timedelta(hours=9))
WF_COLOR = {"1": 0xD97706, "2": 0x2C64C4, "3": 0x1F7A50}
WF_ICON = {"1": "①", "2": "②", "3": "③"}
STATE_ICON = {"running": "🟢", "idle": "⏸️", "stopped": "⏹️"}


def clean(text, limit):
    t = re.sub(r"\*\*|`|__", "", text or "")
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = " ".join(t.split())
    return t if len(t) <= limit else t[:limit - 1] + "…"


def stale(l):
    try:
        upd = datetime.datetime.strptime(f"{datetime.date.today().year}-{l.get('updated')}", "%Y-%m-%d %H:%M")
        return l.get("state") == "running" and (datetime.datetime.now() - upd).total_seconds() > 1800
    except (TypeError, ValueError):
        return False


def loop_card(name, l, titles):
    wf, state, issue = str(l.get("wf", "")), l.get("state", "-"), l.get("issue")
    on = card_ref(titles.get(issue, issue)) if issue else "nothing right now"
    return {
        "title": f"{STATE_ICON.get(state, '•')} {name}",
        "color": WF_COLOR.get(wf, 0x6E7781),
        "description": f"**{WORKFLOW.get(int(wf) if wf.isdigit() else 0, 'workflow ' + wf)}** · {state}"
                       + (" · ⚠️ no update for 30+ min" if stale(l) else ""),
        "fields": [
            {"name": "Working on", "value": on, "inline": False},
            {"name": "Step", "value": loop_eta(l) or clean(l.get("step") or "-", 200), "inline": False},
            {"name": "Since", "value": l.get("since") or "-", "inline": True},
            {"name": "Updated", "value": l.get("updated") or "-", "inline": True},
            {"name": "Machine", "value": l.get("machine") or "-", "inline": True},
        ],
    }


def ideas_card(title, ideas, color, empty):
    fields = [{"name": f"{clean(card_ref(i), 150)} {WF_ICON.get(i['wf'], '·')} · {i['area']} · status:{i['status']}",
               "value": f"[{clean(i['title'], 150)}]({i['url']})", "inline": False} for i in ideas[:20]]
    card = {"title": f"{title} ({len(ideas)})", "color": color}
    if fields:
        card["fields"] = fields
    else:
        card["description"] = empty
    return card


def idea_cards(title, ideas, color, empty):
    return [ideas_card(title, ideas[start:start + 12], color, empty)
            for start in range(0, max(1, len(ideas)), 12)]


def card_batches(cards):
    batch, size = [], 0
    for card in cards:
        card = clamp_embed(card)
        length = sum(len(card.get(k, "")) for k in ("title", "description")) \
               + len(card.get("footer", {}).get("text", "")) \
               + sum(len(f["name"]) + len(f["value"]) for f in card.get("fields", []))
        if batch and (len(batch) == 10 or size + length > 6000):
            yield batch
            batch, size = [], 0
        batch.append(card)
        size += length
    if batch:
        yield batch


def results_card(results, titles):
    fields = []
    for r in results:
        kind = "test" if r["head"].startswith("[test]") else "check"
        stamp = datetime.datetime.fromisoformat(r["at"].replace("Z", "+00:00"))
        when = stamp.astimezone(KST).strftime("%m-%d ") + eta_clock(stamp.isoformat())
        text = clean(re.sub(r"^\[(test|check)\]\s*", "", r["head"]), 170)
        fields.append({"name": f"{card_ref(titles.get(r['n'], r['n']))} · {kind} · {when}",
                       "value": f"{text}\n[open]({r['url']})", "inline": False})
    card = {"title": "🧪 Latest results", "color": 0x0B6E78}
    if fields:
        card["fields"] = fields
    else:
        card["description"] = "None in the last 4 days."
    return card


def analysis_prompt(author, area, fields):
    card = json.dumps(fields, ensure_ascii=False, indent=1)
    return f"""You analyse one hypothesis for team meow's Battlecode bot and turn it into an idea card. Read only: do not modify any files.

- Repo at current main: {RELEASE_DIR}. Bot under development: mybot2/main.cpp. Live bot v61 = mybot2 + toggles in work/v60toggles.txt + POCKET_CAP=48, QUEEN_HOME_CLOSED=true.
- Experiment history (what was tried, kept, rejected): {RELEASE_DIR}/work/plan.md
- Ladder data, 228 meow games: {LOOP_DIR}/work/nr_meow.txt (battleId R|U opponent elo ourSide gameId:Map:W|L:hasReplay,...) and replays {LOOP_DIR}/work/nr/<gameId>.replay. Parser {LOOP_DIR}/replay.py; analysis scripts in {LOOP_DIR}/work/ (paths fixed there).
- Overnight analysis summary: {LOOP_DIR}/loop/ANALYSIS.md
- Area owners: queen survival #2 (QWQ), late-game feeding #3 (Zhe), terrain #4, economy #7.
- The qualifier uses unseen custom maps: no map names, ids or per-map constants; phrase everything as general situations.

Hypothesis from {author} (area: {area}). It may be written in Korean or Chinese; translate it faithfully and keep the author's intent:
{card}

Do this, spending at most about 12 minutes:
1. Find the code behind the current behaviour (functions, constants, line numbers).
2. Check plan.md for earlier attempts at this or similar ideas, and their results.
3. Find evidence in the ladder data or ANALYSIS.md, with numbers and N.
4. Note overlap with the area owners.
5. Check it would work on unseen maps.
6. Sketch an off-by-default toggle (area prefix) and how to test it: a scene test, the held-out map sets, and the mechanism signal to look for.

Return only a JSON object with these English string fields:
title, claim, evidence, expected_signal, falsifier, code_pointers, prior_attempts, ladder_evidence, overlap, toggle_sketch, test_plan, risks, summary (two sentences for Discord).
Keep the author's idea as the claim; put your own findings in the other fields."""


def pr_embed(n, action):
    p = gh(["pr", "view", str(n), "--repo", REPO, "--json",
            "number,title,body,author,url,additions,deletions,changedFiles,headRefName,baseRefName,isDraft,mergedBy"])
    head = {"opened": "New PR", "reopened": "PR reopened", "ready-for-review": "PR ready for review", "merged": "PR merged", "closed": "PR closed"}[action]
    who = p["author"]["login"] if action in ("opened", "reopened") else ((p.get("mergedBy") or {}).get("login") or p["author"]["login"])
    refs = pr_card_refs(p)
    card_links = ", ".join(f"[{ref}](https://github.com/{REPO}/issues/{ref.split()[0][1:]})" for ref in refs)
    return {
        "title": f"{head}: {', '.join(refs) or p['title']}" + (" (draft)" if p.get("isDraft") else ""),
        "url": p["url"],
        "description": (card_links + "\n" if card_links else "") + summarize(p.get("body")),
        "color": COLOR[action],
        "fields": [
            {"name": "By", "value": who, "inline": True},
            {"name": "Branch", "value": f"{p['headRefName']} → {p['baseRefName']}", "inline": True},
            {"name": "Changes", "value": f"{p['changedFiles']} files (+{p['additions']} −{p['deletions']})", "inline": True},
        ],
    }


def idea_embed(number, title, url, body, labels):
    return {
        "title": f"New idea {card_ref({'number': number, 'title': title, 'labels': labels})}",
        "url": url,
        "description": board_card_title(title) + "\n" + summarize(body),
        "color": COLOR["idea"],
        "fields": [{"name": "Labels", "value": ", ".join(label_names({"labels": labels})) or "-", "inline": True}],
    }


def candidate_embed(c, pr=None):
    res = c.get("results") or {}
    changes = "\n".join(f"• {x}" for x in (c.get("changes") or [])) or "-"
    fields = [{"name": "Came from", "value": WORKFLOW.get(c.get("workflow"), str(c.get("workflow"))), "inline": True}]
    for k, label in (("held", "Unseen-style maps"), ("main", "Official maps"), ("mechanism", "Mechanism check"), ("cpu", "CPU peak")):
        if res.get(k):
            fields.append({"name": label, "value": str(res[k]), "inline": k != "mechanism"})
    refs = [card_ref(i) for i in (c.get("issues") or [])]
    links = [f"[{ref}](https://github.com/{REPO}/issues/{i})" for ref, i in zip(refs, c.get("issues") or [])]
    links += ([f"[PR]({pr['url']}) · `{pr['head_sha'][:12]}`"] if pr
              else ([f"[PR](https://github.com/{REPO}/pull/{c['pr']})"] if c.get("pr") else []))
    if links:
        fields.append({"name": "Links", "value": ", ".join(links), "inline": True})
    labels = (pr or {}).get("author_labels") or ["by:unknown"]
    names = ", ".join(author_name(label) for label in labels)
    needs = "1 member" if set(labels) == {"by:ai"} else "author + 1 other"
    if set(labels) - {"by:ai"} == {"by:unknown"}:
        needs = "2 different members (unknown author)"
    oks = ", ".join(MEMBERS[int(uid)] for uid in (pr or {}).get("oks", []) if str(uid) in {str(i) for i in MEMBERS}) or "None"
    fields.append({"name": "OKs", "value": f"Idea by: {names} · needs: {needs}\nCurrent OKs: {oks}", "inline": False})
    if (pr or {}).get("result"):
        fields.append({"name": "Result", "value": pr["result"], "inline": False})
    pointer = (f"[PR]({pr['url']})" if pr else
               f"[PR](https://github.com/{REPO}/pull/{c['pr']})" if c.get("pr") else
               f"[card](https://github.com/{REPO}/issues/{c['issues'][0]})" if c.get("issues") else "")
    return clamp_embed({"title": ", ".join(refs) or c["version"], "description": "What changed:\n" + changes,
            "color": COLOR["candidate"], "fields": fields,
            "footer": {"text": "OK: human author + 1 other; AI-only: 1 member. Confirm merges to main; ships with the next /submit."}}, field_pointer=pointer)


def new_events(st):
    pulls = [p for p in (gh(pr_list_args(REPO)) or []) if isinstance(p, dict) and "number" in p and "headRefOid" in p]
    events = gh(["api", f"repos/{REPO}/events?per_page=100"]) or []
    out = [("pr", p["number"], action) for p, action in pr_activity(st, pulls)]
    last = st.get("last_event_id")
    top = max((int(e["id"]) for e in events), default=last or 0)
    ids = [str(e["id"]) for e in events]
    if last is None:
        st["last_event_id"] = top
        st["seen_event_ids"] = ids
        return out
    # event ids are not ordered across event types, so track the ones already handled
    seen = st.get("seen_event_ids")
    if seen is None:
        seen = [i for i in ids if int(i) <= last]
    known = set(seen)
    fresh = [e for e in events if str(e["id"]) not in known]
    st["seen_event_ids"] = (seen + [str(e["id"]) for e in reversed(fresh)])[-1000:]
    st["last_event_id"] = max(top, last)
    mine = set(st.get("self_ideas", []))
    for e in reversed(fresh):
        p = e.get("payload", {})
        if e["type"] == "IssuesEvent" and p.get("action") == "opened" and p["issue"]["title"].lower().startswith("[idea]") \
                and p["issue"]["number"] not in mine:
            out.append(("idea", p["issue"]["number"], p["issue"]))
        elif e["type"] == "IssuesEvent" and p.get("action") in ("labeled", "unlabeled") \
                and is_board_card(p["issue"]["title"]):
            # payload.label is unreliable (it can name another label on the card), so read the card's
            # status from the labels the event carries.
            number = str(p["issue"]["number"])
            label = next((l["name"] for l in p["issue"].get("labels", []) if l["name"].startswith("status:")), None)
            states = st.setdefault("idea_states", {})
            if label is None:
                states.pop(number, None)
                continue
            if states.get(number) == label:
                continue
            states[number] = label
            status = label.split(":", 1)[1]
            if status in ("needs-info", "needs-look", "tested", "rejected", "inconclusive", "kept", "candidate"):
                kind = "state" if status in ("needs-info", "needs-look", "candidate") else "verdict"
                out.append((kind, int(number), {"issue": p["issue"], "status": status}))
    return out


def candidate_pr(n):
    return gh(["pr", "view", str(n), "--repo", REPO, "--json",
               "number,url,state,baseRefName,headRefOid,mergeable,isDraft,mergeCommit"])


def pr_candidates(p, seen=()):
    if p["state"] != "OPEN":
        return []
    pages = gh(["api", f"repos/{REPO}/pulls/{p['number']}/files?per_page=100", "--paginate", "--slurp"]) or []
    out = []
    for f in (f for page in pages for f in page):
        path = f["filename"]
        if f.get("status") == "removed" or not re.fullmatch(r"candidates/[^/]+\.json", path):
            continue
        name = f"pr:{p['number']}:{p['headRefOid']}:{hashlib.sha256(path.encode()).hexdigest()[:16]}"
        if name in seen:
            continue
        blob = gh(["api", f"repos/{REPO}/contents/{quote(path, safe='/')}?ref={p['headRefOid']}"])
        try:
            c = json.loads(base64.b64decode(blob["content"]))
        except (ValueError, KeyError):
            continue
        if not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip() for k in ("version", "bot_dir")):
            continue
        out.append((name, {"status": "pending", "manifest": c, "pr": p["number"], "url": p["url"],
                           "head_sha": p["headRefOid"], "path": path}))
    return out


def new_candidates(st):
    seen = set(st.get("candidates", {}))
    pages = gh(["api", f"repos/{REPO}/pulls?state=open&per_page=100", "--paginate", "--slurp"]) or []
    out = []
    for p in (p for page in pages for p in page):
        out.extend(pr_candidates({"number": p["number"], "state": "OPEN",
                    "url": p["html_url"], "headRefOid": p["head"]["sha"]}, seen))
    return out


def merge_candidate(rec, force=False):
    r = subprocess.run(["gh", "pr", "merge", str(rec["pr"]), "--repo", REPO, "--merge",
                        "--match-head-commit", rec["head_sha"]] + (["--admin"] if force else []), capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("Merge command failed; check the PR before retrying.")
    p = candidate_pr(rec["pr"])
    commit = (p.get("mergeCommit") or {}).get("oid")
    if p["state"] != "MERGED" or p["baseRefName"] != "main" or p["headRefOid"] != rec["head_sha"] or not commit:
        raise RuntimeError("Merge is not confirmed on main (it may be queued). No upload was attempted.")
    return commit


def sync_release(ref="origin/main"):
    subprocess.run(["git", "-C", RELEASE_DIR, "fetch", "-q", "origin"], check=True)
    subprocess.run(["git", "-C", RELEASE_DIR, "checkout", "-q", "--detach", ref], check=True)


def upload(c, force=False):
    if not UPLOAD_ENABLED and not force:
        return {"ok": False, "result": "Uploads are disabled by UPLOAD_ENABLED."}
    bot = os.path.join(RELEASE_DIR, c["bot_dir"])
    desc = "; ".join(c.get("changes") or [])[:200]
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "submit.js"), "upload", bot, "--name", c["version"], "--desc", desc, "--confirm", "--allow-pending"] + (["--force"] if force else []),
                       capture_output=True, text=True, cwd=ROOT)
    output = re.sub(r"bc_[A-Za-z0-9_-]+", "[REDACTED]", r.stdout + r.stderr)
    tail = "\n".join(output.strip().splitlines()[-4:])
    match = re.search(r"^active: (\d+) " + re.escape(c["version"]) + r";", output, re.M)
    return {"ok": r.returncode == 0 and bool(match), "id": int(match[1]) if match else None,
            "result": ("Uploaded. " if r.returncode == 0 and match else "Upload failed. ") + f"```{tail[:900]}```"}


def submission_list():
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "online.js"), "submissions", "--all", "--json"],
                       capture_output=True, text=True, cwd=ROOT, check=True)
    return json.loads(r.stdout)


def submit_frozen(now=None):
    return (now or datetime.datetime.now(KST)) >= datetime.datetime(2026, 10, 8, 20, tzinfo=KST)


def submit_requester(rec):
    return str(rec.get("requester_id") or next(iter(rec.get("oks", [])), ""))


def submit_ready(rec):
    requester = submit_requester(rec)
    return requester in {str(uid) for uid in MEMBERS} and requester in rec.get("oks", [])


def pending_merges(st):
    shipped = set((st.get("active_submission") or {}).get("merged_commits", []))
    return [r for r in st.get("merged_candidates", []) if r["commit"] not in shipped]


def contains_commit(commit, head):
    return gh(["api", f"repos/{REPO}/compare/{commit}...{head}"])["behind_by"] == 0


def submit_plan(st, ref="main", force=False):
    if submit_frozen() and not force:
        raise RuntimeError(f"Freeze: no new submissions after 2026-10-08 {eta_clock('2026-10-08T20:00:00+09:00')}; rollbacks are handled manually.")
    sha = gh(["api", f"repos/{REPO}/commits/{quote(ref, safe='')}"])["sha"]
    subs = submission_list()
    active = next((s for s in subs if s.get("status") == "active"), None)
    tags = gh(["api", f"repos/{REPO}/tags?per_page=100", "--paginate", "--slurp"]) or []
    names = [s.get("name", "") for s in subs] + [t["name"] for page in tags for t in page]
    names += [r.get("version", "") for r in st.get("submits", {}).values()]
    versions = [int(m.group(1)) for name in names if (m := re.fullmatch(r"v(\d+)", name))]
    version = f"v{max(versions, default=0) + 1}"
    previous = st.get("active_submission") or {}
    known = active and previous.get("id") == active["id"]
    baseline = set(previous.get("merged_commits", [])) if known else set()
    included = [r for r in st.get("merged_candidates", []) if contains_commit(r["commit"], sha)]
    changes = [r for r in included if r["commit"] not in baseline]
    return {"status": "pending", "ref": ref, "commit": sha, "version": version, "bot_dir": "mybot2", "oks": [],
            "previous_id": active["id"] if active else None, "baseline_known": bool(known),
            "merged_commits": [r["commit"] for r in included], "cards": changes,
            "changes": [x for r in changes for x in r.get("changes", [])]}


def submit_embed(rec):
    changes = [f"[PR](https://github.com/{REPO}/pull/{r['pr']}) · " + ", ".join(card_ref(i) for i in r.get("issues", []))
               + ": " + "; ".join(r.get("changes", [])) for r in rec["cards"]]
    description = "\n".join(changes) or "No recorded merged candidates since the active submission."
    if not rec["baseline_known"]:
        description = "Active submission baseline is not recorded; showing all recorded candidates in this commit.\n" + description
    return {"title": f"Submit {rec.get('ref', 'main')[:100]}@{rec['commit'][:12]} as {rec['version']}", "description": description[:4000],
            "color": COLOR["candidate"], "fields": [
                {"name": "Commit", "value": rec["commit"], "inline": False},
                {"name": "OKs", "value": ", ".join(MEMBERS[int(uid)] for uid in rec["oks"]) or "None", "inline": False},
                {"name": "Freeze", "value": "Frozen; manual rollback only." if submit_frozen() else f"Open until 2026-10-08 {eta_clock('2026-10-08T20:00:00+09:00')}.", "inline": False},
                {"name": "Result", "value": rec.get("result", "Requester confirmation uploads this exact commit.")[:1024], "inline": False}],
            "footer": {"text": "Only the requester + confirmation are required to upload. Rollbacks are manual."}}


def bot_token():
    with open(os.path.join(ROOT, "docs", "discord.txt")) as source:
        token = source.read().strip().splitlines()[0].strip()
    return token[4:].strip() if token.lower().startswith("bot ") else token


def announce_file(path, dry_run=False):
    with open(path, encoding="utf-8") as source:
        text = source.read()
    if not text.strip() or len(text) > 2000:
        raise ValueError("Announcement must contain 1–2000 characters of nonempty text.")
    with open(os.path.join(ROOT, "data", "discord", "channel.txt")) as source:
        channel_id = int(source.read().strip())
    if dry_run:
        print(channel_id)
        print(text, end="" if text.endswith("\n") else "\n")
        return
    request = Request(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        data=json.dumps({"content": text}, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bot {bot_token()}", "Content-Type": "application/json",
                 "User-Agent": "meowbot (one-off announcement)"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        response.read()


def snooze_action(action, requester):
    who = MEMBERS.get(requester)
    if not who:
        raise ValueError('Only team members can use /meow.')
    number = action['card']
    try:
        issue = gh(['api', f'repos/{REPO}/issues/{number}'])
    except RuntimeError as exc:
        if '404' in str(exc):
            return f'Card #{number} was not found.'
        raise
    if (not issue or issue.get('state') != 'open' or 'pull_request' in issue
            or not is_board_card(issue.get('title', ''))):
        return f'Card #{number} was not found (an open [Idea]/[Task] card is required).'
    ref = ' '.join(card_ref({**issue, 'number': number}).split())
    if action['action'] == 'unsnooze':
        snooze.clear_snooze(number)
        return f'▶ {ref}: {who} resumed decision checks for this card.'
    entry = snooze.set_snooze(number, who, action['text'])
    return (f'⏸ {ref}: {who} is taking more time on the decision. '
            f'decision checks stay quiet for this card until ~{eta_clock(entry["until"])}. '
            f'"/meow {number} back" ends it early')


class SnoozeMeowUI(MeowUI):
    def __init__(self, *args, **kwargs):
        meow_chat.SCHEMA.update(snooze={'card', 'text'}, unsnooze={'card'})
        super().__init__(*args, **kwargs)

    async def snooze_reply(self, action, requester):
        try:
            return await asyncio.to_thread(snooze_action, action, requester)
        except Exception as exc:
            return (f'Card #{action["card"]} was not found.' if '404' in str(exc)
                    else f'Could not update the snooze for #{action["card"]}; please try again.')

    async def slash(self, it, message):
        action = snooze.parse_intent(message)
        if action is None:
            return await super().slash(it, message)
        if it.user.id not in self.api.MEMBERS:
            await it.response.send_message('Only team members can use /meow.', ephemeral=True)
            return
        await it.response.defer(thinking=True)
        await it.followup.send(await self.snooze_reply(action, it.user.id), allowed_mentions=self.d.AllowedMentions.none())

    async def typed(self, message):
        text = self.typed_text(message)
        action = snooze.parse_intent(text) if text else None
        if action is None:
            return await super().typed(message)
        await self.send(message.channel, await self.snooze_reply(action, message.author.id))
        return True

    async def offer(self, thread, requester, plan, reason=None):
        plan = meow_chat.validate_plan(plan, requester, self.api.MEMBERS)
        remaining = []
        for action in plan['actions']:
            if action['action'] in {'snooze', 'unsnooze'}:
                reply = await asyncio.to_thread(snooze_action, action, requester)
                await self.send(thread, reply)
            else:
                remaining.append(action)
        if remaining:
            await super().offer(thread, requester, {**plan, 'actions': remaining}, reason)


async def post_answer(who, card, text, channel):
    """Post the answer on the card and in the channel; returns why it was not posted, or None."""
    try:
        issue = await asyncio.to_thread(gh, ["api", f"repos/{REPO}/issues/{card}"])
        issue = {**issue, "number": card}
        ref = card_ref(issue)
        if issue["state"] != "open":
            return f"{ref} is not open."
        if "pull_request" in issue or not is_board_card(issue["title"]):
            return f"{ref} is not an [Idea]/[Task] card."
        comment = await asyncio.to_thread(gh, ["api", f"repos/{REPO}/issues/{card}/comments",
                                               "--method", "POST", "-f", f"body=Answer from {who}: {text}"])
        shown = text if len(text) <= 1500 else text[:1499] + "…"
        # Everyone should see answers, so the team can follow the card without opening GitHub.
        await channel.send(f"💬 {who} answered {ref}: {shown}\n{comment['html_url']}")
    except Exception:
        return f"Could not post an answer to {locals().get('ref', f'#{card}')}."


async def answer_card(it, card, text):
    who = MEMBERS.get(it.user.id)
    if not who:
        await it.response.send_message("Only team members can use meowbot commands.", ephemeral=True)
        return
    await it.response.defer(ephemeral=True, thinking=True)
    problem = await post_answer(who, card, text, it.channel)
    await it.followup.send(problem or "posted, everyone can see it above", ephemeral=True)


def typed_answer_parts(content):
    match = re.fullmatch(r"(?is)/answer\s+(?:card\s*[:=]?\s*)?#?(\d+)[\s,:]+(?:text\s*[:=]\s*)?(.+)", content.strip())
    return (int(match[1]), match[2].strip()) if match and match[2].strip() else None


async def typed_answer(message, channel):
    """"/answer …" sent as an ordinary message in #meow; the author is the one answering."""
    who = MEMBERS.get(message.author.id)
    if (message.author.bot or not who or channel is None or message.channel.id != channel.id
            or not re.match(r"(?i)/answer(?:\s|$)", message.content.strip())):
        return False
    parts = typed_answer_parts(message.content)
    problem = (await post_answer(who, *parts, message.channel) if parts
               else 'Which card? Write it like "/answer 39 looks right".')
    if problem:
        await message.reply(problem, mention_author=False)
    return True


def run_bot():
    import discord
    from discord import app_commands

    st = load_state()
    channel_id = int(open(os.path.join(ROOT, "data", "discord", "channel.txt")).read().strip())
    token = bot_token()
    analysis_lock = asyncio.Lock()
    approval_lock = asyncio.Lock()
    release_lock = asyncio.Lock()
    state = {"channel": None}
    chat = SnoozeMeowUI(sys.modules[__name__], discord, st, state, approval_lock, release_lock)

    async def member(it):
        if it.user.id in MEMBERS:
            return MEMBERS[it.user.id]
        await it.response.send_message("Only team members can use meowbot commands.", ephemeral=True)
        return None

    async def post_idea(number, url, title, body, area, wf):
        st.setdefault("self_ideas", []).append(number)
        save_state(st)
        issue = await asyncio.to_thread(gh, ["issue", "view", str(number), "--repo", REPO, "--json", "number,title,labels"])
        await state["channel"].send(embed=discord.Embed.from_dict(clamp_embed(idea_embed(number, f"[Idea] {title}", url, body, label_names(issue)))))

    def text_input(label, key, default="", required=False, style=None, maxlen=1500):
        return discord.ui.TextInput(label=label, custom_id=key, default=(default or "")[:maxlen] or None, required=required,
                                    style=style or discord.TextStyle.paragraph, max_length=maxlen)

    class HypoModal(discord.ui.Modal):
        def __init__(self, mode, area, issue=None, current=None, idea_by=None):
            title = {"light": "New hypothesis", "max": "New hypothesis (deep analysis)", "edit": f"Edit {card_ref(issue)}"[:45]}[mode]
            super().__init__(title=title, timeout=900)
            self.mode, self.area, self.issue = mode, area, issue
            self.idea_by = idea_by
            cur = current or {}
            self.f_title = text_input("Title | name:short-name (optional)", "title", (cur.get("title", "")[:94] + (" | name:" + cur["name"] if cur.get("name") else "")), True, discord.TextStyle.short, 120)
            self.f_claim = text_input("Claim: situation → what our bot should do", "claim", cur.get("claim"), True)
            self.f_evid = text_input("Evidence (replays, numbers, or a hunch)", "evidence", cur.get("evidence"))
            self.f_sig = text_input("Expected signal if it works", "expected_signal", cur.get("expected_signal"))
            self.f_fal = text_input("What would show it's wrong", "falsifier", cur.get("falsifier"))
            for item in (self.f_title, self.f_claim, self.f_evid, self.f_sig, self.f_fal):
                self.add_item(item)

        def values(self):
            return {"title": self.f_title.value.strip(), "claim": self.f_claim.value.strip(), "evidence": self.f_evid.value.strip(),
                    "expected_signal": self.f_sig.value.strip(), "falsifier": self.f_fal.value.strip()}

        async def on_submit(self, it):
            who = MEMBERS.get(it.user.id, it.user.display_name)
            raw = self.values()
            if " | name:" in raw["title"]:
                raw["title"], raw["name"] = map(str.strip, raw["title"].rsplit(" | name:", 1))
                if not valid_slug(raw["name"]):
                    await it.response.send_message("Name must be 1–2 lowercase words, hyphenated, at most 16 characters.", ephemeral=True)
                    return
            supplied_author = self.idea_by or next((body_author(value) for value in raw.values() if body_author(value)), None)
            proposer = author_name(author_label(supplied_author)) if supplied_author else who
            if self.mode == "max":
                await it.response.send_message("Queued for deep analysis. I'll post the card here when it's done (about 5–15 min).", ephemeral=True)
                await state["channel"].send(f"🔬 {who} asked for a deep analysis: **{raw['title']}**. Working on it (about 5–15 min).")
                asyncio.get_running_loop().create_task(run_analysis(proposer, self.area, raw))
                return
            await it.response.defer(ephemeral=True, thinking=True)
            try:
                fields, original = raw, None
                if non_english(*raw.values()):
                    fields, lang = await asyncio.to_thread(translate, raw)
                    original = {k: v for k, v in raw.items() if v}
                if self.mode == "light":
                    body = card_body(proposer, fields, original)
                    number, url = await asyncio.to_thread(create_issue, fields["title"], body, self.area, wf_for(proposer), fields.get("name"))
                    await post_idea(number, url, fields["title"], body, self.area, wf_for(proposer))
                    await it.followup.send(f"Added as {card_ref(number)}: {url}", ephemeral=True)
                else:
                    issue = await asyncio.to_thread(gh, ["issue", "view", str(self.issue), "--repo", REPO, "--json", "title,body,url,labels"])
                    body = replace_sections(issue["body"], fields)
                    if supplied_author:
                        body = re.sub(r"^\s*\*\*Idea by:\*\*.*$", "", body, flags=re.M).lstrip()
                        body = f"**Idea by:** {proposer} (via meowbot).\n\n" + body
                    if original:
                        body = body.rstrip() + "\n\n" + card_body(who, {}, original).split("\n\n")[-1]
                    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
                        fh.write(body)
                    edit_args = ["gh", "issue", "edit", str(self.issue), "--repo", REPO,
                                 "--title", f"[Idea] {fields['title']}", "--body-file", fh.name]
                    label = author_label(supplied_author) or body_author(body)
                    existing = [item["name"] for item in issue.get("labels", []) if item["name"].startswith("by:")]
                    if supplied_author or not existing:
                        if label:
                            for old in existing:
                                if old != label:
                                    edit_args += ["--remove-label", old]
                            edit_args += ["--add-label", label]
                    if raw.get("name"):
                        new_label = await asyncio.to_thread(name_label, fields["title"], raw["name"], self.issue)
                        for old in issue.get("labels", []):
                            if old["name"].startswith("name:"):
                                edit_args += ["--remove-label", old["name"]]
                        edit_args += ["--add-label", new_label]
                    await asyncio.to_thread(subprocess.run, edit_args, check=True)
                    os.unlink(fh.name)
                    await asyncio.to_thread(subprocess.run, ["gh", "issue", "comment", str(self.issue), "--repo", REPO,
                                                             "--body", f"Edited by {who} via meowbot (Discord)."], check=True)
                    await state["channel"].send(f"✏️ {who} edited {card_ref(self.issue)}: {issue['url']}")
                    await it.followup.send(f"Updated {card_ref(self.issue)}.", ephemeral=True)
            except Exception as exc:
                log("hypo error:", exc)
                await it.followup.send(f"Something went wrong: {str(exc)[:300]}", ephemeral=True)

    async def run_analysis(who, area, raw):
        async with analysis_lock:
            try:
                async with release_lock:
                    await asyncio.to_thread(sync_release)
                out = await asyncio.to_thread(claude_json, analysis_prompt(who, area, raw), *ANALYSIS_MODEL,
                                              cwd=RELEASE_DIR, timeout=ANALYSIS_TIMEOUT)
                fields = {k: (out.get(k) or "").strip() for k in ("title", "claim", "evidence", "expected_signal", "falsifier")}
                fields["title"] = fields["title"] or raw["title"]
                extra = {k: (out.get(k) or "").strip() for k, _ in EXTRA}
                original = {k: v for k, v in raw.items() if v} if non_english(*raw.values()) else None
                body = card_body(who, fields, original, extra, via="meowbot, analysed by AI")
                number, url = await asyncio.to_thread(create_issue, fields["title"], body, area, wf_for(who), raw.get("name"))
                await post_idea(number, url, fields["title"], body, area, wf_for(who))
                if out.get("summary"):
                    await state["channel"].send(f"🔬 Analysis for {card_ref(number)}: {out['summary'][:900]}")
            except Exception as exc:
                log("analysis error:", exc)
                await state["channel"].send(f"⚠️ Deep analysis of **{raw['title']}** failed: {str(exc)[:300]}")

    async def edit_candidate(name):
        rec = st["candidates"][name]
        emb = candidate_embed(rec["manifest"], rec)
        if rec.get("by"):
            emb["fields"].append({"name": "Approval", "value": f"{rec['status']} by {rec['by']}", "inline": False})
        if rec.get("merge_commit"):
            sha = rec["merge_commit"]
            emb["fields"].append({"name": "Merge commit", "value": f"[{sha}](https://github.com/{REPO}/commit/{sha})", "inline": False})
        view = CandidateView(name)
        for item in view.children:
            item.disabled = rec["status"] not in ("pending", "hold")
        try:
            await state["channel"].get_partial_message(rec["message_id"]).edit(embed=discord.Embed.from_dict(clamp_embed(emb)), view=view)
        except discord.HTTPException as exc:
            log("candidate card edit failed:", type(exc).__name__)

    async def post_candidates(candidates):
        seen = st.setdefault("candidates", {})
        for name, rec in candidates:
            if name in seen:
                continue
            await asyncio.to_thread(prepare_candidate, rec, seen)
            for old_name, old in list(seen.items()):
                if old.get("pr") == rec["pr"] and old.get("head_sha") != rec["head_sha"] and old.get("status") in ("pending", "hold"):
                    old.update(status="stale", result="PR head changed. Use the new candidate card.")
                    save_state(st)
                    await edit_candidate(old_name)
            msg = await state["channel"].send(embed=discord.Embed.from_dict(clamp_embed(candidate_embed(rec["manifest"], rec))), view=CandidateView(name))
            seen[name] = dict(rec, message_id=msg.id)
            save_state(st)

    class CandidateConfirm(discord.ui.View):
        active = {}

        def __init__(self, candidate, user_id):
            super().__init__(timeout=120)
            self.candidate, self.user_id, self.used = candidate, user_id, False
            self.active[(candidate.name, user_id)] = self
            yes = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
            no = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
            yes.callback, no.callback = self.confirm, self.cancel
            self.add_item(yes)
            self.add_item(no)

        async def on_timeout(self):
            self.used = True

        async def check(self, it):
            if it.user.id != self.user_id or it.user.id not in MEMBERS:
                await it.response.send_message("Only the team member who opened this confirmation can use it.", ephemeral=True)
                return False
            if self.used:
                await it.response.send_message("This confirmation was already handled.", ephemeral=True)
                return False
            return True

        async def cancel(self, it):
            if await self.check(it):
                self.used = True
                await it.response.edit_message(content="Cancelled. No merge or upload was attempted.", view=None)
                self.stop()

        async def confirm(self, it):
            if not await self.check(it):
                return
            rec = await self.candidate.check(it)
            if not rec:
                return
            if not approval_ready(rec):
                await it.response.send_message("More member OKs are required before confirming.", ephemeral=True)
                return
            self.used = True
            async with approval_lock:
                await it.response.defer(ephemeral=True, thinking=True)
                try:
                    p = await asyncio.to_thread(candidate_pr, rec["pr"])
                    if p["headRefOid"] != rec["head_sha"]:
                        rec.update(status="stale", result="PR head changed. Approval refused; a new card is required.")
                        save_state(st)
                        await edit_candidate(self.candidate.name)
                        await post_candidates(await asyncio.to_thread(pr_candidates, p))
                        await it.followup.send(rec["result"], ephemeral=True)
                        return
                    if p["state"] != "OPEN" or p["baseRefName"] != "main" or p["isDraft"]:
                        await it.followup.send("Approval refused: PR must be open, non-draft, target main and be mergeable. Try again after it is ready.", ephemeral=True)
                        return
                    if not await asyncio.to_thread(candidate_current, rec):
                        rec["result"] = await asyncio.to_thread(request_rebase, rec)
                        save_state(st)
                        await edit_candidate(self.candidate.name)
                        await it.followup.send(rec["result"], ephemeral=True)
                        return
                    if p["mergeable"] != "MERGEABLE":
                        await it.followup.send("Approval refused: PR must be mergeable. Try again after it is ready.", ephemeral=True)
                        return
                    rec.update(status="approving", by=MEMBERS[it.user.id], at=datetime.datetime.now().isoformat(timespec="seconds"),
                               result="Merging PR into main…")
                    save_state(st)
                    await edit_candidate(self.candidate.name)
                    rec["merge_commit"] = await asyncio.to_thread(merge_candidate, rec)
                    save_state(st)
                    issues = sorted({i for other in st["candidates"].values() if other.get("pr") == rec["pr"] and other.get("head_sha") == rec["head_sha"]
                                     for i in other["manifest"].get("issues", [])})
                    st.setdefault("merged_candidates", []).append({"pr": rec["pr"], "commit": rec["merge_commit"],
                        "issues": issues, "changes": list(dict.fromkeys(x for other in st["candidates"].values()
                            if other.get("pr") == rec["pr"] and other.get("head_sha") == rec["head_sha"]
                            for x in other["manifest"].get("changes", []))), "at": rec["at"]})
                    save_state(st)
                    await asyncio.to_thread(keep_cards, issues, rec["merge_commit"])
                    rec.update(status="approved", result=f"merged to main as {rec['merge_commit']}; ships with the next /submit")
                except Exception as exc:
                    log("candidate approval failed:", type(exc).__name__)
                    if rec.get("status") == "approving":
                        rec.update(status="error", result="Approval stopped. Check the PR and linked card state manually before retrying; no automatic retry.")
                    else:
                        await it.followup.send("Could not check or refresh the PR. No merge or upload was attempted.", ephemeral=True)
                        return
                finally:
                    save_state(st)
                    self.stop()
                for name, other in st["candidates"].items():
                    if other is not rec and other.get("pr") == rec["pr"] and other.get("status") in ("pending", "hold"):
                        other.update(status="stale", result="This PR was handled through another candidate card. Check that card's result.")
                        save_state(st)
                        await edit_candidate(name)
                await edit_candidate(self.candidate.name)
                merge = f"Merged as {rec['merge_commit']}. " if rec.get("merge_commit") else ""
                await it.followup.send(f"{MEMBERS[it.user.id]}: {merge}{rec['result']}", ephemeral=True)

    class CandidateView(discord.ui.View):
        def __init__(self, name):
            super().__init__(timeout=None)
            self.name = name
            a = discord.ui.Button(label="OK", emoji="✅", style=discord.ButtonStyle.success, custom_id=f"approve:{name}")
            h = discord.ui.Button(label="Hold", emoji="⏸", style=discord.ButtonStyle.secondary, custom_id=f"hold:{name}")
            a.callback, h.callback = self.approve, self.hold
            self.add_item(a)
            self.add_item(h)
            force = discord.ui.Button(label="Force", style=discord.ButtonStyle.secondary, custom_id=f"force:{name}")
            force.callback = lambda it: chat.force(it, {"action": "vote", "candidate": self.name, "vote": "OK"})
            self.add_item(force)

        async def check(self, it):
            if it.user.id not in MEMBERS:
                await it.response.send_message("Only team members can use this.", ephemeral=True)
                return None
            rec = st.get("candidates", {}).get(self.name)
            if not rec or rec.get("status") not in ("pending", "hold"):
                await it.response.send_message("This candidate was already decided.", ephemeral=True)
                return None
            if not rec.get("head_sha"):
                await it.response.send_message("This legacy card is retired. Use a candidate card from an open PR.", ephemeral=True)
                return None
            if approval_lock.locked():
                await it.response.send_message("Another approval is running. Try again when it finishes.", ephemeral=True)
                return None
            return rec

        async def approve(self, it):
            rec = await self.check(it)
            if not rec:
                return
            if "author_labels" not in rec:
                try:
                    labels = await asyncio.to_thread(candidate_authors, rec["manifest"])
                except Exception:
                    await it.response.send_message("Could not read idea authors. No OK was recorded; try again later.", ephemeral=True)
                    return
                rec.setdefault("author_labels", labels)
                rec.setdefault("oks", [])
            if "patch_id" not in rec:
                try:
                    rec["patch_id"] = await asyncio.to_thread(candidate_patch_id, rec)
                except Exception:
                    await it.response.send_message("Could not identify the patch. Try again later.", ephemeral=True)
                    return
            added = record_ok(rec, it.user.id)
            save_state(st)
            ready = approval_ready(rec)
            if not ready:
                await it.response.send_message("OK recorded; waiting for the required members." if added else "Your OK is already recorded.", ephemeral=True)
                await edit_candidate(self.name)
                return
            active = CandidateConfirm.active.get((self.name, it.user.id))
            if active and not active.used:
                await it.response.send_message("Your OK is already recorded. Use your existing Confirm/Cancel prompt.", ephemeral=True)
                await edit_candidate(self.name)
                return
            text = f"Merge {', '.join(card_ref(i) for i in rec['manifest'].get('issues', []))} ([PR]({rec['url']})) into main? Ships with the next /submit."
            await it.response.send_message(text, view=CandidateConfirm(self, it.user.id), ephemeral=True)
            await edit_candidate(self.name)

        async def hold(self, it):
            rec = await self.check(it)
            if not rec:
                return
            rec.update(status="hold", by=MEMBERS[it.user.id])
            save_state(st)
            await it.response.send_message(f"⏸ {MEMBERS[it.user.id]} put {rec['manifest']['version']} on hold. Anyone can still approve it later.")

    async def edit_submit(name):
        rec = st["submits"][name]
        view = SubmitView(name)
        for button in view.children:
            button.disabled = rec["status"] != "pending"
        try:
            await state["channel"].get_partial_message(rec["message_id"]).edit(
                embed=discord.Embed.from_dict(clamp_embed(submit_embed(rec))), view=view)
        except discord.HTTPException as exc:
            log("submit card edit failed:", type(exc).__name__)

    class SubmitConfirm(discord.ui.View):
        def __init__(self, name, user_id):
            super().__init__(timeout=120)
            self.name, self.user_id, self.used = name, user_id, False
            yes = discord.ui.Button(label="Confirm upload", style=discord.ButtonStyle.success)
            no = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
            yes.callback, no.callback = self.confirm, self.cancel
            self.add_item(yes)
            self.add_item(no)

        async def check(self, it):
            if (self.used or it.user.id != self.user_id or it.user.id not in MEMBERS
                    or str(it.user.id) != submit_requester(st["submits"][self.name])):
                await it.response.send_message("This confirmation belongs to its member and can be used once.", ephemeral=True)
                return False
            return True

        async def on_timeout(self):
            self.used = True

        async def cancel(self, it):
            if await self.check(it):
                self.used = True
                await it.response.edit_message(content="Cancelled. OKs retained; no upload attempted.", view=None)
                self.stop()

        async def confirm(self, it):
            if not await self.check(it):
                return
            self.used = True
            await it.response.defer(ephemeral=True, thinking=True)
            async with approval_lock:
                rec = st["submits"][self.name]
                if rec["status"] != "pending" or not submit_ready(rec):
                    await it.followup.send("Requester OK and a pending submit card are required.", ephemeral=True)
                    return
                if submit_frozen():
                    await it.followup.send("Freeze: no new submissions; rollbacks are handled manually.", ephemeral=True)
                    return
                try:
                    subs = await asyncio.to_thread(submission_list)
                    active = next((s for s in subs if s.get("status") == "active"), None)
                    if (active["id"] if active else None) != rec["previous_id"]:
                        rec.update(status="stale", result="Active submission changed. Request a new /submit preview and confirmation.")
                    elif any(s.get("name") == rec["version"] for s in subs):
                        rec.update(status="stale", result="Version name is already used. Request a new /submit.")
                    else:
                        async with release_lock:
                            await asyncio.to_thread(sync_release, rec["commit"])
                            if submit_frozen():
                                raise RuntimeError("Freeze reached before upload; no upload attempted.")
                            rec.update(status="submitting", result="Uploading the approved exact commit…")
                            save_state(st)
                            await edit_submit(self.name)
                            result = await asyncio.to_thread(upload, rec)
                            rec.update(status="submitted" if result["ok"] else "error", result=result["result"],
                                       submission_id=result.get("id"))
                            if result["ok"]:
                                st["active_submission"] = {"id": result["id"], "version": rec["version"],
                                    "commit": rec["commit"], "previous_id": rec["previous_id"],
                                    "merged_commits": rec["merged_commits"]}
                except Exception as exc:
                    rec.update(status="error", result="Submission stopped; check remote state before retrying. " + str(exc)[:500])
                finally:
                    save_state(st)
                    self.stop()
                await edit_submit(self.name)
                await it.followup.send(rec["result"], ephemeral=True)

    class SubmitView(discord.ui.View):
        def __init__(self, name):
            super().__init__(timeout=None)
            self.name = name
            button = discord.ui.Button(label="Review / confirm", emoji="✅", style=discord.ButtonStyle.success, custom_id=f"submit:{name}")
            button.callback = self.approve
            self.add_item(button)
            force = discord.ui.Button(label="Force", style=discord.ButtonStyle.secondary, custom_id=f"force-submit:{name}")
            force.callback = lambda it: chat.force(it, {"action": "submit", "ref": st["submits"][name]["commit"]})
            self.add_item(force)

        async def approve(self, it):
            if it.user.id not in MEMBERS:
                await it.response.send_message("Only team members can use this.", ephemeral=True)
                return
            async with approval_lock:
                rec = st["submits"][self.name]
                if rec["status"] != "pending" or submit_frozen():
                    await it.response.send_message("Submit is no longer pending or the submission freeze has begun.", ephemeral=True)
                    return
                if str(it.user.id) != submit_requester(rec):
                    await it.response.send_message("Only the requester can confirm this submit.", ephemeral=True)
                    return
                record_ok(rec, it.user.id)
                save_state(st)
                if submit_ready(rec):
                    await it.response.send_message(f"Upload {rec['commit']} as {rec['version']}?",
                        view=SubmitConfirm(self.name, it.user.id), ephemeral=True)
                else:
                    await it.response.send_message("Requester OK is required before confirmation.", ephemeral=True)
                await edit_submit(self.name)

    area_choices = [app_commands.Choice(name=a, value=a) for a in AREAS]

    class Bot(discord.Client):
        def __init__(self, **kw):
            super().__init__(**kw)
            self.tree = app_commands.CommandTree(self)

        async def on_message(self, message):
            if not await typed_answer(message, state["channel"]):
                await chat.followup(message)

        async def setup_hook(self):
            chat.restore(self)
            # Restore legacy Force menus already posted in Discord.
            for number in st.get("idea_states", {}):
                self.add_view(chat.CardForceView(int(number)))

            @self.tree.command(name="meow", description="Talk to your teammate; use 'queue' for unresolved requests")
            @app_commands.describe(message="Question, action, or force request")
            async def meow_cmd(it: discord.Interaction, message: str):
                await chat.slash(it, message)

            for name, rec in st.get("candidates", {}).items():
                if rec.get("status") in ("pending", "hold"):
                    self.add_view(CandidateView(name))

            for name, rec in st.get("submits", {}).items():
                if rec.get("status") == "pending":
                    self.add_view(SubmitView(name))

            @self.tree.command(name="submit", description="Preview an exact release and confirm upload as the requesting member")
            @app_commands.describe(ref="Commit or ref to submit (default main)")
            async def submit_cmd(it: discord.Interaction, ref: str = "main"):
                if not await member(it):
                    return
                await it.response.defer(ephemeral=True, thinking=True)
                async with approval_lock:
                    try:
                        rec = await asyncio.to_thread(submit_plan, st, ref)
                        rec["requester_id"] = str(it.user.id)
                        record_ok(rec, it.user.id)
                        name = os.urandom(12).hex()
                        msg = await state["channel"].send(embed=discord.Embed.from_dict(clamp_embed(submit_embed(rec))), view=SubmitView(name))
                        st.setdefault("submits", {})[name] = dict(rec, message_id=msg.id)
                        save_state(st)
                        await it.followup.send(embed=discord.Embed.from_dict(clamp_embed(submit_embed(rec))),
                            view=SubmitConfirm(name, it.user.id), ephemeral=True)
                    except Exception as exc:
                        await it.followup.send(str(exc)[:1000], ephemeral=True)

            async def author_choices(it, current):
                return [app_commands.Choice(name=name, value=name) for name in AUTHOR_LABELS
                        if member_name(current).casefold() in name.casefold()]

            async def task_choices(it, current):
                return [app_commands.Choice(name=name, value=name) for name in ("me", "jun", "Zhe", "QWQ", "all")
                        if member_name(current).casefold() in name.casefold()]

            @self.tree.command(name="hypo", description="Add a hypothesis to the idea board (Korean, Chinese or English)")
            @app_commands.describe(area="Which part of the bot it is about", idea_by="Proposer, if this is someone else's idea")
            @app_commands.autocomplete(idea_by=author_choices)
            @app_commands.choices(area=area_choices)
            async def hypo(it: discord.Interaction, area: app_commands.Choice[str], idea_by: str = None):
                if await member(it):
                    await it.response.send_modal(HypoModal("light", area.value, idea_by=idea_by))

            @self.tree.command(name="hypo-max", description="Add a hypothesis and let the AI analyse it in depth first")
            @app_commands.describe(area="Which part of the bot it is about", idea_by="Proposer, if this is someone else's idea")
            @app_commands.autocomplete(idea_by=author_choices)
            @app_commands.choices(area=area_choices)
            async def hypo_max(it: discord.Interaction, area: app_commands.Choice[str], idea_by: str = None):
                if await member(it):
                    await it.response.send_modal(HypoModal("max", area.value, idea_by=idea_by))

            def cards(dicts):
                return [discord.Embed.from_dict(clamp_embed(d)) for d in dicts[:10]]

            @self.tree.command(name="task", description="What each person needs to do next (private unless share is true)")
            @app_commands.describe(who="Whose tasks to show (default all, you first)", share="Show the answer to everyone in this channel")
            @app_commands.autocomplete(who=task_choices)
            async def task_cmd(it: discord.Interaction, who: str = "all", share: bool = False):
                await reply_tasks(it, st, who, share)

            @self.tree.command(name="board", description="Running loops, the loop queue and the untested ideas (only you see this)")
            async def board(it: discord.Interaction):
                if not await member(it):
                    return
                await it.response.defer(ephemeral=True, thinking=True)
                ideas, (loops, status_url) = await asyncio.gather(asyncio.to_thread(board_state), asyncio.to_thread(loop_status))
                titles = {i["n"]: i for i in ideas}
                running = [loop_card(k, l, titles) for k, l in loops.items() if l.get("state") == "running"]
                if not running:
                    running = [{"title": "▶ Running now", "description": "No loop is running right now.", "color": 0x6E7781}]
                queue = order_cards([i for i in ideas if i["status"] == "ready"],
                                    read_fair(os.path.join(LOOK_DIR, "fair.json")))
                next_up = ("task" if "type:task" in label_names(queue[0]) else
                           {"by:zhe": "Zhe", "by:qwq": "QWQ", "by:junsing": "jun", "by:ai": "AI"}.get(queue_author(queue[0]), "unknown")) if queue else "none"
                waiting = [i for i in ideas if i["status"] != "ready"]
                out = running[:6] + idea_cards(f"⏭ Queue · next up: {next_up}", queue, 0x0E8A16, "Empty. Add `status:ready` to an idea to queue it.") \
                      + idea_cards("📋 Open ideas", waiting, COLOR["idea"], "None.")
                out[-1]["footer"] = {"text": "① Zhe judges · ② area owner judges · ③ AI judges · /loop for details · /board-edit <number> to edit"}
                for batch in card_batches(out):
                    await it.followup.send(embeds=cards(batch), ephemeral=True)

            @self.tree.command(name="loop", description="What every loop is doing now, the queue and the latest results (only you see this)")
            async def loop_cmd(it: discord.Interaction):
                if not await member(it):
                    return
                await it.response.defer(ephemeral=True, thinking=True)
                ideas, (loops, status_url), results = await asyncio.gather(
                    asyncio.to_thread(board_state), asyncio.to_thread(loop_status), asyncio.to_thread(recent_results))
                final_numbers = {i["n"] for i in ideas if i["status"] in FINAL_STATES}
                ideas = [i for i in ideas if i["status"] not in FINAL_STATES]
                loops = {k: l for k, l in loops.items() if l.get("issue") not in final_numbers}
                results = [r for r in results if r["n"] not in final_numbers]
                titles = {i["n"]: i for i in ideas}
                order = {"running": 0, "idle": 1, "stopped": 2}
                loop_cards = [loop_card(k, l, titles) for k, l in sorted(loops.items(), key=lambda kv: order.get(kv[1].get("state"), 3))]
                if not loop_cards:
                    loop_cards = [{"title": "Loops", "description": "No loop has reported yet.", "color": 0x6E7781}]
                queue = order_cards([i for i in ideas if i["status"] == "ready"],
                                    read_fair(os.path.join(LOOK_DIR, "fair.json")))
                next_up = ("task" if "type:task" in label_names(queue[0]) else
                           {"by:zhe": "Zhe", "by:qwq": "QWQ", "by:junsing": "jun", "by:ai": "AI"}.get(queue_author(queue[0]), "unknown")) if queue else "none"
                waiting = [i for i in ideas if i["status"] != "ready"]
                out = loop_cards[:7] + idea_cards(f"⏭ Queue · next up: {next_up}", queue, 0x0E8A16, "Empty.") \
                      + idea_cards("📋 Open ideas", waiting, COLOR["idea"], "None.") + [results_card(results, titles)]
                for batch in card_batches(out):
                    await it.followup.send(embeds=cards(batch), ephemeral=True)

            @self.tree.command(name="status", description="One-screen summary: ladder, PRs, board and loops (only you see this)")
            async def status_cmd(it: discord.Interaction):
                if not await member(it):
                    return
                await it.response.defer(ephemeral=True, thinking=True)
                since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                ideas, (loops, _), ladder, prs, merged, known_cards = await asyncio.gather(
                    asyncio.to_thread(board_state), asyncio.to_thread(loop_status), asyncio.to_thread(ladder_summary),
                    asyncio.to_thread(gh, ["pr", "list", "--repo", REPO, "--state", "open", "--json", "number,title,body,isDraft,author,url"]),
                    asyncio.to_thread(gh, ["pr", "list", "--repo", REPO, "--state", "merged", "--search", f"merged:>={since}", "--json", "number,title,body,url"]),
                    asyncio.to_thread(gh, ["issue", "list", "--repo", REPO, "--state", "all", "--limit", "1000", "--json", "number,title,labels,url"]))
                counts = {}
                for i in ideas:
                    counts[i["status"]] = counts.get(i["status"], 0) + 1
                pr_lines = [pr_line(p, known_cards) + (" (draft)" if p.get("isDraft") else "") for p in (prs or [])]
                mg_lines = [pr_line(p, known_cards) for p in (merged or [])]
                loop_lines = [f"{STATE_ICON.get(l.get('state'), '•')} {WF_ICON.get(str(l.get('wf')), '·')} {k}"
                              + (f" · {card_ref(next((i for i in ideas if i['n'] == l['issue']), l['issue']))}" if l.get("issue") else "")
                              + (f" · {loop_eta(l)}" if l.get("eta_at") else "") for k, l in loops.items()]
                queued = sum(1 for i in ideas if i["ready"] and not i["running"])
                status = {
                    "title": "📊 meow status", "color": COLOR["analysis"],
                    "fields": [
                        {"name": "🏆 Ladder", "value": ladder, "inline": False},
                        {"name": "Submissions", "value": f"Recorded active submission: {(st.get('active_submission') or {}).get('id', 'unknown')} "
                         f"{(st.get('active_submission') or {}).get('version', '')}\nmerged but not yet submitted: "
                         f"{len({i for r in pending_merges(st) for i in r.get('issues', [])})} cards", "inline": False},
                        {"name": f"🔀 Open PRs ({len(pr_lines)})", "value": "\n".join(pr_lines)[:1000] or "None.", "inline": False},
                        {"name": f"✅ Merged in the last day ({len(mg_lines)})", "value": "\n".join(mg_lines)[:1000] or "None.", "inline": False},
                        {"name": "💡 Ideas", "value": "\n".join(f"{k}: {v}" for k, v in sorted(counts.items())) + f"\nqueued: {queued}" if counts else "None.", "inline": True},
                        {"name": "🔁 Loops", "value": "\n".join(loop_lines)[:1000] or "None reported.", "inline": True},
                    ],
                }
                from meow_chat import queue_text
                status["fields"].append({"name": "/meow queue", "value": queue_text(st, limit=5)[:1000], "inline": False})
                await it.followup.send(embeds=cards([status]), ephemeral=True)

            @self.tree.command(name="answer", description="Answer an open idea or task card (Korean, Chinese or English)")
            @app_commands.describe(card="The card's issue number", text="Your answer, posted as written")
            async def answer(it: discord.Interaction, card: int, text: str):
                await answer_card(it, card, text)

            @self.tree.command(name="board-edit", description="Edit an idea on the board by its issue number")
            @app_commands.describe(number="The idea's issue number, as shown by /board", idea_by="Change the idea author")
            @app_commands.autocomplete(idea_by=author_choices)
            async def board_edit(it: discord.Interaction, number: int, idea_by: str = None):
                if not await member(it):
                    return
                try:
                    issue = await asyncio.to_thread(gh, ["issue", "view", str(number), "--repo", REPO, "--json", "number,title,body,state,labels"])
                except RuntimeError:
                    await it.response.send_message(f"#{number} was not found.", ephemeral=True)
                    return
                if not issue["title"].lower().startswith("[idea]"):
                    await it.response.send_message(f"#{number} is not an idea card.", ephemeral=True)
                    return
                sec = parse_card(issue["body"])
                cur = {"title": re.sub(r"^\[Idea\]\s*", "", issue["title"], flags=re.I)}
                cur["name"] = card_name(issue)
                cur.update({k: sec.get(h, "") for k, h in CARD})
                await it.response.send_modal(HypoModal("edit", None, number, cur, idea_by=idea_by))

            ch = await self.fetch_channel(channel_id)
            state["channel"] = ch
            guild = discord.Object(id=ch.guild.id)
            self.tree.copy_global_to(guild=guild)
            try:
                synced = await self.tree.sync(guild=guild)
                log("slash commands synced:", ", ".join(c.name for c in synced))
            except discord.Forbidden:
                log("slash command sync forbidden; re-invite with scope applications.commands:",
                    f"https://discord.com/oauth2/authorize?client_id={self.application_id}&scope=bot+applications.commands&permissions=277025508352")
            self.loop.create_task(self.poll())

        async def poll(self):
            await self.wait_until_ready()
            ch = state["channel"] or await self.fetch_channel(channel_id)
            state["channel"] = ch
            log(f"ready as {self.user}, posting to #{ch.name}")
            while not self.is_closed():
                try:
                    eta_events = await asyncio.to_thread(tail_loop_events, st)
                    save_state(st)
                    for offset, message in eta_events:
                        if message:
                            await ch.send(message, allowed_mentions=discord.AllowedMentions.none())
                        st['loop_events_offset'] = offset
                        save_state(st)
                    for kind, n, extra in await asyncio.to_thread(new_events, st):
                        if kind in ("verdict", "state"):
                            await send_state_message(ch, n, extra, discord)
                            continue
                        if kind == "pr":
                            emb = await asyncio.to_thread(pr_embed, n, extra)
                        else:
                            emb = idea_embed(n, extra["title"], extra["html_url"], extra.get("body"), [l["name"] for l in extra.get("labels", [])])
                        await ch.send(embed=discord.Embed.from_dict(clamp_embed(emb)))
                    if not approval_lock.locked():
                        async with approval_lock:
                            await post_candidates(await asyncio.to_thread(new_candidates, st))
                    await chat.poll(self)
                    await chat.outside_offers(self)
                    save_state(st)
                except Exception as exc:
                    log("poll error:", exc)
                await asyncio.sleep(POLL_SECONDS)

    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_messages = True
    intents.message_content = True
    try:
        Bot(intents=intents).run(token, log_handler=None)
    except discord.errors.PrivilegedIntentsRequired:
        # Message Content Intent is off in the developer portal: run without thread follow-ups.
        log("message content intent is off; /meow follow-ups need /meow each time")
        intents.message_content = False
        Bot(intents=intents).run(token, log_handler=None)


def show(emb):
    emb = clamp_embed(emb)
    print(emb["title"])
    if emb.get("url"):
        print(emb["url"])
    if emb.get("description"):
        print(emb["description"])
    for f in emb.get("fields", []):
        print(f"  {f['name']}: {f['value']}")
    if emb.get("footer"):
        print("  —", emb["footer"]["text"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-pr", type=int)
    ap.add_argument("--preview-candidate")
    ap.add_argument("--preview-candidate-pr", type=int)
    ap.add_argument("--preview-tasks", action="store_true")
    ap.add_argument("--who", type=member_name, choices=("jun", "Zhe", "QWQ", "all"))
    ap.add_argument("--announce-file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.who and not a.preview_tasks:
        ap.error("--who requires --preview-tasks")
    if a.dry_run and not a.announce_file:
        ap.error("--dry-run requires --announce-file")
    if a.announce_file:
        if a.preview_pr or a.preview_candidate or a.preview_candidate_pr or a.preview_tasks:
            ap.error("--announce-file cannot be combined with preview options")
        try:
            announce_file(a.announce_file, a.dry_run)
        except Exception as exc:
            ap.exit(1, f"Announcement failed ({type(exc).__name__}).\n")
        return
    if a.preview_tasks:
        if a.preview_pr or a.preview_candidate or a.preview_candidate_pr:
            ap.error("--preview-tasks cannot be combined with other preview options")
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            print(task_lists.render(task_lists.collect(now), who=a.who, now=now))
        except Exception as exc:
            ap.exit(1, f"Task preview failed: {exc}\n")
        return
    if a.preview_pr:
        show(pr_embed(a.preview_pr, "opened"))
        return
    if a.preview_candidate:
        show(candidate_embed(json.load(open(a.preview_candidate))))
        return
    if a.preview_candidate_pr:
        candidates = pr_candidates(candidate_pr(a.preview_candidate_pr))
        if not candidates:
            print("No valid candidate manifests found in this open PR.")
        for name, rec in candidates:
            print(f"Manifest: {rec['path']}")
            prepare_candidate(rec, {})
            show(candidate_embed(rec["manifest"], rec))
            print("  [OK] [Hold]")
        return
    run_bot()


if __name__ == "__main__":
    main()
