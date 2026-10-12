#!/usr/bin/env python3
"""Card #38 queen-loop (QUEEN_LOOP) against a queen-hunting spar: two paired arms, then the card's own check.

  base      = main 0e03867 mybot2 as it is (switch off)            bots/off
  candidate = main 0e03867 + card #38 (c1c2c29) with QUEEN_LOOP on  bots/on  (the loop's attempt-1/on-src)
  opponent  = main 0e03867 with QUEEN_HUNT=true, QUEEN_CHASE_DIST=8 bots/hunter  (in both arms)

Maps, games and seeds are QWQ's QUEEN_MARGIN hunter run (work/qm_small.sh on origin/claude/sweet-pasteur-shawil):
17 maps x 4 games per arm, SEED0=3000 (seeds 3000 and 3001, both starting sides), replays kept.
Games go through harness/work/ab3.py, one call per map, with the argv and environment the card loop uses for its
mechanism step (work/loop/jobs.py batch()): WORKERS=6, KEEP=1, NOSANDBOX=1, work/bc127/bin first on PATH, nice 10.

The script waits until the card loop's game batch is free (status.json: batch_running false and card 38 no longer on
its outcome step), checks again before every map and before the check, and waits whenever the loop is busy.

usage: nohup python3 run_hunter38.py > nohup.out 2>&1 &
Re-running is safe: finished maps (rows/<map>.json complete, replays present) are skipped.
Test overrides (environment): H38_MAPS, H38_N, H38_WORKERS, H38_STATUS, H38_POLL, H38_START_LIMIT, H38_PAUSE_LIMIT.
"""
import datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / 'harness'
REPLAYS = HERE / 'replays'
ROWS = HERE / 'rows'
LOG = HERE / 'run.log'
ENGINE_BIN = '~/01. Project/개인 프로젝트/battlecode/work/bc127/bin'
STATUS = Path(os.environ.get('H38_STATUS', str(Path.home() / 'meow-loop-out/status.json')))
CARD = '38'
TOGGLE = 'QUEEN_LOOP'
MAPS = os.environ.get('H38_MAPS', 'default,trauma,queen_of_spades,schooltime,portals_v0,slithery_fight_v0,autarky_v0,'
                      'devil_v0,prisoners_dilemma_v0,trophy,around_unsw,australia,islands,maze,stripes,tower_defense,'
                      'weakhold').split(',')
N = int(os.environ.get('H38_N', '4'))
SEED0 = 3000
WORKERS = min(6, int(os.environ.get('H38_WORKERS', '6')))
POLL = int(os.environ.get('H38_POLL', '60'))
START_LIMIT = int(os.environ.get('H38_START_LIMIT', str(3 * 3600)))
PAUSE_LIMIT = int(os.environ.get('H38_PAUSE_LIMIT', str(6 * 3600)))
TAGS = ('base', 'candidate')
NAMES = {'base': 'switch off', 'candidate': 'switch on'}
SOURCES = {'base': 'off', 'candidate': 'on', 'hunter': 'hunter'}
MAIN_SHA = {'off': 'a3504fff49f6a2d7ee52dbce782e4a805261b145c79032223db8656f21992103',
            'on': 'a731dcb9fc235b2f08f15beaed502517c20aedaed4b8e61827cdbf87b8f193e0',
            'hunter': 'fb02cd0bb58f30c8f41a689012c88efe5cb14aeb04a11e056208a80db84cfe8b'}
KST = datetime.timezone(datetime.timedelta(hours=9))


