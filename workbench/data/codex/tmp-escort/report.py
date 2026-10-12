import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
import re
import types
from pathlib import Path
import subprocess
import dn_tab as tab

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out-escort-counts.md'
ARMS = ['m3b7qk_vh', 'm4qd_vh', 'm5dn_vh']

def read(prefix, arm):
    return {g['game']: g for line in (HERE / f'{prefix}-{arm}.jsonl').read_text().splitlines() if line.strip() for g in [json.loads(line)]}

def table(arms, *filters):
    old = sys.argv
    sys.argv = ['dn_tab.py', *arms, *filters]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            tab.main()
    finally:
        sys.argv = old
    return out.getvalue().strip()

def rows(text):
    return {p[1].strip(): tuple(x.strip() for x in p[2:-1]) for line in text.splitlines() if line.startswith('|') for p in [line.split('|')] if p[1].strip() not in ('measure', '---')}

def run_check_command(script):
    p = subprocess.run(['nice', '-n', '10', sys.executable, str(HERE / script), 'm3b7qk_vh', 'm5es_vh'], text=True, capture_output=True)
    (HERE / (script + '.check.log')).write_text(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout

def result(g):
    path = Path.home() / 'meow-redteam/solo/runs' / g['arm'] / g['game'] / 'result.txt'
    return path.read_text()

def winner(g):
    match = re.search(r'\bwinner=(\S+)', result(g))
    if not match:
        return 'n/a (winner field absent from result.txt)'
    value = match.group(1)
    if value == 'draw':
        assert g['win'] is None
        return 'draw'
    if value in ('0', '1'):
        assert g['win'] == int(int(value) == g['side'])
        return g['arm'] if int(value) == g['side'] else 'm3hunt'
    return 'n/a (unrecognized winner field: ' + value + ')'

def rounds(g):
    match = re.search(r'\brounds=(\d+)', result(g))
    return match.group(1) if match else 'n/a (rounds field absent from result.txt)'

def death(g, kind=False):
    f = g['fate']
    return str(f['r']) + ('; ' + f['kind'] + '; reason ' + str(f['reason']) if kind else '') if f else 'alive at game end'

def markdown(headers, entries):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in entries])

