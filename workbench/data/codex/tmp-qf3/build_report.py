import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
import runpy
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'data/analysis/ladder/dossier/local'))
from replay_format import load, point

RUNS = Path('~/meow-redteam/solo/runs')
NAMES = json.loads((HERE / 'games.json').read_text())
ARMS = ['m3b7qk_vh', 'm5q3_vh', 'm4qf_vh', 'm5qh2_vh']
AUDIT = json.loads((HERE / 'audit.json').read_text())
ARMS = [a for a in ARMS if a != 'm4qf_vh' or all(v['replay'] and v['result'] for v in AUDIT[a].values())]
sys.argv = ['qh_table.py', *ARMS]
with contextlib.redirect_stdout(io.StringIO()):
    table_module = runpy.run_path(str(HERE / 'qh_table.py'))
ROWS = {a: table_module['rows'](a) for a in ARMS}
for a in ARMS:
    assert set(ROWS[a]) == set(NAMES), (a, set(NAMES) - set(ROWS[a]))
    assert all(r['finished'] for r in ROWS[a].values()), a
    for n in NAMES:
        meta = json.loads((RUNS / a / n / 'result.json').read_text())
        assert not meta.get('bot_errors') and not meta.get('error') and not meta.get('crash'), (a, n, meta)
SUMS = {a: table_module['summ']([ROWS[a][n] for n in NAMES]) for a in ARMS}


