import json
from pathlib import Path
from collections import Counter
from datetime import datetime

OUT = Path(__file__).resolve().parent
IDS = [1485657, 1485169, 1485170, 1485174, 1485180]
evidence = {gid: json.loads((OUT / f'{gid}-evidence.json').read_text()) for gid in IDS}
audit = {}
for gid in IDS:
    ledger = json.loads((OUT / f'{gid}-ledger.json').read_text())
    turns = json.loads((OUT / f'{gid}-turns.json').read_text())
    assert not ledger['anomalies']
    assert '21126' in evidence[gid]['bots'].values()
    bands = []
    for lo, hi in [(101, 200), (201, 300), (301, 400), (401, 499)]:
        sides = []
        for s in [0, 1]:
            ts = [t for t in turns if t['s'] == s and lo <= t['round'] <= hi]
            sides.append(dict(turns=len(ts), natural=sum(t['natural'] for t in ts),
                              eats=sum(t['eats'] for t in ts),
                              moving_without_eating=sum(bool(t['steps']) and not t['eats'] for t in ts),
                              splits=sum(t['split'] is not None for t in ts)))
        bands.append(dict(rounds=[lo, hi], sides=sides))
    audit[gid] = dict(bands=bands, anomalies=ledger['anomalies'])
    if gid in [1485657, 1485170]:
        audit[gid]['our_deaths_length_ge_9'] = [d for d in ledger['deaths'] if d['side'] == 'us' and d['length'] >= 9]
    if gid == 1485657:
        audit[gid]['leader_drought'] = []
        for i in [533, 503]:
            ts = [t for t in turns if t['id'] == i and 421 <= t['round'] <= 452]
            audit[gid]['leader_drought'].append(dict(id=i, turns=len(ts), eats=sum(t['eats'] for t in ts),
                                                   steps=sum(len(t['steps']) for t in ts)))
    if gid == 1485180:
        ts = [t for t in evidence[gid]['qturns'] if t['s'] == 0 and t['round'] > 110]
        audit[gid]['queen_drought'] = dict(turns=len(ts), eats=sum(t['eats'] for t in ts),
            steps=sum(len(t['steps']) for t in ts), pearl_in_view=sum(any('*' in row for row in t['board']['rows']) for t in ts),
            adjacent_free_pearl=sum(bool(t['neighbour_pearls']) for t in ts))
(OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')

report = '''[M/E] 최다 반복은 여왕 위협의 관측 공백: 3/5판(1485169·1485170·1485174); 직접 여왕패는 2판, Islands는 이후 최장패다.
[C] 카드: BEING BUILT `CUT_BODY_LEN:4`의 미커버 확인; NEW `FEED_BOOT_LEN:4` 부트스트랩.
[M/C/E] 사망·길이·이동은 확실; 내부 판단 분기와 수정 후 승패는 미확인.

[M] 전부 replay botId **21126(one8)**. r은 기보의 0기준, 마지막 r499. 전환은 실제 진행에서 점수순서(여왕→최장→총합)가 마지막으로 뒤진 뒤 회복하지 않은 라운드이며, 승리 불가능 시점이라는 뜻은 아니다. 표의 최종값은 **여왕/최장/총합/생존수**, 우리→상대다. [C] 줄번호는 `data/online/smoke/one8-bot/main.cpp`.

| 경기·우리 편·상대 | 결정 / 최종 양쪽 [M] | 전환 [M] | 단일 주원인·구체 장면 [M; 해석 E] |
|---|---|---|---|
|1485657 Australia B / acegi|최장; 0/56/376/53 → 0/62/106/3|r424|득점 주력의 섭취 정체. #533 r421–452: 34걸음·섭취0, 적 #503: 86걸음·섭취17. r453 #533 47→부모2+자식#595 45; 자식은 살아서56. 큰 몸을 잃은 패배가 아니다.|
|1485169 Australia A / kraken|여왕; 0/56/481/42 → 3/21/82/10|r392|Q#1이 (28,34)→(27,34), 시야 밖 #233 길이6이 (24,34)에서 동3걸음으로 충돌. r412 #371 길이10은 적Q#0까지 빈 경로2걸음인데 공격하지 않음.|
|1485170 Islands A / kraken|최장; 0/17/68/8 → 0/28/148/12|r262|작은 몸의 반복 분열·소모로 축적 실패. r262 당시 최장 #640 6→2+#648 4(출구0), r263 부모 벽사. #518 r310–397 길이4에서 9회 분열. r496 최장#1021 19→2+#1035 17, 자식 생존. 길이9 이상 우리 사망0.|
|1485174 Around UNSW A / kraken|여왕; 0/55/285/30 → 19/27/232/26|r196|Q#0이 시야 경계의 #414를 과소평가[E]. Q (22,32)→(22,33); 보이는 적 몸1칸, 실제길이8. #414 (25,32)에서 남·서·서·서4걸음으로 충돌.|
|1485180 Trauma A / kraken|여왕; 3/6/51/18 → 16/16/61/7|r110|Q#0 r110 5→3+#47 2 뒤 성장 단절. r111–499 389걸음·섭취0; 진주가 시야에 있던 턴31, 빈 인접 진주0. 먹이 없는 곳을 계속 걸음; r301–499 길이2 아군의 Q 맨해튼5 이내 턴215에도 공급0.|

[M] Islands의 섭취 격차는 r101–200 자연진주142:223, r201–300 96:230이다. 후자 우리3994턴 중3645턴은 먹지 않고 이동, 분열85회, 사망95(머리충돌72). 적 여왕은 r193 벽사했으므로 r73 우리 여왕 사망만으로 최종패를 설명하지 않는다.

| 경기 | 여왕 사망의 나머지 사실 [M] | LIVE 방어와 실패 조건 [C], 확인 한계 [E] |
|---|---|---|
|1485657|r361 Q#0 24→2+#533 22로 분열; #268 길이9가 (44,16)→(44,15)→(43,15)→Q(42,15). 적Q#1은 우리#19에게 r252 사망.|`QUEEN_SAFETY:true` 1424–1437: 탈출 실패·현재칸 노출이면 부모2를 남기는 구조. 이 분기 선택은 로그 없어 추정[E]. `RALLY_END_FRESH:5` 6511–6525는 신선도·길이비 등 관문; #533 정체 때 어느 관문이 실패했는지는 미확인. 지도 전역의 공급 보장 없음.|
|1485169|공격 직전 Q 시야에 #233의 머리·몸 모두 없음.|`QUEEN_SAFETY:true` 5274–5319: 머리 목록만 hit-map 원점, `!longs`이면 ghost 확대 없이 반환. stride에는 ghost가 있음(1767); 실제 기억 유무 미확인. **처음 보는 시야 밖 적은 nothing covers this.** `QUEEN_AVENGE:8` 2843–2844와 `QUEEN_SURE_LEN:4` 3478은 길이10 #371 제외.|
|1485170|r73 Q#0이 동쪽 진주를 먹어4→5. 그 뒤 적#9 7→2+#100 5 분열; 새 자식이 (18,15)→(17,15)→(16,15)→Q(16,14).|`QUEEN_SAFETY:true` 5274–5298 원점은 관측한 **머리**, 미래 분열 꼬리 머리는 없음. `SMALL_SPRINT_THREAT:true`도 이것을 만들지 않음. 최장 보호 `is_leader()` 4710–4715는 `board_short() && length<LEADER_FULL_KEEP`이면 해제; 일반분열 1853–1869는 이 예외와 길이4를 허용. 실제 leader 지식은 미확인.|
|1485174|Q 마지막 턴에 #414는 (25,32) 한 칸만 보임.|`QUEEN_SAFETY:true`: 5289–5294의 cut 보정은 최소3, `QS_PAY_REACH:3`으로 유료 reach 상한3. 실제 공격4걸음 누락. `SMALL_SPRINT_THREAT:true`는 여왕 cut 길이 추정 수정이 아님(3374–3381).|
|1485180|Q 살아 있음. r15·110에 각각 길이2 분열; 마지막 섭취 r109.|`QS_KEEP_LEN:3` 1862–1866은 5→3 허용. `EAT_FIRST:true`에는 먹을 빈 인접 진주가 없음. `FEEDER_EAT:true`·`RALLY_END_FRESH:5`도 `feed_len_ok()`(6521–6525)의 **2×2≤3 거짓**을 통과 못함. 이 관문은 확정, 각 아군이 Q를 leader로 알았는지는 미확인.|

| 여왕 사망 후 접근 [M] | 결과 |
|---|---|
|1485657|해당 없음: 적 여왕이 먼저 사망.|
|1485169|있음. r409 #371 거리5, r412 거리2; (31,7)→(32,7)→적Q(33,7)는 몸까지 제외한 빈 경로.|
|1485170|있음. r78 #60 거리5; r86 #105 거리2, 적Q(38,38).|
|1485174|없음. 최소11, r221 #459(53,13) 대 적Q(49,16); 마지막 적Q(48,20).|
|1485180|해당 없음: 우리 여왕 생존.|

[M] 위 접근은 매 몸변경·사망·분열 사건의 머리에서, 벽·포털을 반영한 최단거리다. 몸은 무시하므로 접근 가능성을 넉넉하게 센다. 1485169의 2걸음만 몸까지 검사했다.

| 원인 순위·빈도 [M/E] | 카드·현황·규칙 [C/E] | 확인할 수치 / 반증 |
|---|---|---|
|1. 여왕 관측 공백 3/5; 직접 여왕패2/5|**BEING BUILT**: 잘린 적 몸을 최소4로 취급, `CUT_BODY_LEN:4`. one8 1759–1765, 3374–3379, 5285–5294에 해당; 당시 `QUEEN_SAFETY:true`는 **LIVE-BUT-FAILED**. 새로 재제안하지 않음.|1485174 r196 착지의 실제4걸음 위협이 포착되는지. **최소4의 full reach는3이고 QS_PAY_REACH도3이라 이 카드만으로 커버 불충분.** 시야 밖 #233·미생성 #100도 미커버. 해당 장면이 계속 안전 판정되면 반증.|
|2. 최장 축적 실패 2/5(1485657·1485170), 서로 다른 세부기제|**No card**. `RALLY_END_FRESH:5`는 **LIVE-BUT-FAILED**(최종 집중 실패라는 결과만); 먹이 경로·내부 관문 미확인으로 값을 더 늘리자는 제안 없음.|#533의 무섭취32턴, #518의 반복분열9회, 길이18 이상(1485657)·9 이상(1485170) 사망0을 함께 추적. 피해 회피용 분열을 없애자는 결론은 지지하지 않음.|
|3. 살아 있는 Q 성장 단절 1/5(1485180)|**NEW**: feeding 중 길이4 미만의 알려진 leader에게 자기길이≤leader이면 공급 허용. 기존 스위치 **`FEED_BOOT_LEN:4`**(280,6521–6525); 현재0. Q 전용 효과라고 주장하지 않음.|현 215 근접턴 중 leader=Q·phase·경로가 성립한 수, Q가 실제 회수한 공급진주(현0), r110 이후 Q성장(현0)을 셈. 관문 통과해도 회수0이거나 일반 leader의 공급 손실이 늘면 반증.|

[C/E] 이미 개발 중인 `QUEEN_WAR`도 1485169 r412의 길이10 #371을 ≤8 제한 때문에 놓친다. Around UNSW의 최소거리11에는 무거리제한이 도움이 될 가능성만 있고, 적 여왕 위치 전달 여부는 미검증이다.

[M] 아래는 죽은 우리 여왕의 **마지막 세 자기 턴 시작** 7×7이다. 중앙 Q, q=그 몸, A/a=아군 머리/몸, E/e=적 머리/몸, *=진주, .=빈칸. 오른쪽은 같은 7×7의 벽 비트(북1·동2·남4·서8, 16진수); 포털은 이 벽표에 없고 거리 계산에는 포함했다. 좌표는 (x,y), 위가 북쪽.

| 경기·Q·r·중심 → 행동 | 7×7 점유 [M] | 7×7 벽 [M] |
|---|---|---|
'''
for gid in IDS:
    e = evidence[gid]
    deaths = [d for d in e['qdeaths'] if d['s'] == 0]
    if not deaths:
        continue
    q = e['queens'][0]
    ts = [t for t in e['qturns'] if t['id'] == q and t['round'] <= deaths[0]['round']][-3:]
    assert len(ts) == 3
    for t in ts:
        assert len(t['board']['rows']) == 7 and all(len(row) == 7 for row in t['board']['rows'])
        action = f"분열 {t['split'][3]}+#{t['split'][1]} {t['split'][4]}" if t['split'] else ''.join('북동남서'[d] for d in t['dirs'])
        cells = '<br>'.join(f'<code>{row}</code>' for row in t['board']['rows'])
        walls = '<br>'.join(f'<code>{row}</code>' for row in t['board']['walls'])
        report += f"|{gid} Q#{q} r{t['round']} {tuple(t['head'])} → {action}|{cells}|{walls}|\n"
report += '\n[M] 재현: `analyze.py`(공용 reader·ledger·Geometry import), `focus.py`, `logs.py`, `finish.py`; 근거 `*-evidence.json`, `*-ledger.json`, `*-turns.json`, `audit.json`, `focus.json`. 재계산 최종값은 공용 ledger와 일치, anomalies 전부0. [E] 반사실 대전·봇 재실행·내부 메시지 복원은 하지 않았다. 네트워크·대전·봇 수정 없음.\n'
report += '\n작성 시각: ' + datetime.now().astimezone().isoformat(timespec='seconds') + '\n'
(OUT / 'report.md').write_text(report)
non_table_words = sum(len(line.split()) for line in report.splitlines() if not line.startswith('|'))
assert non_table_words < 600, non_table_words
print('report.md written; non-table words:', non_table_words, '; queen boards:', sum(bool([d for d in e['qdeaths'] if d['s'] == 0]) for e in evidence.values()) * 3)
