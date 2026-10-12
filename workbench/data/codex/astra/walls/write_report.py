import sys
sys.dont_write_bytecode=True
import json,hashlib
from collections import Counter
from pathlib import Path
from datetime import datetime
P=Path(__file__).resolve().parent
S=json.loads((P/'summary.json').read_text());V=json.loads((P/'verification.json').read_text())
lines=['[M/E] 우리 벽·자해 사망 **21,265건 중 2,827건**에 즉시 사망을 피하는 대체 수가 있다. 장기 생존·승률 개선 수는 미확정이다.',
'[M/E] 최대 실행가능 후보는 **시야 밖 포털 진입 2,005건**: 카드 A, 짧은 용은 관측된 열린 일반 길을 우선한다.',
'[M/E] 확신: 사건·물리적 대안 높음, 내부 선택 이유·카드 순효과 낮음. 독립 집계 104판 일치; one11 6판 재독해 일치.',
'',
'[M] 입력 동결 **2026-10-09 06:15:49 KST**. 봇 ID로 선별·게임 ID로 중복 제거한 170판: one8 시험/랭크 75/49, one10 30/10, one11 0/6. 전수 원장은 [deaths.csv](deaths.csv), 출구를 막은 용·칸·사건과 직전 다섯 턴은 `game-<id>.json`이다. 아래 **건수(1,000용턴당)**.',
'',
'| [M] 버전·편 | 용턴 | 강제* | 자유칸 있는데 선택 | 태어날 때부터 봉쇄 | 여왕 분열 직후* |',
'|---|---:|---:|---:|---:|---:|']
for v in ('one8','one10','one11'):
 for side,name in enumerate(('우리','상대')):
  r=S[v]['sides'][side];vals=[]
  for k in ('forced','chosen_free_start','born_boxed','queen_after_split'):
   n=r['classes'].get(k,0);vals.append(f"{n:,} ({1000*n/r['turns']:.3f})")
  lines.append(f"| {v} {name} | {r['turns']:,} | "+' | '.join(vals)+' |')
