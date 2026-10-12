#!/usr/bin/env python3
"""Show teammates that a question is being worked on.
usage: python3 tools/meow_think.py start   post "(thinking)" in #meow and remember the message
       python3 tools/meow_think.py done    delete every remembered "(thinking)" message
The bot token is read through meowbot's own helper and never printed."""
import json, os, sys
from urllib.request import Request, urlopen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meowbot

STORE = os.path.join(meowbot.ROOT, 'data', 'meowbot', 'thinking.json')


def call(method, url, body=None):
    head = {'Authorization': f'Bot {meowbot.bot_token()}', 'User-Agent': 'meowbot (thinking note)'}
    data = None
    if body is not None:
        data = json.dumps(body).encode(); head['Content-Type'] = 'application/json'
    with urlopen(Request(url, data=data, headers=head, method=method), timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def ids():
    try: return json.load(open(STORE))
    except (OSError, ValueError): return []


def main(argv):
    channel = int(open(os.path.join(meowbot.ROOT, 'data', 'discord', 'channel.txt')).read().strip())
    base = f'https://discord.com/api/v10/channels/{channel}/messages'
    if argv[1:] == ['start']:
        if ids():
            return  # one note is enough
        msg = call('POST', base, {'content': '(thinking)', 'allowed_mentions': {'parse': []}})
        json.dump([msg['id']], open(STORE, 'w'))
    elif argv[1:] == ['done']:
        for mid in ids():
            try: call('DELETE', f'{base}/{mid}')
            except Exception: pass
        json.dump([], open(STORE, 'w'))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main(sys.argv)
