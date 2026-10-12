import sys, json, subprocess
from pathlib import Path
sys.dont_write_bytecode = True
from analyze import OUT, SM, TARGET, Geo, replay, ledger, make_key, unseal

checks = []
for gid in sorted(TARGET):
    folder = SM / 'one8-k1-old'
    meta = json.loads((folder / f'game-{gid}.json').read_text())
    root = replay.load(folder / f'M{gid}.replay').root()
    lines = [s.split() for s in root.text(0).splitlines()]
    w, h = map(int, lines[0][1:3])
    geo = Geo(w, h, [tuple(map(int, s[1:4])) for s in lines if s[0] == 'EDGE'])
    assert all(c in geo.adj[n] for c, row in enumerate(geo.adj) for n in row)
    teams = {i: int(s[1]) for i, s in enumerate(s for s in lines if s[0] == 'DRAGON')}
    own = int(meta['teamAId'] != 1119)
    key = make_key(w, h, 2 if own == 0 else 1)
    cache, streams, states, total = {}, {}, [], 0
    for event in root.pointer(3):
        kind, p = event.u16(0), event.pointer(0)
        if kind == 10:
            teams[p.i32(4)] = p.u16(8)
        if kind != 12 or teams[p.i32(0)] != own:
            continue
        total += 1
        wire = p.u64(16)
        if wire not in cache:
            cache[wire] = unseal(key, wire, streams)
        message = cache[wire]
        assert message is not None
        if message >> 63 == 0:
            states.append((message >> 26) & 3)
        elif (message >> 42) & 0x7ff == 0x2b5:
            states.append((message >> 24) & 3)
    cached = json.loads((OUT / f'detail-{gid}.json').read_text())
    assert total == len(cached['pings'])
    assert states and set(states) == {0}
    checks.append(dict(gid=gid, raw_own_pings=total, raw_state_pings=len(states), states=sorted(set(states)), symmetric_geometry=True))
    print(gid, total, flush=True)

growth = []
for path in sorted(OUT.glob('ledger-*.json')):
    cached = json.loads(path.read_text())
    if not all(s[3] for s in cached['ends']):
        continue
    gid, label = cached['gid'], cached['src']
    folder = SM / (label + '-old')
    meta = json.loads((folder / f'game-{gid}.json').read_text())
    measured = ledger(label, folder / f'M{gid}.replay', meta)
    assert measured == cached, gid
    growth.append(gid)
    print('growth', gid, flush=True)
report = (OUT / 'report.md').read_text()
words = len(' '.join(s for s in report.splitlines() if not s.startswith('|')).split())
assert words < 450
result = dict(time=subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip(), sonar=checks, growth_recomputed= growth, report_words_excluding_tables=words)
(OUT / 'audit-resume.json').write_text(json.dumps(result, indent=2))
print('OK', words)
