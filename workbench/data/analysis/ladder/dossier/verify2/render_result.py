import json
from pathlib import Path
p=Path('data/analysis/ladder/dossier/verify2')
s=json.loads((p/'summary.json').read_text())
from statistics import mean
islands=[json.loads(x) for x in (p/'per-game-recount.jsonl').open() if json.loads(x)['layout']=='Islands #1']
for lo in ('101','151'):
    for side in ('0','1'):
        s['islands'][lo][side]['alive_start']=mean(r['intervals'][lo][side]['alive_start'] for r in islands if r['last']>=int(lo))
lines=['허용차: 수치 3% 또는 경기 수 1. 순서: 앞 구간→뒤 구간, 우리→상대. A–C는 독립 코드 recount.py로 기보를 재집계했다.','', '| item | report value | your value | match / mismatch | note |','|---|---|---|---|---|']
def row(item,rep,val,ok,note=''):
    lines.append(f'| {item} | {rep} | {val} | {"match" if ok else "mismatch"} | {note} |')
def nums(item,rep,vals,note=''):
    row(item,', '.join(f'{x:.1f}' for x in rep),', '.join(f'{x:.2f}' for x in vals),all(abs(a-b)<=abs(a)*.03 for a,b in zip(rep,vals)),note)
for name,field,reps in [('분열','split',[[42.3,16.3],[59.1,54.7]]),('진주, 모든 타일','eat',[[113.5,55.5],[191.2,199.5]]),('생존 평균','alive_start',[[40.5,35.6],[51.7,55.3]])]:
    for side,label in ((0,'우리'),(1,'상대')):
        nums('A '+name+' '+label,reps[side],[s['islands'][lo][str(side)][field] for lo in ('101','151')],'r101–150, r151–200; '+('24, 23경기' if field=='alive_start' else '24경기'))
nums('A 우리 사망',[41.2],[s['islands']['101']['0']['death']],'r101–150')
reports={'ALL':[[40,77],[21,84]],'Islands #1':[[1,7],[0,17]],'Australia #1':[[3,4],[6,31]],'Around UNSW #1':[[15,30],[0,2]],'Slithery Fight #1':[[17,32],[1,5]],'Schooltime #2':[[4,4],[6,9]],'Schooltime #1':[[0,0],[8,20]]}
for lay,rep in reports.items():
    val=s['B'][lay]
    fmt=lambda pairs:'; '.join(f'{a}/{b}' for a,b in pairs)
    row('B '+lay,fmt(rep),fmt(val),all(abs(a-b)<=1 for x,y in zip(rep,val) for a,b in zip(x,y)),'full; not full')
nums('C1 정면충돌, 상대 시작→우리 시작',[44.5,6.0],list(reversed(s['australia']['meetings'])),'r101–300; 35경기')
for side,label in ((0,'우리'),(1,'상대')):
    nums('C2 생존 '+label,[[36.7,46.4,42.1,35.1],[35.7,51.7,57.7,59.0]][side],[s['australia'][str(n)]['alive'][side] for n in (100,150,200,300)],'r100,150,200,300 종료 상태')
    nums('C3 총 길이 '+label,[[90.9,119.1],[90.2,261.0]][side],[s['australia'][str(n)]['length'][side] for n in (100,300)],'r100,300 종료 상태')
for k,rep in [('59+',[45,85]),('50-58',[6,19]),('<50',[10,56])]:
    val=s['C4'][k]
    row('C4 r150 '+k,f'{rep[0]}/{rep[1]}',f'{val[0]}/{val[1]}',all(abs(a-b)<=1 for a,b in zip(rep,val)),'r150까지 도달한 경기만')
raw=(p/'d-rerun.txt').read_text()
for label,frac,rate in [('우리 <59','75 of 673','0.111'),('우리 ≥59','62 of 77','0.805'),('상대, 우리 <59','473 of 680','0.696')]:
    a,b=map(int,frac.split(' of '))
    ok=f"'can_edge': {b}" in raw and f"'took_edge': {a}" in raw and rate in raw
    row('D '+label,f'{rate} ({a}/{b})',f'{a/b:.3f} ({a}/{b})',ok,'원본 au_scan2.py 재실행; d-rerun.txt')
lines += ['', 'Definition differences', '- A 생존 평균은 관측된 라운드의 경기별 평균을 다시 평균한다(r101–150 24경기, r151–200 23경기; 1305216은 r145 종료). 빈 구간은 생존 평균에서 제외하며 사건 수는 0이다.',
'- 보고서 생존 평균은 경기별 평균이 아니라 라운드를 합친 가중 평균과 일치한다: 우리 40.5155→35.5737, 상대 51.6611→55.2806. 경기별 평균과는 정의가 다르다.',
'- A 생존 평균과 B full은 isl_zone.py처럼 각 라운드 첫 턴 직전 상태를 쓴다. C 스냅숏은 au_scan.py처럼 해당 라운드 종료 상태다.', '- B는 조기 종료 경기의 관측된 r101–150만 평균하며, 관측이 없으면 0으로 분류한다. 종료 이후 상태를 채우지 않는다. 무승부는 분모에 포함하고 승리로 세지 않는다.', f"- C4 r150 미도달 제외: {s['missing150']}. Australia 스냅숏별 분모(r100,150,200,300): "+', '.join(str(s['australia'][str(n)]['n']) for n in (100,150,200,300))+f". 여섯 대형 지도 무승부: {s['draws']}.", '- D 우위: 보고서는 아군 머리 ≥ 적군 머리라고 쓰지만, 코드는 행위자 자신을 제외한 아군 ≥ 적군이다. 자신을 포함하면 아군이 적군보다 1 이상 많아야 한다. 양편에 같은 식을 쓴다.', '- D capk는 양편 모두 alive[우리]로 정한다. 보고서의 “our count”와 같지만 상대의 자체 59 제한을 비교하는 값은 아니다.', '- D 팀은 입력 our_side로 매핑한다. 독립 코드가 161경기(그중 Australia 35경기)의 메타데이터 팀 1119와 일치함을 확인했다. 여왕 id 0/1은 양편 행위자에서 똑같이 제외하며, 표적 여왕은 양편에 포함된다.', '- D r101–300은 포함 경계이고, 양편 reach는 턴 시작 길이−1이다. 벽·현재 몸 점유를 막고 포털을 포함한다. 턴 중 진주 섭취·꼬리 이동으로 새로 열리는 경로는 반영하지 않는다.', '- D track은 길이 ≤4만 검사해 보고서의 길이 2–4와 달리 하한 2 검사가 없다. 지도별 최소 아군 수·feeding 종료·leader 제외 조건도 분모에서 검사하지 않는다.', '- D taken은 기회와 우위가 있던 턴의 행위자 정면충돌 사망이다. 실제 피해자가 그 턴 시작에 찾은 동길이 이상 표적인지는 검사하지 않는다.', '', 'Could not check', '- 없음: A–D 요청 항목을 모두 집계하거나 재실행했다.']
assert len(lines)<=60
(p/'result.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
