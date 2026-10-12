import json,statistics
from pathlib import Path
O=Path('data/codex/astra/band');S=json.loads((O/'summary.json').read_text())
order=['Preyas','Computers','Codehammer 40K','Adrak vali chai','acegi','Cache me outside','WeHaveQuizzes']
f=lambda x: '—' if x is None else f'{x:.1f}'
lines=['[M] 상대 진영 지문. 길이·머릿수·진주는 판당 평균, 첫 분열은 중앙값, 사건은 합계.','',
'| 팀 (N; 랭크) | 첫 분열 r | 머리 r25/r50 | r50 진주 전체/자연 | 램/1000턴 (건) | L2–4/유료범위 램 % | 우리 여왕 램 | 여왕 생존; L300→끝 (n300) | 여왕 섭취 자연/아군/적군; 아군 주원인 | 머리 r350→끝 (n350) | 끝 최장 | 후반 근접 정지류/자기충돌 | 벽사망 건(%) |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in order:
 if name not in S:continue
 s=S[name];q=s['qfood']
 donors={k:v for k,v in s['qdonors'].items() if k.startswith('them:')}
 top=max(donors,key=donors.get) if donors else ''
 names={'them:other:no action':'무행동','them:other:illegal split':'무효분열','them:own body:None':'자기충돌','them:wall:None':'벽','them:head-on:None':'램','them:other dragon body:None':'다른몸'}
 supply=f"{names.get(top,top)} {donors[top]}" if top else '—'
 lines.append(f"| {name} ({s['n']}; {s['ranked']}) | {s['split']:g} | {f(s['h25'])}/{f(s['h50'])} | {f(s['pearls50'])}/{f(s['natural50'])} | {s['ram_rate']:.2f} ({s['rams']}) | {s['ram24_pct']}/{s['paid_ram_pct']} | {s['queen_rams']} | {s['q_alive']}/{s['n']}; {f(s['q300'])}→{f(s['qend'])} ({s['n300']}) | {q.get('n',0)}/{q.get('own',0)}/{q.get('foe',0)}; {supply} | {f(s['h350'])}→{f(s['hend350'])} ({s['n350']}) | {f(s['longest'])} | {s['late_stop']}/{s['late_self']} | {s['walls']} ({s['wall_pct']}) |")
lines+=['','[M] 우리의 전적과 패배 판정. T는 끝까지 상대 점수 우세가 유지되기 시작한 라운드(라운드 말 상태 기준).','',
'| 상대 | 우리 승/무/패 | 패배: 여왕/최장/총길이/전멸 | T 중앙값 [범위] | 패배 순간 예시: 게임:r (판정) |','|---|---:|---:|---:|---|']
for name in order:
 if name not in S:continue
 s=S[name];L=s['loss'];T=s['turn_rounds'];ts=[t[1] for t in T]
 examples=T[:3]
 lines.append(f"| {name} | {s['ours'].get('win',0)}/{s['ours'].get('draw',0)}/{s['ours'].get('loss',0)} | {L.get('queen',0)}/{L.get('longest',0)}/{L.get('total',0)}/{L.get('elim',0)} | {s['turn_med']:g} [{min(ts)}–{max(ts)}] | "+'; '.join(f"{gid}:r{r} ({how})" for gid,r,how in examples)+' |')
(O/'tables.md').write_text('\n'.join(lines)+'\n')
