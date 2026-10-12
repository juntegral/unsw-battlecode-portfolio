#!/usr/bin/env python3
"""Read-only ladder collection and conservative poll-to-poll attribution."""
import argparse
import fcntl
import gzip
import json
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/analysis/ladder'
RAW = ROOT / 'data/online/ladder'
KST = ZoneInfo('Asia/Seoul')
COLLECT_FDS = []
FIELDS = ('id ranked opponentId opponent opponentElo eloChange results wins losses outcome replayId at').split()

def read_lines(path):
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def atomic(path, value, jsonl=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    text = ''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in value) if jsonl else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    with tmp.open('w') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)

def online(*args):
    p = subprocess.run(['node', str(ROOT / 'tools/online.js'), *map(str, args)], cwd=ROOT, capture_output=True, text=True, timeout=600, pass_fds=tuple(COLLECT_FDS))
    if p.returncode: raise RuntimeError(f'online {args[0]} failed (exit {p.returncode})')
    return p.stdout

def finished(b):
    return bool(b.get('ranked') and b.get('outcome') in ('win', 'loss', 'draw') and b.get('results') and all(x in ('win', 'loss', 'draw') for x in b['results']))

def replay_valid(path, meta):
    """A saved replay is whole: the advertised byte size matches and, if it is gzip, it reads to the end. The server sends replays unzipped, so a plain file is judged by its size alone and needs one."""
    if not path.exists() or not path.stat().st_size:return False
    expected=(meta.get('replay') or {}).get('bytes')
    if expected is not None and path.stat().st_size!=expected:return False
    with path.open('rb') as f:zipped=f.read(2)==b'\x1f\x8b'
    if not zipped:return expected is not None
    try:
        with gzip.open(path,'rb') as f:
            while f.read(1024*1024):pass
        return True
    except (OSError,EOFError):return False

def local_games(folder):
    idx = folder / 'index.json'
    if not idx.exists(): return []
    result = []
    for g in json.loads(idx.read_text()).get('games', []):
        gid = g['gameId']; meta = folder / f'game-{gid}.json'; rp = folder / f'M{gid}.replay'
        if meta.exists():
            j = json.loads(meta.read_text())
            if j.get('status') in ('completed', 'draw'):
                result.append(dict(id=gid, map=j.get('mapName'), complete=replay_valid(rp,j)))
    return sorted(result, key=lambda g: g['id'])

def complete(b, games):
    return len(games) == len(b['results']) and all(g['complete'] for g in games)

def submission_for(b, polls):
    if not b.get('at'): return None
    at = datetime.fromisoformat(b['at'].replace('Z', '+00:00'))
    for prev, curr in zip(polls, polls[1:]):
        if datetime.fromisoformat(prev['time']) < at <= datetime.fromisoformat(curr['time']):
            before = {s['id']: s for s in prev['submissions']}
            rose = []
            for s in curr['submissions']:
                if s['id'] not in before: continue
                a = sum(s.get(k, 0) or 0 for k in ('wins','losses','draws'))
                z = sum(before[s['id']].get(k, 0) or 0 for k in ('wins','losses','draws'))
                if a > z: rose.append(s['id'])
            return rose[0] if len(rose) == 1 else None
    return None

def recheck(out=OUT, raw=RAW):
    """Refresh each ledger battle's games and complete flag from the files on disk. No server call."""
    battles = read_lines(out / 'battles.jsonl'); changed = 0
    for b in battles:
        games = local_games(raw / str(b['id'])); done = complete(b, games)
        if games and (done != b.get('complete') or len(games) != len(b.get('games') or [])):
            b.update(games=[{k:g[k] for k in ('id','map')} for g in games], complete=done); changed += 1
    if changed: atomic(out / 'battles.jsonl', battles, True)
    return dict(battles=len(battles), changed=changed, incomplete=sum(not b.get('complete') for b in battles))

