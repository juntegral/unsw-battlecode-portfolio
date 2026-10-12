#!/usr/bin/env python3
"""Analyse every game of ours that came in since the last round (jun, 2026-10-09 04:08 KST: every 30 minutes, lost games deeper).
  sweep_games.py --round     start a round: Astra analysts on the lost games (5 a job), one sol job on the wins
  sweep_games.py --synth     for every round whose reports are all in and that has no synthesis yet, start the synthesis job
Rounds: data/codex/astra/sweep/<HHMM>/ (manifest.json, <job>/report.md, synth/report.md). Ledger: data/codex/astra/sweep/ledger.txt."""
import json, sys, glob, os, subprocess, time, collections
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
BASE = 'data/codex/astra/sweep'
LEDGER = BASE + '/ledger.txt'
FIRST = '2026-10-08T18:40'
def launch(name, brief, model):
    subprocess.Popen(['nohup', 'tools/cx.sh', 'data/codex/astra-%s.log' % name.replace('/', '-'), '-m', model, '-c', 'model_reasoning_effort=high',
                      '-s', 'workspace-write', '-C', ROOT, 'Follow the brief in %s exactly.' % brief],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
def games():
    G = {}
    for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/one*-old/game-*.json'):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if 1119 not in (j.get('teamAId'), j.get('teamBId')) or (j.get('completedAt') or '') < FIRST:
            continue
        d = os.path.dirname(f)
        if not os.path.exists('%s/M%d.replay' % (d, j['id'])):
            continue
        a = j['teamAId'] == 1119
        co, ct = (j.get('eloChangeA'), j.get('eloChangeB')) if a else (j.get('eloChangeB'), j.get('eloChangeA'))
        eo, et = (j.get('teamAElo'), j.get('teamBElo')) if a else (j.get('teamBElo'), j.get('teamAElo'))
        gap = (eo - (co or 0)) - (et - (ct or 0)) if eo is not None and et is not None and j.get('ranked') else None
        g = dict(id=j['id'], dir=d, map=j['mapName'], side='A' if a else 'B', ranked=bool(j.get('ranked')),
                 opp=j['teamBName'] if a else j['teamAName'], opp_id=j['teamBId'] if a else j['teamAId'],
                 win=j.get('winner') == ('a' if a else 'b'), at=(j.get('completedAt') or '')[:16], gap=gap,
                 label=os.path.basename(d) if 'smoke' in d else 'ranked')
        if j['id'] not in G or 'smoke' in d:
            G[j['id']] = g
    return G
def versions():
    v = {}
    if os.path.exists('data/online/smoke/versions.tsv'):
        for l in open('data/online/smoke/versions.tsv'):
            p = l.split()
            if len(p) == 2:
                v[p[0]] = p[1]
    return v
def bot_of(g):
    try:
        from ladder_replay import replay
        root = replay.load('%s/M%d.replay' % (g['dir'], g['id'])).root()
        return root.text(1 if g['side'] == 'A' else 2).strip()
    except Exception:
        return '?'
def line(g):
    s = '- game %d, `%s/M%d.replay`, played by our bot %s (%s), map %s, we are side %s, against %s (team %d), %s' % (
        g['id'], g['dir'], g['id'], g.get('bot', '?'), g.get('ver', '?'), g['map'], g['side'], g['opp'], g['opp_id'], 'ranked' if g['ranked'] else 'test set ' + g['label'])
    if g['gap'] is not None and g['gap'] >= 100 and not g['win']:
        s += ', **LOST TO A TEAM RATED %d BELOW US: cause and fix are mandatory**' % g['gap']
    return s
COMMON = '''Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `%s/`. Report `%s/report.md`.'''
def start_round():
    os.makedirs(BASE, exist_ok=True)
    seen = set(open(LEDGER).read().split()) if os.path.exists(LEDGER) else set()
    new = [g for g in games().values() if str(g['id']) not in seen]
    if not new:
        print('no new games')
        return
    V = versions()
    for g in new:
        g['bot'] = bot_of(g)
        g['ver'] = V.get(g['bot'], 'unknown version')
    rid = time.strftime('%H%M')
    rdir = '%s/%s' % (BASE, rid)
    os.makedirs(rdir, exist_ok=True)
    losses = sorted([g for g in new if not g['win']], key=lambda g: (g['ver'], g['opp'], g['id']))
    wins = sorted([g for g in new if g['win']], key=lambda g: (g['ver'], g['opp'], g['id']))
    jobs = []
    for i in range(0, len(losses), 3):
        chunk = losses[i:i + 3]
        name = 'loss%d' % (i // 3 + 1)
        jdir = '%s/%s' % (rdir, name)
        os.makedirs(jdir, exist_ok=True)
        brief = '%s/brief.md' % jdir
        open(brief, 'w').write('# Astra analyst: sweep %s %s (lost games)\n\n' % (rid, name) + COMMON % (jdir, jdir) + '''

The team analyses every game as it comes in. These are LOST games; each needs its cause, not a summary.
%s
For each game: 1. how it was decided (queen / longest / total / wiped out), the final state of both sides, and the round it turned
for good; 2. the single event or habit of ours that lost it, with rounds and dragon ids (if our queen died: the round, the cause,
her last three own turns drawn as 7 by 7 boards, what the attacker did; if she lived and was shorter: why she did not grow; if
we were outgrown: from which round and what our dragons were doing instead of eating; if the longest decided: what happened to
our long ones); 3. which LIVE switch in the bot that played was meant to prevent it and the exact condition in the code that
failed, or "nothing covers this"; 4. after our queen died, did any dragon of ours get within 5 steps of their queen, and if not,
where was she.
Then: the causes ranked by how many of these games they explain, and for each a card: the rule, the lines, the existing switch
if one does it (paste form `CONST:value`), the count that would show it works. Mark every card as NEW, BEING BUILT or
LIVE-BUT-FAILED against CARDS.md. Under 600 words plus tables; first three lines = the top cause, its card, how sure.
''' % '\n'.join(line(g) for g in chunk))
        launch('sweep-%s-%s' % (rid, name), brief, 'gpt-6-astra')
        jobs.append(name)
    for i in range(0, len(wins), 12):
        chunk = wins[i:i + 12]
        name = 'win%d' % (i // 12 + 1)
        jdir = '%s/%s' % (rdir, name)
        os.makedirs(jdir, exist_ok=True)
        brief = '%s/brief.md' % jdir
        open(brief, 'w').write('# Analyst: sweep %s %s (won games)\n\n' % (rid, name) + COMMON % (jdir, jdir) + '''

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
%s
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
''' % '\n'.join(line(g) for g in chunk))
        launch('sweep-%s-%s' % (rid, name), brief, 'gpt-6.1-sol')
        jobs.append(name)
    json.dump(dict(round=rid, jobs=jobs, games=[g['id'] for g in new], losses=len(losses), wins=len(wins), started=time.strftime('%H:%M:%S')),
              open(rdir + '/manifest.json', 'w'))
    with open(LEDGER, 'a') as f:
        for g in new:
            f.write('%d\n' % g['id'])
    weak = [g for g in losses if g['gap'] is not None and g['gap'] >= 100]
    print('round', rid, 'by version', dict(collections.Counter(g['ver'] for g in new)), 'losses', len(losses), 'wins', len(wins), 'jobs', jobs, 'weak-team losses', [(g['id'], g['map'], g['opp']) for g in weak])
def synth():
    for mf in sorted(glob.glob(BASE + '/*/manifest.json')):
        m = json.load(open(mf))
        rdir = os.path.dirname(mf)
        if os.path.exists(rdir + '/synth/brief.md'):
            continue
        done = [j for j in m['jobs'] if os.path.exists('%s/%s/report.md' % (rdir, j))]
        age = time.time() - os.path.getmtime(mf)
        if len(done) < len(m['jobs']) and age < 1500:
            continue
        if not done:
            continue
        os.makedirs(rdir + '/synth', exist_ok=True)
        open(rdir + '/synth/brief.md', 'w').write('''# Astra analyst: sweep %s synthesis

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Rules), `data/codex/astra/CARDS.md`, and every report of this round:
%s
Write only under `%s/synth/`; report `%s/synth/report.md`, under 350 words plus one table. The lead reads ONLY this file, so it
must stand alone. Do not re-analyse replays; check a number only where two reports disagree.
1. One table: cause, games it explains this round (ids), status against CARDS.md (NEW / BEING BUILT / LIVE-BUT-FAILED), the card
   in one line (paste form `CONST:value` if an existing switch does it, otherwise the rule and the lines), which report has the detail.
   Ranked by games explained; merge causes that are the same thing under different names.
2. Losses to teams rated 100 or more below us: each game id with its cause and whether a listed card covers it.
3. Live fixes that failed this round, each with the condition that failed.
4. From the won games: what is working, and the weakest point.
5. The three things the lead should build or switch next, in order.
''' % (m['round'], '\n'.join('- `%s/%s/report.md`' % (rdir, j) for j in done), rdir, rdir))
        launch('sweep-%s-synth' % m['round'], rdir + '/synth/brief.md', 'gpt-6-astra')
        print('synth started for round', m['round'], 'reports', len(done), 'of', len(m['jobs']))
def pending():
    seen = set(open(LEDGER).read().split()) if os.path.exists(LEDGER) else set()
    new = [g for g in games().values() if str(g['id']) not in seen]
    print(sum(1 for g in new if g['ranked'] and not g['win']), len(new))
if __name__ == '__main__':
    if '--pending' in sys.argv:
        pending()
    if '--synth' in sys.argv:
        synth()
    if '--round' in sys.argv:
        start_round()
