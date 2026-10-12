"""sig.py <run> ...: games with the traced bot on BOTH sides. Per side: the round the other side's queen died, the first local
proof (see) and its rule, the round our queen knew, and every see/know logged while that queen was still alive (EARLY).
Run from the repo root: python3 -B data/codex/astra/qdead-opus/sig.py qd_dkdk"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'

tot = Counter()
for run in sys.argv[1:]:
    for folder in sorted((RUNS / run).glob('*-seed*-side?')):
        if not (folder / 'result.txt').exists():
            continue
        root = replay.load(folder / 'game.replay').root()
        teams, n = {}, 0
        for line in root.text(0).splitlines():
            q = line.split()
            if q and q[0] == 'DRAGON':
                teams[n] = int(q[1])
                n += 1
        queens = {t: min(i for i in teams if teams[i] == t) for t in set(teams.values())}
        died, alive, rnd, last = {}, set(teams), -1, {}
        for ev in root.pointer(3):
            k = ev.u16(0)
            p = ev.pointer(0)
            if k == 0:
                rnd = p.i32(0)
            elif k == 10:
                teams[p.i32(4)] = p.u16(8)
            elif k == 11:
                died[p.i32(0)] = rnd
        logs = [l.split() for l in Path(str(folder) + '.qdk').read_text().splitlines()]
        for t, q in sorted(queens.items()):
            foe = [x for tt, x in queens.items() if tt != t][0]
            rf = died.get(foe)
            mine = [[l[0]] + [int(x) for x in l[1:]] for l in logs if teams.get(int(l[2])) == t]
            see = [l for l in mine if l[0] == 'see']
            rule = Counter(l[4] for l in mine if l[0] == 'rule')
            knowq = [l[1] for l in mine if l[0] == 'knowq']
            know = [l for l in mine if l[0] in ('know', 'knowq')]
            unknow = [l for l in mine if l[0] == 'unknow']
            early = [l for l in see + know if rf is None or l[1] < rf]
            ownalive = died.get(q) is None or (rf is not None and died[q] > rf)
            tot['sides'] += 1
            tot['their queen died'] += rf is not None
            tot['... and a dragon proved it'] += rf is not None and bool(see)
            tot['... and our living queen learned it'] += rf is not None and bool(knowq)
            tot['their queen died while ours was alive'] += rf is not None and ownalive
            tot['EARLY see/know lines (queen still alive)'] += len(early)
            tot['unknow lines'] += len(unknow)
            for r, c in rule.items():
                tot['see by new rule %d' % r] += c
            tot['see by the old rule'] += len(see) - sum(rule.values())
            print(' %-30s team %d | their queen dies %s | our queen dies %s | see %d first %s new rules %s | knowers %d | our queen knew %s | unknow %d | EARLY %d' % (
                folder.name.replace('gx_', '')[:30], t, rf, died.get(q), len(see), see[0][1] if see else None, dict(rule), len(know),
                knowq[0] if knowq else None, len(unknow), len(early)))
for k, v in tot.items():
    print('  %-48s %d' % (k, v))
