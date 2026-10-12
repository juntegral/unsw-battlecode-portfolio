"""Read-only task collection and Discord text, without Discord or model calls."""
import datetime as dt
import json
import os
import re

from card_names import card_ref, label_names
from decision_nudge import PEOPLE
import snooze
from member_names import member_name

NAMES = ('jun', 'Zhe', 'QWQ')
OFFSETS = {'jun': 9, 'Zhe': 2, 'QWQ': 11}
FOOTER = ('to answer a card, reply to its ping or tell @meowbot in your own words, or use /answer card:N text:…'
          ' · "/meow N still deciding" quiets the hourly check')
ACTIONS = {'needs-info': "answer the loop's questions before the build",
           'needs-look': 'check 2 to 3 replays',
           'tested': 'decide: ship it, drop it or revise',
           'candidate': 'OK the candidate'}


def stamp(value):
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError):
        return None


def read_snapshot(path):
    try:
        with open(path, encoding='utf-8') as stream:
            return json.load(stream).get('cards', {})
    except (OSError, ValueError, TypeError, AttributeError):
        return {}


def collect(now, state=None):
    # Import lazily so previews and the running bot share the same read helpers.
    import meowbot as bot
    cards = bot.board_state()
    prs = bot.gh(['pr', 'list', '--repo', bot.REPO, '--state', 'open', '--limit', '200',
                  '--json', 'number,title,url,createdAt,updatedAt,headRefOid,files']) or []
    state = bot.load_state() if state is None else state
    snapshot = read_snapshot(os.path.join(bot.LOOK_DIR, 'status.json'))
    quiet = snooze.read_store()
    people = {name: {'todo': [], 'yours': [], 'parked': []} for name in NAMES}
    data = {'people': people, 'anyone': [], 'now': now.isoformat()}
    by_number = {c['n']: c for c in cards}
    open_prs = {p['number']: p for p in prs}
    handled = set()
    candidate_prs = {p['number'] for p in prs if any(
        re.fullmatch(r'candidates/[^/]+\.json', f.get('path', '')) for f in p.get('files', []))}
    records = list(state.get('candidates', {}).values())
    for pr in prs:
        if pr['number'] in candidate_prs and not any(
                r.get('pr') == pr['number'] and r.get('head_sha') == pr.get('headRefOid') for r in records):
            for _, rec in bot.pr_candidates(dict(pr, state='OPEN')):
                records.append({**rec, 'unposted': True, 'oks': [],
                                'author_labels': bot.candidate_authors(rec['manifest'])})

    def todo(name, ref, action, reply, since, number=None):
        entry = quiet.get(str(number), {}) if number is not None else {}
        until = stamp(entry.get('until'))
        people[name]['todo'].append({'ref': ref, 'action': action, 'reply': reply,
                                    'since': since, 'waited': age(since, now),
                                    'quiet_until': entry['until'] if until and until > now else None})

    for rec in records:
        pr = open_prs.get(rec.get('pr'))
        if not pr:
            continue
        if rec.get('status') not in ('pending', 'hold') or rec.get('head_sha') != pr.get('headRefOid'):
            continue
        candidate_prs.add(pr['number'])
        numbers = rec.get('manifest', {}).get('issues', [])
        handled.update(numbers)
        labels = set((rec.get('author_labels') or ['by:unknown']) if 'author_labels' in rec
                     else bot.candidate_authors(rec['manifest']))
        authors = {person[0] for label, person in PEOPLE.items() if label in labels}
        votes = {bot.MEMBERS[int(uid)] for uid in rec.get('oks', []) if str(uid) in {str(i) for i in bot.MEMBERS}}
        others = set(NAMES) - authors
        missing = []
        if labels == {'by:ai'}:
            if not votes:
                missing = [('1 member OK', set(NAMES))]
        elif not authors:
            if len(votes) < 2:
                missing = [(f'{2 - len(votes)} distinct member OK(s)', set(NAMES) - votes)]
        else:
            if not votes & authors:
                missing.append(('author OK: ' + '/'.join(n for n in NAMES if n in authors), authors))
            if not votes & others:
                missing.append(('non-author OK', others))
        refs = ', '.join(card_ref(by_number.get(n, {'n': n})) for n in numbers)
        ref = (refs + ' · ' if refs else '') + f"PR #{pr['number']}"
        since = pr.get('updatedAt') or pr.get('createdAt')
        reply = (f"open {pr['url']} (wait for the candidate post)" if rec.get('unposted')
                 else 'press OK on the candidate post')
        for name in NAMES:
            needs = [kind for kind, eligible in missing if name in eligible]
            if needs:
                todo(name, ref, 'give ' + ' + '.join(needs), reply, since,
                     numbers[0] if len(numbers) == 1 else None)
            elif not missing and name in votes:
                todo(name, ref, 'confirm merge', reply + ', then Confirm', since,
                     numbers[0] if len(numbers) == 1 else None)
        shared = [(kind, eligible) for kind, eligible in missing if not kind.startswith('author OK:')]
        if shared:
            need = '; '.join(kind + ' from ' + '/'.join(n for n in NAMES if n in eligible) for kind, eligible in shared)
            data['anyone'].append({'text': f"[PR #{pr['number']}]({pr['url']}): missing {need}; {reply}", 'since': since})

    for card in cards:
        labels = label_names(card)
        name = next((PEOPLE[l][0] for l in labels if l in PEOPLE), None)
        if not name:
            continue
        status, number, ref = card['status'], card['n'], card_ref(card)
        if status in ACTIONS:
            if status == 'candidate' and number in handled:
                continue
            if status == 'needs-look' and name != 'Zhe':
                people[name]['yours'].append({'ref': ref, 'step': 'replay check passes by itself', 'eta_at': None})
                continue
            todo(name, ref, ACTIONS[status], 'press OK on the candidate post' if status == 'candidate'
                 else f'tell @meowbot, or /answer card:{number} text:…', card.get('updated') or card.get('created'), number)
        elif status in ('ready', 'building', 'testing', 'in-progress') or card.get('ready') or card.get('running'):
            info = snapshot.get(str(number), {})
            step = 'in progress by hand' if status == 'in-progress' else info.get('step') or (
                'queued' if status == 'ready' or card.get('ready') else status)
            eta = (info.get('new_eta_at') if info.get('late') else None) or info.get('eta_at')
            people[name]['yours'].append({'ref': ref, 'step': step, 'eta_at': eta if status != 'in-progress' else None})
        elif status not in bot.FINAL_STATES:
            people[name]['parked'].append({'ref': ref})

    for pr in prs:
        created = stamp(pr.get('createdAt'))
        if pr['number'] not in candidate_prs and created and now - created > dt.timedelta(days=1):
            data['anyone'].append({'text': f"[PR #{pr['number']}]({pr['url']}): review {clean(pr['title'], 70)} (open {age(pr['createdAt'], now)})",
                                  'since': pr['createdAt']})
    if (state.get('active_submission') or {}).get('commit') and bot.pending_merges(state):
        data['anyone'].append({'text': 'main has recorded merges ahead of the live bot; /submit uploads main', 'since': now.isoformat()})
    for person in people.values():
        person['todo'].sort(key=lambda r: stamp(r['since']) or now)
    data['anyone'].sort(key=lambda r: stamp(r['since']) or now)
    return data


