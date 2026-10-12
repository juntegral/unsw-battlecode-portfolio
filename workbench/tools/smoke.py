#!/usr/bin/env python3
"""Online smoke orchestration; all API operations use the existing Node tools."""
from member_names import member_state
import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/online'
STATE = DATA / 'smoke'
FINISHED = {'completed', 'draw'}
FREEZE = datetime(2026, 10, 9, 5, 30, tzinfo=timezone.utc)
# SMOKE_RESTORE_BEST=0 restores exactly the submission that was live before the test.
RESTORE_SWITCH = 'SMOKE_RESTORE_BEST'
RESTORABLE = {'active', 'idle'}


def check_freeze():
    if datetime.now(timezone.utc) >= FREEZE:
        raise RuntimeError('Frozen after 2026-10-09 14:30 KST; no mutations allowed')


def safe(text):
    text = re.sub(r'bc_[A-Za-z0-9_-]+', '[REDACTED]', str(text))
    return re.sub(r'(?i)(bearer\s+)[^\s"\']+', r'\1[REDACTED]', text)


def run(tool, *args, json_output=False):
    cmd = ['node', str(ROOT / 'tools' / tool), *map(str, args)]
    if json_output:
        cmd.append('--json')
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{tool} {args[0]} failed (exit {result.returncode}): ' + safe(result.stderr or result.stdout))
    if json_output:
        return json.loads(result.stdout)
    return safe(result.stdout)


def label(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', value):
        raise argparse.ArgumentTypeError('label must be 1–80 letters, digits, dots, underscores or hyphens')
    return value


def state_path(name, baseline=False):
    return STATE / f"{'baseline-' if baseline else ''}{name}.json"


def save(state):
    STATE.mkdir(parents=True, exist_ok=True)
    path = state_path(state['label'], state['kind'] == 'baseline')
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(member_state(state), indent=2) + '\n')
    tmp.replace(path)


def load(name, baseline=False):
    path = state_path(name, baseline)
    if not path.exists():
        raise RuntimeError(f'No state: {path.relative_to(ROOT)}')
    return member_state(json.loads(path.read_text()))


def active():
    text = run('submit.js', 'active').strip()
    match = re.match(r'^(\d+)\s+(.+?)\s+\(', text)
    if not match:
        raise RuntimeError('No readable active submission; a rollback target is required')
    return {'id': int(match[1]), 'name': match[2]}


def upload_description(args, current, opponents):
    explicit = getattr(args, 'desc', None)
    if explicit is not None:
        return explicit[:190]
    live = f"live {current['id']}"
    try:
        submissions = run('subs.js', 'list', json_output=True)
        match = next(sub for sub in submissions if sub['id'] == current['id'])
        if match.get('version') is not None:
            if args.command == 'pair' or getattr(args, 'pair', False):
                current['version'] = match['version']
            live = f"v{match['version']}"
    except (RuntimeError, ValueError, KeyError, TypeError, StopIteration, OSError):
        pass
    ref = getattr(args, 'ref', None) or args.name
    return f"TEST. {live} main + {ref}. vs {', '.join(o['name'] for o in opponents)}"[:190]


def pair_versions(state):
    try:
        submissions = run('subs.js', 'list', '--last', '40', json_output=True)
        versions = {sub['id']: sub['version'] for sub in submissions if sub.get('version') is not None}
        hashes = {sub['id']: sub['sourceHash'] for sub in submissions
                  if isinstance(sub.get('sourceHash'), str) and sub['sourceHash']}
        for sub in [state['rollback']] + [h['submission'] for h in state['halves'].values()]:
            if sub is not None and sub['id'] in versions:
                sub['version'] = versions[sub['id']]
            if sub is not None and sub['id'] in hashes:
                sub['source_hash'] = hashes[sub['id']]
    except (RuntimeError, ValueError, KeyError, TypeError, OSError):
        pass


def opponent(spec):
    if spec.isdecimal():
        tid = int(spec)
        if tid < 1:
            raise RuntimeError('Opponent id must be positive')
    else:
        board = run('online.js', 'leaderboard', '--top', '1000000', json_output=True)
        matches = [t for t in board['rows'] if t['name'].casefold() == spec.casefold()]
        if len(matches) != 1:
            raise RuntimeError(f'Opponent name {spec!r}: {len(matches)} matches in leaderboard; use an exact numeric id (unranked DEV teams may be absent)')
        tid = matches[0]['id']
    team = run('online.js', 'team', tid, json_output=True)['team']
    if not team.get('dev'):
        raise RuntimeError('Opponent is not marked DEV; refusing to spend the normal allowance')
    if not team.get('hasBot') or team.get('settings', {}).get('unranked') is False:
        raise RuntimeError('Opponent cannot accept unranked games')
    return {'id': team['id'], 'name': team['name'], 'dev': True}


