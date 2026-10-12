import json,csv,hashlib,subprocess
from pathlib import Path
from collections import Counter
O=Path('data/codex/astra/avengewhy'); ids=[1485169,1485170,1485174,1485181,1485182]
details={int(p.stem.split('-')[1]):json.loads(p.read_text()) for p in O.glob('detail-*.json')}
ledgers={int(p.stem.split('-')[1]):json.loads(p.read_text()) for p in O.glob('ledger-*.json')}
now=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
rows=[]
for gid in ids:
 d=details[gid]
 for t in d['reach']:
  rows.append(dict(game=gid,round=t['r'],dragon=t['id'],length=t['L'],head=t['head'],queen=t['foeq'],queen_visible=t['visible'],steps=t['reach'],free=t['free'],ram_path=''.join('NESW'[z] for z in t['ram_path']),actual_action=t['action']['kind'],actual_dirs=''.join('NESW'[z] for z in t['action']['dirs']),actual_path=t['path'],state=t['state_after'],known=t.get('known')))
with (O/'all-reach-turns.tsv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');wr.writeheader();wr.writerows(rows)
text='''[M/C] 다섯 판의 송신 사망상태는 모두 0이었다. 복수가 무장되지 않았고, 검사한 경로에서 L≤8의 즉시 충돌 기회도 없었다. Islands는 상대 여왕도 죽었으므로 ‘여왕 때문에 진 다섯 판’이 아니다.
[E] 카드 A: 보이는 적 여왕에 도달 가능한 비여왕의 길이·사망신호 제한 해제. 카드 B: 살아 있는 여왕 L<4에 한해 L2 동료의 먹이기 허용.
[M/C/E] 상태·행동·먹이기 차단은 높은 확신; 변경 후 승리는 미검증. 다섯 판을 모두 이기는 규칙은 입증할 수 없다.

'''
text+=f'[M] 작성 {now}. one8 세 세트 45판; 양 여왕 최종 생존 6판. r은 기보의 0–499 표기다.\n\n'
text+='|[M] 경기|우리 여왕 사망|최종 Q 우리/적|사망 뒤 머리 목격 용·턴|L≤4 / L≤8 충돌 가능 턴|분류 [E]|\n|---|---:|---:|---:|---:|---|\n'
for gid in ids:
 d=details[gid];text+=f"|{gid} {d['map']}|{d['death']}|{'/'.join(map(str,d['finalQ']))}|{sum(map(len,d['sightings'].values()))}|{sum(t['L']<=4 for t in d['reach'])} / {sum(t['L']<=8 for t in d['reach'])}|never armed{'；적 여왕 r193 벽 충돌, 최장 17/28' if gid==1485170 else ''}|\n"
text+='''
[C] `one8/main.cpp:2810–2867`은 직전 턴에 본 여왕 머리 칸의 새 진주만 인정한다. `2842–2844`의 자격은 L≤4이며, `QUEEN_AVENGE=8`은 추격 거리다. `1371–1379`는 기존 목적지·먹이기·8턴 유효기간에도 막힌다.
[C] 별도의 `QUEEN_SURE_LEN=4`, `QUEEN_SURE_STEPS=3` 경로(`3477–3489`)는 사망신호 없이도 충돌한다. 따라서 무장만 고쳐서는 부족하다.

|[M/E] 사망 신호 재구성|직전 관측→사후 관측|음파 결과|
|---|---|---|
|Australia 392|#95 r391 머리 (28,34); r392 그 칸이 시야 밖. 사망 머리는 (27,34)|사망상태 생성 없음|
|Islands 73|사망 r73–74에 직전 머리 관측을 보유한 아군 없음|동일|
|Around UNSW 196|r196–197 동일|동일|
|Portals 105|#156 r104 (13,15) 목격, r105 같은 칸 사체 목격; 그럼에도 상태 0|[E] 남은 차단은 이전 생성타이머 ≤2. 타이머는 기보에서 삭제되어 값 확인 불가|
|Slithery 335|#1008 r334 머리 (20,2); r335 그 칸에 진주 없음|사망 머리는 (23,2), 상태 생성 없음|

'''
text+='|[M] 경기|사망 뒤 leader / queen ping|아군에 닿은 음파 전체|사망상태 수신자|\n|---|---:|---:|---|\n'
for gid in ids:
 d=details[gid];p=[p for p in d['pings'] if p['r']>=d['death']];c=Counter(p['kind'] for p in p)
 text+=f"|{gid}|{c['leader']} / {c['queen']}|{sum(p['hit'] in (3,4) for p in p)}|없음(모든 상태 0)|\n"
