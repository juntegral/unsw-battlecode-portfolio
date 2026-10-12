import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from statistics import mean

OUT = Path(__file__).resolve().parent
G = [json.loads(l) for l in (OUT/'games.jsonl').read_text().splitlines()]
assert len(G) == len({g['gid'] for g in G}) == 45
for label, wins in (('one5-w1', 3), ('one5-c1', 6), ('one5-d1', 0)):
    games = [g for g in G if g['label'] == label]
    assert len(games) == 15 and sum(g['result']=='win' for g in games)==wins
for g in G:
    assert g['bots'][g['ours']] == '20980' and not g['anomalies']
    assert g['final'] == g['snapshots'][str(g['last_round'])]
    assert sorted(map(int, g['snapshots'])) == list(range(g['last_round']+1))
    meta = json.loads(Path(g['path']).with_name(f"game-{g['gid']}.json").read_text())
    assert meta['scores'+g['ours']] == g['final']['us']['total']
    assert meta['scores'+('B' if g['ours']=='A' else 'A')] == g['final']['them']['total']
    if g['result'] == 'loss':
        m, t = g['measure'], g['last_level']
        assert g['snapshots'][str(t)]['us'][m] >= g['snapshots'][str(t)]['them'][m]
        assert all(s['us'][m] < s['them'][m] for r,s in g['snapshots'].items() if int(r)>t)
        assert t < g['last_round']
    u,v = g['final']['us'], g['final']['them']
    if u['alive'] and v['alive']:
        actual = 'win' if tuple(u[k] for k in ('queen_length','longest','total')) > tuple(v[k] for k in ('queen_length','longest','total')) else 'loss'
        assert g['result'] == actual
    else:
        assert g['result'] == ('win' if u['alive'] else 'loss')
A = [g for g in G if g['bucket']=='a' and g['label']!='one5-d1']
assert len(A)==11
assert sum(g['cells']<=1200 for g in A)==9
assert sum(g['snapshots'][str(min(150,g['last_round']))]['us']['alive']*2 < g['snapshots'][str(min(150,g['last_round']))]['them']['alive'] for g in A)==9
B = json.loads((OUT/'behavior.json').read_text())
b=[r for r in B if r['label']!='one5-d1']
assert sum(r['splits'][0]<r['splits'][1] for r in b)==10
assert sum(r['natural'][0]<r['natural'][1] for r in b)==10
E = json.loads((OUT/'early_behavior.json').read_text())
assert len(E)==11 and sum(r['adjacent_away'][0]>0 for r in E)==10
assert sum(r['away'][0]*r['turns'][1]>r['away'][1]*r['turns'][0] for r in E)==6

intro = '''[M] one5 주 표본 21패의 최대 묶음은 a(전멸 또는 r150 머릿수 열세) 11패다. 최장 용 7, 여왕만 2, 기타 1이다.
[E] no card. 다수 판에서 가까운 진주에 전진하지 않는 이동은 보이지만, 하나의 코드 규칙이 원인이라고 확인하지 못했다.
[M/E] 집계 확신은 높음(45판·one5 제출 20980 확인); 공통 행동의 인과 설명은 낮음.

[M] 분류는 기존 o1_buckets.py와 같은 우선순위다: a=전멸 또는 r150 N우리×2<N상대; b=여왕 패배·우리 여왕 사망·r300 총길이≥상대 80%; c=최장 용 패배; d=나머지. 조기 종료 뒤 체크포인트는 종료 상태를 유지(†). 본문 외 숫자는 모두 표에 있다.
[M] t는 실제 최종 승부 기준에서 마지막 동률·우세였던 **라운드 말**이다. 이후 모든 라운드에서 뒤짐을 검사했다. tN은 머릿수의 같은 값이다. 이는 실제 역전 불가능성을 뜻하지 않는다. 게임 라운드 표기는 기보의 r0–499다. 직전 창은 (t−30,t], 초기 창은 r0에서 자른다. 최대 사망은 몸길이 기준이며 동률이면 첫 사건이다.

'''
after = '''
[M] a의 11판 중 9판은 r150 머릿수도 절반 미만이고, 9판은 ≤1200칸이다. 하지만 Default(1472010)는 tN=201, Cache Stripes(1472756)는 tN=227 뒤 전멸했다. a 전체를 “r150 전에 결정”이라고 해석하면 틀린다. Cache Australia(1472753)는 끝 머릿수에서 회복했고 실제 패배 기준은 최장 길이다.

[M] Cache 승패 평균은 r100부터 갈린다(승리군 총길이 75.3:70.5, 패배군 52.6:75.9); r200·300에는 패배군 격차가 유지된다. 그러나 초반 우세는 충분조건이 아니다. 1472756 r200은 15마리/38 대 11/28인데 r300은 1/3 대 21/57이다. 1472761 r300은 245:173, 종료도 285:248이나 최장 35:63으로 졌다. 반대로 1472764 r300은 39:146인데 종료 여왕 43:36으로 이겼다. 1472765 r200은 53:98이나 종료 최장 51:19로 이겼다. [E] 체크포인트 평균만으로 한 규칙의 효과를 분리할 수 없다.

[M] 최대 묶음의 공통 행동: **가까운 미선점 진주에 전진하지 않고 이동함**. r0–100 한 걸음 옆 진주 비전진은 10/11판; 전체 비전진 비율이 상대보다 높은 판은 6/11이다. r0–150 자연진주 섭취와 분열 모두 상대보다 적은 판은 10/11이지만, 섭취·분열 부족은 원인으로 확정한 행동이 아니라 결과다.
[M] 실제 순간: 1472010 r97 #57 L2, (3,3)에서 진주 (3,2) 대신 (4,3); 1472015 r54 #6 L2, (32,7)에서 진주 (33,7) 대신 (32,6); 같은 판 r64 #29 L3은 같은 진주 대신 (31,7). 진주까지 한 걸음, 더 가까운 동료 없음, 목표 주변 적 머리 거리>3, 분석 도구의 출구 지표는 1이었다. [E] 이 조건만으로 안전성을 보장하지 않는다.
[C] one5-bot/main.cpp:112에서 EAT_FIRST는 이미 켜져 있고 :6003–6007은 주머니·막힘·위협·위험·적 도달로 보정을 제한한다. [E] 해당 순간의 내부 점수/관문을 재현하지 않아 이를 풀 카드 근거가 없다.

[M] 미확인: 내부 점수·음파 기억·동료 공유 시야, 진주 비전진의 안전한 대안과 승패 인과, 신규 규칙의 작동/CPU. 지도는 설명용이며 지도별 규칙은 제안하지 않았다. 새 대전·네트워크·봇 수정은 없었다.
'''
after += '\n[M] 확인 시각: '+datetime.now().astimezone().isoformat(timespec='seconds')+'; 재현: analyze.py → behavior_check.py → summarize.py → finalize.py.\n'
report = intro+(OUT/'tables.md').read_text()+after
words=sum(len(line.split()) for line in report.splitlines() if not line.lstrip().startswith('|'))
assert words < 450, words
(OUT/'report.md').write_text(report)
verification = dict(checked_at=datetime.now().astimezone().isoformat(), games=45, main_losses=21, separate_dev_losses=15,
                    prose_words=words, own_bot='20980', assertions='inventory, unique ids, submission, metadata totals and winners, end states, every-round last-level permanence, bucket and behavior counts',
                    reused='games.jsonl from interrupted run; imported replay readers and o1_scan; cached o1_mid (three sample games independently rerun)')
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(verification,ensure_ascii=False,indent=2))
