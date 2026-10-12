#!/usr/bin/env python3
"""Mirror one Discord channel into local files so Claude can read the team chat.

usage: python3 tools/discord_sync.py [--channel <id>] [--show N] [--wait SECONDS]
  token:   docs/discord.txt, bot token on the first line (git-excluded, never printed)
  channel: pass --channel once; it is remembered in data/discord/channel.txt
  output:  data/discord/<channel>.jsonl (raw, append-only), data/discord/<channel>.md (KST log)
           and data/discord/files/ (text attachments such as Discord's message.txt), all git-ignored
  prints the new messages, or the last N with --show N; --wait polls until a new message arrives
The bot needs View Channel + Read Message History on the channel and Message Content Intent turned on.
"""
import argparse, datetime, json, os, ssl, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'data', 'discord')
FILES = os.path.join(DIR, 'files')
TOKEN_FILE = os.path.join(ROOT, 'docs', 'discord.txt')
CHANNEL_FILE = os.path.join(DIR, 'channel.txt')
API = 'https://discord.com/api/v10'
UA = 'DiscordBot (https://github.com/juntegral/unsw-swarm, 1.0)'
KST = datetime.timezone(datetime.timedelta(hours=9))
INLINE_MAX = 20000
# python.org builds ship without a CA bundle; fall back to the macOS one
_CA = ssl.get_default_verify_paths().openssl_cafile
TLS = ssl.create_default_context() if os.path.exists(_CA or '') or not os.path.exists('/etc/ssl/cert.pem') \
    else ssl.create_default_context(cafile='/etc/ssl/cert.pem')


def read_token():
    try:
        with open(TOKEN_FILE) as f:
            tok = next((line.strip() for line in f if line.strip()), '')
    except OSError:
        sys.exit(f'토큰 파일을 읽지 못했다: {TOKEN_FILE}')
    if not tok:
        sys.exit(f'토큰 파일이 비어 있다: {TOKEN_FILE}')
    return tok[4:].strip() if tok.lower().startswith('bot ') else tok


def get(path, tok):
    req = urllib.request.Request(API + path, headers={'Authorization': 'Bot ' + tok, 'User-Agent': UA})
    for _ in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30, context=TLS) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    wait = float(json.load(e).get('retry_after', 1))
                except Exception:
                    wait = 1.0
                time.sleep(wait + 0.2)
                continue
            hint = {401: '토큰이 틀렸다', 403: '봇에게 이 채널을 볼 권한이 없다', 404: '채널 ID가 틀렸거나 봇이 서버에 없다'}.get(e.code, '')
            sys.exit(f'Discord API {e.code} {hint}'.strip())
        except urllib.error.URLError as e:
            sys.exit(f'Discord에 연결하지 못했다: {e.reason}')
    sys.exit('Discord API 요청 제한이 풀리지 않는다')


def pull(channel, tok, last):
    new = []
    while True:
        batch = get(f'/channels/{channel}/messages?limit=100&after={last}', tok)
        if not batch:
            return new
        batch.sort(key=lambda m: int(m['id']))
        new += batch
        last = batch[-1]['id']
        if len(batch) < 100:
            return new


def text_path(m, a):
    if not (a.get('content_type') or '').startswith('text/') or a.get('size', 0) > 2 * 1024 * 1024:
        return None
    return os.path.join(FILES, f'{m["id"]}-{os.path.basename(a.get("filename") or "file.txt")}')


def save_texts(msgs):
    # signed CDN links expire after about a day, so fetch while the link is fresh; no token is sent
    for m in msgs:
        for a in m.get('attachments', []):
            path = text_path(m, a)
            if not path or os.path.exists(path):
                continue
            try:
                req = urllib.request.Request(a['url'], headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=30, context=TLS) as r:
                    data = r.read()
            except (urllib.error.URLError, OSError, KeyError):
                continue
            os.makedirs(FILES, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)


def name(m):
    a = (m or {}).get('author') or {}
    return a.get('global_name') or a.get('username') or '?'


def render(m):
    t = datetime.datetime.fromisoformat(m['timestamp']).astimezone(KST).strftime('%m-%d %H:%M')
    if m.get('type') not in (0, 19):
        return f'- {t} ({name(m)}: 시스템 메시지 type {m.get("type")})'
    parts, blocks = [(m.get('content') or '').strip()], []
    for a in m.get('attachments', []):
        path = text_path(m, a)
        if path and os.path.exists(path):
            parts.append(f'[파일 {a.get("filename")} → {os.path.relpath(path, ROOT)}]')
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
            if len(text) > INLINE_MAX:
                text = text[:INLINE_MAX] + '\n(이하 생략, 전체는 파일 참고)'
            blocks.append('\n'.join('  > ' + line for line in text.rstrip('\n').split('\n')))
        else:
            parts.append(f'[파일 {a.get("filename")}]({a.get("url")})')
    parts += [f'[링크]({e["url"]})' for e in m.get('embeds', []) if e.get('url')]
    if m.get('sticker_items'):
        parts.append('[스티커]')
    body = ' '.join(p for p in parts if p) or '(내용 없음)'
    reply = f'↪ {name(m.get("referenced_message"))}에게 답장: ' if m.get('referenced_message') else ''
    return '\n'.join([f'- {t} **{name(m)}**: {reply}' + body.replace('\n', '\n  ')] + blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--channel')
    ap.add_argument('--show', type=int, default=0)
    ap.add_argument('--wait', type=int, default=0)
    args = ap.parse_args()
    os.makedirs(DIR, exist_ok=True)
    if args.channel:
        with open(CHANNEL_FILE, 'w') as f:
            f.write(args.channel.strip() + '\n')
    try:
        channel = open(CHANNEL_FILE).read().strip()
    except OSError:
        sys.exit('처음 한 번은 --channel <채널 ID>를 넘긴다')
    raw, log = os.path.join(DIR, f'{channel}.jsonl'), os.path.join(DIR, f'{channel}.md')
    msgs = []
    if os.path.exists(raw):
        with open(raw) as f:
            msgs = [json.loads(line) for line in f if line.strip()]
    tok = read_token()
    deadline = time.time() + args.wait
    while True:
        new = pull(channel, tok, msgs[-1]['id'] if msgs else '0')
        if new or time.time() >= deadline:
            break
        time.sleep(10)
    if new:
        with open(raw, 'a') as f:
            for m in new:
                f.write(json.dumps(m, ensure_ascii=False) + '\n')
        msgs += new
        if all(m.get('type') in (0, 19) and not m.get('content') and not m.get('attachments') for m in new):
            print('경고: 새 메시지 내용이 모두 비어 있다. 개발자 포털에서 Message Content Intent를 켰는지 확인한다.')
    save_texts(msgs)
    with open(log, 'w') as f:
        f.write('# Discord 채널 기록 (KST)\n\n' + '\n'.join(render(m) for m in msgs) + '\n')
    print(f'새 메시지 {len(new)}개, 전체 {len(msgs)}개 → {os.path.relpath(log, ROOT)}')
    for m in (msgs[-args.show:] if args.show else new):
        print(render(m))


if __name__ == '__main__':
    main()