def map_set(spec):
    pool = sorted((m for m in run('online.js', 'maps', json_output=True) if m.get('active') and not m.get('private')), key=lambda m: m['id'])
    if spec == 'all':
        chosen = pool
    else:
        norm = lambda s: re.sub('[^a-z0-9]', '', str(s).lower())
        chosen = []
        for part in spec.split(','):
            part = part.strip()
            matches = [m for m in pool if (str(m['id']) == part if part.isdecimal() else norm(m['name']) == norm(part))]
            if len(matches) != 1:
                raise RuntimeError(f'Unknown or ambiguous map: {part!r}')
            if matches[0] not in chosen:
                chosen.append(matches[0])
    if not chosen:
        raise RuntimeError('No public active maps selected')
    return [{'id': m['id'], 'name': m['name']} for m in chosen]


def batches(maps, games):
    ids = [m['id'] for m in maps]
    width = min(len(ids), 60)
    return [[ids[i % len(ids)] for i in range(start, min(start + width, games))] for start in range(0, games, width)]


def rollback_command(state):
    return f"node tools/submit.js activate {state['rollback']['id']} --confirm"


def restore_best():
    return os.environ.get(RESTORE_SWITCH, '1').strip().lower() not in {'0', 'off', 'false', 'no'}


def rating_of(sub):
    value = sub.get('rating')
    return value if type(value) in (int, float) and math.isfinite(value) else None


def choose_restore(state):
    """Record and return what to activate after a test: the best-rated copy of the code that was live before it.
    Whatever cannot be verified keeps the original submission."""
    original = state['rollback']
    keep = {'id': original['id'], 'name': original.get('name'), 'version': original.get('version'), 'rating': None}
    choice = dict(keep, rule='exact', reason='', source_hash=None, original_rating=None, candidates=[])

    def pick():
        if not restore_best():
            return f'{RESTORE_SWITCH} is off; exact restore'
        choice['rule'] = 'best-rated'
        try:
            subs = run('online.js', 'submissions', '--all', json_output=True)
        except (RuntimeError, ValueError, OSError):
            return 'submissions list unreadable; original kept'
        if (not isinstance(subs, list) or not all(isinstance(s, dict) and type(s.get('id')) is int for s in subs)
                or len({s['id'] for s in subs}) != len(subs)):
            return 'submissions list malformed; original kept'
        mine = next((s for s in subs if s['id'] == original['id']), None)
        if mine is None:
            return 'original is not in the submissions list; original kept'
        code = mine.get('sourceHash')
        if not isinstance(code, str) or not code.strip():
            return 'original has no source hash; original kept'
        copies = [s for s in subs if s.get('sourceHash') == code]
        choice.update(source_hash=code, original_rating=rating_of(mine), rating=rating_of(mine),
                      candidates=[{k: s.get(k) for k in ('id', 'name', 'version', 'rating', 'status', 'wins', 'losses')}
                                  for s in copies])
        if mine.get('version') is not None:
            choice['version'] = mine['version']
        if choice['original_rating'] is None:
            return 'original has no readable rating; original kept'
        usable = [s for s in copies if s['id'] != original['id'] and s.get('status') in RESTORABLE
                  and rating_of(s) is not None]
        if not usable:
            return 'no other usable copy of the same code; original kept'
        best = max(usable, key=lambda s: (rating_of(s), -s['id']))
        if rating_of(best) == choice['original_rating']:
            return f"tie with {best['id']}; original kept"
        if rating_of(best) < choice['original_rating']:
            return 'original is the best-rated copy'
        choice.update(id=best['id'], name=best.get('name'), version=best.get('version'), rating=rating_of(best))
        return 'higher-rated copy of the same code'

    try:
        choice['reason'] = pick()
    except Exception as exc:
        choice.update(keep, reason=f'restore choice failed ({type(exc).__name__}); original kept')
    choice['chosen_at'] = datetime.now(timezone.utc).isoformat()
    state['restore'] = choice
    save(state)
    return choice


def activate_restore(state, target, live_id):
    """Swap to the chosen target; a test bot that is itself the chosen copy stays live."""
    if target['id'] == live_id and target['id'] != state['rollback']['id']:
        return f"No swap: {target['id']} is live and is the chosen copy of the same code"
    return swap('activate', target['id'], '--confirm')


def restored_ids(state):
    return {state['rollback']['id'], (state.get('restore') or {}).get('id', state['rollback']['id'])}


def compatible(candidate, baseline):
    return (candidate['opponent']['id'] == baseline['opponent']['id'] and candidate['batches'] == baseline['batches'] and candidate['rollback']['id'] == baseline['submission']['id'] and candidate['our_team'] == baseline['our_team'])


def prepare(args):
    if args.command != 'baseline' and not (Path(args.botdir) / 'bot.toml').is_file():
        raise RuntimeError('botdir must contain bot.toml')
    current = active()
    opp = opponent(args.opp)
    maps = map_set(args.maps)
    mine = run('online.js', 'team', json_output=True)['team']
    if mine['id'] == opp['id']:
        raise RuntimeError('Cannot request our own team')
    return {'schema': 1, 'kind': 'baseline' if args.command == 'baseline' else 'candidate', 'label': args.name,
            'created_at': datetime.now(timezone.utc).isoformat(), 'rollback': current,
            'description': upload_description(args, current, [opp]) if args.command != 'baseline' else None,
            'submission': current if args.command == 'baseline' else None, 'opponent': opp,
            'our_team': mine['id'], 'maps': maps, 'batches': batches(maps, args.games),
            'battle_ids': [], 'requests': [], 'phase': 'prepared', 'baseline_label': args.baseline,
            'download_dir': f"smoke/{'baseline-' if args.command == 'baseline' else ''}{args.name}/replays"}


