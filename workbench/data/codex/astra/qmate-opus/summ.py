"""qmate-opus: per game, on against off: queen death (round, class, free cells), pearls and dragons at r100, result,
first round where the on and off games' length tables differ (the bot's log lines are not kept in local replays).
Usage (repo root): python3 -B data/codex/astra/qmate-opus/summ.py"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
sys.path.insert(0, 'data/codex/astra/qmate-opus')
from pathlib import Path
from o1_local import rows, snap
from qdeath import scan as qscan
from qcls import cls
RUNS = Path.home() / 'meow-redteam/solo/runs'
for opp in ('mD17', 'm3base'):
    print('== against', opp)
    print('%-24s %-3s %4s %4s %4s %4s %-34s %s' % ('map', 'arm', 'p100', 'd100', 'u100', 'div', 'result', 'queen death: round class | detail | f1 f0a'))
    got = {}
    for arm in ('qm_17', 'qm_on'):
        for g in rows('qm_%s_%s' % (arm, opp)):
            got[g['folder'], arm] = g
    for folder_name in sorted({k[0] for k in got}):
        pair = [got.get((folder_name, a)) for a in ('qm_17', 'qm_on')]
        div = '-'
        if all(pair):
            a, b = pair
            div = next((r for r in range(0, 501) if a['snaps'].get(str(r)) != b['snaps'].get(str(r))), 'same')
        for arm, g in zip(('off', 'on'), pair):
            if not g:
                continue
            folder = RUNS / ('qm_qm_%s_%s' % ('17' if arm == 'off' else 'on', opp)) / folder_name
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder_name)
            p100 = sum(1 for e in g['eats'] if e[1] == 0 and 0 < e[0] <= 100)
            s = snap(g, 100)[0]
            res = (folder / 'result.txt').read_text().strip().replace('\n', ' ')
            res = re.sub(r'rounds=.*', '', res).replace('winner=', 'w').replace('how=', '')[:34]
            q = qscan(folder / 'game.replay', int(m[3]))
            dd = []
            for d in q['deaths']:
                k, x = cls(d)
                walls = [w[0] + (':%s%s' % (w[3][0], w[2]) if len(w) > 3 else '') for w in (d.get('start1') or [])]
                dd.append('r%s %s | %s | f1=%s f0a=%s %s' % (d.get('r'), k[:34], x[:30], d.get('f1'), d.get('f0a'), ','.join(walls)))
            print('%-24s %-3s %4d %4d %4d %4s %-34s %s' % (m[1][:24], arm, p100, s[0], s[1], div, res, ' ;; '.join(dd) or 'alive, final len %s' % q.get('qlen')))
