#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import json, re, subprocess, hashlib, csv
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNS = Path.home() / 'meow-redteam/solo/runs'
sys.path.insert(0, str(ROOT / 'data/analysis/ladder/dossier/local'))
from replay_format import Message
UNPACK = ROOT / 'data/analysis/ladder/dossier/target/tg_unpack'
ARMS = sorted(p for p in RUNS.iterdir() if p.is_dir() and
              (p.name in ('mGx6_vb', 'mDone7', 'mDone8', 'mH62_vb', 'mHzr_vb') or
               re.fullmatch(r'm[EFJ].*_vb', p.name)))
DEATH = ['wall', 'self', 'other_body', 'head_on', 'no_valid_action']


def scan(folder, record):
    rp = folder / 'game.replay'
    root = Message(subprocess.run([str(UNPACK)], input=rp.read_bytes(), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, check=True).stdout).root()
    teams = {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q and q[0] == 'DRAGON':
            teams[len(teams)] = int(q[1])
    own = int(folder.name[-1])
    assert folder.parent.name in root.text(1 + own)
    assert 'm3base' in root.text(2 - own)
    assert root.pointer(4) is not None and root.pointer(4).bit(0)
    alive = set(teams)
    turns, deaths, action_deaths = Counter(), [Counter(), Counter()], [Counter(), Counter()]
    rounds, actor, last_action = -1, None, None
    moments, metrics, timeout_actions = [], 0, [0, 0]
    total_alive_sum, peak_alive = 0, len(alive)
    for ev in root.pointer(3):
        kind = ev.u16(0)
        if kind not in (0, 1, 4, 10, 11):
            continue
        p = ev.pointer(0)
        if kind == 0:
            rounds, actor, last_action = p.i32(0), None, None
        elif kind == 1:
            actor, last_action = p.i32(0), None
            assert actor in alive
            turns[teams[actor]] += 1
            total_alive_sum += len(alive)
            peak_alive = max(peak_alive, len(alive))
        elif kind == 4:
            assert p.i32(0) == actor
            a, usage = p.pointer(0), p.pointer(1)
            tag = a.u16(0) if a else None
            steps = list(a.pointer(0)) if a and tag == 0 and a.pointer(0) is not None else []
            timeout = p.bit(32) or (usage is not None and usage.bit(64))
            if timeout:
                subtype = 'timeout'
                timeout_actions[teams[actor]] += 1
            elif tag == 0:
                subtype = 'move' if steps else 'empty_move'
            elif tag == 1:
                subtype = 'split'
            else:
                subtype = 'no_action'
            last_action = {'kind': subtype, 'steps': len(steps), 'timeout': bool(timeout)}
            metrics += usage is not None
        elif kind == 10:
            child = p.i32(4)
            teams[child] = p.u16(8)
            alive.add(child)
        elif kind == 11:
            i, reason = p.i32(0), p.u16(4)
            assert i in alive
            deaths[teams[i]][DEATH[reason] if reason < 5 else str(reason)] += 1
            if reason == 4:
                act = last_action if i == actor else None
                subtype = (act or {}).get('kind', 'no_action_without_actor')
                subtype = {'move': 'unpaid_sprint', 'split': 'illegal_split'}.get(subtype, subtype)
                action_deaths[teams[i]][subtype] += 1
                moments.append({'round': rounds, 'log_round': rounds+1, 'id': i,
                                'side': 'ours' if teams[i] == own else 'old_main',
                                'action': act, 'classification': subtype})
            alive.remove(i)
    assert record['rounds'] == rounds + 1
    assert record['a_dragons'] == sum(teams[i] == 0 for i in alive)
    assert record['b_dragons'] == sum(teams[i] == 1 for i in alive)
    log = (folder / 'engine.log').read_text()
    log_deaths = Counter((int('AB'.index(t)), reason) for _, _, t, reason in
                         re.findall(r'round (\d+): dragon (\d+), team ([AB]): (.+)', log))
    for s in (0, 1):
        assert log_deaths[s, 'no valid action'] == deaths[s]['no_valid_action']
    nt = sum(turns.values())
    return dict(width=w, height=h, cells=w*h, replay_rounds=rounds+1, finished=True,
                own_side=own, turns_ours=turns[own], turns_old_main=turns[1-own], turns_total=nt,
                ms_per_turn=record['seconds']*1000/nt if nt else None,
                turns_per_round=nt/(rounds+1),
                mean_alive_at_turn=total_alive_sum/nt if nt else None, peak_alive=peak_alive,
                death_ours=dict(deaths[own]), death_old_main=dict(deaths[1-own]),
                action_death_ours=dict(action_deaths[own]), action_death_old_main=dict(action_deaths[1-own]),
                timeout_actions_ours=timeout_actions[own], timeout_actions_old_main=timeout_actions[1-own],
                turns_with_usage=metrics, no_valid_action_moments=moments,
                replay_bots=[root.text(1), root.text(2)],
                replay_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())


def main():
    inventory = []
    for arm in ARMS:
        for folder in sorted(arm.glob('gx_*')):
            m = re.search(r'_(\d+)x(\d+)_', folder.name)
            if not m or not folder.is_dir():
                continue
            row = dict(arm=arm.name, game=folder.name, path=str(folder), cells=int(m[1])*int(m[2]),
                       available={n:(folder/n).is_file() for n in ('result.json','result.txt','game.replay','engine.log')})
            inventory.append(row)
    (HERE/'inventory.json').write_text(json.dumps(dict(as_of=datetime.now().astimezone().isoformat(),
                                                      entries=inventory), indent=2)+'\n')
    rows = []
    with (HERE/'games.jsonl').open('w') as out:
        for n, entry in enumerate(inventory):
            folder = Path(entry['path'])
            row = dict(entry)
            if not all(entry['available'].values()):
                row['finished'] = False
                log = (folder/'engine.log').read_text() if entry['available']['engine.log'] else ''
                rr = [int(x) for x in re.findall(r'round (\d+):', log)]
                row['last_log_death_round'] = max(rr) if rr else None
                row['log_error_lines'] = [l for l in log.splitlines() if not re.match(r'round \d+: dragon \d+, team [AB]:', l)]
            else:
                record = json.loads((folder/'result.json').read_text())
                row.update(seconds=record.get('seconds'), native=record.get('native'),
                           bot_errors=record.get('bot_errors'), how=record.get('how'),
                           result_rounds=record.get('rounds'), record_bots=[record.get('botA'),record.get('botB')])
                try:
                    row.update(scan(folder, record))
                except Exception as e:
                    row['scan_error'] = repr(e)
            out.write(json.dumps(row,separators=(',',':'))+'\n');out.flush()
            rows.append(row)
            if n % 25 == 0:
                print(f'{n+1}/{len(inventory)} {entry["arm"]} {entry["game"]}',flush=True)
    groups = defaultdict(list)
    for row in rows:
        groups[row['arm'], row['cells']].append(row)
    summaries = []
    for (arm, cells), group in sorted(groups.items()):
        clean = [g for g in group if g.get('finished') and not g.get('scan_error')]
        a,b=Counter(),Counter()
        for g in clean:
            a.update(g['action_death_ours']);b.update(g['action_death_old_main'])
        total_turns=sum(g['turns_total'] for g in clean)
        summaries.append(dict(arm=arm,cells=cells,dirs=len(group),complete=len(clean),
                             incomplete=[g['game'] for g in group if not g.get('finished')],
                             scan_errors=[(g['game'],g['scan_error']) for g in group if g.get('scan_error')],
                             bot_errors=sum(len(g.get('bot_errors') or []) for g in group),
                             timeouts_ours=sum(g['timeout_actions_ours'] for g in clean),
                             timeouts_old_main=sum(g['timeout_actions_old_main'] for g in clean),
                             action_death_ours=dict(a),action_death_old_main=dict(b),
                             seconds=sum(g['seconds'] for g in clean),turns_total=total_turns,
                             ms_per_turn=sum(g['seconds'] for g in clean)*1000/total_turns if total_turns else None,
                             median_game_ms_per_turn=median(g['ms_per_turn'] for g in clean) if clean else None,
                             median_alive_at_turn=median(g['mean_alive_at_turn'] for g in clean) if clean else None,
                             max_peak_alive=max((g['peak_alive'] for g in clean),default=0)))
    (HERE/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    fields=['arm','cells','dirs','complete','bot_errors','timeouts_ours','timeouts_old_main',
            'seconds','turns_total','ms_per_turn','median_game_ms_per_turn','median_alive_at_turn','max_peak_alive',
            'action_death_ours','action_death_old_main','incomplete','scan_errors']
    with (HERE/'summary.tsv').open('w') as f:
        wr=csv.DictWriter(f,fieldnames=fields,delimiter='\t');wr.writeheader()
        wr.writerows({k:s[k] for k in fields} for s in summaries)
    print('DONE',len(rows),'games',len(summaries),'groups',flush=True)

if __name__=='__main__':main()