def plan(args, state):
    allowance = run('online.js', 'tickets', json_output=True)
    print(f"Active / rollback target: {state['rollback']['id']} {safe(state['rollback']['name'])}")
    print(f"Opponent: {state['opponent']['id']} {safe(state['opponent']['name'])}; DEV verified via team.dev (no DEV flag)")
    print(f"Unranked: {sum(map(len, state['batches']))} games in {len(state['batches'])} sequential requests; normal cost 0")
    print('Maps: ' + ', '.join(f"{m['id']}:{safe(m['name'])}" for m in state['maps']))
    print(f"Ticket estimate: DEV {allowance['dev']['remaining']}/60 remaining; normal {allowance['normal']['remaining']}/60 (rolling hour, estimate only)")
    print('Requests stop on insufficient allowance or failure; pending batches are polled before the next request.')
    if state['kind'] == 'candidate':
        print('Upload: ' + shlex.join(['node', 'tools/submit.js', 'upload', args.botdir, '--name', args.name, '--desc', state['description'], '--confirm']))
        path = state_path(args.baseline, True)
        if not path.exists():
            print(f'Baseline missing: baseline-{args.baseline}.json; record it once with baseline --name {args.baseline} --opp {args.opp} --confirm')
        else:
            base = load(args.baseline, True)
            print('Baseline: ' + ('compatible' if compatible(state, base) else 'INCOMPATIBLE (submission, team, opponent or map schedule differs)'))
    for batch in state['batches']:
        print(f"Request: node tools/online.js request {state['opponent']['id']} --maps {','.join(map(str, batch))} --purpose 'smoke {args.name}' --confirm --expect-active <{'current' if state['kind'] == 'baseline' else 'new'} id>")
    print('Rollback: ' + rollback_command(state))
    print('Plan only; no upload, activation or request executed.')



def pair_prepare(args):
    check_freeze()
    if not getattr(args, 'old_only', False) and not (Path(args.botdir) / 'bot.toml').is_file():
        raise RuntimeError('botdir must contain bot.toml')
    current = active()
    mine = run('online.js', 'team', json_output=True)['team']
    if args.top:
        board = run('online.js', 'leaderboard', '--eligible', '--top', '1000000', json_output=True)
        ids = [t['id'] for t in sorted(board['rows'], key=lambda t: t['elo'], reverse=True)
               if t['id'] != mine['id'] and t['elo'] > mine['elo']][:args.top]
        if len(ids) != args.top:
            raise RuntimeError('Not enough eligible teams above us by elo')
    else:
        parts = (args.opp or '').split(',')
        if not all(p.strip().isdecimal() and int(p) > 0 for p in parts):
            raise RuntimeError('pair needs --opp positive ids or --top N')
        ids = list(dict.fromkeys(int(p.strip()) for p in parts))
    opponents = []
    for tid in ids:
        team = run('online.js', 'team', tid, json_output=True)['team']
        if tid == mine['id'] or not team.get('hasBot') or team.get('settings', {}).get('unranked') is False:
            raise RuntimeError(f'Opponent {tid} cannot accept unranked games')
        opponents.append({'id': tid, 'name': team['name'], 'dev': bool(team.get('dev'))})
    maps = map_set(args.maps)
    new_only = bool(getattr(args, 'new_only', False))
    old_only = bool(getattr(args, 'old_only', False))
    if old_only and new_only:
        raise RuntimeError('--old-only cannot be combined with --new-only')
    half = args.games if new_only or old_only else args.games // 2
    if half < len(opponents):
        raise RuntimeError('--games must allow at least one game per opponent in each half')
    schedule = []
    for i, opp in enumerate(opponents):
        count = half // len(opponents) + (i < half % len(opponents))
        schedule.extend({'opponent': opp, 'maps': batch} for batch in batches(maps, count))
    halves = {}
    for key, sub in (('old', current), ('new', None)):
        halves[key] = {'schema': 1, 'kind': 'pair-half', 'label': args.name, 'submission': sub,
                       'our_team': mine['id'], 'opponents': opponents, 'batches': schedule,
                       'battle_ids': [], 'requests': [],
                       'download_dir': f'smoke/{args.name}/{key}/replays'}
    return {'schema': 2, 'kind': 'pair', 'label': args.name, 'created_at': datetime.now(timezone.utc).isoformat(),
            'rollback': current, 'active_submission': current, 'active_verified': True,
            'our_team': mine['id'], 'opponents': opponents, 'maps': maps, 'schedule': schedule,
            'ref': getattr(args, 'ref', None) or args.name,
            'description': None if old_only else upload_description(args, current, opponents),
            'planned_total': half * (1 if new_only or old_only else 2), 'new_only': new_only, 'old_only': old_only, 'halves': halves, 'phase': 'prepared',
            'rollback_command': rollback_command({'rollback': current})}


def pair_cost(state):
    sides = 1 if state.get('new_only') or state.get('old_only') else 2
    dev = sides * sum(len(b['maps']) for b in state['schedule'] if b['opponent']['dev'])
    return state['planned_total'] - dev, dev