text+='''
[M] L≤8 규칙의 ‘최초 즉시 도달 턴’은 관측 경로에서는 전부 없음이다. 추적을 바꾼 뒤의 최초 턴은 반사실이므로 기보만으로 산출할 수 없다. Portals는 사망 후 적 여왕과 아군이 서로 다른 지형 연결성분에 있다. Australia는 긴 용에게 기회가 있었다: 아래 표. 우리 용의 적 여왕 몸 충돌은 다섯 판 모두 0회다.

|[M] Australia|용/길이|적 머리|필요 걸음|실제 이동|
|---|---|---|---|---|
'''
for t in details[1485169]['reach']:
 if t['visible'] and t['r'] in (410,411,412,441):
  text+=f"|r{t['r']}|#{t['id']} / {t['L']}|{tuple(t['foeq'])}|{t['reach']} ({'무료' if t['free'] else '유료 포함'})|{''.join('NESW'[z] for z in t['action']['dirs'])} → {tuple(t['end'])}|\n"
text+='\n|[M] 양 여왕 생존 경기|Q r300 우리→최종 / 적 최종|우리 섭취 자연/아군사체/적사체|그중 아군 정지사망 유래|분열/유료손실|queen_game 태그 턴|L2–3 동료 머리 ≤3칸 턴|\n|---|---|---:|---:|---:|---:|---:|\n'
for gid in sorted(details):
 d=details[gid];l=ledgers[gid]
 if not all(d['finalQ']):continue
 ts=[t for t in d['qturns'] if t['r']>=300];e=[e for e in l['eats'] if e[0]>=300 and e[1]==0 and e[2]=='q'];c=Counter(e[3] for e in e);pd=sum(p[3] for p in l['paids'] if p[0]>=300 and p[1]==0 and p[6]);sp=sum(len(t['splits']) for t in ts)
 text+=f"|{gid} {d['map']} ({l['src']})|{ts[0]['L']}→{d['finalQ'][0]} / {d['finalQ'][1]}|{c['n']}/{c['own']}/{c['foe']}|{sum(e[3]=='own' and e[4]=='stop' for e in e)}|{sp}/{pd}|{sum(t['queen_game_tag'] for t in ts)}/200|{sum(any(m[1] in (2,3) and m[2]<=3 for m in t['mates']) for t in ts)}|\n"