def clean(value, limit=160):
    text = ' '.join(str(value).replace('`', "'").split())
    return text if len(text) <= limit else text[:limit - 1] + '…'


def age(since, now):
    start = stamp(since)
    if start is None:
        return '?'
    minutes = max(0, int((now - start).total_seconds() // 60))
    if minutes >= 48 * 60:
        return f'{minutes // 1440}d'
    return f'{minutes // 60}h {minutes % 60}m' if minutes >= 60 else f'{minutes}m'


def render(data, who=None, now=None, caller=None):
    now = now or stamp(data.get('now')) or dt.datetime.now(dt.timezone.utc)
    who, caller = member_name(who), member_name(caller)
    if who == 'me':
        if caller not in NAMES:
            raise ValueError('who=me requires a team caller')
        who = caller
    if who not in (None, 'all', *NAMES):
        raise ValueError('Unknown person')
    names = [who] if who in NAMES else list(NAMES)
    if caller in names:
        names.remove(caller)
        names.insert(0, caller)
    sections = []
    for name in names:
        person = data['people'][name]
        waiting = sum(not row.get('quiet_until') for row in person['todo'])
        local = '' if name == 'jun' else f" ({now.astimezone(dt.timezone(dt.timedelta(hours=OFFSETS[name]))):%H:%M} there)"
        head = f'**{name}**{local} · {waiting} waiting'
        rows = []
        for row in person['todo']:
            action = clean(row['action'], 100) + ' · ' + row['reply']
            if row.get('quiet_until'):
                action += f" (still deciding, quiet until ~{snooze.quiet_until({'until': row['quiet_until']})})"
            rows.append((clean(row['ref'], 65), action, age(row['since'], now)))
        yours = []
        for row in person['yours']:
            eta = stamp(row.get('eta_at'))
            finish = f" · done ~{eta.astimezone(snooze.KST):%H:%M} KST" if eta else ''
            yours.append(f"{clean(row['ref'], 65)} ({clean(row['step'], 70)}{finish})")
        parked = [clean(row['ref'], 65) for row in person['parked']]
        sections.append({'head': head, 'todo': rows, 'yours': yours, 'parked': parked})
    anyone = [row['text'] for row in data['anyone']]
    lists = [s[k] for s in sections for k in ('todo', 'yours', 'parked')] + [anyone]
    limits = [len(rows) for rows in lists]

    def build():
        parts = [f'📋 tasks · {now.astimezone(snooze.KST):%H:%M} KST']
        index = 0
        for section in sections:
            parts.append(section['head'])
            todo_rows = section['todo'][:limits[index]]
            hidden = len(section['todo']) - limits[index]
            index += 1
            if section['todo']:
                width = max((len(row[0]) for row in todo_rows), default=4)
                action_width = max((len(row[1]) for row in todo_rows), default=10)
                block = [f'{ref:<{width}}  {action:<{action_width}}  {waited}' for ref, action, waited in todo_rows]
                if hidden:
                    block.append(f'… and {hidden} more')
                parts.append('```\n' + '\n'.join(block) + '\n```')
            for key, title in (('yours', 'yours, nothing to do now'), ('parked', 'parked')):
                shown = section[key][:limits[index]]
                hidden = len(section[key]) - limits[index]
                index += 1
                if section[key]:
                    text = '; '.join(shown + ([f'… and {hidden} more'] if hidden else []))
                    parts.append(title + ': ' + text + (' · queue it with status:ready or close it' if key == 'parked' else ''))
            if not any(section[k] for k in ('todo', 'yours', 'parked')):
                parts.append('nothing waiting')
        if anyone:
            parts.append('**anyone**')
            parts.extend(anyone[:limits[index]])
            if len(anyone) > limits[index]:
                parts.append(f'… and {len(anyone) - limits[index]} more')
        parts.append(FOOTER)
        return '\n'.join(parts)

    message = build()
    while len(message) >= 1900:
        available = [i for i, limit in enumerate(limits) if limit]
        longest = max(available, key=lambda i: sum(len(str(row)) for row in lists[i][:limits[i]]))
        limits[longest] -= 1
        message = build()
    return message