def pair_budget(state):
    allowance = run('online.js', 'tickets', json_output=True)
    normal_cost, dev_cost = pair_cost(state)
    if allowance['normal']['remaining'] < normal_cost:
        raise RuntimeError('Insufficient normal allowance estimate for the planned total; nothing started')
    if allowance['dev']['remaining'] < dev_cost:
        raise RuntimeError('Insufficient DEV allowance estimate for the planned DEV games')
    return allowance


def pair_plan(args, state):
    allowance = run('online.js', 'tickets', json_output=True)
    new_only = state.get('new_only')
    normal_cost, dev_cost = pair_cost(state)
    old_only = state.get('old_only')
    per_bot = state['planned_total'] // (1 if new_only or old_only else 2)
    print(f"Pair: {state['planned_total']} games, {per_bot} per bot (requested budget {args.games})"
          + ('; live bot only, no upload or swap' if old_only else '; new bot only, the live bot is not replayed' if new_only else ''))
    print(f"Active / rollback: {state['rollback']['id']} {safe(state['rollback']['name'])}")
    print(f"Normal allowance estimate: {allowance['normal']['remaining']}/60; required {normal_cost}; "
          + ('sufficient' if allowance['normal']['remaining'] >= normal_cost else 'REFUSE to start'))
    print(f"DEV allowance estimate: {allowance['dev']['remaining']}/60; required {dev_cost}")
    for opp in state['opponents']:
        ids = [mid for b in state['schedule'] if b['opponent']['id'] == opp['id'] for mid in b['maps']]
        print(f"{'Live bot' if old_only else 'New bot' if new_only else 'Both bots'} vs {opp['id']} {safe(opp['name'])}: {len(ids)} games; maps {','.join(map(str, ids))}")
    if old_only:
        print('Order: live requests → wait ALL; no upload, swap or rollback')
        print('Plan only; no requests executed.')
        return
    print('Order: ' + ('' if new_only else 'old requests → wait ALL → ') + 'upload / verify new → ' + ('' if new_only else 'same ') + 'requests → wait ALL → rollback / verify')
    print('Upload: ' + shlex.join(['node', 'tools/submit.js', 'upload', args.botdir, '--name', args.name, '--desc', state['description'], '--confirm']))
    print('Rollback: ' + state['rollback_command'])
    print('Restore rule: ' + ('the best-rated copy of the same code as the live bot' if restore_best()
                              else f'exactly the live bot ({RESTORE_SWITCH} is off)'))
    print('Freeze: 2026-10-09 14:30 KST. Plan only; no upload, activation or request executed.')


def allow_pending():
    return os.environ.get('SMOKE_ALLOW_PENDING', '0').strip().lower() in {'1', 'on', 'true', 'yes'}


def no_pending():
    if allow_pending():
        return
    recent = run('online.js', 'battles', '--limit', '200', json_output=True)
    if any(b.get('outcome') not in {'win', 'loss', 'draw'} or 'pending' in (b.get('results') or []) for b in recent):
        raise RuntimeError('Our battles are live or pending; refusing to swap or start')


def wait_no_pending(seconds=900):
    """Other teams' battles against us can be live at a swap; wait for them instead of stopping."""
    deadline = time.monotonic() + seconds
    while True:
        try:
            return no_pending()
        except RuntimeError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(15)


def swap(*args, before_retry=None):
    deadline = time.monotonic() + 900
    if allow_pending() and args and args[0] in ('upload', 'activate'):
        args = (*args, '--allow-pending' if args[0] == 'upload' else '--force')
    while True:
        try:
            return run('submit.js', *args)
        except RuntimeError as exc:
            if 'live or pending' not in str(exc) or time.monotonic() >= deadline:
                raise
            time.sleep(15)
            if time.monotonic() >= deadline:
                raise
            if before_retry is not None:
                before_retry()


def verified_active(state, expected):
    current = active()
    state.update(active_submission=current, active_verified=True)
    save(state)
    if current['id'] != expected:
        raise RuntimeError('Active submission identity not verified')
    return current


def pair_time_left(state):
    remaining = (datetime.fromisoformat(state['expires_at']) - datetime.now(timezone.utc)).total_seconds()
    if remaining <= 0:
        raise RuntimeError('Pair hour expired; no further requests or uploads')
    return remaining


def pair_half(args, state, key):
    half = state['halves'][key]
    state['phase'] = key + '-games'
    save(state)
    for batch in state['schedule']:
        check_freeze()
        pair_time_left(state)
        verified_active(state, half['submission']['id'])
        attempt = {'opponent': batch['opponent']['id'], 'maps': batch['maps'], 'status': 'in-flight',
                   'requested_at': datetime.now(timezone.utc).isoformat()}
        half['requests'].append(attempt)
        save(state)
        check_freeze()
        pair_time_left(state)
        output = run('online.js', 'request', attempt['opponent'], '--maps', ','.join(map(str, attempt['maps'])),
                     '--purpose', f'pair {args.name} {key}', '--confirm', '--expect-active', half['submission']['id'])
        found = re.findall(r'(?:신청됨|requested)\s+.*?:\s*201\s+ids\s+([\d,]+)', output)
        ids = list(dict.fromkeys(int(v) for group in found for v in group.split(',')))
        duplicate = bool(set(ids) & set(half['battle_ids']))
        half['battle_ids'].extend(ids)
        attempt.update(status='accepted' if len(ids) == len(attempt['maps']) and not duplicate else 'uncertain', ids=ids)
        save(state)
        if attempt['status'] != 'accepted':
            raise RuntimeError('Request acceptance/count not verified; inspect requests.jsonl before retrying')
        wait_batch(half, ids, min(args.wait_seconds, pair_time_left(state)))
    wait_batch(half, half['battle_ids'], min(args.wait_seconds, pair_time_left(state)))
    half['phase'] = 'finished'
    save(state)


