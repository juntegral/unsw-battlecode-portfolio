import sys,json
sys.dont_write_bytecode=True
from scan import OUT
from collections import Counter,defaultdict
from datetime import datetime

labels=['one4-w1','one4-d1','one4-ranked','one5-w1','one5-c1','one5-d1','one5-ranked','mDo5_vh']
counts=defaultdict(Counter);games=Counter();nearest=defaultdict(Counter);diag=defaultdict(Counter)
for f in sorted(OUT.glob('anytwo-*.json')):
    d=json.loads(f.read_text());label=d['meta']['label'];games[label]+=1
    for r in d['rows']:
        for w in ['all']+(['early'] if r['r']<=100 else []):
            counts[label,w,r['mate']][r['cls']]+=1
            if not r['adjacent']:nearest[label,w,r['mate']][r['cls']]+=1
for f in sorted(OUT.glob('diag-*.json')):
    d=json.loads(f.read_text());label=d['meta']['label']
    for r in d['rows']:
        for w in ['all']+(['early'] if r['r']<=100 else []):
            c=diag[label,w];c['away']+=1;c[r['assignment']]+=1;c['safe_unclaimed']+=r['safe_unclaimed']
T=json.loads((OUT/'traps.json').read_text());trap=Counter(r['status'] for r in T['rows']);N=sum(trap.values())
timestamp=datetime.now().astimezone().isoformat(timespec='seconds')