text+='''
[C/M] 성장모드 고장이 아니다. `6521–6525`는 동료 길이×2≤여왕 길이를 요구하고 `FEED_BOOT_LEN=0`이다. Trauma 1485180은 r300 #134(L3)가 2칸, #173(L2)가 4칸인데 모두 탈락한다. r300–499 섭취·분열·유료손실 모두 0이다. 반면 1483019는 r300 L6에서 시작해 r303 첫 섭취, 아군 정지사체 24개를 먹고 L39가 됐다. Schooltime은 동료 접근 부족도 겹친다.
[M] 1485180 상대 여왕은 r300 종료 L5에서 자기편 사체 진주 12개(정지사망 6개)를 먹고, 유료손실 1로 L16이 됐다. 첫 섭취 r431, 연속 성장 r436–438, 마지막 섭취 r492다. 의도적 먹이기인지는 상대 코드 없이 확정하지 않는다.

|카드|구체 규칙·위치 [C/E]|기존 스위치|확인 / 반증 [M/E]|
|---|---|---|---|
|A: 즉시 여왕 충돌|보이는 적 여왕 머리까지 합법 경로가 있으면 비여왕은 길이·리더·아군 사망신호와 관계없이 무료/유료 충돌. one8:3477–3503,3542; one5:2703–2753,2786|QUEEN_HUNT만 켜도 avenge 분기가 우선하므로 해결 안 됨. QUEEN_SURE_LEN=4도 제한|Australia r410 #371의 5걸음, r412의 무료 2걸음이 실제 머리를 죽여야 함. 몸 충돌·미도달은 반증. 나머지 판 구제 근거 없음|
|B: 여왕 첫 성장|feeding_phase에서 실제 살아 있는 여왕 L<4를 목표로 하는 L2 동료만 길이비율을 면제. 기존 안전·거리 조건 유지. one8:6521–6525 및3194–3208; one5:5585–5589 및2439–2453|FEED_BOOT_LEN>3은 일반 리더·L3 동료도 허용하므로 더 넓은 변경|1485180의 가까운 L2가 실제 여왕에게 사체 진주를 전달해 L4 이상 진입. 다른 용이 먹거나 여왕이 죽으면 실패|

[M/E] 방법: 현재 몸을 장애물로 둔 지형·포털 최단 경로, 무료 ceil(L/4), 유료 L−2; L≤8은 중간 진주를 먹는 12걸음 경로도 조사했다. 자기 꼬리 이동을 이용한 경로·변경 후 추격·승리·CPU는 미검증이다. 본문 코드 줄은 `data/online/smoke/one8-bot/main.cpp` 기준이다. 순수 포털음파 턴의 내부 상태는 직접 확인하지 못했다. 전체 도달 턴과 실제 행동은 [TSV](all-reach-turns.tsv); 숨겨진 타이머 때문에 Portals의 마지막 차단은 추론이다.

'''
text+='|[M] 양 여왕 생존 경기, r300–499|우리 여왕 실제 걸음 / 이동한 턴|상대 Q r300 종료→최종|상대 섭취 자연/자기편사체/우리사체|상대 분열/유료손실|\n|---|---:|---|---:|---:|\n'
for gid in sorted(details):
 d=details[gid];l=ledgers[gid]
 if not all(d['finalQ']):continue
 ts=[t for t in d['qturns'] if t['r']>=300];es=[e for e in l['eats'] if e[0]>=300 and e[1]==1 and e[2]=='q'];c=Counter(e[3] for e in es)
 sp=sum(s[0]>=300 and s[1]==1 and bool(s[5]) for s in l['splits']);paid=sum(p[3] for p in l['paids'] if p[0]>=300 and p[1]==1 and p[6])
 text+=f"|{gid}|{sum(len(t['path']) for t in ts)} / {sum(bool(t['path']) for t in ts)}|{l['snaps']['300'][1][3]}→{d['finalQ'][1]}|{c['n']}/{c['own']}/{c['foe']}|{sp}/{paid}|\n"
text+='\n'
text+='|[M] 경기|r (종료)|적 머리 (x,y)|현재 목격 아군|최근접 #id / 지형 걸음 / L|아군 L≤4|이후 25라운드 목격 용·턴|\n|---|---:|---|---:|---|---:|---:|\n'
for gid in ids:
 d=details[gid]
 for s in d['snaps']:
  if (s['r']-d['death'])%25 and s['r']!=499:continue
  r=s['r'];near=s['nearest'];end=min(r+24,499);sight=sum(len(v) for rr,v in d['sightings'].items() if r<=int(rr)<=end)
  nd='∞' if near[1]==9999 else near[1]
  text+=f"|{gid}|{r}|{tuple(s['q'])}|{s['view']}|#{near[0]} / {nd} / {near[2]}|{s['small']}|{sight}|\n"
text+='\n[M] 거리에는 몸을 제외한 지형·포털만 반영했다. ∞이면 접근 불가능하며 최근접 용은 정의되지 않으므로 표시 id는 정렬상 첫 용이다. Islands는 적 여왕 생존 구간(r73–192)만 표시했다. 마지막 r499 행의 목격은 그 라운드만 센다.\n'
(O/'report.md').write_text(text)
print('report words excluding tables',len(' '.join(l for l in text.splitlines() if not l.startswith('|')).split()))
print('all reach',len(rows),'visible',sum(r['queen_visible'] for r in rows))