def pair_execute(args, state):
    check_freeze()
    if state_path(args.name).exists():
        raise RuntimeError('State already exists; refusing duplicate pair')
    pair_budget(state)
    if not state.get('old_only'):
        no_pending()
    started = datetime.now(timezone.utc)
    state.update(started_at=started.isoformat(), expires_at=(started + timedelta(hours=1)).isoformat())
    save(state)
    try:
        if state.get('old_only'):
            pair_versions(state)
            save(state)
        verified_active(state, state['rollback']['id'])
        if state.get('new_only'):
            state['halves']['old']['phase'] = 'skipped'
        else:
            pair_half(args, state, 'old')
        if state.get('old_only'):
            state['halves']['new']['phase'] = 'skipped'
            state.update(phase='rolled-back', rollback_required=False)
            save(state)
            print('Live bot games finished; no upload, swap or rollback performed.')
            return
        check_freeze()
        pair_time_left(state)
        wait_no_pending()
        verified_active(state, state['rollback']['id'])
        state.update(phase='uploading', active_verified=False, rollback_required=True)
        save(state)
        check_freeze()
        pair_time_left(state)
        swap('upload', args.botdir, '--name', args.name, '--desc', state['description'], '--confirm',
             before_retry=lambda: (check_freeze(), pair_time_left(state)))
        new = active()
        state.update(active_submission=new, active_verified=True)
        save(state)
        if new['id'] == state['rollback']['id'] or new['name'] != args.name:
            raise RuntimeError('Uploaded submission identity not verified')
        state['halves']['new']['submission'] = new
        pair_versions(state)
        save(state)
        pair_half(args, state, 'new')
        check_freeze()
        wait_no_pending()
        verified_active(state, new['id'])
        target = choose_restore(state)
        state.update(phase='rolling-back', active_verified=False)
        save(state)
        check_freeze()
        activate_restore(state, target, new['id'])
        verified_active(state, target['id'])
        state.update(phase='rolled-back', rollback_required=False)
        save(state)
        print(f"Pair finished; rollback verified: {target['id']} ({target['reason']}; live before the test: "
              f"{state['rollback']['id']}); report {args.name}")
    except (Exception, KeyboardInterrupt) as exc:
        try:
            current = active()
            state.update(active_submission=current, active_verified=True,
                         rollback_required=not state.get('old_only') and current['id'] not in restored_ids(state))
        except Exception as probe:
            state.update(active_verified=False, active_probe_error=safe(probe), rollback_required=not state.get('old_only'))
        state.update(phase='failed', error=safe(exc) or 'Interrupted')
        print('STOPPED: ' + safe(exc), file=sys.stderr)
        print('Active state: ' + safe(json.dumps(state['active_submission']))
              + (' (verified)' if state['active_verified'] else ' (last observation; verification unavailable)'), file=sys.stderr)
        if state['rollback_required']:
            print('ROLLBACK REQUIRED (wait for ALL pending battles to finish):\n' + state['rollback_command'], file=sys.stderr)
        try:
            save(state)
        except OSError as write_error:
            print('STATE WRITE FAILED: ' + safe(write_error), file=sys.stderr)
        raise RuntimeError('Pair stopped safely; see state file for active status and rollback command') from exc

def details(state):
    return [run('online.js', 'battle', bid, json_output=True) for bid in state['battle_ids']]


def done(detail):
    return detail['match'].get('status') in FINISHED and bool(detail.get('games')) and all(g.get('status') in FINISHED for g in detail['games'])


def wait_batch(state, ids, timeout):
    deadline = time.monotonic() + timeout
    while True:
        if all(done(run('online.js', 'battle', bid, json_output=True)) for bid in ids):
            return
        if time.monotonic() >= deadline:
            raise RuntimeError('Timed out waiting for previous batch; no further requests made')
        time.sleep(min(10, max(0, deadline - time.monotonic())))