def outnumbered(path, side):
    root = load(path).root()
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
    queen = min(i for i in bodies if teams[i] == side)
    def gap(a, b):
        dx, dy = abs(a % w-b % w), abs(a // w-b // w)
        return min(dx, w-dx), min(dy, h-dy)
    def man(a, b):
        return sum(gap(a, b))
    counts, turns = Counter(), []
    rnd, actor, cur = -1, None, None
    def finish():
        nonlocal cur
        if cur is None:
            return
        counts['turns'] += 1
        hd, end = cur['start'], cur['end']
        d0, d1 = man(hd, cur['enemy']), man(end, cur['enemy'])
        direction = 'away' if d1 > d0 else 'toward' if d1 < d0 else 'level'
        counts[direction] += 1
        cur['enemy_direction'] = direction
        if cur['mate'] is not None:
            m0, m1 = man(hd, cur['mate']), man(end, cur['mate'])
            counts['mate_available'] += 1
            counts['toward_mate'] += int(m1 < m0)
            counts['away_and_toward_mate'] += int(d1 > d0 and m1 < m0)
            cur['toward_mate'] = m1 < m0
        else:
            counts['no_mate'] += 1
        counts['no_step'] += int(cur['steps'] == 0)
        counts['multiple_steps'] += int(cur['steps'] > 1)
        counts['died'] += int(cur['died'])
        turns.append(cur)
        cur = None
    for ev in root.pointer(3):
        k, p = ev.u16(0), ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            if actor != queen:
                continue
            hd = bodies[queen][0]
            visible = [(i, b[0]) for i, b in bodies.items() if max(gap(hd, b[0])) <= 3]
            own = [(i, c) for i, c in visible if teams[i] == side]
            enemy = [(i, c) for i, c in visible if teams[i] != side]
            if len(enemy) <= len(own):
                continue
            mates = [(i, c) for i, c in own if i != queen]
            nearest = lambda heads: min(heads, key=lambda ic: (man(hd, ic[1]), ic[0]))[1]
            cur = dict(r=rnd, own=len(own), enemy_count=len(enemy), start=hd, end=hd,
                       enemy=nearest(enemy), mate=nearest(mates) if mates else None, steps=0, died=False)
        elif k == 9:
            i = p.i32(0)
            hd, tl = point(p.pointer(0)), point(p.pointer(1))
            hd, tl = hd[1]*w+hd[0], tl[1]*w+tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == queen and cur is not None:
                    cur['end'] = hd
                    cur['steps'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(c[1]*w+c[0] for c in map(point, p.pointer(z)))
                teams[i] = p.u16(8)
        elif k == 11:
            i = p.i32(0)
            if i == queen and cur is not None:
                cur['died'] = True
            bodies.pop(i)
    finish()
    assert counts['away'] + counts['toward'] + counts['level'] == counts['turns']
    return dict(counts), turns


SMALL, DETAILS = {}, {}
for a in ('m3b7qk_vh', 'm5q3_vh'):
    pooled, DETAILS[a] = Counter(), {}
    for n in NAMES:
        path = RUNS / a / n / 'game.replay'
        root = load(path).root()
        result = root.pointer(4)
        assert result.bit(0)
        winner = result.u16(6) if result.u16(4) == 1 else None
        assert winner is None or f'winner={winner}' in AUDIT[a][n]['result_text']
        counts, turns = outnumbered(path, int(n[-1]))
        pooled.update(counts)
        DETAILS[a][n] = dict(counts=counts, turns=turns)
    SMALL[a] = dict(pooled)
(HERE / 'outnumbered.json').write_text(json.dumps(DETAILS, indent=2)+'\n')

lines = ['# QF3 여왕 기보 집계', '',
         '`m5q3_vh`의 8개 지도·시드 × 양쪽 진영 = 16판. 모든 열은 같은 16판이며 상대는 `m3hunt`이다.', '',
         '기존 표는 복사한 `qh_counts.py`·`qh_table.py`의 집계와 반올림을 그대로 사용했다. 거리 tiles는 토러스 맨해튼, steps는 몸을 무시한 열린 간선·포털 경로다. own3/own5는 여왕을 제외한 아군 머리다. e3/추격은 적 여왕을 제외한다. depth/home-rank는 4라운드마다, 나머지 구간 평균은 여왕 턴으로 가중한다. 조기 종료 판의 r100/r300 상태는 기존 스크립트대로 마지막 상태를 사용한다.', '',
         '| measure | '+' | '.join(ARMS)+' |', '|---|'+'---|'*len(ARMS)]
for key in SUMS[ARMS[0]]:
    lines.append('| '+key+' | '+' | '.join(str(SUMS[a][key]) for a in ARMS)+' |')
lines += ['', '각 arm 집계 판수: '+', '.join(f'{a} {len(ROWS[a])}/16' for a in ARMS)+'.']
missing = [f'{a}/{n}: '+', '.join(k+' 없음' for k in ('replay', 'result') if not v[k]) for a, games in AUDIT.items() for n, v in games.items() if not v['replay'] or not v['result']]
lines += ['누락: '+('; '.join(missing) if missing else '없음')+'.',
          '미완료 또는 집계 실패: 없음.']
if 'm4qf_vh' not in ARMS:
    available = sum(v['replay'] and v['result'] for v in AUDIT['m4qf_vh'].values())
    lines += [f'`m4qf_vh`는 대상 중 기보·결과가 있는 판이 {available}/16판이므로 열에서 제외했고 집계하지 않았다.']
lines += ['', '첫 갈림은 복사한 `qh_div.py`의 순서대로 이동·분열·죽음 사건을 비교한 원시 라운드다.', '']
lines += ['- '+s for s in (HERE / 'first-div.txt').read_text().splitlines()]
lines += ['', '판별 결과 (`result.txt` 원문):', '']
for n in NAMES:
    for a in ARMS:
        lines.append('- '+n+' — '+a+': '+ROWS[a][n]['result'])
lines += ['', '## 적 머리가 더 많은 턴의 이동', '',
          '턴 시작의 토러스 7×7 시야(각 축 거리 ≤3)에서 적 머리 수 > 아군 머리 수인 여왕 턴만 센다. 아군에는 여왕 자신, 적에는 적 여왕을 포함한다. 가장 가까운 적·아군은 그 시야 안에서 토러스 맨해튼 거리로 고르고, 동률은 낮은 id로 정한다. 목표 머리의 위치는 턴 시작 위치에 고정한다. 턴 시작에서 마지막으로 기록된 이동 머리 위치까지의 순거리 변화를 센다(다중 걸음 포함). 이동 사건이 없는 턴은 거리 유지에 포함하며, 죽는 충돌 시도의 기록되지 않은 목적지는 추정하지 않는다. 아군에게 가까워짐은 적 거리의 세 분류와 중복될 수 있다.', '',
          '| measure | m3b7qk_vh | m5q3_vh |', '|---|---|---|']
for key, label in [('turns', '해당 턴 수'), ('away', '가장 가까운 적에게서 멀어짐'), ('toward', '가장 가까운 적에게 가까워짐'), ('level', '가장 가까운 적과 거리 유지'), ('toward_mate', '가장 가까운 아군에게 가까워짐 (중복 집계)'), ('away_and_toward_mate', '적에게서 멀어지며 아군에게 가까워짐'), ('mate_available', '시야에 다른 아군 머리 있음'), ('no_mate', '시야에 다른 아군 머리 없음'), ('no_step', '머리 이동 사건 없음 (거리 유지에 포함)'), ('multiple_steps', '머리 이동 사건 2개 이상'), ('died', '해당 턴에 여왕 죽음')]:
    lines.append('| '+label+' | '+' | '.join(str(SMALL[a].get(key, 0)) for a in ('m3b7qk_vh', 'm5q3_vh'))+' |')
lines += ['', '## 5줄 요약', '']
b, q = SUMS['m3b7qk_vh'], SUMS['m5q3_vh']
div = (HERE / 'first-div.txt').read_text().splitlines()
lines += [f'같은 16판 중 사건이 달라진 판은 {sum("first differs" in s for s in div)}판, 동일한 판은 {sum("identical" in s for s in div)}판이다.  ',
          f'여왕 생존 r100/r150/종료는 기준 {b["queen alive r100"]}, {b["queen alive r150"]}, {b["queen alive end"]} → QF3 {q["queen alive r100"]}, {q["queen alive r150"]}, {q["queen alive end"]}이다.  ',
          '여왕 사망 rammed/boxed/dead_end/into_head는 기준 '+ '/'.join(b['died: '+k] for k in ('rammed','boxed','dead_end','into_head'))+' → QF3 '+ '/'.join(q['died: '+k] for k in ('rammed','boxed','dead_end','into_head'))+'이다.  ',
          f'추격 수는 기준 {b["chases a game"]} → QF3 {q["chases a game"]}, 추격당 턴은 {b["turns per chase"]} → {q["turns per chase"]}, 판당 여왕 진주 섭취는 {b["pearls she eats a game"]} → {q["pearls she eats a game"]}이다.  ',
          f'적 머리가 더 많은 턴은 기준 {SMALL["m3b7qk_vh"]["turns"]} → QF3 {SMALL["m5q3_vh"]["turns"]}, 적에게서 멀어짐은 {SMALL["m3b7qk_vh"].get("away",0)} → {SMALL["m5q3_vh"].get("away",0)}, 아군에게 가까워짐은 {SMALL["m3b7qk_vh"].get("toward_mate",0)} → {SMALL["m5q3_vh"].get("toward_mate",0)}이다.']
(REPO / 'data/codex/out-qf3.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'summaries': SUMS, 'outnumbered': SMALL}, ensure_ascii=False, indent=2))
