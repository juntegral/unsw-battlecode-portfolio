"""Render the concise report and complete per-game appendix."""
import csv,json
from pathlib import Path
from datetime import datetime
from collections import Counter

P=Path(__file__).resolve().parent
S=json.loads((P/'summary.json').read_text()); G=json.loads((P/'games.json').read_text())
L=[g for g in G if g['result']=='loss']; s=S['loss']; a=S['all']; ledger=S['count_ledger']
inventory=json.loads((P/'inventory.json').read_text())

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers)]+['| '+' | '.join(map(str,row))+' |' for row in rows])
def pair(d,digits=None):
    return '/'.join(str(d[x]) if digits is None else f'{d[x]:.{digits}f}' for x in ('us','them'))
def rate(d): return f"{d['taken']}/{d['n']} ({100*d['taken']/d['n']:.1f}%)" if d['n'] else '0/0'
def snap(g,r):return g['snapshots'][str(min(r,g['last_round']))]

early=sum(g['final']['us']['alive']==0 and g['last_round']<=150 for g in L)
half=sum(2*snap(g,150)['us']['alive']<snap(g,150)['them']['alive'] for g in L)
netus=ledger['splits31_100_us']-ledger['deaths31_100_us']; netthem=ledger['splits31_100_them']-ledger['deaths31_100_them']
equal=s['candidate_filters']['equal_behind']; filtered=s['candidate_filters']['equal_behind_no_nearer']
report=[f"[M] 발견: r30→100 머릿수 순증은 우리 {netus}, 상대 {netthem}; 열세에서 우리가 건 동길이 충돌의 5라운드 진주 회수는 {pair(equal['recovered5'])}다.",
        '[E] 카드: no card. 동길이 교환 일괄 금지를 지지하지 않는다.',
        f"[M/E] 확신: 사건 집계 높음({len(G)}판 교차 검증); 행동 변경의 생존·승패 효과 미검증.", '',
        f"[M] 집계 마감 {inventory['time'][:19]} KST; 작성 {datetime.now().astimezone().isoformat(timespec='seconds')}. 소형 ≤1200칸. one3/4/5 각 상대 세트 15판씩 완비. 소형 {len(G)}판 중 패배 {len(L)}판(버전별 {s['by_build']['one3']}/{s['by_build']['one4']}/{s['by_build']['one5']}); 랭크 소형 13판 포함, one5 랭크 기보 없음. r150까지 전멸 {early}판, r150 머릿수 절반 미만 {half}판. 이하 우리/상대 순서.", '',
        '[M] 패배별 r0–150 매 10라운드 머릿수·사망·교환 비용 전수는 [tables.md](tables.md), 개별 길이/시야/보드 수는 [collisions.csv](collisions.csv), 먹은 용 id·시각은 [drops.csv](drops.csv).', '',
        '[M] 집단별 패배 머릿수 평균', '',
        table(['집단','패배','r30','r100','r150'],[[k,v['games'],pair(v['curves']['30'],1),pair(v['curves']['100'],1),pair(v['curves']['150'],1)] for k,v in S['groups'].items()]), '',
        '[M] r31–100 분열/사망/순증 원장', '',
        table(['항목','우리','상대'],[['분열',ledger['splits31_100_us'],ledger['splits31_100_them']],['사망',ledger['deaths31_100_us'],ledger['deaths31_100_them']],['순증',netus,netthem]]), '',
        f"[M] 격차 확대 {ledger['gap_change']} = 분열 차 {ledger['split_gap']} + 사망 차 {ledger['death_gap']}. [E] 이는 원장 분해이며, 분열 억제가 원인이라는 증명은 아니다.", '',
        '[M] 우리 사망, r0–150', '',
        table(['피격','선제 충돌','벽','자기 몸','아군 몸','적 몸','아군 머리','무효이동/무행동'],[[s['deaths'].get(k,0) for k in ('rammed','rams','wall','self','mate_body','enemy_body','mate_head')]+[sum(s['deaths'].get(k,0) for k in ('unpaid sprint','illegal split','no action','timeout'))]]), '',
        f"[M] 분열 당일/다음 라운드·빈 출구 0·비머리충돌은 {s['postsplit_boxed_proxy']}건(위 원인과 중복). [E] 봉쇄의 보조 지표이며 분열의 인과 효과나 굶음을 확정하지 않는다.", '',
        '[M] 우리 보드 머릿수가 열세일 때의 충돌, r0–150', '',
        table(['시작한 편','건수/경기','잃은 길이','회수≤5','직접 순손익','보드 길이 Δ5 평균','5라운드 미완료'],[[who,f"{v['n']}/{v['games']}",pair(v['lost']),pair(v['recovered5']),pair(v['direct_net5']),pair(v['mean_board_delta5'],2),v['censored']] for who,v in s['behind_collisions'].items()]), '',
        '[M] 직접 순손익=−사망 길이+해당 시체 진주 회수. 보드 Δ는 다른 사건도 포함한다. '+f"우리 선제 {s['behind_collisions']['us']['n']}건 중 trade 기하 조건 {s['behind_collisions']['us']['trade_geometry']}, HUNT_SMALL_RATIO 기하 조건 {s['behind_collisions']['us']['hunt_geometry']}건. 실제 분기 발동은 미확인.", '',
        '[M] 교전 기회 채택률: 전체 소형 승패 포함. 시야 내 적 머리까지 ≤3 공짜 걸음·몸 없는 경로가 분모.', '',
        table(['상대/구간','상대가 열세','상대가 우세'],[['전체/r0–150',rate(a['opportunities']['them_behind']),rate(a['opportunities']['them_ahead'])]]+[[op+'/r31–100 L2–4',rate(a['opportunities_stratified'][op+'|31-100|L2-4|behind']),rate(a['opportunities_stratified'][op+'|31-100|L2-4|ahead'])] for op in ('WeHaveQuizzes','dev test 1 :P')]), '',
        '[E] 열세에서 공격 채택률이 낮다. dev의 열세 표본은 작고, 의도적인 회피 여부는 모른다.', '',
        '[M] 충돌 진주별 가까운 생존 머리와 5라운드 회수(벽·포털 최단거리, 몸 무시)', '',
        table(['가까운 편','진주','우리 회수','상대 회수','미회수'],[[k,v['drops'],v.get('us',0),v.get('them',0),v.get('uneaten5',0)] for k,v in s['drop_distance'].items()]), '',
        '[M] 가상 필터의 적용 범위(비여왕 시작 길이≤4, 동길이 충돌)', '',
        table(['필터','표시 건수/경기','잃은 길이','회수≤5'],[[name,f"{v['n']}/{v['games']}",pair(v['lost']),pair(v['recovered5'])] for name,v in [("보드 열세",equal),("보드 열세+아군이 충돌점에 더 가깝지 않음",filtered),("자기 팀 8마리 미만",s['candidate_filters']['equal_us_lt8'])]]), '',
        f"[E] 거리 필터는 {filtered['games']}판의 {filtered['n']}개 행동을 표시한다. 거부했을 때 살아남을지, 어느 판의 결과를 바꿀지는 모른다. 상대 전체 수는 사후 정보다. 이 단계에서는 카드로 채택하지 않는다.", '',
        '[C] one5 `main.cpp:557,2831–2844`: 작은 지도 aggressive가 동길이를 허용하므로 `TRADE_EVEN`만 꺼도 유지된다. `:2773–2774`는 전체 적 길이가 아닌 보이는 몸 조각 비율이다. 삽입 후보 위치는 `mark_trade_targets():2841`이나 방어 예외·hunt 우선 경로를 보존해야 한다.', '',
        '[M] 기보 장면', '',
        table(['발견','경기/라운드','확인한 상태'],[
            ['순증 격차','1465970 r30→100 / 1468670 r30→100','Tower Defense 머릿수 3/3→11/16; 3/2→10/19'],
            ['분열 직후 봉쇄','1465505 r39 #58 / 1465978 r39 #32','둘 다 당일 태어난 L2, 빈 출구 0; 벽 / 아군 몸 사망'],
            ['선제 충돌·회수 거리','1465970 r96 #25→#19','L2/L2, 보드11/16, 시야5/2, 거리3/5; 우리 #40이 r96–97 진주2 회수'],
            ['선제 충돌·회수 거리','1465500 r72 #23→#22','L2/L2, 보드6/10, 시야2/2, 거리3/2; 적 #14가 r74 진주2 회수'],
            ['피격 손실','1471466 r39 / r40','적 #10(L3)→우리 #0(L3), 적 #7(L3)→우리 #13(L2); 회수0/4, 0/2'],
            ['열세 기회 비채택','1465492 r89 #24 / 1470227 r39 #11','WHQ 머릿수10:12 / 4:15, 적 머리 공격 가능; 두 차례 모두 충돌하지 않음'],
            ['열세에서도 공격','1465503 r39 #24 / 1472014 r45 #19','WHQ 머릿수10:11 / 9:11, 두 차례 모두 충돌 실행']]), '',
        '[E] 미확인: 분기 표식·내부 기억·대체 행동·패치 재경기·CPU. 거리와 회수의 관계는 인과 검증이 아니다. 재현·정의·검열·전수 검증은 [methods.md](methods.md).', '']