def execute(args, state):
    check_freeze()
    path = state_path(args.name, state['kind'] == 'baseline')
    if path.exists():
        raise RuntimeError('State already exists; refusing to overwrite or request duplicate games')
    allowance = run('online.js', 'tickets', json_output=True)
    if allowance['dev']['remaining'] < sum(map(len, state['batches'])):
        raise RuntimeError('Insufficient DEV estimate for the full run; nothing uploaded or requested')
    save(state)
    try:
        if state['kind'] == 'candidate':
            state['phase'] = 'uploading'
            save(state)
            check_freeze()
            run('submit.js', 'upload', args.botdir, '--name', args.name, '--desc', state['description'], '--confirm')
            new = active()
            if new['id'] == state['rollback']['id'] or new['name'] != args.name:
                raise RuntimeError('Uploaded submission identity not verified')
            state['submission'] = new
            save(state)
        for batch in state['batches']:
            check_freeze()
            if active()['id'] != state['submission']['id']:
                raise RuntimeError('Active submission changed; refusing next request')
            state['phase'] = 'requesting'
            attempt = {'maps': batch, 'status': 'in-flight'}
            state['requests'].append(attempt)
            save(state)
            output = run('online.js', 'request', state['opponent']['id'], '--maps', ','.join(map(str, batch)), '--purpose', f'smoke {args.name}', '--confirm', '--expect-active', state['submission']['id'])
            found = re.findall(r'(?:신청됨|requested)\s+.*?:\s*201\s+ids\s+([\d,]+)', output)
            ids = list(dict.fromkeys(int(v) for group in found for v in group.split(',')))
            state['battle_ids'].extend(ids)
            attempt.update(status='accepted' if len(ids) == len(batch) else 'uncertain', ids=ids)
            save(state)
            if len(ids) != len(batch):
                raise RuntimeError('Request acceptance/count not verified; inspect requests.jsonl before retrying')
            if len(state['requests']) < len(state['batches']):
                wait_batch(state, ids, args.wait_seconds)
        state['phase'] = 'requested'
        save(state)
        print(f"Saved {len(state['battle_ids'])} battle ids: {path.relative_to(ROOT)}")
    except Exception as exc:
        state.update(phase='failed', error=safe(exc))
        save(state)
        print('Stopped. Exact rollback command: ' + rollback_command(state), file=sys.stderr)
        raise


def table(games):
    totals = defaultdict(lambda: [0, 0, 0, 0])
    for game in games:
        row = totals[game.get('mapName', '?')]
        winner, side = game.get('winner'), game.get('ourSide')
        row[3 if side is None else 2 if not winner else 0 if winner.upper() == side.upper() else 1] += 1
    lines = ['| Map | W | L | D | Unknown |', '| --- | --- | --- | --- | --- |']
    for name, counts in sorted(totals.items()):
        lines.append('| ' + safe(name).replace('|', '\\|') + ' | ' + ' | '.join(map(str, counts)) + ' |')
    counts = [sum(row[i] for row in totals.values()) for i in range(4)]
    lines.append('| Total | ' + ' | '.join(map(str, counts)) + ' |')
    return lines


def download(state):
    records = details(state)
    if not records or not all(map(done, records)):
        raise RuntimeError('Battles are not all complete; use status first')
    run('online.js', 'download', ','.join(map(str, state['battle_ids'])), '--out', state['download_dir'])
    directory = DATA / state['download_dir']
    index = directory / 'index.json'
    if not index.exists():
        raise RuntimeError('Download did not produce index.json')
    games = json.loads(index.read_text())['games']
    expected = {g['id'] for d in records for g in d['games']}
    if expected != {g['gameId'] for g in games} or any(not g.get('replay') or not (directory / f"M{g['gameId']}.replay").exists() for g in games):
        raise RuntimeError('Download incomplete; rerun report to retry')
    opponents = {o['id'] for o in state['opponents']} if 'opponents' in state else {state['opponent']['id']}
    if any(g.get('ourSubmission') != state['submission']['id'] or g.get('opponentTeam') not in opponents for g in games):
        raise RuntimeError('Downloaded submission/opponent differs from recorded run')
    return directory, games


def picks(directory, team):
    tool = ROOT / 'tools/smoke_pick.py'
    if not tool.exists():
        return 'smoke_pick.py missing; mechanism facts unavailable.'
    result = subprocess.run([sys.executable, str(tool), str(directory), '--us', str(team), '--focus', 'all', '--n', '5'], cwd=ROOT, capture_output=True, text=True)
    return safe(result.stdout + ('\nPicker warning: ' + result.stderr if result.stderr else '') + (f'\nPicker failed (exit {result.returncode}); mechanism coverage unavailable.' if result.returncode else ''))


def paired_facts(candidate, baseline):
    def rows(text):
        return [line.strip('| ').split(' | ') for line in text.splitlines()
                if line.startswith('| ') and not line.startswith('| Game') and not line.startswith('| ---')]
    left, right = rows(candidate), rows(baseline)
    lines = ['| Selected rank | Candidate replay / alive / portals / splits / suicides / longest | Baseline replay / alive / portals / splits / suicides / longest |',
             '| --- | --- | --- |']
    def facts(row):
        return ' / '.join(row[i] for i in (0, 5, 6, 7, 8, 9)) if len(row) >= 10 else 'unavailable'
    for i in range(max(len(left), len(right))):
        lines.append(f"| {i + 1} | {facts(left[i]) if i < len(left) else 'unavailable'} | {facts(right[i]) if i < len(right) else 'unavailable'} |")
    return lines if left or right else ['Side-by-side mechanism facts unavailable.']



