"""How the queens that died at length 2 got to 2 (split of a 4-long queen, a paid segment, or other), and how long before death.
Also: losses in which the enemy queen died first, by the length of our queen at her death. Usage: q2.py"""
import json
from collections import Counter
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in ('h2h_mDone11_v8', 'h2h_mDone10_v8'):
    T = [json.loads(l) for l in (HERE / ('turns-%s.jsonl' % arm)).read_text().splitlines()]
    S = {json.loads(l)['folder']: json.loads(l) for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines()}
    print(arm, len(T), 'games')
    for s, nm in ((0, 'NEW'), (1, 'old')):
        how = Counter()
        conv = Counter()
        for g in T:
            if g['folder'] not in S:
                continue
            q = g['qlen'][s]; o = g['qlen'][1 - s]
            dead = [r for r in range(1, len(q)) if q[r - 1] and not q[r]]
            if not dead:
                continue
            r = dead[0]; L = q[r - 1]
            foe_dead = not o[r - 1]
            res = S[g['folder']]['result']
            lost = (res == 'loss') if s == 0 else (res == 'win')
            if foe_dead and lost:
                conv['enemy queen already dead, game lost, own queen died at length %s' % ('5+' if L >= 5 else L)] += 1
            if L != 2:
                continue
            k = r - 1
            while k > 0 and q[k - 1] == 2:
                k -= 1
            prev = q[k - 1] if k > 0 else 2
            cause = {4: 'split of a 4-long queen', 3: 'paid 3 to 2', 2: 'started at 2'}.get(prev, 'other')
            how[(cause, 'within 2 rounds' if r - k <= 2 else '3+ rounds before')] += 1
        print('  %s queen died at 2:' % nm, dict(sorted(how.items())))
        print('  %s:' % nm, dict(sorted(conv.items())))
