import json
from pathlib import Path
from datetime import datetime
from collections import Counter,defaultdict
O=Path(__file__).resolve().parent
G=[json.loads(p.read_text()) for p in sorted(O.glob('game-*.json'))]
g=next(x for x in G if x['game']==1478190)
C=defaultdict(Counter);examples=[]
for x in G:
 c=C[x['label']];c['games']+=1;d=x['death']
 if not d:continue
 ram=d['reason']==3 and d['actor']!=x['queen'];c['ram']+=ram
 if not ram:continue
 ts=d['last3'];forced=len(ts[-1]['options'])==1;c['forced']+=forced
 fork=forced and len(ts)>1 and len(ts[-2]['options'])>=2;c['fork']+=fork
 if forced:examples.append((x['game'],d['r'],x['queen'],d['actor']))
 if fork and ts[-2]['pearls'] and str(d['actor']) in ts[-2]['visible']:c['food_fork']+=1
(O/'counts.json').write_text(json.dumps(C,indent=2))
now=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
text=f'''[M/C/E] 원인: r172 즉시 피격 위험 없는 북쪽을 좁은 포털 방으로 제외하고, 유료 공격을 받는 서쪽을 허용해 여왕 #1이 r173 피격됐다.
[E] 카드 없음: 북쪽 우선이나 포털 허용이 실제 탈출로 이어지는지 미검증이다. 검증된 단일 수정이 없다.
[M/C/E] 확신: 사건·코드 조건 높음, 피할 수 있는 장기 경로·수정 효과 미확인.

[M] {now}. **1478190, Maze, 우리 B, f2p 1890 대 우리 2095**. 메타데이터 제출값은 null이지만 기보 B 이름은 **21033(one6)**이다.

[M] r499 여왕 **0:62**로 패배. 총길이는 **114:104**, 최장은 **58:62**. r172까지 판정상 동률 이상으로 돌아왔으나 **r173부터 끝까지 열세**였다. 이는 사후 지속 열세 시점이며, 상대 여왕을 이후 죽일 가능성까지 없어진 시점은 아니다.

[M] 아래는 라운드 종료 상태, 각 칸 **드래곤 수 / 총길이 / 최장 / 여왕**.

| r | 우리 B | 상대 A |
|---:|---:|---:|
'''
for r in list(range(0,500,25))+[499]:
 a,b=g['snapshots'][str(r)];text+=f"| {r} | {' / '.join(map(str,a))} | {' / '.join(map(str,b))} |\n"
text+='''
[M] 여왕 마지막 세 턴. Q=여왕, b=자기 몸, E=#196; 모두 y=11, x는 열 번호. 22·23·25열은 남북이 벽이다. r171의 나머지 몸은 (26,10).

```text
x       21  22  23  24  25  26
r171     .---.---.---.---Q---b   Q 서→(24,11)
r172     .---.---.---Q---b---b   Q 서→(23,11)
r173     E→  × ← Q---b---b---.   (22,11) 충돌
                      |
                24열 북쪽 퇴로:
                (24,10) 진주 → (24,9) → 포털(32,4)
```

[M] #196은 여왕 턴 시작 기준 r171 (21,13) L3, r172 (21,12) L3, r173 (21,11) L4. r172 북쪽 한 걸음으로 진주를 먹었고, r173 동쪽 한 걸음으로 여왕을 죽였다. 여왕의 r173 유일한 빈 목적지는 (22,11); L3이라 분열 대기도 불가능했다.

[C] 사용 소스는 `data/online/smoke/one6-bot/main.cpp`. **QUEEN_SAFETY:true**(142)는 작동 대상이다. r172 #196 몸이 시야 경계에 걸려(1584–1585) 길이 추정이 최소4, 공격 범위가 **3걸음**으로 늘어난다(4356–4363). 서쪽 (23,11)은 유료 위험이다. 진주 성장 미반영을 이 사건의 누락 원인으로 보면 틀린다.

[C/M] **QUEEN_NO_PORTAL:true**(168,4155–4156,5632,3182–3183)는 북쪽을 두 칸 방으로 만든다. room=2<5라 closed(5999), 위험이 없어도 열린 안전 대안에서 제외한다(6074). escape 역시 room≥5 또는 꼬리 도달을 요구한다(4528). **pay_open && risk_at(chosen_index)<2**는 유료 위험인 서쪽 이동을 허용한다(738–741). [E] 이 분기가 관측 행동과 일치한다; 전체 봇 재실행은 하지 않았다.

[M/C] r173에는 서쪽만 빈칸이며 적의 무료 공격 범위다. L3이라 분열 불가, QUEEN_WAIT 최소4에도 미달(4160). 비상 탐색 뒤 qs_plain 복귀(750)가 외길 피격을 막지 못한다. [M/E] 적은 r172에도 N,E,E로 진주를 먹으며 L3→4→3→2로 즉시 충돌 가능했다([경로 검증](mechanism.json)); 실제로는 N만 했다.

[M] 같은 제출의 중복 제거 45판. ‘외길 피격’은 마지막 자기 턴에 빈 이동 목적지가 정확히 하나인 여왕 피격. ‘직전 갈림길’은 바로 전 자기 턴에 목적지≥2. 벽·몸 점유 기준이며 분열·사냥 대안까지 뜻하지 않는다.

| 묶음 | 판 | 여왕 피격 | 외길 피격 | 직전 갈림길 |
|---|---:|---:|---:|---:|
'''
for label in ['one6-w1','one6-c1','ranked']:
 c=C[label];text+=f"| {label} | {c['games']} | {c['ram']} | {c['forced']} | {c['fork']} |\n"
text+='''
[M] 반복 장면: 1474985 Maze r136 #1←#145, 1474992 Trophy r75 #0←#49. 직전 갈림길 세 사례 중 보이는 진주·공격자가 함께 있는 것은 이번 판뿐(1/45; WHQ·Cache 세트 0/30). [E] 나머지 외길 사망까지 동일한 코드 원인이라고 단정하지 않는다.

[M] [재집계](analyze.py), [검증](verification.json): 45판 양편 최종 네 지표와 서버 총길이 일치; 대상 500개 라운드 상태는 기존 집계기와 일치. [E] 미확인: 전체 봇 점수·음파 기억 재실행, 북쪽 포털 탈출의 생존, 수정 전후 효과. 효과 확인 기보 **0판**; 구현·대전 없음.
'''
(O/'report.md').write_text(text)
(O/'DECISIONS.md').write_text(f'''# 분석 결정\n\n{now}\n- 브리프대로 이 폴더에만 기록. 원격 접근·대전·봇 변경 없음.\n- 기보 이름으로 제출 21033(one6) 확인; 메타데이터 null을 버전 추정으로 대체하지 않음.\n- 여왕 피격 및 직전 포털 퇴로 제외·유료 위험 이동 허용 확인. 시야 경계 보정 때문에 이 장면은 공격 범위 누락이 아님. 단일 안전한 수정의 효과가 검증되지 않아 카드 없음.\n- 45판 최종 상태 대조 및 대상 모든 라운드 독립 대조 완료. nice -n 10은 샌드박스가 setpriority를 거부했으나 명령은 실행됨; 한 프로세스로 순차 집계.\n''')
print('wrote report; whitespace words',len(text.split()))