lines += ['',
'[M] 전체 벽/자해: 우리 **14,265 (7.478) / 7,000 (3.670)**, 상대 **10,685 (5.732) / 14,871 (7.978)**.',
'',
'[M/C/E] *분류는 배타적이다. 강제는 출생·여왕 분열 행을 제외한다. 여왕 9건은 분열 직후 사망이며 `queen_wait()` 발동 확정은 아니다(5804–5830행). 대상 전부 MOVE 사망; 통상 먹이기는 무행동 반환(1449–1455행)이므로 해당하지 않는다. 의도적 먹이기 확정 0건, 상대 의도 미상. 긴 아군 ≤3칸인 자유칸 사망 406건도 의도로 단정하지 않았다. 로그는 0건이다.',
'',
'| [M] 마지막 출구가 닫힌 뒤 사망까지 | 우리 | 같은 경기 상대 |',
'|---|---:|---:|',
'| 같은 라운드 / 1라운드 / 2라운드 / ≥3라운드 | 3,165 / 8,536 / 8,566 / 0 | 5,056 / 8,732 / 7,338 / 448 |',
'| 닫은 주체: 본인 / 아군 / 적 / 출생·초기 | 14,495 / 4,809 / 90 / 873 | 13,405 / 6,386 / 33 / 1,750 |',
'',
'[M/E] 우리 강제 20,267건의 본인 진입은 일반 진주 7,917, 포털 3,676, 일반 무진주 2,902건이다. 봉쇄 후 부모가 분열한 9,047건은 수확·탈출 비용일 수 있어 일괄 구제 대상으로 삼지 않았다. 이것은 **출구 0의 연속 구간**이며, 더 이른 회피 불가능 시점의 증명은 아니다. 위협장 도주·복도 선택의 내부 동기는 복원하지 못했다.',
'',
'| 카드 | [M] 직접 대응 사건: one8 / one10 / one11 | [C] one11 위치·기존 설정 | [E] 규칙·반증 |',
'|---|---:|---|---|',
'| A: 짧은 용의 포털 우선순위 | 1,344 / 385 / 276 = **2,005** | 5794–5797, 7812, 7973–7975행. `WEIGHT_PORTAL_SCOUT=0.40`; `QUEEN_PORTAL_LAST`는 여왕만 보호. | 비여왕 L≤3가 시야 밖 포털과 다음 출구까지 보이는 일반 수를 함께 가지면 일반 수 선택. 이후 분열 없는 실제 봉쇄만 셈. 탐색·진주 접근 감소가 구제보다 크면 기각. |',
'| B: 최종 이동의 물리적 유효성 | 563 / 224 / 35 = **822** | 7819–7822행 먹이기 금지, 7979·8014행 거절점수에도 동점·선택; 758–761행 불법 경로 검사 실패 시 반환. 전용 상수 없음. | MOVE가 첫걸음부터 벽·자해라면 보이는 일반 출구로 교체. 660행 뒤, 여왕 희생 처리 669행 앞에 둔다. 여왕 봉쇄·먹이기 방해 증가 시 기각. |',
'',
'[C/E] 기존 `QUEEN_PORTAL_LAST`는 one11에서도 비여왕을 보호하지 못한다. B의 822건은 전부 r≥300이고 먹이기 진입금지와 거절점수 선택이 원인 후보다; 정확한 분기·기억은 미확인이다. [M] 나머지 자유칸 사망 176건은 보이는 일반 2걸음 대안 없음 168건, 이동 도중 충돌 8건이다. 두 카드 모두 **해당 즉시 사망 회피 기회**이며 구제 실적이 아니다. 아군 봉쇄의 전역 대안 830건은 원격 피해자 가시성을 보증하지 못해 별도 카드로 올리지 않았다.',
'',
'| [M] 카드·버전 | 게임 / 용 | 진입→사망 라운드 | 실제 수 → 열린 대안 |',
'|---|---|---|---|',
'| A one8 | 1483015 / #5 | 15→16 | (20,31) 동쪽 포털 → 남쪽 (20,32) |',
'| A one10 | 1489833 / #201 | 160→161 | (4,39) 북쪽 포털 → 동쪽 (5,39) |',
'| A one11 | 1496003 / #187 | 278→279 | (4,39) 북쪽 포털 → 동쪽 (5,39) |',
'| B one8 | 1483007 / #435 | 404→404 | (23,10) 서쪽 → 북쪽 (23,9) |',
'| B one10 | 1489831 / #370 | 405→405 | (7,8) 남쪽 → 북쪽 (7,7) |',
'| B one11 | 1496002 / #143 | 410→410 | (21,1) 북쪽 → 동쪽 (22,1) |',
'',
'[M/E] 대안은 해당 판면의 한 걸음과 다음 빈칸만 검증했다. 이후 적 대응·동시 카드 적용·생산성·CPU는 미검증이다. one11은 6판뿐이며 상대 구성 차이를 버전 효과로 해석하지 않는다. 재현: `analyze.py` → `verify.py` → `summarize.py`; [검증 결과](verification.json), [집계](summary.json).',
'']
G=[json.loads(p.read_text()) for p in P.glob('game-*.json')]
D=[d for g in G for d in g['deaths'] if d['side']==0]
T=S['all']['sides']; n11=S['one11']['games']; n=len(G)
coverage=json.loads((P/'coverage.json').read_text())
A=[S[v]['sides'][0]['tags'].get('portal_last_card',0) for v in ('one8','one10','one11')]
B=[S[v]['sides'][0]['tags'].get('legal_veto',0) for v in ('one8','one10','one11')]
counts=Counter((g['version'],'test' if '/smoke/' in g['path'] else 'ranked') for g in G)
parent=sum(bool(d['lastsplit'] and d['closure'] and d['lastsplit']['event']>d['closure']['event']) for d in D if not d['startfree'])
geom=Counter()
for d in D:
 if d['startfree']:continue
 c=d['closure'];st=c.get('step')
 if c['by']==d['id'] and st:
  o=next((o for o in st['options'] if o['n']==st['dest']),None)
  geom['portal' if o and o['portal'] else 'pearl' if st['eat'] else 'plain']+=1
