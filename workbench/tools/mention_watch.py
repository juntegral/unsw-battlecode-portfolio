#!/usr/bin/env python3
"""Wake-up watcher, no model: exits when a teammate mentions or replies to meowbot in #meow.
usage: python3 tools/mention_watch.py [seconds, default 28800] [poll seconds, default 90]
It refreshes the mirror with team_watch.py and looks for a new line by someone other than the bot and jun that
carries the bot's mention or a reply arrow to it."""
import os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "data/discord/900000000000000004.md")
BOT = "900000000000000001"
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 28800
POLL = float(sys.argv[2]) if len(sys.argv) > 2 else 90
PAT = re.compile(r"^- \S+ \S+ \*\*(?!meowbot|준싱|jun)([^*]+)\*\*: .*(<@%s>|↪ meowbot)" % BOT)


def hits():
    try:
        return [l for l in open(MIRROR, encoding="utf-8") if PAT.match(l)]
    except OSError:
        return []


seen = len(hits())
end = time.time() + LIMIT
while time.time() < end:
    time.sleep(POLL)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/team_watch.py")], cwd=ROOT, capture_output=True, timeout=300)
    now = hits()
    if len(now) > seen:
        print("WAKE: a teammate called the bot:", now[-1].strip()[:400])
        sys.exit(0)
print("no call in the window")
