#!/usr/bin/env python3
"""Hand a team member a ready-made /meow plan with one Confirm button.

usage: python3 tools/meow_offer.py --to Zhe --text-file FILE --plan JSON [--reason TEXT] [--thread ID]
                                   [--wait SECONDS] [--dry-run]
  --to      Zhe, QWQ or jun: the only person who can press Confirm
  --text-file  file with the message shown above the plan (1–1500 characters)
  --plan    the plan, in the schema /meow plans use: {"actions":[{"action":"set_state","card":39,...}]}
  --reason  for a forced plan: the member's own words, recorded as the responsibility reason.
            Without it the member is asked for one line after Confirm.
  --thread  an existing /meow thread id; default is #meow itself
  --wait    wait this long for the running bot to post it (it looks about once a minute)
This only writes a file for the bot. Nothing is applied until the named member presses Confirm in Discord;
the bot validates the plan again and re-checks the card when they do. The offer stays valid for 12 hours
(2 hours when it contains a vote or a submit).
"""
import argparse, datetime, json, os, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meow_chat
import meowbot


def build(to, text, plan, reason=None, thread=None):
    data = {'id': uuid.uuid4().hex, 'member': to, 'text': text, 'plan': plan,
            'created': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if reason is not None:
        data['reason'] = reason
    if thread is not None:
        data['thread'] = thread
    return data, meow_chat.check_offer(data, meowbot.MEMBERS)


def write(data, directory=None):
    directory = directory or meowbot.OFFER_DIR
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, data['id'] + '.json')
    with open(path + '.tmp', 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    os.replace(path + '.tmp', path)
    return path


def wait(key, seconds, directory=None):
    path = os.path.join(directory or meowbot.OFFER_DIR, 'handled', key + '.result.json')
    deadline = time.time() + seconds
    while True:
        try:
            with open(path, encoding='utf-8') as source:
                return json.load(source)
        except (OSError, ValueError):
            if time.time() >= deadline:
                return None
            time.sleep(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--to', required=True)
    ap.add_argument('--text-file', required=True)
    ap.add_argument('--plan', required=True)
    ap.add_argument('--reason')
    ap.add_argument('--thread')
    ap.add_argument('--wait', type=float, default=0)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    try:
        with open(a.text_file, encoding='utf-8') as source:
            text = source.read().strip()
        data, offer = build(a.to, text, json.loads(a.plan), a.reason, a.thread)
    except (OSError, ValueError) as exc:
        ap.exit(1, f'Offer refused: {exc}\n')
    who = meowbot.MEMBERS[offer['member']]
    force = any(action.get('force') for action in offer['plan']['actions'])
    steps = 'one Confirm' if offer['reason'] or not force else 'Confirm, then a one-line reason'
    print(f"offer {data['id']} for {who}: {steps}, valid {offer['ttl'] // 3600} h")
    if a.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    write(data)
    if a.wait:
        result = wait(data['id'], a.wait)
        if not result:
            ap.exit(1, 'not posted yet; the bot may be down or still on an earlier step\n')
        if result.get('status') != 'posted':
            ap.exit(1, f"refused by the bot: {result.get('error')}\n")
        print('posted')
    else:
        print('written; the bot posts it within about a minute')


if __name__ == '__main__':
    main()