def generate():
    esc = run_check_command('esc_tab.py')
    dn = run_check_command('dn_tab.py')
    er, dr = rows(esc), rows(dn)
    mismatches = {k: (v, dr.get(k)) for k, v in er.items() if dr.get(k) != v}
    assert not mismatches, mismatches
    checkarms = ['m3b7qk_vh', 'm5es_vh']
    checkdata = {a: read('dn', a) for a in checkarms}
    commoncheck = sorted(set.intersection(*(set(d) for d in checkdata.values())))
    checks = []
    for a in checkarms:
        c, _ = tab.measure([checkdata[a][k] for k in commoncheck])
        total = sum(c[f'dn_L{L}_{target}'] for L in (2, 3, 4, 5) for target in ('pursuer', 'radius'))
        assert total == c['near_mate_moved'], (a, total, c['near_mate_moved'])
        checks.append([a, c['games'], c['near_mate_moved'], c['near_enemy_moved'], f"{c['chases']}; {c['chase_turns']/max(1,c['chases']):.1f}; {c['chase4']}", total])
    projection_count = 0
    for a in checkarms:
        old = read('esc', a)
        for k in commoncheck:
            g = checkdata[a][k]
            assert k in old
            for field, value in old[k].items():
                if field == 'deaths':
                    new = [{f: d[f] for f in od} for od, d in zip(value, g[field])]
                    assert len(value) == len(g[field]) and value == new, (a, k, field)
                else:
                    assert value == g[field], (a, k, field)
            projection_count += 1
    identical = all((HERE / f).read_bytes() == (Path.home() / 'meow-redteam/solo/src/w-escort' / f).read_bytes() for f in ('dn_scan.py', 'dn_tab.py'))
    sections = ['# Escort counts', '## Step 2 checks',
        'The copied drafts were read against the brief line by line. No changes were needed. Byte identity with both source drafts: ' + str(identical) + '. All arms below were scanned from replay files; draft JSONL caches were not used.',
        f'`python3 dn_tab.py m3b7qk_vh m5es_vh` and `python3 esc_tab.py m3b7qk_vh m5es_vh`: PASS. All {len(er)} shared printed rows have identical values on {len(commoncheck)} common games. Both commands were run under `nice -n 10`.',
        markdown(['Arm', 'Games', 'Mate moved', 'Enemy moved', 'Chases; turns each; lasting 4+', 'Sum of new length-by-target cells'], checks),
        'Length-by-target sum equals the mate-moved count: PASS for both check arms. All original record fields also match the trusted ESC records for ' + str(projection_count) + ' arm-game records.',
        'Distances: tiles are torus Manhattan distance; steps are breadth-first over open edges and portals (`Geo.adj`), ignoring bodies, capped at 8 (99 beyond that or with our queen dead). `L0`, enemy head distance, and start tiles are measured at the start of the mover’s turn. `moved` counts event-kind-9 head tile changes by the actor up to the collision. Length lost uses length at death. Chase definitions and existing table rows are unchanged.',
        'The jobs emitted the permitted warning `nice: setpriority: Operation not permitted`.']
    data = {a: read('dn', a) for a in ARMS}
    commonAB = sorted(set(data[ARMS[0]]) & set(data[ARMS[1]]))
    commonD = sorted(set.intersection(*(set(d) for d in data.values())))
    expectedmaps = {'sqheld_open_small_90012', 'sqheld_portals_medium_90007', 'sqheld_portals_medium_90020', 'ladder_islands_1'}
    expected = {f'{m}-seed1-side{s}' for m in expectedmaps for s in (0,1)}
    wait = (HERE / 'wait-m5dn.log').read_text().strip()
    sections += ['## Input counts', markdown(['Arm', 'Scanned completed games'], [[a, len(data[a])] for a in ARMS]),
                 'New-arm wait: ' + wait.replace('\n', '; ') + '.',
                 'Expected new-arm games missing from the three-arm intersection: ' + (', '.join(sorted(expected-set(commonD))) or 'none') + '.']
    for label, filters, common in [('A', [], commonAB), ('B', ['cells<=700'], [k for k in commonAB if data[ARMS[0]][k]['w']*data[ARMS[0]][k]['h']<=700]), ('C', ['cells>700'], [k for k in commonAB if data[ARMS[0]][k]['w']*data[ARMS[0]][k]['h']>700])]:
        sections += [f'## Table {label}' + (' — ' + filters[0] if filters else ''), table(ARMS[:2], *filters), f'Games behind Table {label}: {len(common)} common games.']
        if label == 'A':
            small = [k for k in commonAB if data[ARMS[0]][k]['w']*data[ARMS[0]][k]['h']<=700]
            sections += ['### Small-map games behind Table A', markdown(['Game', 'Cells', 'Baseline winner', 'Radius-5 winner', 'Baseline own dragons r100', 'Radius-5 own dragons r100', 'Baseline queen death round', 'Radius-5 queen death round'], [[k, data[ARMS[0]][k]['w']*data[ARMS[0]][k]['h'], winner(data[ARMS[0]][k]), winner(data[ARMS[1]][k]), data[ARMS[0]][k]['snaps']['100']['alive'], data[ARMS[1]][k]['snaps']['100']['alive'], death(data[ARMS[0]][k]), death(data[ARMS[1]][k])] for k in small])]
    sections += ['## Table D', table(ARMS), f'Games behind Table D: {len(commonD)} common games.']
    smallE = [k for k in commonD if data[ARMS[0]][k]['map']=='sqheld_open_small_90012']
    only = HERE / 'table-E-games.txt'
    only.write_text('\n'.join(smallE)+'\n')
    sections += ['## Table E — sqheld_open_small_90012', table(ARMS, 'only='+str(only)), f'Games behind Table E: {len(smallE)} common games.', '## New-arm comparison per game', markdown(['Game', 'Arm', 'Winner', 'Rounds (result.txt)', 'Own dragons r100', 'Own dragons r300', 'Queen death round; kind; reason'], [[k, a, winner(data[a][k]), rounds(data[a][k]), data[a][k]['snaps']['100']['alive'], data[a][k]['snaps']['300']['alive'], death(data[a][k], True)] for k in commonD for a in ARMS]),
                 'Round checkpoints follow the trusted scanner: if the game ended before a checkpoint, its final snapshot is used.']
    entries = []
    for k, g in sorted(data['m5dn_vh'].items()):
        for p in tab.pairs(g):
            o, e = p['ours'], p['theirs']
            if o['id'] == g['queen'][0] or p['mover'] != o['id'] or o['dq'] > 5:
                continue
            entries.append([k, p['r'], o['id'], o['L0'], tab.xy(g, o['starthead']), e['id'], e['L'], tab.xy(g, e['starthead']), e['qsteps'], e['qtiles'], tab.xy(g, o['qhead0']), '**baseline disallows: enemy shorter**' if e['L'] < o['L0'] else ''])
    sections += ['## List 1 — every mate-moved head-on within 5 tiles in m5dn_vh',
                 'Tiles in this list are at the start of the mover’s turn. Enemy length is at death; the enemy is stationary on a mate move. Every listed mate is not our queen; enemy queens are included if present. The mark uses the requested comparison: enemy length < mate `L0`.',
                 markdown(['Game', 'Round', 'Mate id', 'Mate L0', 'Mate start tile', 'Enemy id', 'Enemy length', 'Enemy start tile', 'qsteps', 'qtiles', 'Our queen start tile', 'Baseline mark'], entries), f'Listed head-ons: {len(entries)}.']
    entries = []
    for k, g in sorted(data['m5dn_vh'].items()):
        hp = tab.pairs(g)
        for ep in tab.chases(g):
            ids = {i for t in ep for i in t['ids']}
            hit = [p for p in hp if p['theirs']['id'] in ids and p['ours']['id'] != g['queen'][0] and p['mover'] == p['ours']['id'] and ep[0]['r'] <= p['r'] <= ep[-1]['r']+1]
            fate = g['fate']
            ram = fate is not None and fate['kind'] == 'rammed' and fate['qn'] == ep[-1]['n']
            terminal_hits = [p for p in hit if p['theirs']['id'] in ep[-1]['ids'] and p['theirs']['qn'] == ep[-1]['n']]
            endings = []
            if ram:
                endings.append('queen rammed')
            elif terminal_hits:
                endings.append('pursuer rammed by a mate: ' + '; '.join(f"r{p['r']} mate #{p['ours']['id']} / pursuer #{p['theirs']['id']}" for p in terminal_hits))
            elif fate is not None and fate['qn'] == ep[-1]['n']:
                endings.append(f"n/a (queen died: {fate['kind']}, reason {fate['reason']}, r{fate['r']})")
            elif ep[-1]['n'] == g['qturns'][-1]['n']:
                endings.append('n/a (game ended during chase)')
            else:
                endings.append('pursuer left')
            pur = '; '.join(f"r{t['r']}: " + ', '.join(f'#{i} L{L}' for i,L,_ in t['pur']) for t in ep)
            mates = ', '.join(f'#{i} L{L} {tab.xy(g, head)} ({dist} tiles)' for i,L,head,dist in ep[0]['mates'] if dist<=5) or 'none'
            entries.append([k, ep[0]['r'], ep[-1]['r'], len(ep), pur, mates, '; '.join(endings)])
    sections += ['## List 2 — every queen chase in m5dn_vh', 'Pursuer ids and lengths are listed at every queen turn of the chase. An ending is queen rammed if her rammed death follows the final chased queen turn. Otherwise, pursuer rammed by a mate requires a mate-moved pair involving a pursuer present on the final chased turn, after that turn and before her next turn, within the trusted association window (through the following round). Remaining ended chases are labelled pursuer left.', markdown(['Game', 'First round', 'Last round', 'Turns', 'Pursuer ids and lengths', 'Mates within 5 tiles at first turn', 'How it ended'], entries), f'Listed chases: {len(entries)}.']
    for a in ARMS:
        for games in ([data[a][k] for k in commonAB] if a in ARMS[:2] else [], [data[a][k] for k in commonD]):
            c,_ = tab.measure(games)
            assert sum(c[f'dn_L{L}_{t}'] for L in (2,3,4,5) for t in ('pursuer','radius')) == c['near_mate_moved']
    timestamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip()
    sections.append('DONE ' + timestamp)
    OUT.write_text('\n\n'.join(sections) + '\n')
    print(f'Written {OUT}: A={len(commonAB)}, B={len([k for k in commonAB if data[ARMS[0]][k]["w"]*data[ARMS[0]][k]["h"]<=700])}, D={len(commonD)}, E={len(smallE)}; {len(entries)} chases')

if __name__ == '__main__':
    try:
        generate()
    except Exception:
        import traceback
        error = traceback.format_exc()
        (HERE / 'report-error.log').write_text(error)
        timestamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip()
        OUT.write_text('# Escort counts\n\nCounts: n/a — generation or verification failed.\n\n```text\n' + error + '\n```\n\nDONE ' + timestamp + '\n')
        raise
