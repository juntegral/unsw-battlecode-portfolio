#!/usr/bin/env python3
"""Ranked games lost to a team rated 100 or more below us (jun's rule, 2026-10-09 02:52 KST).
  weak_watch.py --list            print every such game collected so far
  weak_watch.py --new             print the ones not yet in the ledger, add them, and start one Codex analyst per battle
Reads data/online/live-one1/b*/game-*.json (written by collect.sh). Ledger: data/online/live-one1/weak-handled.txt."""
import json, sys, glob, os, subprocess, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
LEDGER = 'data/online/live-one1/weak-handled.txt'
GAP = 100
def games():
    out = []
    for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json')):
        j = json.load(open(f))
        if not j.get('ranked') or 1119 not in (j.get('teamAId'), j.get('teamBId')):
            continue
        a = j['teamAId'] == 1119
        ours, theirs = (j.get('teamAElo'), j.get('teamBElo')) if a else (j.get('teamBElo'), j.get('teamAElo'))
        co, ct = (j.get('eloChangeA'), j.get('eloChangeB')) if a else (j.get('eloChangeB'), j.get('eloChangeA'))
        if ours is not None and theirs is not None:
            ours, theirs = ours - (co or 0), theirs - (ct or 0)
        if ours is None or theirs is None or ours - theirs < GAP:
            continue
        if j.get('winner') == ('a' if a else 'b'):
            continue
        out.append(dict(game=j['id'], battle=os.path.basename(os.path.dirname(f)), map=j['mapName'], ours=ours, theirs=theirs,
                        opp=j['teamBName'] if a else j['teamAName'], opp_id=j['teamBId'] if a else j['teamAId'],
                        change=j.get('eloChangeA') if a else j.get('eloChangeB'), sub=j.get('submissionAId') if a else j.get('submissionBId'),
                        at=j.get('completedAt', '')[:16], side='A' if a else 'B'))
    return out
def main():
    gs = games()
    if '--list' in sys.argv:
        for g in gs:
            print(g)
        return
    seen = set(open(LEDGER).read().split()) if os.path.exists(LEDGER) else set()
    new = [g for g in gs if str(g['game']) not in seen]
    by = collections.defaultdict(list)
    for g in new:
        by[g['battle']].append(g)
    for battle, lst in by.items():
        name = 'weak-' + battle
        lines = '\n'.join('- game %d, map %s, we are side %s, our rating %d against %d (%s, team %d), rating change %s, our submission %s' % (
            g['game'], g['map'], g['side'], g['ours'], g['theirs'], g['opp'], g['opp_id'], g['change'], g['sub']) for g in lst)
        brief = 'data/codex/brief-astra-%s.md' % name
        open(brief, 'w').write('''# Astra analyst: %s

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `%s`. The team's standing rule: every game lost to a team rated 100 or
more below us gets its cause found and fixed. Earlier findings on such losses: `data/codex/astra/weak/report.md` (all ten earlier
ones had our queen dead; in six the enemy queen lived), `data/codex/astra/qwq3/report.md`.
Lost games in `data/online/live-one1/%s/` (replays `M<game id>.replay`); the bot that played is the submission id below
(21086 = one7 `data/online/smoke/one7-bot/main.cpp`, 21033 = one6, 20980 = one5; a later id is a later version in
`data/online/smoke/one*-bot/`, see `docs/SESSION-STATE.md` grep "라이브 = one"):
%s
For each game: 1. how it was decided and the round it turned for good; dragons, total length, longest and queen length of both
sides every 25 rounds; 2. the single event or habit of ours that lost it (our queen's death: round, cause, her last three turns
drawn; a pin, a pocket, a portal loop, standing still, feeding the enemy, never reaching their queen), with rounds and dragon
ids; 3. which switch of the bot that played was supposed to prevent it and why it did not (read the code; say the condition that
failed); 4. whether the same thing is in other games of the same submission (count over its sets).
Then one card per distinct cause: the rule, the lines, whether an existing switch does it (paste form `CONST:value`), the replay
count that shows it works. Report under 500 words plus tables; first three lines = cause, card, how sure.
''' % (name, name, battle, lines))
        subprocess.Popen(['nohup', 'tools/cx.sh', 'data/codex/astra-%s.log' % name, '-m', 'gpt-6-astra', '-c', 'model_reasoning_effort=high',
                          '-s', 'workspace-write', '-C', ROOT, 'Follow the brief in %s exactly.' % brief],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        print('started', name, [(g['game'], g['map'], g['opp'], g['ours'], g['theirs'], g['sub']) for g in lst])
    if new and '--new' in sys.argv:
        with open(LEDGER, 'a') as f:
            for g in new:
                f.write('%d\n' % g['game'])
if __name__ == '__main__':
    main()
