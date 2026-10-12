#!/usr/bin/env python3
"""DM jun from meowbot, and watch #meow for people addressing him.

  jun_dm.py --send-file <path>     send that text (1-2000 chars) to jun as a direct message
  jun_dm.py --watch [seconds]      wait until someone other than jun or the bot mentions jun or replies to him in
                                   #meow; DM him the message at once, print it and exit 0. Exit 3 on timeout.
The mirror file is refreshed here with tools/team_watch.py. Secrets: docs/discord.txt (read only by this tool).
"""
import json, os, re, ssl, subprocess, sys, time
from urllib.request import Request, urlopen

_CA = ssl.get_default_verify_paths().openssl_cafile
TLS = ssl.create_default_context() if os.path.exists(_CA or "") or not os.path.exists("/etc/ssl/cert.pem") \
    else ssl.create_default_context(cafile="/etc/ssl/cert.pem")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUN = 900000000000000005
MIRROR = os.path.join(ROOT, "data", "discord", "900000000000000004.md")
HEAD = re.compile(r"^- (\d\d-\d\d \d\d:\d\d) \*\*([^*]+)\*\*: (.*)")


def token():
    with open(os.path.join(ROOT, "docs", "discord.txt")) as source:
        t = source.read().strip().splitlines()[0].strip()
    return t[4:].strip() if t.lower().startswith("bot ") else t


def call(path, payload):
    request = Request("https://discord.com/api/v10" + path, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      headers={"Authorization": f"Bot {token()}", "Content-Type": "application/json",
                               "User-Agent": "meowbot (dm to jun)"}, method="POST")
    with urlopen(request, timeout=30, context=TLS) as response:
        return json.loads(response.read() or b"{}")


def send(text):
    text = text.strip()
    if not text or len(text) > 2000:
        raise ValueError("DM must contain 1-2000 characters")
    channel = call("/users/@me/channels", {"recipient_id": str(JUN)})["id"]
    return call(f"/channels/{channel}/messages", {"content": text})["id"]


def addressed():
    out = []
    try:
        lines = open(MIRROR, encoding="utf-8").readlines()
    except OSError:
        return out
    for line in lines:
        m = HEAD.match(line)
        if not m:
            continue
        when, who, text = m.groups()
        if who.startswith("meowbot") or who.strip().lower() in ("jun", "준싱", "juntegral"):
            continue
        if f"<@{JUN}>" in text or f"<@!{JUN}>" in text or re.match(r"↪ (jun|준싱|juntegral)", text) or re.search(r"(?i)@jun\b", text):
            out.append((when, who, text))
    return out


def watch(seconds):
    seen = len(addressed())
    end = time.time() + seconds
    while time.time() < end:
        time.sleep(45)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "team_watch.py")], capture_output=True, cwd=ROOT)
        now = addressed()
        if len(now) > seen:
            for when, who, text in now[seen:]:
                body = f"🔔 {who} mentioned you in #meow ({when} KST)\n> {text[:1700]}"
                try:
                    send(body)
                    print("DM sent:", body)
                except Exception as error:
                    print("DM FAILED:", repr(error), "|", body)
            return 0
    return 3


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--send-file":
        print(send(open(sys.argv[2], encoding="utf-8").read()))
    elif len(sys.argv) >= 2 and sys.argv[1] == "--watch":
        sys.exit(watch(int(sys.argv[2]) if len(sys.argv) > 2 else 86400))
    else:
        sys.exit(__doc__)
