#!/usr/bin/env python3
"""Render the Korean observation from full-population tables and fixed films.

Writes exactly research/observations/elite-counterplay.md. Never writes the final
SUMMARY.txt marker: it must be written separately, after verification. Numeric
tables are generated from aggregate.json; cases.py contains the human readings.
Run with guard.py. No original input or bot is changed.
"""
from pathlib import Path
from collections import Counter
import csv
import json

from cases import CASES

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / '.cache/elite-counterplay'
OUT = ROOT / 'research/observations/elite-counterplay.md'
A = json.loads((C / 'aggregate.json').read_text())
M = json.loads((C / 'manifest.json').read_text())
X = json.loads((C / 'auxiliary.json').read_text())
S = json.loads((C / 'selection.json').read_text())
NAMES = M['names']
TEAM_ORDER = ['306', '70', '20', '801', '264', '46', '545']
MAP_ORDER = ['Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy',
             'Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']
PHASES = ['p0:0–99', 'p1:100–249', 'p2:250–349', 'p3:350–449', 'p4:450–499']
SIG = ['swarm50', 'homeRaid', 'kingRam', 'sprintKingRam', 'lateResupply', 'kingFeed']
CLASSES = ['E1', 'E2', 'E3', 'E4', 'K5', 'I6', 'C7', 'G8']
TASK = {t['key']: t for t in M['tasks']}


def fmt(x, places=1):
    if x is None:
        return '—'
    if isinstance(x, int):
        return f'{x:,}'
    return f'{x:.{places}f}'


def seq(a):
    return ' / '.join(fmt(v) for v in a)


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |',
                      *['| ' + ' | '.join(str(x) for x in row) + ' |' for row in rows]])


def relative_link(label, path):
    return f'[{label}](../../{path})'


def film_link(key):
    t = TASK[key]
    label = f"{t.get('battleId', t.get('set'))} / game {t['gameId']}"
    return relative_link(label, t['file'])


def wl(t):
    return f"{t['W']} / {t['L']} / {t['D']}"


def output_team(tid, number):
    t = A['teams'][tid]
    c = A['contrast'][tid]
    r = A['reference'][tid]
    x = X['byTeam'][tid]
    case = CASES[tid]
    b = r['seats']['B']
    parts = [f"## {number}. {tid} — {NAMES[tid]}\n",
             f"**관측 서명: {case['signature']}.**\n",
             f"**[사실]** {case['facts']}\n",
             f"**[해석]** {case['interpretation']}\n"]
    parts.append('### 전체 부류와 지도 가족\n\n[사실] 아래는 primary 전부다. 부류는 중복 없이 세었고 표에 0도 남겼다.\n\n' +
                 table(['N', '승/패/무', *CLASSES], [[60, wl(t), *[t['classes'].get(k, 0) for k in CLASSES]]]) + '\n')
    parts.append(table(['지도 가족', 'N', '승/패/무', '전멸 N', '전멸 r 중앙값', '끝 최장 평균 우리/상대',
                        'r50 머릿수 우리/상대', 'r100 머릿수 우리/상대'],
                       [[label, v['N'], wl(v), v['eliminated'], fmt(v['elimMedian']),
                         f"{fmt(v['finalUsMean'])} / {fmt(v['finalEnemyMean'])}",
                         f"{fmt(v['u50'], 2)} / {fmt(v['e50'], 2)}", f"{fmt(v['u100'], 2)} / {fmt(v['e100'], 2)}"]
                        for kind, label in [('elim', '전멸형'), ('r500', '500형')]
                        for v in [A['families'][tid][kind]]]) + '\n')
    parts.append('[사실] 가족별 자연 진주 합. 각 칸은 **우리/상대**이며 전멸 뒤의 국면은 0이다.\n\n' +
                 table(['지도 가족', 'N', *PHASES],
                       [[label, v['N'], *[f"{fmt(v['intakeUs'][p])} / {fmt(v['intakeEnemy'][p])}" for p in range(5)]]
                        for kind, label in [('elim', '전멸형'), ('r500', '500형')]
                        for v in [A['families'][tid][kind]]]) + '\n')
    parts.append('[사실] 가족별 사망과 박힘의 국소 조건. 아군/적 머릿수는 피해자와 직접 충돌 상대를 제외한 사망 순간 값이다.\n\n' +
                 table(['지도 가족', 'N판 / N사망', '박힘/갇힘/자해/아군 머리', '사망 p0/p1/p2/p3/p4',
                        '가해 L 평균(박힘 N)', '박힘 d3/d8 평균', '킹 박힘/그중 질주'],
                       [[label, f"{v['N']} / {fmt(v['deaths'])}",
                         seq([v['causes'].get(k, 0) for k in ['rammed', 'trap', 'sac', 'allyHead']]),
                         seq([v['deathPhases'].get(str(p), 0) for p in range(5)]),
                         f"{fmt(v['ramKillerMean'], 2)} ({v['rammed']})", f"{fmt(v['ramD3Mean'], 2)} / {fmt(v['ramD8Mean'], 2)}",
                         f"{v['kingRams']} / {v['kingSprint']}"]
                        for kind, label in [('elim', '전멸형'), ('r500', '500형')]
                        for v in [A['families'][tid][kind]]]) + '\n')
    parts.append('### 지도별 전부: 결과·섭취·사망·영토\n\n[사실] 지도마다 W5–W10 **N=6**이다. 전멸 라운드 중앙값은 해당 지도에서 실제 전멸한 판만의 값이다. 끝 최장은 전멸 0을 포함한 경기 평균이다.\n\n' +
                 table(['지도', 'N', '승/패/무', '전멸 N', '전멸 r 중앙값', '끝 최장 평균 우리/상대', '킹 박힘/그중 질주'],
                       [[m, v['N'], wl(v), v['eliminated'], fmt(v['elimMedian']),
                         f"{fmt(v['finalUsMean'])} / {fmt(v['finalEnemyMean'])}", f"{v['kingRams']} / {v['kingSprint']}"]
                        for m in MAP_ORDER for v in [A['maps'][tid][m]]]) + '\n')
    parts.append('[사실] 지도별 자연 진주 합, 각 칸 **우리/상대**. 시간당·턴당 비율이 아닌 해당 N판의 실제 섭취 개수다.\n\n' +
                 table(['지도', 'N', *PHASES, '전 국면 합 우리/상대'],
                       [[m, v['N'], *[f"{fmt(v['intakeUs'][p])} / {fmt(v['intakeEnemy'][p])}" for p in range(5)],
                         f"{fmt(sum(v['intakeUs']))} / {fmt(sum(v['intakeEnemy']))}"]
                        for m in MAP_ORDER for v in [A['maps'][tid][m]]]) + '\n')
    parts.append('[사실] 아래 원인은 장부의 배타적 원인이다. `S` 원시 자기 충돌은 이와 겹치는 별도 축이다. `d3/d8`와 가해 길이 평균은 **박힘 피해만**의 평균이고, 다른 원인의 같은 지표와 국면별 값은 [death-strata.csv](../../.cache/elite-counterplay/death-strata.csv)에 모두 있다.\n\n' +
                 table(['지도', 'N판 / N사망', '박힘/갇힘/자해', '우리가 박음/아군 머리/적 몸/질주 길이소진', '원시 자기 충돌 S(중복 축)',
                        '사망 p0/p1/p2/p3/p4', '박힘 가해 L 평균', '박힘 d3/d8 평균'],
                       [[m, f"{v['N']} / {fmt(v['deaths'])}",
                         seq([v['causes'].get(k, 0) for k in ['rammed', 'trap', 'sac']]),
                         seq([v['causes'].get(k, 0) for k in ['ram', 'allyHead', 'enemyBody', 'sprintDeath']]),
                         v['rawReasons'].get('S', 0),
                         seq([v['deathPhases'].get(str(p), 0) for p in range(5)]), fmt(v['ramKillerMean'], 2),
                         f"{fmt(v['ramD3Mean'], 2)} / {fmt(v['ramD8Mean'], 2)}"]
                        for m in MAP_ORDER for v in [A['maps'][tid][m]]]) + '\n')
    parts.append('[사실] 같은 출발 영토 기준으로 먹은 위치. 네 칸 모두 순서가 **우리 영토 / 중립 / 상대 영토**다. 두 팀이 먹는 땅의 순서를 바꾸지 않았다. 자연과 사망 드롭은 분리했다.\n\n' +
                 table(['지도', 'N', '우리 자연', '상대 자연', '우리 사망 드롭', '상대 사망 드롭'],
                       [[m, v['N'], seq([v['usOwn'], v['usNeutral'], v['usEnemy']]),
                         seq([v['enemyOur'], v['enemyNeutral'], v['enemyOwn']]), seq(v['dropTerrUs']),
                         seq(v['dropTerrEnemy'][::-1])]
                        for m in MAP_ORDER for v in [A['maps'][tid][m]]]) + '\n')
    parts.append(f"[사실] 전 지도 {t['N']}판의 박힘 {fmt(t['rammed'])}회 중 질주 {fmt(t['sprintRammed'])}회다. "
                 f"가해 L≤3은 {fmt(x['rammedKillerAtMost3'])}/{fmt(t['rammed'])}, d3<0은 {fmt(t['ramD3Negative'])}/{fmt(t['rammed'])}, "
                 f"d8<0은 {fmt(t['ramD8Negative'])}/{fmt(t['rammed'])}다. 실질 킹 사망 원인: " +
                 ', '.join(f'{k} {v}' for k, v in sorted(x['kingDeathCauses'].items())) + '. ' +
                 f"킹 박힘의 피해 길이 평균 {fmt(t['kingLenSum']/t['kingRams'], 2)}, 가해 길이 평균 {fmt(t['kingKillerSum']/t['kingRams'], 2)}. "
                 f"r400 이후 킹 박힘 {t['kingRamLate']}회. 짧은 질주 접근 대리 사건 {x['approachingRaidProxyN']}회는 사냥 의도·성공으로 세지 않았다.\n")
    parts.append(f"[사실] 대비 시대 {c['N']}판은 승/패/무 {wl(c)}, 전멸 {c['eliminated']}/{c['N']}, "
                 f"킹 박힘 {c['kingRams']}회·질주 {c['kingSprint']}회다. primary의 대응 수는 "
                 f"{t['eliminated']}/{t['N']}, {t['kingRams']}회·{t['kingSprint']}회다. 같은 시드의 처리 비교가 아니다.\n")
    parts.append('### 다른 상위권 상대에게도 하는가\n\n' +
                 f"[사실] reference 전체 팀·경기 N={r['all']['N']:,}, 그중 승리 N={r['wins']['N']:,}, "
                 f"좌석 A N={r['seats']['A']['N']:,}, B N={b['N']:,}다. "
                 '아래 분자는 해당 팀의 서명이 나타난 경기 수다. 전체 행은 패배와 무승부도 포함한다.\n\n' +
                 table(['집단', 'N', 'r50 수적우세', '상대밭 섭취', '최장 박힘', '질주 최장 박힘', '후기 분열', '킹 회수'],
                       [[label, v['N'], *[v['signature'][k] for k in SIG]]
                        for label, v in [('전체', r['all']), ('승리만', r['wins']), ('A', r['seats']['A']), ('B', b),
                                          ('전멸형 전체', r['families']['elim']), ('500형 전체', r['families']['r500'])]]) + '\n')
    parts.append('[사실] reference 지도별 전체 N과 좌석 B N을 모두 표시했다. 서명 분자는 **전체 좌석** 기준이다. B의 지도별 분자·섭취·결과·전멸·끝 최장은 [reference-strata.csv](../../.cache/elite-counterplay/reference-strata.csv)에 있다.\n\n' +
                 table(['지도', '전체 N', 'B N', 'r50 수적우세', '상대밭 섭취', '질주 최장 박힘', '후기 분열', '킹 회수'],
                       [[m, v['N'], r['mapSeatB'][m]['N'], *[v['signature'][k] for k in ['swarm50', 'homeRaid', 'sprintKingRam', 'lateResupply', 'kingFeed']]]
                        for m in MAP_ORDER for v in [r['maps'][m]]]) + '\n')
    parts.append('[해석] 같은 서명이 다른 상위권 상대에게도 반복된다. 아래 선별 top 기보는 그 행동의 구체적인 예다. 우리 상대에서 더 높은 빈도라는 사실만으로 우리 소스나 INDICATOR를 읽고 맞춤 대응했다고 추론하지 않는다.\n')
    parts.append('### 고정 규칙으로 고른 네 기보\n')
    for key, text in case['films']:
        kind = 'reference' if TASK[key]['src'] == 'top' else '역전 승리' if key in S['teams'][tid]['win'] else '최대 패배 부류'
        parts.append(f"#### {film_link(key)} — {kind}\n\n{text}\n")
    return '\n'.join(parts)