def poll(fetch=online, now=None, raw=RAW):
    subs = json.loads(fetch('submissions', '--all', '--json'))
    table = json.loads((raw / 'submissions.json').read_text()) if (raw / 'submissions.json').exists() else {}
    table.update({str(s['id']): {k: s.get(k) for k in ('version','name','description','sourceHash','uploadedAt')} for s in subs if s.get('id') is not None})
    atomic(raw / 'submissions.json', table)
    active = next((s for s in subs if s.get('status') == 'active'), None)
    stamp = now or datetime.now(KST).isoformat()
    record = dict(time=stamp, active={k: active.get(k) for k in ('id','version','name','sourceHash','rating')} if active else None,
                  submissions=[{k: s.get(k, 0) if k in ('wins','losses','draws') else s.get(k) for k in ('id','wins','losses','draws')} for s in subs])
    rows = read_lines(raw / 'active.jsonl'); rows.append(record)
    atomic(raw / 'active.jsonl', rows, True)
    return rows

def collect(fetch=online, out=OUT, raw=RAW, sleep=time.sleep, polls=None):
    atomic(out / 'new-this-hour.json', [])
    polls = polls if polls is not None else poll(fetch, raw=raw)
    battles = [b for b in json.loads(fetch('battles', '--limit', '200', '--json')) if finished(b)]
    prior = {b['id']: b for b in read_lines(out / 'battles.jsonl')}
    added=[]; downloaded=0; attempts=0; errors=0
    for b in sorted(battles, key=lambda x: (x.get('at') or '', x['id'])):
        folder = raw / str(b['id']); games = local_games(folder)
        if not complete(b, games) and attempts < 150:
            if attempts: sleep(1)
            attempts += 1
            before = {g['id'] for g in games if g['complete']}
            for g in games:
                rp=folder/f'M{g["id"]}.replay'
                if not g['complete'] and rp.exists():rp.rename(rp.with_name(rp.name+f'.incomplete-{time.time_ns()}'))
            try: fetch('download', b['id'], '--out', f'ladder/{b["id"]}', '--no-events', '--purpose', 'ladder analysis')
            except (RuntimeError, subprocess.TimeoutExpired): errors += 1
            games = local_games(folder)
            downloaded += sum(g['complete'] and g['id'] not in before for g in games)
        row = {k: b.get(k) for k in FIELDS}
        row.update(at_kst=datetime.fromisoformat(b['at'].replace('Z','+00:00')).astimezone(KST).isoformat() if b.get('at') else None,
                   games=[{k:g[k] for k in ('id','map')} for g in games], complete=complete(b,games), our_submission=submission_for(b,polls))
        if row['complete'] and (b['id'] not in prior or not prior[b['id']].get('complete')): added.append(b['id'])
        prior[b['id']] = row
        atomic(out / 'battles.jsonl', sorted(prior.values(),key=lambda x:(x.get('at') or '',x['id'])), True)
    listed = {b['id'] for b in battles}
    for b in prior.values():
        if b['id'] not in listed and not b.get('complete'):
            games = local_games(raw / str(b['id']))
            if games and complete(b, games): b.update(games=[{k:g[k] for k in ('id','map')} for g in games], complete=True); added.append(b['id'])
    for b in prior.values(): b['our_submission'] = submission_for(b, polls)
    atomic(out / 'battles.jsonl', sorted(prior.values(),key=lambda x:(x.get('at') or '',x['id'])), True)
    atomic(out / 'new-this-hour.json', added)
    return dict(ranked=len(battles), attempts=attempts, added=len(added), downloaded_games=downloaded, incomplete=sum(not b.get('complete') for b in prior.values()), errors=errors,
                bytes=sum(p.stat().st_size for p in raw.rglob('*') if p.is_file()))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--poll-only',action='store_true'); ap.add_argument('--recheck',action='store_true'); args=ap.parse_args()
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW / '.collect.lock').open('a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: print('collector: already running'); return
        COLLECT_FDS.append(lock.fileno())
        if args.recheck: print('collector: recheck '+json.dumps(recheck(),ensure_ascii=False))
        elif args.poll_only:
            polls=poll(); print(f'collector: poll saved ({len(polls)} polls)')
        else: print('collector: '+json.dumps(collect(),ensure_ascii=False))
if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'collector: failed ({type(e).__name__}: {e})');raise SystemExit(1)
