import json
from pathlib import Path
from collections import Counter
P=Path('data/codex/astra/topqueen2');S=json.loads((P/'summary.json').read_text());inv=json.loads((P/'inventory.json').read_text());games=[json.loads(l) for l in (P/'games.jsonl').read_text().splitlines()]
def f(x):return '—' if x is None else str(x)
def vec(a):return '/'.join(f(x) for x in a)
def table(headers,rows):return '|'+ '|'.join(headers)+'|\n|'+'|'.join('---' for _ in headers)+'|\n'+''.join('|'+ '|'.join(map(str,r))+'|\n' for r in rows)
ranks=inv['top'];labels={r['id']:f"{r['rank']}·{r['name']}({r['id']})" for r in ranks};top=[(labels[r['id']],S['top3-'+str(r['id'])]) for r in ranks if 'top3-'+str(r['id']) in S]
result=table(['팀(10/7 순위) [M]','N','여왕/최장/총길이/전멸 %','여왕 생존 n(%)·평균 L','여왕승 중 양쪽생존'],[[k,v['n'],vec([v['end_pct'][x] for x in ['queen','longest','total','wipe']]),f"{v['alive']}({v['alive_pct']})·{v['endL']}",f"{v['qwin_both_alive']}/{v['queen_wins']}"] for k,v in top])
growth=table(['팀 [M]','r499 생존 완주 N','같은 여왕의 r99/199/299/399/499 평균 L','전체판 섭취 자연/아군사체/적사체','아군사체: 제공자 L 중앙값·3칸내 비율·섭취지연 중앙값'],[[k,v['full_survivors'],vec(v['survivor_growth']),vec([v['all_eats'].get(x,0) for x in ['natural','mate','enemy']]),f"{v['donors']['length_med']}·{round(100*v['donors']['within3']/v['donors']['pearls'],1) if v['donors']['pearls'] else '—'}%·{v['donors']['wait_med']}r"] for k,v in top])
intake=table(['팀 [M]','r0–99 자연/아군/적','r100–199','r200–299','r300–399','r400–499'],[[k]+[vec([z['per100'][x] for x in ['natural','mate','enemy']]) for z in v['eating100']] for k,v in top])
position=table(['팀 [M]','r300+ 여왕턴','최근접 아군/적 머리 평균칸','5칸내 아군 평균·홀로 %','표시 경계 평균칸/켈프변 수','폐쇄성분≤16칸 %'],[[k,v['late']['turns'],vec([v['late']['mate'],v['late']['enemy']]),vec([v['late']['mates5'],v['late']['alone']]),vec([v['late']['edge'],v['late']['kelp']]),v['late']['sealed16_pct']] for k,v in top+[(f'one{z} 대 kraken (별도)',S[f'one{z}']) for z in [9,10] if f'one{z}' in S]])
attack=table(['공격 팀 [M]','여왕피격 N','공격 L 중앙/최대','무료범위/유료걸음진입(실제지불)','도중섭취 공격/진주','직전여왕시야 밖','5칸내 공격팀 머리 중앙값','공격 r 중앙값','자기여왕 사후'],[[k,v['kill']['n'],vec([v['kill']['Lmed'],v['kill']['Lmax']]),f"{v['kill']['freeonly']}/{v['kill']['paid_slot']}({v['kill']['paid_actual']})",vec([v['kill']['pearls_runs'],v['kill']['pearls']]),v['kill']['outside'],v['kill']['near5_med'],v['kill']['rmed'],v['kill']['afterdead']] for k,v in top+[(f'one{z} 대 kraken (별도)',S[f'one{z}']) for z in [9,10] if f'one{z}' in S]])
ownkeys=[f'{p}{o}-one{v}' if p=='opp' else f'one{v}-opp{o}' for v in [9,10] for o in [87,952,989] for p in ['ours','opp']]
own=table(['우리/상대 코호트 [M]','N','여왕/최장/총길이/전멸 %','여왕생존·평균L','완주생존N·L99/199/299/399/499','후반 자연/아군/적 섭취수','여왕사냥 N(자기여왕 사후)'],[[k,S[k]['n'],vec([S[k]['end_pct'][x] for x in ['queen','longest','total','wipe']]),f"{S[k]['alive']}·{S[k]['endL']}",f"{S[k]['full_survivors']}·{vec(S[k]['survivor_growth'])}",vec([sum(z['eats'].get(x,0) for z in S[k]['eating100'][3:]) for x in ['natural','mate','enemy']]),f"{S[k]['kill']['n']}({S[k]['kill']['afterdead']})"] for k in ownkeys if k in S])
kr=[]
orig={1482056,1482057,1482058,1482059,1482060,1483343,1483344,1483345,1483346,1483347}
for g in sorted(games,key=lambda g:g['gid']):
 if g['gid'] not in orig:continue
 s=g['teams'].index(989);ts=[t for t in g['turns'][s] if t['r']>=300];e=g['eats'][s];c=Counter(z['origin'] for z in e);ds=g['defends'][s]
 from statistics import mean
 avg=lambda k:round(mean([t[k] for t in ts if t[k] is not None]),1) if any(t[k] is not None for t in ts) else '—'
 kr.append([g['gid'],g['version'],g['map'],f"{g['final'][s][0]}:{g['final'][1-s][0]}",vec([avg('mate'),avg('enemy')]),vec([c[x] for x in ['natural','mate','enemy']]),f"{len(ds)}({sum(z['r']>=300 for z in ds)})"])
kraken=table(['원래10판 ID [M]','one','지도(식별만)','kraken:우리 여왕L','후반 아군/적 거리','kraken 섭취 자연/아군/적','여왕5칸내 아군 능동램(후반)'],kr)
(P/'tables.md').write_text('\n\n'.join([result,growth,intake,position,attack,own,kraken]))
print('tables written')