PROPOSALS = r'''## 9. 다음에 만들 두 메커니즘

**[해석·검증 전 제안]** 아래 숫자는 이번 자료에서 효과를 추정한 값이 아니라 다음 구현 전에 동결할 게이트 초안이다. 새 코드·경기·제출은 이 연구의 산출물이 아니다. 각 기능은 OFF/ON 단독 비교로 시작하며, 모든 대상 판·발동 기회·비발동 이유를 기록한다. 승률이나 G를 채택 게이트로 쓰지 않는다. 설계 상황·즉시 효과·기존 기능·건강 지표를 따로 판정한다. 부분 적용은 목적 지표가 움직였는지와 실패 기보를 함께 보고 유지 여부를 정한다.

### 제안 A — `PRESSURE_RETREAT_ON`: 고립된 작은 수확자를 아군 쪽으로 빼기

**겨냥한 관측.** 7팀 모두 많은 L2–3 머리로 우리를 교환한다. 우리 박힘 3,813회 중 가해 L≤3이 3,432회다. W5–W10의 탈출 질주는 L6 이상이고, stack10 `lnt`는 우리 교환 후보의 가치·거부를 바꾼다. L2–5가 상대의 다음 교환을 피할 이동 선택은 별도의 검증 대상이다. 이 제안이 길이 8 이상 킹 급습 133회를 직접 모두 막는다고 약속하지 않는다.

**toggle / INDICATOR.** `PRESSURE_RETREAT_ON`; 적용 이동에 `pr e<EV3> a<AV3> q<before>:<after> alt<N> g<before>:<after>`를 덧붙인다. 비발동 기회에는 `pr0 why=stub|noexit|wall|nosafe|trade|lowpressure`를 남긴다. `EV3/AV3`는 현재 보이는 Chebyshev 3의 적/아군 머리 수이고, `q`는 알려진 이동 그래프와 턴 순서로 해당 끝 칸에 다음 행동까지 도달 가능한 적 머리 수다. 연구용 M3와 섞지 않는다.

**trigger.** r0–449, L2–5, 최근 탈출 분열의 버리는 부모 토막이 아님. 현재 시야에 EV3≥2이고 EV3>AV3이며, 알려진 열린 경로상 현재 머리에 두 걸음 이내 접근 가능한 적이 있다. 기존 후보 안에 즉시 자기·아군 몸 충돌 없이 끝나는 이동이 있고, 그 후보가 현재 최선보다 `q`를 줄이며 가장 가까운 안전한 아군 머리로 가는 경로를 1칸 이상 줄이거나 가장 가까운 적의 실제 경로 거리를 1칸 이상 늘린다. 공격자가 나중 ID인지, 이미 이번 라운드에 움직였는지, 포털·비워질 꼬리·분열 잠재 자식을 기존 `tg` 규칙과 같은 상태로 평가한다. 벽 너머 평면 거리의 다수만으로 발동하지 않는다.

**적용 방식.** 설계 조건을 만족하는 이동끼리 기존 진주·면적 값을 비교한다. 위험을 낮추는 대안이 없으면 원래 생존·탈출·교환 처리를 쓴다. 유리한 `lnt` 공격과 긴 적 킹 예외를 이동 단계가 덮지 않도록 후보 종류를 기록한다. 안전한 자리로 간다는 이유로 매 라운드 계속 뒤로만 걸어 공급원을 모두 내주는지 측정한다.

**사전등록 가능한 적용·즉시 효과 게이트.**

| 항목 | 분모 | 동결할 초안 |
| --- | --- | --- |
| 도달 가능성 | 원시 EV3 열세 턴 전체 → 몸·벽·토막 제외 → 안전 대안 있는 적격 턴 | 각 단계를 N으로 보고. 해당 팀×가족에서 적격 턴 30회 미만이면 그 층은 미판정; 0회 발동으로 통과 금지 |
| 상황·발동 | 적격 턴 / 실제 `pr` 발동 턴 | 적격 턴 적용 ≥90%; 발동 중 정의를 모두 만족 ≥95% |
| 실제 선택 | `pr` 발동 턴 | 같은 결정 상태에서 q 감소 ≥90%; 명령 무효·자기 몸 즉시 충돌 0회; 거리 변화도 원 사건에서 재계산 |
| 즉시 생존 | `pr` 발동 계보 | 발동 후 2라운드 주요 몸·자손 생존 ≥95%; 부모 ID 생존은 참고로 별도 |
| 공급 보존 | ON/OFF의 같은 지도·판본·시드 전체 | r0–250 우리 자연 섭취 평균 ON/OFF≥0.95; 단순 후퇴로 밭을 모두 양보하면 적용 성공이어도 개선 판정 보류 |

**가설 수준 지표.** 같은 지도·판본·좌석·시드의 전체 비교에서 L2–5의 시야 열세 턴 비율이 상대적으로 ≥15% 감소하는가; 적 시작 박힘/100 수확자 턴이 ≥15% 감소하는가; r100 살아 있는 수확자와 우리 출발 영토 자연 섭취가 함께 유지 또는 증가하는가. 사전 목표와 함께 연속 효과량·N·짝별 차이·95% 구간을 보고한다. 게이트가 적용돼도 이 목적이 안 움직이면 “수확대 보존” 가설은 지지되지 않는다. 한 가족에서만 움직이면 범위를 그 가족으로 제한한다.

**지도 가족·상대.** 우선 전멸형 Default/Devil/Queen Of Spades/Trophy, 500형 Schooltime/Slithery Fight/Trauma. Prisoners Dilemma는 통로 밖 수확자만, Autarky/Portals는 안전한 격리 구간을 유지하는 보존 층으로 별도 보고한다. cheji·forgot·DEV를 주된 소모 검증 대상으로 삼되 7팀 전부를 센다. 선택한 상대만으로 최종 효과를 보고하지 않는다.

**읽기 전용 구현 위치.** stack10 [params.hpp](../../exp/cand-stack10/bot/params.hpp)의 탈출·`lnt` 설정 옆에 새 toggle·기준을 둘 자리; [plan.hpp](../../exp/cand-stack10/bot/plan.hpp)의 위협 필드·새 후보 진단 상태; [plan.cpp](../../exp/cand-stack10/bot/plan.cpp) `computeEnemyDistance()`(42), `threatAt()`(189), `lntD3()`(596), `lntVeto()`(626), 후보 생성(1260 이후), `escapeOn`(1339), 최선 후보 선택(1531 이후), INDICATOR 조립(1694 이후). `lnt`를 다시 구현하는 제안이 아니라 그 교환 판정 뒤 남은 이동의 고립을 다룬다. 이번에는 어느 위치도 수정하지 않았다.

### 제안 B — `PATCH_HOLD_ON`: 생산 중인 수확 지점은 회수 마감까지 남기기

**겨냥한 관측.** I6는 153/378패이고 우리 출발 영토의 먹힌 자연 진주 중 상대 몫은 54.3%다. 상대의 후기 분열·킹 회수 서명은 모든 팀의 reference에도 있다. 반면 현재 `computeFountainGoal()`은 r340에 종료되고, `lsplit`도 r340에 종료된다. 현재 `feed`·`conv`는 실제로 연결되는 사례가 있으며 우리 최종 계보의 자해 회수 비중은 상대보다 높다. 부족한 것은 절대 공급량이라는 가설을 먼저 시험한다. 이 자료만으로 r340 정책이 부족량의 원인이라고 확정하지 않는다.

**toggle / INDICATOR.** `PATCH_HOLD_ON`; `ph src<x>,<y> eta<N> rel<R> mode=hold|release|handoff`를 남긴다. 적격이지만 해제한 경우 `ph0 why=unsafe|covered|deadline|stale|unknownyield`를 기록한다. `src`는 봇이 현재 아는 분수·생성 지점이다. 분석의 전지도 참값을 봇 trigger에 넣지 않는다.

**trigger.** r340–429의 비킹 수확자 L2–6. 지도 표 또는 관측으로 확인된 아군 쪽 생성 지점이 알려진 경로 6칸 이내이고, 다른 최근 아군 머리가 더 가까이 맡지 않았다. 이미 알려진 생성 시각·분수 규칙으로 앞으로 20라운드에 자연 진주 ≥2개가 기대되며, 그 구역에 도달 가능한 적 압박이 낮고 적보다 먼저 도착할 수 있다. 최근 확인·음파·릴레이의 긴 아군으로 가는 알려진 경로, 예상 진주 회수 이동, 길이의 절반 환원 시간과 8라운드 여유를 합친 마감이 남아 있다. 새 토막·사망 드롭 유인만 있는 칸은 제외한다.

**적용 방식·해제.** 해당 수확자의 `g` 집결과 이른 `feed/conv`만 잠시 보류하고 기존 `F/F2` 수확·위협·탈출 판정을 계속 쓴다. 맹목적으로 모든 용의 집결을 늦추지 않는다. 수확 후 `남은 시간 ≤ 경로+예상 회수+8`이 되거나 늦어도 r430에 해제한다. 더 가까운 아군에게 지점이 넘어가면 `handoff`, 알려진 압박이 높아지면 `release`한다. 마감 전 집결 경로가 확인되지 않는 경우 유지 자격을 잃는다. 후기 재분열의 단순 전역 연장은 이 첫 구현에 섞지 않는다. 수확 보존 단독 효과를 본 뒤 별도 토글로 다룰 문제다.

**사전등록 가능한 적용·즉시 효과 게이트.**

| 항목 | 분모 | 동결할 초안 |
| --- | --- | --- |
| 적격 기회 | r340–429 비킹 수확자 턴 전체 → 생산·아군 배분·안전·마감 조건 통과 | 조건별 N과 탈락 이유 모두 보고. 팀×가족의 유지 에피소드 20회 미만이면 그 층 미판정 |
| 상황·발동 | 적격 턴 / `ph hold` 턴 | 적격 턴 적용 ≥90%; 실제 발동의 적격 정합 ≥95% |
| 즉시 생산 | 지점×수확 계보의 첫 유지 에피소드; 20라운드 관찰창 | 자연 진주 ≥2개 섭취 에피소드 ≥70%; 사망 드롭을 생산으로 세지 않음; 같은 지점의 겹친 유지 턴을 독립 성공으로 부풀리지 않음 |
| 즉시 생존·해제 | 유지 계보 / 마감 도달 에피소드 | 20라운드 몸·자손 생존 ≥90%; r430 또는 계산 마감까지 release/handoff ≥95%; 0개 생산·지속 후퇴·미해제 사례 모두 기보로 남김 |
| 최종 회수 보존 | 해제 시 길이 ≥4이고 최신 긴 아군 경로가 있는 에피소드 | 그 에피소드 이후 자기 드롭을 아군이 끝까지 먹은 비중 ≥70%; 최종 계보 유입량도 따로 보고. 실제 마감 생략으로 총 자연 섭취만 늘면 보류 |

**가설 수준 지표.** 대상 지점의 r350–429 자연 진주 중 우리 섭취 몫이 ON/OFF 대비 ≥10%p 증가하는가; 대상 지도·판본의 그 국면 우리 자연 섭취가 ≥15% 증가하는가; r350 이후 최종 점수 계보에 들어간 아군 자해 진주 **절대 개수**가 ≥15% 증가하는가. 최종 길이의 변화와 길이 8 이상 계보 사망은 함께 보고하되 승률을 게이트로 쓰지 않는다. 생산은 늘었지만 계보 공급이 그대로면 “후기 수확→점수 줄기” 가설은 일부만 적용된 것이다. 모든 수확자가 빨리 회수되는 것이 좋다는 정책도, 모두 끝까지 수확하는 것이 좋다는 정책도 이번 자료에서 확정하지 않는다.

**지도 가족·상대.** 우선 500형 Schooltime/Trauma/Slithery Fight와 끝까지 살아 있는 전멸형 Default. 조기 종료 판도 모집단에 그대로 남기며 “r340 기회 없음”을 기록한다. Cutlery·calc·801·Sabotage-d·DEV가 주된 공급 검증 대상이며 cheji·forgot도 제외하지 않는다. Autarky/Portals/Prisoners Dilemma는 처음에는 OFF 보존 층으로 두고, 별도 후속 실험에서 실제 통로 밖 생산 지점과 마감이 확인된 경우에만 열어 본다. 특히 이미 자연 진주를 더 먹고도 지는 Autarky에 단순 후기 공급 증가를 일반 처방으로 쓰지 않는다.

**읽기 전용 구현 위치.** stack10 [params.hpp](../../exp/cand-stack10/bot/params.hpp)의 `GATHER_START`(127), `FGUARD/F2`·`LSPLIT_END`(481) 주변에 독립 toggle·시간 기준을 둘 자리; [plan.hpp](../../exp/cand-stack10/bot/plan.hpp)의 `fTarget_`·`goalId_`·보류/해제 상태; [plan.cpp](../../exp/cand-stack10/bot/plan.cpp) `computeAttract()`(324, 실제 생성 시각/분수), `computeFountainGoal()`(926, r340 종료), `computeGoal()`(1048), `conv` 조기 반환(1170 이후), `feed`(1212 이후), INDICATOR(1694 이후). `computeGoal()`보다 먼저 적격 상태를 정하거나 별도 두 목표를 유지해야 하며, 이른 `conv/feed` 반환에도 보류 상태가 적용되어야 한다. 이번에는 어느 위치도 수정하지 않았다.

### 두 제안의 검증 경계

**[해석]** 먼저 A와 B를 각각 단독으로 켜고, 둘의 결합은 각각의 설계 상황·즉시 효과가 확인된 뒤 별도 비교한다. 주된 반증은 A의 과도한 후퇴로 자연 섭취 감소, B의 늦은 해제로 최종 계보 공급 감소다. 기존 `csplit/floor/kcap/lsplit`, `F/F2/cl/cov`, `gx/conv/feed`의 적격 기회 대비 적용률·의도 결과를 같은 지도·판본·국면에서 비교하고 절대 감소 5%p 이상이면 원인 기보를 읽는다. 미판정 층을 합쳐 “전 상대 통과”라고 쓰지 않는다.

**[해석]** 미래 측정에서는 전체 예정 지도·판본·시드와 A/B 좌석을 미리 동결하고 한쪽 결과가 나쁘다는 이유로 판을 빼지 않는다. 독립성을 턴 수로 부풀리지 않도록 게임/시드 묶음의 짝별 차이와 구간을 쓴다. 온라인 웨이브는 상대 버전이 동시 변경될 수 있으므로 그 비교는 적용 관측으로 해석한다. 시간 초과·무효 명령·표식 누락은 원시 사건 전부로 센다. 이 연구는 로컬 경기를 실행하거나 새 봇을 제출하지 않았다.
'''