near=sum(any(m['L']>d['L'] and m['distance']<=3 for m in d['history'][-1]['mates']) for d in D if d['startfree'])
mid=sum(bool(d['history'][-1]['moves']) for d in D if d['startfree'])
remaining=T[0]['classes'].get('chosen_free_start',0)-sum(B)
protect=T[0]['tags'].get('queen_protection_unresolved',0)
rate=lambda side,key:f"{T[side][key]:,} ({1000*T[side][key]/T[side]['turns']:.3f})"
who=lambda side:' / '.join(f"{T[side]['closers'].get(k,0):,}" for k in ('self','mate','enemy','birth'))
delay=lambda side:' / '.join([f"{T[side]['blocked_rounds'].get(str(k),0):,}" for k in (0,1,2)]+[f"{sum(v for k,v in T[side]['blocked_rounds'].items() if int(k)>=3):,}"])
replacements={
 '**21,265건 중 2,827건**':f"**{T[0]['deaths']:,}건 중 {sum(A)+sum(B):,}건**",
 '2,005건':f'{sum(A):,}건',
 'one11 6판':f'one11 {n11}판', '170판:':f'{n}판:',
 'one11 0/6':f"one11 {counts['one11','test']}/{counts['one11','ranked']}",
 '2026-10-09 06:15:49 KST':datetime.fromisoformat(coverage['at']).strftime('%Y-%m-%d %H:%M:%S KST'),
 '14,265 (7.478) / 7,000 (3.670)':f"{rate(0,'wall')} / {rate(0,'body')}",
 '10,685 (5.732) / 14,871 (7.978)':f"{rate(1,'wall')} / {rate(1,'body')}",
 '여왕 9건':f"여왕 {T[0]['classes'].get('queen_after_split',0)}건",
 '406건':f'{near}건',
 '3,165 / 8,536 / 8,566 / 0':delay(0),
 '5,056 / 8,732 / 7,338 / 448':delay(1),
 '14,495 / 4,809 / 90 / 873':who(0),
 '13,405 / 6,386 / 33 / 1,750':who(1),
 '20,267건':f"{T[0]['deaths']-T[0]['classes'].get('chosen_free_start',0):,}건",
 '일반 진주 7,917, 포털 3,676, 일반 무진주 2,902건':f"일반 진주 {geom['pearl']:,}, 포털 {geom['portal']:,}, 일반 무진주 {geom['plain']:,}건",
 '9,047건':f'{parent:,}건',
 '1,344 / 385 / 276 = **2,005**':' / '.join(f'{a:,}' for a in A)+f' = **{sum(A):,}**',
 '563 / 224 / 35 = **822**':' / '.join(f'{b:,}' for b in B)+f' = **{sum(B):,}**',
 '822건':f'{sum(B):,}건',
 '176건은 보이는 일반 2걸음 대안 없음 168건, 이동 도중 충돌 8건':f'{remaining}건은 일반 2걸음 대안 없음 {remaining-mid-protect}건, 이동 도중 충돌 {mid}건, 여왕 보호 여부 미확정 {protect}건(카드 제외)',
 '830건':f"{T[0]['tags'].get('mate_closure_alternative',0):,}건",
 'one11은 6판':f'one11은 {n11}판',
}
import re
pattern=re.compile('|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True)))
report=pattern.sub(lambda m:replacements[m.group()], '\n'.join(lines))
(P/'report.md').write_text(report)
text='\n'.join(l for l in lines if not l.startswith('|'))
print('non-table whitespace words',len(text.split()))
ROOT=P.parents[3]
paths=[ROOT/'data/online/smoke'/f'one{n}-bot/main.cpp' for n in (8,10,11)]
paths += [P/'analyze.py',P/'verify.py',P/'summarize.py']
(P/'sources.json').write_text(json.dumps(dict(written_at=datetime.now().astimezone().isoformat(),sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2))
