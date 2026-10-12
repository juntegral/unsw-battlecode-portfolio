#!/usr/bin/env python3
"""Run one native match with the installed engine's own process controller."""
import argparse
from contextlib import contextmanager
from dataclasses import asdict
import fcntl
import json
import os
from pathlib import Path
import signal
import sys
import time

from unswbc.bot import Bot, Pool
from unswbc.engine import EngineModule
from unswbc.run import _verdict, DEATH_REASONS

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def game_slot():
    """All callers share the same four flock slots (two until 10-09 13:52; a game uses 4 to 5 cores, so more only thrashes); never unlink lock files."""
    lockdir = ROOT / '.locks'
    lockdir.mkdir(exist_ok=True)
    handles = [(lockdir / f'game-{i}.lock').open('a+') for i in range(4)]
    selected = None
    try:
        while selected is None:
            for handle in handles:
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    continue
                selected = handle
                break
            if selected is None:
                time.sleep(0.1)
        yield
    finally:
        for handle in handles:
            handle.close()


def local_path(path):
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError('game inputs and outputs must be inside this workspace')
    return resolved


def bot_path(path):
    target = local_path(path)
    if target.is_dir():
        target = local_path(target / 'bot')
    if not target.is_file() or not os.access(target, os.X_OK):
        raise ValueError(f'not an executable bot: {path}; build bot directories first')
    return target


def interrupted(signum, frame):
    raise KeyboardInterrupt


def run_match(bot_a, bot_b, map_path, seed, output):
    # nice is set by play.sh and verified here before spawning any bots.
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 15:
        os.nice(15 - priority)
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('output directory must be empty (existing replays are preserved)')
    started = time.monotonic()
    pools, live = {}, {}
    teams, bot_errors, notices = {}, [], []
    engine = EngineModule()
    with (output / 'engine.log').open('w') as log:
        def notice(line):
            notices.append(line)
            print(line, file=log, flush=True)

        def spawn(dragon_id, init):
            team = next(line.split()[1] for line in init.decode().splitlines()
                        if line.startswith('TEAM '))
            teams[dragon_id] = team
            live[dragon_id] = Bot(pools[team], init=init, name=str(dragon_id))

        def reply(dragon_id, block):
            bot = live[dragon_id]
            out = bot.ask(block)
            if bot.error:
                entry = {'id': dragon_id, 'team': teams[dragon_id], 'error': bot.error}
                bot_errors.append(entry)
                print(json.dumps(entry), file=log, flush=True)
            return out

        def death(dragon_id, round_num, reason):
            print(f'round {round_num + 1}: dragon {dragon_id}, team {teams[dragon_id]}: '
                  f'{DEATH_REASONS.get(reason, reason)}', file=log, flush=True)
            bot = live.pop(dragon_id, None)
            if bot is not None:
                bot.stop()

        try:
            for team, binary in [('A', bot_a), ('B', bot_b)]:
                pools[team] = Pool([str(binary)], cwd=str(binary.parent), size=1)
            result = engine.run(map_path.read_bytes(), reply, death, spawn, notice, debug=0, seed=seed)
            replay = engine.replay(str(bot_a.relative_to(ROOT)), str(bot_b.relative_to(ROOT)))
        finally:
            for bot in live.values():
                bot.stop()
            for pool in pools.values():
                pool.close()
    (output / 'game.replay').write_bytes(replay)
    elapsed = time.monotonic() - started
    winner = {'A': 0, 'B': 1, None: 'draw'}[result.winner]
    end = 'elimination' if result.end_reason == 0 else 'round_limit'
    record = dict(asdict(result), winner=winner, how=end, verdict=_verdict(result),
                  rounds=result.rounds + 1, final_lengths=[result.a_length, result.b_length],
                  botA=str(bot_a.relative_to(ROOT)), botB=str(bot_b.relative_to(ROOT)),
                  map=str(map_path.relative_to(ROOT)), seed=seed, seconds=round(elapsed, 3),
                  nice=priority, native=True, bot_errors=bot_errors, map_notices=notices)
    line = (f'winner={winner} how={end} ({record["verdict"]}) rounds={record["rounds"]} '
            f'final_lengths={result.a_length},{result.b_length}')
    record['line'] = line
    (output / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    (output / 'result.txt').write_text(line + '\n')
    print(line, flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('botA')
    parser.add_argument('botB')
    parser.add_argument('map_file')
    parser.add_argument('seed', type=lambda s: int(s, 0))
    parser.add_argument('out_dir')
    args = parser.parse_args()
    try:
        a, b = bot_path(args.botA), bot_path(args.botB)
        map_path, output = local_path(args.map_file), local_path(args.out_dir)
        if not map_path.is_file():
            raise ValueError('map file does not exist')
        if not 0 <= args.seed < 2**64:
            raise ValueError('seed must be an unsigned 64-bit integer')
        signal.signal(signal.SIGTERM, interrupted)
        with game_slot():
            run_match(a, b, map_path, args.seed, output)
    except KeyboardInterrupt:
        print('game interrupted', file=sys.stderr)
        return 130
    except Exception as error:
        print(f'game failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