def main():
    if (ROOT / 'exp/elite-counterplay/SUMMARY.txt').exists():
        raise SystemExit('Completion marker exists; do not rewrite the report after completion.')
    o = A['overall']
    assert o['N'] == 420 and sum(o['classes'].get(k, 0) for k in CLASSES) == o['L'] == 378
    assert A['keyNumbers']['primaryFirst'] == A['keyNumbers']['primarySecond']
    assert not any(A['checks'].values()) and not A['recountDisagreements']
    assert len({t['key'] for t in M['tasks']}) == 9192
    assert all(A['teams'][t]['N'] == 60 for t in TEAM_ORDER)
    for tid in TEAM_ORDER:
        expected = set(S['teams'][tid]['losses'] + S['teams'][tid]['win'])
        actual = {key for key, _ in CASES[tid]['films'] if TASK[key]['src'] == 'online'}
        assert expected == actual
    parts = ['# 극상위권 7팀은 우리 봇을 어떻게 이기나 — 상대별 카운터플레이 연구\n',
             '- 작성: 2026-10-01 KST. 팀 583. primary W5–W10 **420판**, 대비 시대 **490판**, 상위권 기준 **8,213판**. 분석한 고유 경기 **N=9,123**, 기준 팀·경기 **N=9,321**. 기준 후보 8,282판 중 멈춘 팀 69판 제외.\n'
             '- 시작 경계: 2026-09-30 23:14:06 KST, 목록 동결: 23:17:58 KST. 시작 당시 `cand-stack10-online`(W11)은 없었다. 이후 도착 여부와 관계없이 이번 모집단에는 넣지 않았다. stack10 소스는 존재하여 제안 위치만 읽었다.\n'
             '- 기록 위치: `research/observations/elite-counterplay.md`; 계산 코드 `exp/elite-counterplay/`; 캐시 `.cache/elite-counterplay/`. 기존 파일·봇·도구·백로그 변경, 경기 실행, 네트워크·업로드·커밋은 이 작업에서 0건이다.\n',
             '**[사실]** 현재 모집단은 41승·378패·1무다. 패배의 가장 큰 부류는 섭취 열세로 생존한 I6 153판, 이어 중반 소모 전멸 E3 109판이다. 7팀 모두 우리 출발 영토에서 우리보다 많은 자연 진주를 먹었다. 실질 킹 박힘 133회 중 질주는 86회지만, 801의 주된 패배 부류는 킹 사망 없이도 나타나는 섭취 열세다.\n',
             '**[해석]** 가장 강한 공통 가설 대상은 **작은 수확자의 고립·소모와 후기 수확대의 공급 지속**이다. 팀별로 급습의 강도와 전멸 시점은 다르다. 큰 킹 방어만 강화하거나 모든 지도에서 더 많이 분열하는 처방은 이 자료의 반례를 설명하지 못한다. 다음에는 고립된 작은 수확자의 이동과 생산 중인 지점의 조건부 후기 유지 두 기능을 분리해 검증할 것을 제안한다.\n',
             '## 0. 모집단·세 단계·재계산\n']
    parts.append('### 모집단\n\n[사실] 요청된 범위의 시작 시점 전체를 사용했다. 통계 계산에 표본 추출은 없다. 이후 들어온 경기로 분모가 변하지 않게 인덱스 SHA-256과 키를 [manifest.json](../../.cache/elite-counterplay/manifest.json)에 보존했다.\n\n' +
                 table(['집단', '세트/선택 범위', '원래 N', '제외 N', '분석 N'],
                       [['primary', 'W5, W6, W7=stack6-r2, W8, W9, W10', 420, 0, 420],
                        ['대비', 'merge2 / r2 / r3 + stack1 / 2 / 3 / 4', 490, 0, 490],
                        ['reference', '동결 top 인덱스에서 7팀 중 하나 이상 포함', '8,282', 69, '8,213'],
                        ['고유 경기 합', '온라인 910 + reference', '9,192', 69, '9,123']]) + '\n')
    parts.append('[사실] `r1-online` 194판, `r1-autoscrim` 5판은 요청대로 범위 밖이다. `g1`, `g2`는 시작 인벤토리에서 폴더만 있고 인덱스·리플레이는 0개다. 이 **199판은 위 9,192판에 처음부터 들어 있지 않아 이중 차감하지 않는다**. 누락 리플레이 0개, 동결 키 중복 0개다.\n')
    parts.append('[사실] reference 멈춤 제외는 라운드 수 ≥100이고 한 팀이라도 음파 ping 0회·분열 ≤3회인 판의 합집합이다. 제외 69판의 멈춘 팀은 SSS 64, Sponge(Albert and Bob) 1, Team SKKU 1, 龙虎豹 1, WeHaveQuizzes 1, 中国必须人能飞😡 1이다. [excluded-top.json](../../.cache/elite-counterplay/excluded-top.json)에 경기 키와 두 팀의 원래 ping·분열 수가 있다. 이전 연구의 시간 초과 필터는 추가하지 않았다. 짧은 경기(<100)는 이 규칙으로 제외하지 않았다.\n')
    parts.append('[사실] top에는 대상 두 팀이 같이 들어간 판도 있어 8,213 **고유 경기**가 9,321 **대상 팀·경기**로 나타난다. 우리 온라인 910판은 모두 A다. 주어진 팀 이름과 top `teamA/teamB`를 연결했고, 545는 reference에서도 전부 B다. 기준 집단의 시기 범위는 2026-09-29 10:17:46Z–2026-09-30 13:45:02Z, primary는 2026-09-30 06:55:45Z–13:42:56Z다. 이름의 현재 순위·레이팅을 외부 조회하지 않았다.\n')
    parts.append('### 상대별 관측 판정 한눈에\n\n[사실] 경기 결과와 가장 큰 배타적 패배 부류. 끝의 전술명은 아래 7개 절에서 기보와 기준 전체로 확인한 행동을 요약한 이름이다.\n\n' +
                 table(['팀', 'N', '승/패/무', '전멸 N', '가장 큰 패배 부류 N / 패배 N', '킹 박힘/질주', '관측 행동'],
                       [[f'{tid} {NAMES[tid]}', v['N'], wl(v), v['eliminated'],
                         f"{S['teams'][tid]['largestClass']} {S['teams'][tid]['largestN']} / {v['L']}",
                         f"{v['kingRams']} / {v['kingSprint']}", CASES[tid]['signature']]
                        for tid in TEAM_ORDER for v in [A['teams'][tid]]]) + '\n')
    parts.append('### 계산 순서와 기보 선택\n\n'
                 '1. **전체 계산:** `extract.js`로 온라인 910판의 이동·분열·진주 출처·모든 죽음·태그를 복원했다. reference 8,282판 중 이미 검증된 원 장부 4,851판을 읽기 전용으로 재사용하고, 없는 3,431판을 새 캐시에 복원했다. 온라인과 기준의 모든 키에서 최종 상태·장부·자연/드롭 잔량·분열 등 점검 합이 0이다. `recount.js`는 공식 리플레이 파서만 공유하고 장부·추출기·기존 영토 계산을 가져오지 않은 채 온라인 **910판 전부**를 다시 센다.\n'
                 '2. **분류:** 배타적 E1→E2→E3→E4→K5→I6→C7→G8 순서로 primary 패배를 분류한다. 지도 가족·지도·판본·국면과 중복 가능한 전술 서명을 함께 보존했다. 모든 결과는 [aggregate.json](../../.cache/elite-counterplay/aggregate.json)에 있다.\n'
                 '3. **깊이 읽기:** **기보를 읽기 전에** 팀마다 가장 큰 패배 부류에서 game id가 작은 2판과 primary 승리 중 가장 작은 1판을 택한다. 부류 동률은 위 우선순위다. 7팀 모두 승리가 있어 온라인 21판이다. 기준 예시는 해당 최대 부류에 대응하는 서명이 있는 미제외 승리 중 가장 작은 game id 1판씩(총 7판). E1/E3/E4→r50 수적우세, E2/K5→질주 킹 박힘, I6→상대밭 섭취, C7/G8→킹 회수로 대응한다. **28판은 설명용이고 모집단 통계의 분모를 대체하지 않는다.**\n')
    parts.append('[사실] 고정 선택은 아래와 같다. 가장 작은 ID 규칙 때문에 대표 패배 14판은 모두 W5다. 최신 버전을 대표한다는 뜻은 아니며 최신까지의 빈도는 420판 전체 표를 따른다.\n\n' +
                 table(['팀', '최대 부류', '해당 패배 N / 전체 패배 N', '패배 game id 2개', '승리 game id', '기준 battle:game'],
                       [[f'{tid} {NAMES[tid]}', S['teams'][tid]['largestClass'],
                         f"{S['teams'][tid]['largestN']} / {A['teams'][tid]['L']}",
                         ', '.join(str(TASK[k]['gameId']) for k in S['teams'][tid]['losses']),
                         str(TASK[S['teams'][tid]['win'][0]]['gameId']), CASES[tid]['films'][-1][0]] for tid in TEAM_ORDER]) + '\n')
    parts.append('### 핵심 5개 숫자: 별도 원 사건 재계산\n\n[사실] 첫 계산은 이동을 시뮬레이션하고, 독립 계산은 `dragonUpdate`의 머리·꼬리와 `dragonSplit`의 몸 배열로 현재 몸을 재구성한다. 자연/사망 진주는 `tileChange` 순서로, 영토는 따로 작성한 포털·해초·경계 그래프 BFS로 센다. 두 코드가 같은 표의 합계를 다시 더한 검산이 아니다.\n\n' +
                 table(['primary 핵심 항목', '장부 계산', '독립 원 사건 계산', '경기별 불일치 N / 420'],
                       [[label, fmt(A['keyNumbers']['primaryFirst'][key]), fmt(A['keyNumbers']['primarySecond'][key]), '0 / 420']
                        for key, label in [('eliminated', '우리 전멸 판수'), ('naturalUs', '우리 자연 진주 섭취'),
                                           ('enemyOurTerritory', '상대가 우리 출발 영토에서 먹은 자연 진주'),
                                           ('kingRams', '우리 실질 킹의 적 시작 박힘 사망'), ('kingSprint', '위 박힘 중 적 질주 ≥2걸음')]]) + '\n')
    parts.append('[사실] 대비 490판도 같은 다섯 값이 **261, 47,023, 68,346, 211, 150**으로 각각 일치한다. 온라인 910판의 전멸 라운드와 양쪽 끝 최장도 경기별 불일치 0이고, 독립 코드의 최종 수·총길이·최장은 모든 리플레이 결과와 일치했다. 기준 8,282판에는 장부 복원 점검을 전부 적용했으나 별도 원 사건 코드로 이 다섯 값을 다시 세지는 않았다.\n')
    parts.append('### 정의\n\n'
                 '- **승패·점수:** 공식 규칙상 r500 끝 살아 있는 단일 최장 길이를 우선 비교하고, 같으면 총길이를 비교한다. 용이 0마리가 된 팀은 그때 즉시 진다. 자연 섭취 합·총길이·분열 수는 최종 점수와 다르다. [공식 death](../../../unsw-arena/rules/death.md), [game-format](../../../unsw-arena/rules/game-format.md), [execution-order](../../../unsw-arena/rules/execution-order.md)를 읽었다.\n'
                 '- **라운드:** `roundStart`의 0 기반 r. r252 전멸은 253라운드를 실행한 판이다. 500라운드 판은 마지막 r499 행동까지 포함한다. r50·r100 상태는 해당 라운드 초반의 살아 있는 수다. 조기 종료 뒤의 상태 시계열은 끝 상태를 이어 붙이는 원 장부 규약이며, 전멸팀은 0·승자 수는 끝 상태다. 실제 이후 행동이 있었다는 뜻이 아니다.\n'
                 '- **지도 가족:** 500형 = Autarky/Portals/Schooltime/Slithery Fight/Trauma; 나머지 Default/Devil/Prisoners Dilemma/Queen Of Spades/Trophy는 전멸형. 실제 종료 종류와 다른 분류다. Default도 r500에 도달하고 Autarky도 기준에서 전멸한다. 판본(a/b, PD 6/10)은 지도 사건으로 판정해 CSV에 남겼다.\n'
                 '- **국면:** p0 r0–99, p1 r100–249, p2 r250–349, p3 r350–449, p4 r450–499. 국면별 진주 개수는 종료 뒤 0이며 국면별로 길이가 다르다.\n'
                 '- **자연 진주:** 초기 진주와 자연 생성 전부. 모든 사망 드롭은 제외한다. 위치는 출발 몸의 정적 이동 그래프 최단거리 Voronoi(해초·포털·경계 순환 반영)로 우리 영토/중립/상대 영토를 정한다. 현재 점유·머릿수·전선의 영토라는 뜻은 아니다. 동거리·양쪽 도달 불가는 중립이다.\n'
                 '- **사망 원인:** `rammed`=적이 움직여 우리 머리와 함께 죽음, `ram`=우리가 움직여 적 머리와 교환, `enemyBody`=적 몸통 충돌, `allyHead`=아군 머리 교환, `trap`=그 턴 시작에 빈 출구가 없음, `sac`=빈 출구가 있었는데 스스로 죽음, `sprintDeath`=질주 길이 소진. `sac`는 행동 대리 분류이고 의도적 급식임은 `feed/conv`나 드롭 회수를 추가로 확인해야 한다. 엔진 원시 `S` 자기 충돌은 급식·갇힘과 겹치므로 따로 남긴다. 배타적 사망 분류에 `S`를 다시 더하지 않는다.\n'
                 '- **토막:** 최근 분열에서 작게 남긴 부모의 사망(`stub`)을 별도 기록한다. 몸을 받은 자식이 살아 있으면 본체 보존은 성공할 수 있다. 갇힘 수를 모두 적이 만든 포위 수로 읽지 않는다. `trapEnemy`는 적 몸도 막은 갇힘의 보조값이지 적만이 원인이라는 인과 판정이 아니다.\n'
                 '- **국소 머릿수 d3/d8:** 사망 순간 죽는 용과 직접 충돌 상대를 빼고 torus Manhattan 거리 ≤3/8의 아군 a3/a8, 적 e3/e8을 센다. d3=a3−e3, d8=a8−e8. 킬러 길이는 충돌 직전 실제 길이이고 질주 도중 먹거나 지불한 변화를 포함한다.\n'
                 '- **실질 킹:** 그 순간 아군 최장, 동길이면 작은 ID, L≥8. r500의 최종 킹과 다를 수 있고 한 판에 여러 실질 킹이 죽을 수 있다. `kingAny`는 L 제한 없이 별도 원자료에 남겼다. 적 시작 킹 박힘의 **사건 수**와 그 사건이 있는 **경기 수**를 별도 표기한다.\n'
                 '- **성공 질주 급습:** 적의 요청 이동 ≥2걸음이 현재 실질 킹 머리와 충돌한 실제 사건. 엔진은 충돌 뒤 꼬리를 빼지 않고, 치명적 걸음은 길이를 지불하지 않는다. 공격 전 L보다 사망 가해 L가 다를 수 있다. 다른 원인의 킹 사망도 원자료에 남겼다.\n'
                 '- **짧은 질주 접근 대리:** 더 짧은 적이 실질 킹의 M8 안에서 ≥2걸음 이동하여 거리 감소·끝 M3 안인 사건. 후처리 시점의 최장에 대한 접근 관측이며 킹 사냥 의도나 성공을 증명하지 않는다. 성공 박힘과 합산하지 않는다.\n'
                 '- **압박 턴:** 원 장부 보조는 M3 적≥2·적>아군이다. 별도 원 사건 대응 분석은 실제 7×7의 Chebyshev 3 적≥2·적>아군이다. 둘은 다른 분모다. 평면 거리 수는 벽과 포털의 도달을 보장하지 않는다. 따라서 M3 적 0을 “시야 밖”이라고 쓰지 않는다.\n'
                 '- **몸 생존:** 부모와 뒤에 생긴 자손의 계보로 본다. ID 생존은 참고다. 현재 대응 분석의 +10 생존은 경기 종료가 더 빠르면 종료 시점까지의 생존이다. 여러 턴이 같은 용·경기에 속하므로 독립 실험 반복 수가 아니다.\n')
    parts.append('### 부류와 전술 서명의 고정 정의\n\n[사실] 다음 패배 부류는 인과 판정이 아니라 관측된 결과·수치에 붙인 이름이다. 위에서 먼저 맞는 부류로 넣는다. 승리 W·무승부 D는 패배 부류 밖이다.\n\n' +
                 table(['부류', '정의', 'primary N / 패배 378'],
                       [['E1', '우리 전멸 r<100', 6],
                        ['E2', '전멸 r≥100, 직전 30라운드 안에 실질 킹의 적 시작 박힘/적 몸통/적 몸 포함 갇힘', 11],
                        ['E3', '위 E2 제외, 전멸 r100–299', 109], ['E4', '위 E2 제외, 전멸 r≥300', 29],
                        ['K5', '생존 패배, r≥400에 같은 실질 킹 피격 원인', 20],
                        ['I6', '생존 패배, 상대 자연 섭취 ≥우리 1.5배이면서 차이 ≥20', 153],
                        ['C7', '생존 패배, 우리 끝 총길이 ≥상대 끝 최장>우리 끝 최장', 26],
                        ['G8', '나머지 생존 패배', 24]]) + '\n')
    parts.append('[사실] 전술 서명은 서로 겹친다. 이름이 아니라 아래 수치 정의를 비교한다. 후기 분열·킹 회수에는 원시 행동을 쓰므로 상대의 정책 의도를 확인한 수라고 부르지 않는다.\n\n' +
                 table(['서명', '해당 팀 기준 정의'],
                       [['swarm50 / r50 수적우세', 'r50 머릿수≥8, 동시에 상대의 2배 이상'],
                        ['homeRaid / 상대밭 섭취', '상대 출발 영토에서 자연 진주≥10, 그 영토에서 두 팀이 먹은 자연 중 해당 팀 몫≥30%'],
                        ['kingRam / 최장 박힘', '상대 실질 킹 적 시작 박힘≥1'], ['sprintKingRam', '위에서 ≥2걸음 질주≥1'],
                        ['lateResupply / 후기 분열', '경기 라운드≥350, r250 이후 모든 분열≥20(탈출 포함)'],
                        ['kingFeed / 킹 회수', 'r500 도달, 끝 최장≥20, r250 이후 그때그때 최장이 먹은 자기 팀 자해 드롭≥10']]) + '\n')
    parts.append('### 대비 시대와 최신까지의 변화\n\n[사실] 웨이브별 전체 결과다. 분열·표식이 다른 버전이 섞였고 상대 버전·시드·판본도 다를 수 있으므로 처리 효과나 채택 판정으로 쓰지 않는다.\n\n' +
                 table(['세트', '시대', 'N', '승/패/무', '전멸 N', '우리 자연 진주', '실질 킹 박힘/질주'],
                       [[s, 'primary' if s in M['primarySets'] else '대비', v['N'], wl(v), v['eliminated'],
                         fmt(sum(v['intakeUs'])), f"{v['kingRams']} / {v['kingSprint']}"]
                        for s in M['contrastSets'] + M['primarySets'] for v in [A['sets'][s]]]) + '\n')
    parts.append('[사실] 대비 전멸 261/490(53.3%) → primary 155/420(36.9%), 우리 자연 섭취 평균 96.0→151.3개/판이다. 그러나 승리는 51/490→41/420이며 이 이동만으로 새 기능의 채택·인과 효과를 판정하지 않는다. `GATHER_START=340`, `ESCAPE_MIN_LEN=6`은 primary 소스 전체에서 같다. `COV_ON`은 W5–W9 OFF, W10 ON이므로 `cov`의 전체 420판 효과라고 합치지 않았다. stack10 현재 읽은 소스는 `LNT_ON=true`, `UTAB_ON=false`, `LSPLIT_END=340`이며 W11 경기의 적용·성능은 이 연구에서 관측하지 않았다.\n')
    parts.append('### 실행 자원\n\n[사실] 무거운 패스 전 `memory_pressure`와 `df -g /`를 확인하고 메모리 자유 비율 10%·디스크 20GB 하한을 검사했다. `guard.py`와 각 복원 패스가 이를 수행하며 reference 계산은 최대 2개 분할 프로세스였다. 모든 무거운 명령을 `nice -n 15`로 요청했지만 이 샌드박스는 `setpriority: Operation not permitted`를 냈다. 따라서 실제 nice 15 적용은 보장하지 못했고, 워커 수 ≤2·프로세스별 메모리 한도·기보 사이 양보를 지켰다. 기존 장부 캐시는 읽기만 하고 본 연구 캐시에만 결과를 썼다.\n')
    for n, tid in enumerate(TEAM_ORDER, 1):
        parts.append(output_team(tid, n))
    parts.append('## 8. 공통 카운터와 우리 메커니즘의 약점\n\n### 같은 기준으로 본 상대별 서명\n\n[사실] primary에서는 상대가 모두 B다. 아래 기준 B율은 reference 좌석 B에서 각 지도율을 낸 뒤 **10지도 동일 가중 평균**한 값이다. 전체 B N이 분모인 단일 이항 비율이 아니며 primary 각 지도 N=6의 지도 구성을 맞춘 설명용 표준화다. 판본·시기·상대 강도까지 통제한 효과는 아니다. 각 팀의 전체/A/B/승리/가족/지도 N과 분자는 앞 절에 있다.\n\n' +
                 table(['팀', 'primary N / 기준 B N', '수적우세 primary / 기준 B 표준화', '상대밭 primary / 기준 B 표준화',
                        '질주 킹 박힘 primary / 기준 B 표준화', '후기 분열 primary / 기준 B 표준화', '킹 회수 primary / 기준 B 표준화'],
                       [[f'{tid} {NAMES[tid]}', f"60 / {A['reference'][tid]['seats']['B']['N']}",
                         *[f"{A['teams'][tid]['sig'][k]}/60 ({100*A['teams'][tid]['sig'][k]/60:.1f}%) / {100*A['reference'][tid]['mapStandardizedB'][k]:.1f}%"
                           for k in ['swarm50', 'homeRaid', 'sprintKingRam', 'lateResupply', 'kingFeed']]] for tid in TEAM_ORDER]) + '\n')
    parts.append('[해석] 적이 다른 엘리트에게도 하는 일반적인 전략이 우리에게 더 자주 성립한다. 수적우세 서명은 primary에서 모든 팀이 기준 B 표준화율보다 높다. 이것은 우리 수확대가 상대적으로 얇다는 설명과 맞지만 고의적인 맞춤 counter의 증거는 아니다. cheji는 우리에게 전멸을 일찍 만들어 후기 서명 자체의 기회가 줄고, reference의 상대 강도·종료 시각·판본도 다르다.\n')
    parts.append('### 공유되는 전술 → 무력화되는 기능\n\n' +
                 table(['카운터 전술', '[사실] 전체 primary N과 팀 범위', '[해석] 어떤 기능의 목적이 꺾이는가', '다음 검증의 중심'],
                       [['작은 머리의 수적 선점·교환', 'r50 수적우세 248/420; 7팀 모두. 우리 박힘 3,813회 중 가해 L≤3 3,432회',
                         'csplit/floor/kcap의 수가 있어도 고립 수확자는 소모된다. L6 이상 escape와 킹 보호만으로 L2–5를 보존하기 어렵다', '제안 A: 형성된 수를 전장에 유지'],
                        ['우리 출발 밭의 자연 진주 선점', '상대밭 서명 299/420; 실제 상대의 우리 영토 섭취 69,837개, 우리 자체 섭취 58,767개; 7팀 모두 상대가 더 많이 먹음',
                         'F/F2·cl·cov의 목표/아군 배분이 실제 적보다 빠른 섭취를 보장하지 않는다. grab 회수만으로 자연 부족을 메우기 어렵다', '제안 A+B: 도달 경쟁·후기 생산 유지'],
                        ['후기 수확대와 점수용 급식을 함께 유지', '후기 분열 291/420, 킹 회수 199/420; 모든 팀 reference에서도 나타남',
                         'r340 F 종료·lsplit 종료·g 집결과 공급 지속이 충돌할 수 있다. conv/feed가 연결되어도 절대 재료가 적다', '제안 B: 수확과 회수의 마감 분리'],
                        ['싼 용의 최장 급습·포털 우회', '킹 박힘 133회/84판, 질주 86회/58판, 가해 L≤4 113/133; forgot가 31/24회, 801은 4/3회',
                         'tg가 위험을 기록해도 후보 선택·턴 순서·도달을 놓치면 점수 줄기가 끊긴다. 단일 거리·평면 머릿수는 포털 급습을 설명 못 함', '기존 보호의 적용 진단; A의 좁은 범위 밖인 긴 킹은 별도 층'],
                        ['몸을 자식에 넘겨 후기 길이 보존', '선별 calc/cheji/Sabotage/Cutlery의 실제 큰 몸 인계와 최종 계보 회수; 전체 kin/split 원자료 보존',
                         '상대 분열을 점수 포기로, 우리 토막 죽음을 본체 사망으로 읽으면 잘못된 목표를 세운다. gx/escape-split은 가족 기준으로 봐야 함', '기존 몸 생존 규약 유지']]) + '\n')
    parts.append('### 사망·공급 수치가 반박하는 과대 주장\n\n[사실] 우리 전체 사망 N=39,500의 원인은 박힘 3,813, 갇힘 31,916, 자해 2,282, 우리가 박음 766, 아군 머리 702, 적 몸통 19, 질주 길이소진 2다. 원시 자기 충돌 S=2,334는 겹치는 축이다. 갇힘 중 26,090회는 분열 토막이며 적 몸이 일부 막은 갇힘은 472회다. 총 갇힘을 모두 상대의 적극적인 포위라고 주장할 수 없다.\n')
    parts.append('[사실] 실질 킹 사망 N=237은 적 시작 박힘 133, 갇힘 50, 아군 머리 43, 자해 4, 우리가 박음 4, 적 몸통 3이다. 133회 박힘 중 r400 이후는 31회다. 마지막 INDICATOR에 신뢰 완화 `T`가 붙은 것은 **0/133**, `tgx`는 5/133, `ks`는 0/133이다. 표식 시각이 사망 전 2라운드 이내인 것은 122/133이다. 태그 부재가 내부 모든 판단의 부재를 증명하지는 않지만, “신뢰 때문에 킹이 대부분 죽으니 trust만 초기화”는 현재 자료에서 뒷받침되지 않는다.\n')
    parts.append('[사실] r350 이후 우리 팀이 먹은 아군 자해 진주는 3,866개, 그중 최종 점수 계보에 들어간 것은 1,679개(43.4%)다. 상대는 24,446개 중 5,878개(24.0%)다. 우리의 **비율은 더 높고 절대 유입량은 상대가 약 3.5배**다. 그때그때의 킹 회수 서명과 최종 계보 회수는 다른 지표다. 이 자료로 우리 급식 대상의 비율이 상대보다 나쁘다고 주장하지 않는다.\n')
    parts.append('[사실] Chebyshev 3 열세 턴의 별도 대응 계산은 멀어짐 101,438턴(+10 가족 생존 92,302), 거리 유지 47,253(41,807), 다가감 74,065(66,480), 분열 13,483(13,162)이다. 각각 91.0%, 88.5%, 89.8%, 97.6%다. 벽·용 길이·상황·반복 턴이 통제되지 않았고 조기 종료도 있어 “후퇴를 강제하면 생존이 그 차이만큼 증가”라고 쓰지 않는다. 원 장부 M3 압박 턴 73,407/1,504,377과 합치지 않는다.\n')
    parts.append('[사실] Autarky는 상대별 N=6, 전체 N=42다. 다음 표는 자연 섭취와 최장 점수가 다른 문제라는 반례를 모두 남긴다.\n\n' +
                 table(['팀', 'N', '승/패/무', '자연 진주 우리/상대', '끝 최장 평균 우리/상대'],
                       [[f'{tid} {NAMES[tid]}', v['N'], wl(v), f"{fmt(sum(v['intakeUs']))} / {fmt(sum(v['intakeEnemy']))}",
                         f"{fmt(v['finalUsMean'])} / {fmt(v['finalEnemyMean'])}"] for tid in TEAM_ORDER for v in [A['maps'][tid]['Autarky']]]) + '\n')
    parts.append('[해석] 분리된 지도의 점수 전환, 공유 전장의 자연 공급 부족, 긴 킹 급습은 서로 다른 축이다. 현재 801을 설명하려면 공급을 다뤄야 하고, forgot의 실패에는 급습도 남는다. Cutlery·801·Sabotage의 Autarky에는 더 많이 먹고도 지는 반례가 있어 단일 섭취 처방을 전지도에 확장하지 않는다. 후기 공급 보존 제안의 범위를 생산 지점·회수 마감이 성립하는 공유 전장부터 제한한다.\n')
    parts.append(PROPOSALS)
    parts.append('## 부록 A. 재현·감사 경로\n\n'
                 '[사실] 계산 코드와 원자료 연결은 모두 새 출력 경로 안에 있다. 다음 경로는 저장된 결과를 다시 읽기 위한 것이며 새 경기나 네트워크 명령이 아니다.\n\n' +
                 table(['산출물', '내용'],
                       [[relative_link('exp/elite-counterplay/', 'exp/elite-counterplay/'), 'manifest/guard/extract/import_reference/recount/aggregate/film/inspect_films/audit_tables/cases/write_report/verify 코드'],
                        [relative_link('manifest.json', '.cache/elite-counterplay/manifest.json'), '시작 목록·키·인덱스 해시·W11 경계'],
                        [relative_link('aggregate.json', '.cache/elite-counterplay/aggregate.json'), '전체/팀/가족/지도/대비/좌석/서명과 재계산 5개'],
                        [relative_link('per-game.csv', '.cache/elite-counterplay/per-game.csv'), '910판 각각 결과·양쪽 끝 최장·전멸 라운드·국면 자연·영토·급습'],
                        [relative_link('our-deaths.csv', '.cache/elite-counterplay/our-deaths.csv'), '모든 우리 사망: 경기·r·#·좌표·길이·원인·가해 L·a3/e3/a8/e8/d3/d8·태그'],
                        [relative_link('death-strata.csv', '.cache/elite-counterplay/death-strata.csv'), '시대×팀×가족/지도×국면×원인 전수 사망층 2,590행'],
                        [relative_link('territory-phase.csv', '.cache/elite-counterplay/territory-phase.csv'), '시대×팀×가족/지도×국면×먹는 쪽×자연/드롭 영토층 3,640행'],
                        [relative_link('raid-proxies.csv', '.cache/elite-counterplay/raid-proxies.csv'), '성공 킹 박힘과 접근 대리 사건을 서로 다른 type으로 보존'],
                        [relative_link('reference-strata.csv', '.cache/elite-counterplay/reference-strata.csv'), '전체 기준의 팀×가족/지도×좌석 260층: N·결과·전멸·끝 최장·국면 자연·영토·서명'],
                        [relative_link('reference-games.jsonl', '.cache/elite-counterplay/reference-games.jsonl'), '9,321 대상 팀·경기 전부의 기준 특징'],
                        [relative_link('recount.jsonl', '.cache/elite-counterplay/recount.jsonl'), '원 사건 독립 재계산 910판'],
                        [relative_link('selection.json', '.cache/elite-counterplay/selection.json'), '깊이 읽기 전 동결된 선택'],
                        [relative_link('film-index.json', '.cache/elite-counterplay/film-index.json'), '선택 28개 상세 행동/분열/진주/사망/점수 계보'],
                        [relative_link('auxiliary.json', '.cache/elite-counterplay/auxiliary.json'), '킹 사망의 다른 원인·짧은 가해·국면·판본·읽은 stack10 소스 해시']]) + '\n')
    parts.append('최종 감사 `verify.py`는 910판의 CSV·독립 재계산, 모든 사망·영토층 합계, 기준 포함/제외 키, 선별 28판, 표 열 수와 로컬 링크를 검사하며 `.cache/elite-counterplay/validation.json`에 보고서 해시를 남긴다.\n')
    parts.append('재현 순서는 `guard.py`를 통해 extract online/reference → recount → aggregate → film → audit_tables → write_report → verify다. 기존 동결 manifest를 바꾸지 않으며 완료 키는 건너뛴다. 참고 장부의 누락분을 두 프로세스로 나누려면 `extract.js reference --shard 0/2`, `--shard 1/2`를 각각 실행한다. 끝 marker `exp/elite-counterplay/SUMMARY.txt`는 이 보고서와 감사가 끝난 뒤 마지막으로 작성한다.\n')
    text = '\n'.join(parts)
    assert text.count('#### [') == 28
    assert all(f'## {n}. {tid} — ' in text for n, tid in enumerate(TEAM_ORDER, 1))
    OUT.write_text(text)
    print(json.dumps({'report': str(OUT.relative_to(ROOT)), 'lines': len(text.splitlines()),
                      'characters': len(text), 'deepReads': 28, 'proposals': 2}, ensure_ascii=False))


if __name__ == '__main__':
    main()