def log(text):
    with open(LOG, 'a') as f:
        f.write(f"{datetime.datetime.now(KST):%Y-%m-%d %H:%M:%S} KST  {text}\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def loop_busy():
    """Why the card loop needs the machine, or '' when it is free."""
    try:
        s = json.loads(STATUS.read_text())
    except Exception as exc:
        return f'status.json not readable ({type(exc).__name__})'
    if s.get('batch_running'):
        return f"batch_running (status updated {s.get('updated', '?')})"
    if ((s.get('cards') or {}).get(CARD) or {}).get('step_kind') == 'outcome':
        return f"card {CARD} step_kind is outcome (status updated {s.get('updated', '?')})"
    return ''


def wait_free(limit, what):
    start, polls = time.time(), 0
    while True:
        why = loop_busy()
        if not why:
            if polls:
                log(f'loop is free after {round((time.time() - start) / 60)} min; {what}')
            return True
        if time.time() - start >= limit:
            log(f'GAVE UP after {round(limit / 3600, 1)} h waiting for the loop before: {what} (last: {why})')
            return False
        if polls % 10 == 0:
            log(f'waiting for the loop before: {what} ({why})')
        polls += 1
        time.sleep(POLL)


def game_env():
    env = os.environ.copy()
    for key in ('KEEP', 'FAST', 'DIST', 'NOSANDBOX'):
        env.pop(key, None)
    env.update(WORKERS=str(WORKERS), SEED0=str(SEED0), KEEP='1', NOSANDBOX='1',
               PATH=ENGINE_BIN + os.pathsep + env.get('PATH', ''))
    return env


def expected(m):
    return {(t, m, SEED0 + k // 2, k % 2) for k in range(N) for t in TAGS}


def read_rows(m):
    dest = ROWS / f'{m}.json'
    try:
        rows = json.loads(dest.read_text())
    except Exception:
        return None
    keys = {(r['tag'], r['map'], r['seed'], r['side']) for r in rows}
    if len(rows) != len(keys) or keys != expected(m):
        return None
    if not all((REPLAYS / f'{t}_{mm}_{s}_{side}.replay').is_file() for t, mm, s, side in keys):
        return None
    return rows


def play_map(m, env):
    dest = ROWS / f'{m}.json'
    argv = ['nice', '-n', '10', sys.executable, str(HARNESS / 'work/ab3.py'), m, 'hunter', str(N), str(dest),
            'base@base:', f'candidate@candidate:{TOGGLE}=true']
    for attempt in (1, 2, 3):
        with open(ROWS / f'{m}.log', 'a') as out:
            try:
                code = subprocess.run(argv, cwd=HARNESS, env=env, stdout=out, stderr=subprocess.STDOUT,
                                      stdin=subprocess.DEVNULL, timeout=3600).returncode
            except subprocess.TimeoutExpired:
                code = 'timeout'
        for tag in TAGS:
            built = HARNESS / 'tune_runs/ab2' / tag / 'main.cpp'
            if not built.is_file() or sha(built) != MAIN_SHA[SOURCES[tag]]:
                raise RuntimeError(f'{m}: the built {tag} bot is not the expected source')
        rows = read_rows(m)
        if code == 0 and rows is not None:
            return rows
        if dest.exists():
            dest.rename(ROWS / f'{m}-incomplete-{time.time_ns()}.json')
        log(f'{m}: attempt {attempt} incomplete (exit {code}); see rows/{m}.log')
    raise RuntimeError(f'{m}: no complete set of games after 3 attempts')


def tally(rows):
    by = {t: {(r['map'], r['seed'], r['side']): r for r in rows if r['tag'] == t} for t in TAGS}
    out = {}
    for t in TAGS:
        rs = list(by[t].values())
        out[t] = {'games': len(rs), 'wins': sum(r['win'] for r in rs),
                  'side': {s: [sum(r['win'] for r in rs if r['side'] == s), sum(r['side'] == s for r in rs)] for s in (0, 1)},
                  'how': {h: [sum(r['win'] for r in rs if r['how'] == h), sum(r['how'] == h for r in rs)]
                          for h in sorted({r['how'] for r in rs})},
                  'wiped': sum(r['wiped'] for r in rs), 'wiped_them': sum(r['wiped_them'] for r in rs),
                  'rounds': round(sum(r['rounds'] for r in rs) / max(1, len(rs)), 1)}
    plus = [k for k, r in by['candidate'].items() if r['win'] and not by['base'][k]['win']]
    minus = [k for k, r in by['candidate'].items() if by['base'][k]['win'] and not r['win']]
    return out, sorted(plus), sorted(minus), by


def table(head, lines):
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(str(x) for x in l) + ' |' for l in lines]


def write_result(rows, check, check_error):
    t, plus, minus, by = tally(rows)
    b, c = t['base'], t['candidate']
    pairs = len(by['base'])
    text = [f'# Card #38 {TOGGLE} against a queen-hunting spar', '',
            f"Finished {datetime.datetime.now(KST):%Y-%m-%d %H:%M} KST. {len(MAPS)} maps x {N} games per arm (seeds "
            f"{SEED0}-{SEED0 + (N - 1) // 2}, both starting sides), {pairs} pairs. Both arms play the same opponent: main "
            "0e03867 with QUEEN_HUNT=true and QUEEN_CHASE_DIST=8. Switch off = main 0e03867; switch on = main 0e03867 + "
            f"card #38 (c1c2c29) with {TOGGLE}=true.", '',
            '## Games', '']
    text += table(['', 'switch off (base)', 'switch on (candidate)'],
                  [['wins', f"{b['wins']} of {b['games']}", f"{c['wins']} of {c['games']}"],
                   ['wins starting as side 0', '{} of {}'.format(*b['side'][0]), '{} of {}'.format(*c['side'][0])],
                   ['wins starting as side 1', '{} of {}'.format(*b['side'][1]), '{} of {}'.format(*c['side'][1])],
                   ['games we were wiped out', b['wiped'], c['wiped']],
                   ['games the hunter was wiped out', b['wiped_them'], c['wiped_them']],
                   ['mean rounds', b['rounds'], c['rounds']]]
                  + [[f'ended by {h} (wins of games)', '{} of {}'.format(*b['how'].get(h, [0, 0])),
                      '{} of {}'.format(*c['how'].get(h, [0, 0]))] for h in sorted(set(b['how']) | set(c['how']))])
    text += ['', f'Paired flips (same map, seed and side): switch on won where switch off lost in {len(plus)} pairs, '
             f'lost where switch off won in {len(minus)} pairs.',
             'Won only with the switch on: ' + (', '.join(f'{m} {s}/{side}' for m, s, side in plus) or 'none') + '.',
             'Won only with the switch off: ' + (', '.join(f'{m} {s}/{side}' for m, s, side in minus) or 'none') + '.', '']
    if check:
        bv, cv = check['base'], check['candidate']

        def row(label, f):
            return [label, f(bv), f(cv)]

        text += ['## Our queen (work/card_38_check.py on the kept replays)', '']
        text += table(['', 'switch off (base)', 'switch on (candidate)'], [
            row('queen alive at the end', lambda v: f"{v['queen_alive_at_end']} of {v['games']}"),
            row('queen deaths (before r300)', lambda v: f"{v['queen_deaths']} ({v['queen_deaths_before_r300']})"),
            row('rammed by an enemy head', lambda v: v['queen_rammed_by_an_enemy_head']),
            row('of those right after a lap step', lambda v: v['of_those_right_after_a_lap_step']),
            row('deaths by cause', lambda v: ', '.join(f'{k} {n}' for k, n in v['queen_deaths_by_cause'].items()) or '-'),
            row('mean death round', lambda v: v['queen_death_round_mean'] if v['queen_deaths'] else '-'),
            row('loop share (lap steps per queen decision before r300)',
                lambda v: f"{v['loop_share_pct']}% ({v['lap_steps_before_r300']} of {v['queen_decisions_before_r300']})"),
            row('loops, lap steps per loop', lambda v: f"{v['loops']}, {v['lap_steps_per_loop']}"),
            row('on the loop with a seen head inside reach + 1 of her square',
                lambda v: f"{v['on_the_loop_tight']} decisions"),
            row('of those, she took the next lap step anyway', lambda v: v['tight_and_went_on']),
            row('same by the real enemy length (went on / decisions)',
                lambda v: f"{v['true_tight_and_went_on']} / {v['on_the_loop_true_tight']}"),
            row('push-offs (followed by a lap step near the pusher)',
                lambda v: f"{v['push_offs']} ({v['push_offs_followed_by_a_lap_step_near_the_pusher']})"),
            row('alive at r100 / r200 / r300', lambda v: ' / '.join(str(v['queen_alive_and_mean_length_at'][k][0])
                                                                     for k in ('r100', 'r200', 'r300'))),
            row('queen pearls eaten before r300', lambda v: v['queen_pearls_eaten_before_r300'])])
        text += ['', f"The check's own verdict: passed = {check['passed']}. Its pass rule was fixed for games against main "
                 '(does she loop, does she step off); here it is shown for reference only, and the deaths and rams above '
                 'are raw counts.', '',
                 '## Per map', '']
        maps = check.get('by_map', {})
        text += table(['map', 'off wins', 'on wins', 'off queen alive', 'on queen alive', 'off rammed', 'on rammed', 'on loop share'],
                      [[m, f"{maps[m]['base']['wins']}/{maps[m]['base']['games']}", f"{maps[m]['candidate']['wins']}/{maps[m]['candidate']['games']}",
                        maps[m]['base']['queen_alive_at_end'], maps[m]['candidate']['queen_alive_at_end'],
                        maps[m]['base']['queen_rammed_by_an_enemy_head'], maps[m]['candidate']['queen_rammed_by_an_enemy_head'],
                        f"{maps[m]['candidate']['loop_share_pct']}%"] for m in MAPS if m in maps])
        groups = check.get('by_map_group', {})
        text += ['', 'By map size (the check splits at 600 tiles):', '']
        text += table(['group', 'pairs', 'off wins', 'on wins', 'off queen alive', 'on queen alive', 'off rammed', 'on rammed'],
                      [[g, groups[g]['base']['games'], groups[g]['base']['wins'], groups[g]['candidate']['wins'],
                        groups[g]['base']['queen_alive_at_end'], groups[g]['candidate']['queen_alive_at_end'],
                        groups[g]['base']['queen_rammed_by_an_enemy_head'], groups[g]['candidate']['queen_rammed_by_an_enemy_head']]
                       for g in ('small', 'big') if g in groups and groups[g]['base']['games']])
        text += ['', "## The check's note", '', check['note'], '']
    else:
        text += ['## Our queen', '', f'The check did not produce a result: {check_error}. See check.log.', '',
                 '## Per map', '']
        text += table(['map', 'off wins', 'on wins'],
                      [[m, sum(r['win'] for k, r in by['base'].items() if k[0] == m),
                        sum(r['win'] for k, r in by['candidate'].items() if k[0] == m)] for m in MAPS])
        text += ['']
    text += ['## Next to QWQ\'s numbers', '',
             "QWQ's QUEEN_MARGIN run used the same 17 maps, 4 games per map and SEED0=3000; there the base won 36 of 68 "
             'against the hunter. His base and hunter were built from main fa61861; here both are built from main 0e03867, '
             'so the switch-off arm is the like-for-like line, not an exact repeat.', '',
             'Files: hunt.json (all game rows), rows/ (per map), replays/, check.json, check.log, run.log.', '']
    (HERE / 'result.md').write_text('\n'.join(text))


def main():
    try:
        os.setsid()
    except OSError:
        pass
    pid_file = HERE / 'run.pid'
    try:
        other = int(pid_file.read_text())
        os.kill(other, 0)
        sys.exit(f'already running as pid {other}')
    except (OSError, ValueError):
        pass
    pid_file.write_text(str(os.getpid()))
    for d in (REPLAYS, ROWS):
        d.mkdir(exist_ok=True)
    subprocess.Popen(['caffeinate', '-i', '-w', str(os.getpid())], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f'start pid {os.getpid()}: {len(MAPS)} maps x {N} games x 2 arms against the hunter, SEED0={SEED0}, WORKERS={WORKERS}')
    for name, digest in MAIN_SHA.items():
        if sha(HERE / 'bots' / name / 'main.cpp') != digest:
            raise RuntimeError(f'bots/{name}/main.cpp is not the source this test was prepared with')
    env = game_env()
    if not wait_free(START_LIMIT, 'first map'):
        sys.exit(2)
    rows = []
    for i, m in enumerate(MAPS, 1):
        done = read_rows(m)
        if done is None:
            if not wait_free(PAUSE_LIMIT, f'map {i}/{len(MAPS)} {m}'):
                sys.exit(2)
            started = time.time()
            done = play_map(m, env)
            took = f'{round(time.time() - started)} s'
        else:
            took = 'already there'
        rows += done
        wins = {t: sum(r['win'] for r in done if r['tag'] == t) for t in TAGS}
        log(f"map {i}/{len(MAPS)} {m}: switch off {wins['base']}/{N}, switch on {wins['candidate']}/{N} ({took})")
    (HERE / 'hunt.json').write_text(json.dumps(rows))
    t, plus, minus, _ = tally(rows)
    log(f"games done: switch off {t['base']['wins']}/{t['base']['games']}, switch on {t['candidate']['wins']}/"
        f"{t['candidate']['games']}, flips +{len(plus)} -{len(minus)}")
    if not wait_free(PAUSE_LIMIT, 'check'):
        sys.exit(2)
    check, check_error = None, ''
    out = HERE / 'check.json'
    out.unlink(missing_ok=True)
    with open(HERE / 'check.log', 'w') as f:
        code = subprocess.run(['nice', '-n', '10', sys.executable, str(HARNESS / 'work/card_38_check.py'),
                               '--replays', str(REPLAYS), '--base', 'base', '--candidate', 'candidate', '--output', str(out)],
                              cwd=HERE, env=env, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode
    try:
        check = json.loads(out.read_text())
    except Exception:
        tail = (HERE / 'check.log').read_text().strip().splitlines()[-1:] or ['no output']
        check_error = f'exit {code}: {tail[0][:300]}'
    write_result(rows, check, check_error)
    if check is None:
        log(f'check failed ({check_error}); result.md has the game numbers only')
        log('FAILED: check')
        sys.exit(1)
    log(f"check done: passed={check['passed']}; result.md written")
    with open(LOG, 'a') as f:
        f.write('DONE\n')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        log(f'FAILED: {type(exc).__name__}: {exc}')
        raise