def census(w):
    lines=['| [M] 자료(판수) | 시야 내 아군 머리 | 적격 턴 | 접근 | 이탈 | 옆 | 분열 | 이동 전 사망 |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for label in labels:
        if not games[label]:continue
        for mate in (True,False):
            c=counts[label,w,mate]
            lines.append(f'| {label} ({games[label]}) | {"있음" if mate else "없음"} | {sum(c.values())} | '+ ' | '.join(str(c[k]) for k in ['toward','away','sideways','split','died'])+' |')
            assert c['no_step']==0
    return lines

lines=[
'[M/C/E] 두 칸 진주 이탈에는 아군 선점·영토 점수가 관련된다. 별도 dead 추적 후보의 97.6%는 다른 몸을 고정하면 탈출 불가였다.',
'[E] 카드 1: 안전하고 선점되지 않은 두 칸 진주 접근에도 EAT_FIRST의 영토 손실 보정을 적용한다(검증 후보).',
'[M/E] 확신: 행동 집계 높음, 영토 원인 중간, 카드의 실전 효과 미검증. 막다른길 판정의 일괄 완화는 제안하지 않는다.',
'',f'[M] 작성 {timestamp}. 대상·재현 절차: [methods.md](methods.md), 개별 사건: `anytwo-*.json`, `diag-*.json`, `traps.json`.',
'',
'[M] 아래는 전체 라운드. 비여왕, 보이는 진주까지 **몸이 없는 통로 정확히 두 걸음**, 적 머리까지 열린 변·포털 거리 >4. 첫 성공 걸음으로 분류하며 여러 진주는 최단거리 집합으로 취급한다. 바로 옆 진주가 있는 턴도 포함한다. 아군은 자신 제외 7×7 안 머리. 무료 이동 예산도 두 걸음 이상인 L≥5 집계는 methods에 있다. WHQ·Cache를 주 표본, dev test 1을 보조로 읽는다.',
'']+census('all')+[
'',
'[M/C/E] 원인 진단은 바로 옆 진주가 없는 이탈만 사용했다. “아군 선점”은 모든 두 칸 진주에 보이는 아군이 한 걸음 거리인 경우다. “안전·미선점”은 다른 몸을 고정하고 두 걸음 접근·섭취 후 몸 전체가 성장한 길이+2걸음 이동할 수 있는 진주가 있는 경우다. 이 둘을 최종 점수 원인의 완전한 분류로 해석하면 안 된다.',
'',
'| [M] 자료 | 이탈 | 모든 목표 아군 선점 | 안전·미선점 목표 있음 |',
'|---|---:|---:|---:|']
for label in labels:
    if not games[label]:continue
    c=diag[label,'all'];lines.append(f'| {label} | {c["away"]} | {c["all_mate_nearer"]} | {c["safe_unclaimed"]} |')
lines += [
'',
'| 코드 항목 | 판정 |',
'|---|---|',
'| [C] 아군 선점 | `ally_race_steps`가 `share`, `dist_pearl`, `look_cell_value`를 꺼버림: one5 main.cpp:3125–3151, 3665. 단순 영토 손실과 별개. |',
'| [C/E] 영토 | 5644–5649의 `WEIGHT_TERRITORY=1.5`; 6005, 6023–6043 보정은 인접 진주만. 아래 재구성 사례에서 접근 불이익 확인. |',
'| [C] 막다른길·주머니 | 5651–5672의 tight/trapped/no-tail, 5731–5742의 pocket. 기보의 탈출 불가와 실제 실행 플래그는 구별해야 함. |',
'| [C] leader zone / ZONE_NEARER | 2485–2510, 5753: 초반 r≤100에는 zone 비활성(47–48, 284, 558); ZONE_NEARER는 우리가 더 가까우면 금지를 해제함. |',
'| [C] crowd load | 291의 CROWD_MARGIN=0이므로 3232–3237의 ally_load는 0. |',
'| [C/E] SPAWN_CLEAR | 267–270, 5744–5750의 빈 생성칸 −300. 온라인 countdown이 가려져 턴별 기여 미확정. |',
'',
'[M] 막다른길 검증은 **기존 m9etr1 추적 8판의 별도 표본**이다. one4/one5에는 점수 로그가 없어 그 모집단의 실제 dead 플래그 비율은 산출 불가. chosen=0·dead=1·비분열·비여왕을 기보와 대조한 3,202턴, 3,247 진주 후보다.',
'',
'| [M] 섭취 후 몸 탐색 결과 | 후보 | 비율 |',
'|---|---:|---:|',
f'| 다른 용을 전부 지워도 탈출 불가 | {trap["intrinsic_trap"]} | {100*trap["intrinsic_trap"]/N:.1f}% |',
f'| 다른 몸을 고정하면 불가, 지우면 가능 | {trap["occupied_exit"]} | {100*trap["occupied_exit"]/N:.1f}% |',
f'| 다른 몸을 고정해도 탈출 경로 존재 | {trap["safe"]} | {100*trap["safe"]/N:.1f}% |',
'',
f'[M/E] 현재 다른 몸을 고정한 함정률은 {(100*(N-trap["safe"])/N):.1f}%. 실제 다음 턴의 다른 용 행동까지 반영한 함정률은 아니다. 분열·유료 단축·새 진주 생성은 제외했다.',
'',
'[M/E] 판면: 1470218 r12 #4는 (18,24)→(19,24), 진주는 (17,25). 개인 시야 재구성에서 접근 방향의 영토 손실 하한 728.25점, 진주 거리 이득 160점. one5 WHQ 1472005 r23 #25는 (40,7)→(39,7), 진주 (41,6), 같은 하한 617.25점. 1471459 r17 #7은 (44,5)→(45,5), 진주 (42,5), 하한 144.75점. 세 사례 모두 방향별 방 크기가 같고 꼬리에 도달한다. 실제 내부 기억을 보장한 점수 추적은 아니다(`territory.json`).',
'',
'[M] 함정 사례: m9etr1/Australia-side0 r17 #18→(36,2)는 섭취 직후 출구 없음; Around-UNSW-side0 r6 #24도 탈출 불가. 반례: blobs-large-side0 r90 #181→(19,52)는 S,E,N,N,N,N으로 탈출한다. 거절 후보의 추적값은 room=4, cramped=10800이다. 추가 반례 Around-UNSW-side1 r27 #20은 room=8이지만 탈출 가능.',
'',
'[E] 카드 조건: 비여왕·비리더·비피더, 인접 진주 없음, 현재 보이는 미선점 진주까지 두 열린 걸음, 적 머리 4걸음 이내 없음. 접근·섭취 양쪽의 기존 pocket/dead/zone/threat/risk 검사를 통과할 때만 첫 걸음의 영토 손실을 보정한다. 위치: 6003–6008의 후보 판정과 6023–6043. 기존 EAT_FIRST만으로는 두 칸에 적용되지 않으므로 별도 기본-off 스위치가 필요하다. 성공: 위 안전·미선점 이탈의 접근 전환과 두 자기 턴 안 섭취를 짝지어 센다. 반증: 함정/zone 금지 우회, 분열 변화, 접근 뒤 충돌 증가 또는 CPU 초과. 막다른길 완화 카드는 없음.',
'',
'[M/E] 미확인: 전체 away의 정확한 항별 점수 분해, 실제 봇 기억·생성 타이머·경로 덮어쓰기, 카드 빌드·대전·CPU·온라인 개선. 88판 집계 대조와 77개 탈출 경로 재검증은 통과했다. 새 게임·네트워크·봇 변경은 하지 않았다.'
]
(OUT/'report.md').write_text('\n'.join(lines)+'\n')

details=['[M] 재현 및 정의', '', f'[M] 생성 {timestamp}.', '',
'[M] 실행 순서: `python3 -B data/codex/astra/approach/scan.py`, `anytwo.py`, `diagnose.py`, `traps.py`, `territory.py`, `verify.py`, `make_report.py` (뒤 파일도 같은 디렉터리). 기존 reader `tools/ladder_replay.py`와 `o1_scan.STEP`를 import했다. 모든 쓰기는 이 디렉터리 안이다. nice -n 10을 요청했지만 샌드박스가 setpriority를 거부하여 로그에 남았다.', '',
'[M] 중복 제거: smoke one4/one5 old와 live-one1을 game id로 구분. ranked는 시작 시각이 아닌 replay bot id 20941/20980으로 판정했다. 로컬은 완료 result.txt가 있는 mDo5_vh 8판. inventory.json과 verification.json에 경로·id·검증을 보존했다.', '',
'[M] D2 거리: 턴 시작 보드, kelp 차단·포털 연결·토러스 적용·모든 몸 칸 차단. 목표는 현재 7×7에 보이며 최단거리가 정확히 2인 진주 전부다. 거리 1 진주 유무도 기록했다. 첫 성공 걸음에서 시작 점유를 고정하되 이전 머리 칸만 풀고 목표집합까지 거리를 다시 잰다. 감소/증가/동일이 접근/이탈/옆이다. 분열을 먼저 분류하고 성공 걸음 없이 죽으면 별도 열. 실제 시도했지만 실패한 방향은 추측하지 않는다.', '',
'[M] 머리 안전 필터는 전지적 기보의 열린 변·포털 그래프 거리이며 몸을 무시한다. 적 머리가 하나라도 4 이하이면 제외. 아군 있음은 현재 7×7의 다른 아군 머리; 몸만 보이는 아군은 포함하지 않는다.', '',
'[M] 아래 r0–100 포함 집계. 과거 15.9%와 분모·첫 걸음/최종 위치 정의가 다르므로 직접 전후 효과로 비교하지 않는다.', '']+census('early')
details+=['','[M] 한 턴의 무료 이동 예산이 실제로 두 걸음 이상인 경우(L≥5)의 별도 전체 집계.','',
'| 자료 | 시야 내 아군 머리 | 적격 | 접근 | 이탈 | 옆 | 분열 | 이동 전 사망 |','|---|---|---:|---:|---:|---:|---:|---:|']
for label in labels:
    if not games[label]:continue
    for mate in (True,False):
        c=Counter()
        for f in OUT.glob('anytwo-'+label+'-*.json'):
            for r in json.loads(f.read_text())['rows']:
                if r['L']>=5 and r['mate']==mate:c[r['cls']]+=1
        details.append(f'| {label} | {"있음" if mate else "없음"} | {sum(c.values())} | '+' | '.join(str(c[k]) for k in ['toward','away','sideways','split','died'])+' |')
details+=['','[M] 막다른길 표본: w-eat/tr/flip-*.log와 m9etr1의 같은 game.replay를 (round,id)로 결합했다. 머리·길이·진주 위치를 assert로 확인. trace_cases는 인접 진주 중 하나라도 chosen=1이면 제외한다. 여러 거절 진주를 가진 턴은 후보별로 센다. 비율의 분모는 3,247 후보이고 턴은 3,202개다.', '',
'[M] 함정 탐색: 진주를 먹어 길이를 1 늘린 정확한 몸을 시작 상태로 놓고 성장 후 L+2번의 후속 이동이 가능한지 완전 상태 DFS. 자기 몸 전체(꼬리 포함)와 다른 몸의 현재 칸은 충돌 처리. 매번 진주 소비/성장/꼬리 이동을 갱신한다. 추가 진주도 실제로 먹는다. 상태 상한 50,000에 도달하면 unknown; 이번 표본은 unknown 0. 다른 몸을 지운 탐색도 새로 돌려 벽·자기 몸과 일시적 점유를 구별한다. 이 검사는 다음 다른 용의 정책, 상대가 만드는 진주, 미래 자연 생성, 분열과 유료 이동으로 줄어드는 몸을 예측하지 않는다.', '',
'[M/E] 안전 경로는 주어진 보드의 유한 시간 생존 증명이며 영구 생존 증명이 아니다. 다른 몸을 지웠을 때의 함정 역시 현재 진주를 고정한 모형의 결과다. 77개의 safe 경로는 verify.py가 다시 이동시켜 충돌·성장·길이를 확인한다. 실제 mDo5/온라인 dead 플래그를 이 비율로 대신하지 않는다.', '',
'[C/E] territory.py는 선택한 세 사건의 해당 용이 차례를 받은 모든 7×7 창을 누적하고, 알려진 벽과 현재 보이는 다른 몸, 자기 몸 해제 시간을 사용해 survey_from을 부분 재구성했다. 원본 3089–3245의 BFS, 아군 거리, 진주 기억을 따른다. 보이는 칸의 실제 타이머가 없어서 territory_weight는 [0,1]의 범위로만 계산하며 미관측 칸은 정확히 0.5 가중치다. 손실 하한은 1.5×(선택 방향 최소−접근 방향 최대). 알려진 포털이 있는 사례는 지원하지 않아 제외했다. sonar/몸 기억/CPU budget/각종 route 상태와 hot/soon 보상은 실행한 봇의 정확한 상태와 대조하지 않았다. 이 때문에 원인 확신은 [E]이며 실측 score trace로 부르지 않는다.', '',
'[C] 코드 줄 번호는 data/online/smoke/one5-bot/main.cpp를 기준으로 한다. EAT_FIRST의 안전 조건을 풀지 않고 두 칸까지 확장하는 카드만 제안한다. CRAMPED_EAT(72,5654)은 다른 의미의 tight/no-tail 완화이며 이번 카드의 대체 스위치가 아니다.', '',
'[M] 요청받은 모든 away에 정확한 단일 score term을 붙이는 일은 완료하지 못했다. 온라인 기보는 내부 점수와 스폰 타이머가 없고 브리프는 새 게임/봇 실행을 허용하지 않는다. 계산 가능한 선점·탈출·영토 범위와 확인 불가를 분리했으며, 미확인 턴을 territory로 임의 분류하지 않았다.']
(OUT/'methods.md').write_text('\n'.join(details)+'\n')
(OUT/'summary.json').write_text(json.dumps(dict(generated=timestamp,games=dict(games),counts=[dict(label=k[0],window=k[1],mate=k[2],counts=dict(v)) for k,v in counts.items()],diagnostics=[dict(label=k[0],window=k[1],counts=dict(v)) for k,v in diag.items()],trap=dict(trap)),indent=2))
print('report.md',len('\n'.join(lines).split()),'words including tables',dict(games))