(P/'report.md').write_text('\n'.join(report))

curves=list(csv.DictReader((P/'count-curves.csv').open()))
pergame=list(csv.DictReader((P/'per-game.csv').open()))
tabs=['# 소형 패배 전수 표','',f"[M] {len(curves)}판; 기준 {inventory['time']}. 우리/상대. 조기 종료 뒤 최종 상태 유지.",'']
for rounds in (range(0,80,10),range(80,151,10)):
    keys=[f'r{r}' for r in rounds]
    tabs += [f"[M] 머릿수 {keys[0]}–{keys[-1]}",'',table(['경기','버전/세트','지도','종료']+keys,[[r['gid'],r['build']+'/'+r['label'],r['map'],r['end']]+[r[k] for k in keys] for r in curves]),'']
tabs += ['[M] 사망 r0–150; 봉쇄는 다른 사인과 중복하는 분열 직후 보조 지표. 무효이동·무행동·불법분열·timeout은 전수 0.','',table(['경기','피격','선제','벽','자기 몸','아군 몸','적 몸','아군 머리','분열 직후 봉쇄'],[[r['gid']]+[r[k] for k in ('rammed','rams','wall','self','mate_body','enemy_body','mate_head','postsplit_boxed_proxy')] for r in pergame]),'']
for who in ('us','them'):
    tabs += [f'[M] 우리 보드 머릿수 열세일 때 {who}가 시작한 충돌, r0–150. 길이/회수/직접순손익은 우리/상대.','',table(['경기','건수','사망 길이','회수≤5','직접순손익','보드 Δ5 평균','미완료'],[[r['gid'],r[f'{who}_starts_us_behind']]+['/'.join(r[f'{who}_starts_{metric}_{s}'] for s in ('us','them')) for metric in ('lost','recovered5','net5','mean_board_delta5')]+[r[f'{who}_censored5']] for r in pergame]),'']
(P/'tables.md').write_text('\n'.join(tabs))
body='\n'.join(line for line in report if not line.startswith('|'))
print('report prose words',len(body.split()),'loss rows',len(curves),'verified',sum(g['verified'] for g in G))