def pair_report(state):
    halves = state['halves']
    for half in halves.values():
        if (not half['submission'] or len(half['requests']) != len(state['schedule'])
                or any(r['status'] != 'accepted' for r in half['requests'])):
            raise RuntimeError('Pair is partial or uncertain; comparison withheld')
    downloaded = {key: download(half) for key, half in halves.items()}
    rows = {}
    for key, (directory, games) in downloaded.items():
        expected = sorted((b['opponent']['id'], mid) for b in state['schedule'] for mid in b['maps'])
        observed = sorted((g['opponentTeam'], g['map']) for g in games)
        if observed != expected:
            raise RuntimeError('Downloaded team/map schedule differs from the recorded pair')
        rows[key] = []
        for game in games:
            detail = json.loads((directory / f"game-{game['gameId']}.json").read_text())
            result = (detail.get('replay') or {}).get('result') or {}
            side = game['ourSide']
            if side not in ('A', 'B'):
                raise RuntimeError('Our side is missing; comparison withheld')
            other = 'B' if side == 'A' else 'A'
            rows[key].append(dict(game, our_longest=result.get('team' + side, {}).get('longestDragon'),
                                  their_longest=result.get('team' + other, {}).get('longestDragon'),
                                  ending=result.get('endReason', result.get('reason', 'unavailable'))))
    def wins(games):
        return sum(bool(g.get('winner')) and g['winner'].upper() == g['ourSide'] for g in games)
    def lengths(games):
        valid = [g for g in games if g['our_longest'] is not None and g['their_longest'] is not None]
        if not valid:
            return 'unavailable (0 measured)'
        return f"{sum(g['our_longest'] for g in valid) / len(valid):.1f} / {sum(g['their_longest'] for g in valid) / len(valid):.1f} (n={len(valid)})"
    def endings(games):
        counts = defaultdict(int)
        for g in games:
            counts[str(g['ending'])] += 1
        return ', '.join(f'{safe(k)}: {v}' for k, v in sorted(counts.items()))
    old, new = halves['old']['submission'], halves['new']['submission']
    lines = [f"Pair {state['label']}: old {old['id']} {safe(old['name'])} vs new {new['id']} {safe(new['name'])}; same opponent/map list.",
             f"Wins (small sample): old {wins(rows['old'])}/{len(rows['old'])}; new {wins(rows['new'])}/{len(rows['new'])}.",
             f"Recorded phase: {state['phase']}; last active {state['active_submission']['id']} (verified={state['active_verified']}); replay ids below for Zhe.", '',
             '| Opponent | Old games | Old wins (small sample) | New games | New wins (small sample) | Old final longest mean: ours / theirs | New final longest mean: ours / theirs | Old endings | New endings |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for opp in state['opponents']:
        a, b = ([g for g in rows[key] if g['opponentTeam'] == opp['id']] for key in ('old', 'new'))
        values = [f"{opp['id']} {opp['name']}", len(a), wins(a), len(b), wins(b), lengths(a), lengths(b), endings(a), endings(b)]
        lines.append('| ' + ' | '.join(safe(v).replace('|', r'\|') for v in values) + ' |')
    lines += ['', 'Final longest and endings by replay:', '',
              '| Bot | Opponent | Replay id | Map | Our longest | Their longest | End |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for key in ('old', 'new'):
        for g in rows[key]:
            values = [key, g['opponentTeam'], g['gameId'], g.get('mapName', '?'),
                      g['our_longest'] if g['our_longest'] is not None else 'unavailable',
                      g['their_longest'] if g['their_longest'] is not None else 'unavailable', g['ending']]
            lines.append('| ' + ' | '.join(safe(v).replace('|', r'\|') for v in values) + ' |')
        lines += ['', f"smoke_pick: {key} ({downloaded[key][0].relative_to(ROOT)})", '',
                  picks(downloaded[key][0], state['our_team'])]
    lines += ['', 'keep vs roll back: author + one OK']
    text = safe('\n'.join(lines) + '\n')
    path = STATE / f"{state['label']}-report.md"
    path.write_text(text)
    print(text, end='')
    print(f'Report: {path.relative_to(ROOT)}')

def report(state):
    if state['kind'] == 'pair':
        return pair_report(state)
    if len(state['requests']) != len(state['batches']) or any(r['status'] != 'accepted' for r in state['requests']):
        raise RuntimeError('Run is partial or uncertain; inspect state and requests.jsonl before reporting')
    directory, games = download(state)
    lines = [f"# Smoke report: {state['label']}", '', 'Win count: noise at 60 games (±8). No keep/rollback decision.', '', *table(games), '', '## How games ended']
    for g in games:
        path = directory / f"game-{g['gameId']}.json"
        detail = json.loads(path.read_text()) if path.exists() else {}
        ending = (detail.get('replay') or {}).get('result')
        lines.append(f"- {g['gameId']}: " + safe(json.dumps(ending) if ending is not None else 'end reason unavailable'))
    candidate_picks = picks(directory, state['our_team'])
    lines += ['', '## Mechanism facts and top replay ids for Zhe to eyeball', '', 'Candidate / this run:', '', candidate_picks]
    if state['kind'] == 'candidate':
        path = state_path(state['baseline_label'], True)
        if path.exists():
            baseline = load(state['baseline_label'], True)
            if compatible(state, baseline):
                base_dir, base_games = download(baseline)
                baseline_picks = picks(base_dir, state['our_team'])
                lines += ['', 'Stored baseline:', '', *table(base_games), '', baseline_picks, '', *paired_facts(candidate_picks, baseline_picks), '', 'Selected ranks are independent examples, not paired games or population averages. Suicides are actions, not proof of successful feeding.']
            else:
                lines += ['', 'Stored baseline incompatible; comparison withheld.']
        else:
            lines += ['', 'Stored baseline missing; comparison unavailable.']
        previous = {}
        for index in DATA.rglob('index.json'):
            if index.parent == directory:
                continue
            try:
                rows = json.loads(index.read_text()).get('games', [])
            except (OSError, ValueError):
                continue
            for g in rows:
                if g.get('ourSubmission') == state['rollback']['id'] and g.get('opponentTeam') == state['opponent']['id']:
                    previous[g['gameId']] = g
        lines += ['', '## Previous submission vs same opponent (historical, unmatched)', *table(previous.values())] if previous else ['', 'No previous-version games against this opponent found in local indexes.']
    lines += ['', 'Keep vs roll back: the area owner decides, plus one OK from someone else. Nothing is automatic.']
    text = safe('\n'.join(lines) + '\n')
    path = STATE / f"{'baseline-' if state['kind'] == 'baseline' else ''}{state['label']}-report.md"
    path.write_text(text)
    print(text, end='')
    print(f'Report: {path.relative_to(ROOT)}')


def perform_rollback(state):
    if state.get('old_only'):
        print('Live-only run: no rollback is needed or performed.')
        return
    check_freeze()
    no_pending()
    check_freeze()
    target = choose_restore(state)
    live = active()['id'] if target['id'] != state['rollback']['id'] else None
    print(activate_restore(state, target, live))
    current = active()
    if current['id'] != target['id']:
        raise RuntimeError('Rollback verification failed')
    state['phase'] = 'rolled-back'
    if state['kind'] == 'pair':
        state.update(active_submission=current, active_verified=True, rollback_required=False)
    save(state)
    print(f"Verified active: {current['id']} {safe(current['name'])} ({target['reason']})")


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest='command', required=True)
    for command in ('plan', 'start', 'baseline', 'pair'):
        p = sub.add_parser(command)
        if command != 'baseline':
            p.add_argument('botdir')
        p.add_argument('--name', type=label, required=True)
        if command in ('plan', 'pair'):
            selection = p.add_mutually_exclusive_group()
            selection.add_argument('--opp')
            selection.add_argument('--top', type=int)
        else:
            p.add_argument('--opp', default='dev_test_1')
        if command == 'plan':
            p.add_argument('--pair', action='store_true')
        if command in ('plan', 'pair'):
            mode = p.add_mutually_exclusive_group()
            mode.add_argument('--new-only', action='store_true')
            mode.add_argument('--old-only', action='store_true')
        if command != 'baseline':
            p.add_argument('--desc', help='upload description (maximum 190 characters)')
            p.add_argument('--ref', help='card reference for the default upload description')
        p.add_argument('--maps', default='all')
        p.add_argument('--games', type=int, default=60)
        p.add_argument('--baseline', type=label, default='v61')
        p.add_argument('--wait-seconds', type=int, default=1800)
        if command != 'plan':
            p.add_argument('--confirm', action='store_true')
    for command in ('status', 'report', 'rollback'):
        p = sub.add_parser(command)
        p.add_argument('label', type=label)
        p.add_argument('--baseline', action='store_true')
        if command == 'rollback':
            p.add_argument('--confirm', action='store_true')
    args = cli.parse_args(argv)
    try:
        if args.command in ('plan', 'start', 'baseline', 'pair'):
            if not 1 <= args.games <= 60 or args.wait_seconds < 1:
                raise RuntimeError('--games must be 1–60 and --wait-seconds positive')
            is_pair = args.command == 'pair' or (args.command == 'plan' and args.pair)
            if is_pair:
                if args.games < 2 or (args.top is not None and args.top < 1):
                    raise RuntimeError('pair requires --games 2–60 and positive --top')
                state = pair_prepare(args)
                if args.command == 'plan' or not args.confirm:
                    pair_plan(args, state)
                else:
                    pair_execute(args, state)
            else:
                if args.command == 'plan':
                    if args.top is not None:
                        raise RuntimeError('--top requires plan --pair')
                    args.opp = args.opp or 'dev_test_1'
                state = prepare(args)
                if args.command == 'plan' or not args.confirm:
                    plan(args, state)
                else:
                    execute(args, state)
        else:
            state = load(args.label, args.baseline)
            if args.command == 'status':
                halves = list(state['halves'].values()) if state['kind'] == 'pair' else [state]
                for detail in [d for h in halves for d in details(h)]:
                    print(f"Battle {detail['match']['id']}: {'done' if done(detail) else 'pending'}")
                    for game in detail['games']:
                        print(safe(f"  {game['id']} {game.get('mapName', '?')}: {game['status']} winner={game.get('winner') or '-'}"))
                print(f"Phase: {state['phase']}; " + '; '.join(f"{len(h['requests'])}/{len(h['batches'])} request batches recorded" for h in halves))
            elif args.command == 'report':
                report(state)
            elif not args.confirm:
                print('Plan only. Rollback: ' + rollback_command(state))
            else:
                perform_rollback(state)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print('Error: ' + safe(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
