import sys
sys.dont_write_bytecode=True
import json,subprocess,hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_fast as a
OUT=a.OUT

def meanraw(runs,pars,par,lo,hi):
    return sum(sum(sum(lo<=r<=hi for r in rs) for c,rs in run['births'].items() if pars[int(c)]==par) for run in runs)/len(runs)

def main():
    checks=json.loads((OUT/'checks.json').read_text());est=json.loads((OUT/'estimates-renewal.json').read_text());validation=json.loads((OUT/'validation.json').read_text());inv=json.loads((OUT/'inventory.json').read_text())
    when=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip();classes={};raw_fail=[];adjust_fail=[];prefix_fail=[]
    for slug in a.TARGETS:
        assert est[slug]['classes']==validation['maps'][slug]['classes']
        saved=json.loads((OUT/'checks'/slug/'runs.json').read_text());data=(OUT/('ladder_'+slug+'.map')).read_bytes();assert saved['map_sha256']==hashlib.sha256(data).hexdigest();assert len(saved['runs'])==64
        assert all(r['rounds']==499 and r['ate']==0 for r in saved['runs'])
        pars={int(c):tuple(p) for c,p in saved['controller']['parameters'].items()};cs=sorted(set(pars.values())-{(0,0)});classes[slug]=cs
        for par in cs:
            entry=checks[slug]['classes']['%d %d'%par]
            for z,(lo,hi) in enumerate([(0,100),(101,300)]):entry['phases'][z]['raw_local_per_game']=meanraw(saved['runs'],pars,par,lo,hi)
        for r in checks[slug]['comparable_totals']:
            if not .85<=r['ratio']<=1.15:adjust_fail.append([slug,r['phase'],r['ratio']])
            if not .85<=r['prefix_ratio']<=1.15:prefix_fail.append([slug,r['phase'],r['prefix_ratio']])
        if not .85<=checks[slug]['raw_total_0_100']['ratio']<=1.15:raw_fail.append(slug)
    checks['_method']=dict(engine='unswbc 1.2.7 WASM, venv engine, seeds 0..63, sequential runs',engine_games=384,adjusted_local='Class-pooled first-birth hazards measured in the 64 no-eating engine runs, multiplied by ladder tile-round exposure while the tile is untouched and has not yet had a natural birth.',ladder='First natural births in the same risk exposure, stopping at a body visit, death drop, earlier natural birth or window end. Games must reach the window end. Initial body tiles and both control routes are excluded.',prefix_matching='Preserved separately: local first births masked by each ladder visit cutoff without conditioning on earlier absence. This can bias late-window comparison.',raw='All-map natural births, excluding death drops. Local bots never eat; ladder bots do, so repeated births differ.',adjusted_failures=adjust_fail,prefix_failures=prefix_fail,raw_failures=raw_fail)
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    def f(x):return '—' if x is None else f'{x:.2f}'
    lines=['# 래더 지도 6개: 생성 간격 복원', '',
           f'작성 {when}; 자료 스냅숏 {inv["snapshot_local"]}. 기보 {inv["examined_files"]}개 조사, 동일 구조 1,411경기(500개 main 중 해당 161개 + 추가 1,250개; 중복 제외).',
           '`TILE x y min max`: 시도 후 정수 G를 [min,max]에서 양 끝 포함 균등 추출; 라운드 시작에 감소하며 0이면 시도하고 성공 여부와 무관하게 재추출한다.',
           '진주·몸이 있으면 생성만 실패한다. 먹힘·비워짐·점유는 타이머를 멈추거나 초기화하지 않는다. 초기에도 G를 뽑으므로 첫 시도는 r=G−1; max=0은 영구 비활성이다.',
           '대칭 쌍은 타이머를 공유한다: y는 x↔W−1−x, xy는 180° 회전. `~/meow-redteam/engine/venv`의 1.2.7 WASM, docs/helper의 countdown 설명, `rules/ALL.md`를 대조하고 `semantics.json`·probe 기보로 측정했다.',
           '모든 경기의 몸·진주 점유, 첫 생성, 재생성, 미생성 검열을 사용한 갱신 모형으로 쌍별 추정했다. 대부분 작은 값 집합이며, 긴 간격은 동일 구조 기존 지도값이 전체 모형의 95% 프로필 지지 안일 때만 적용했다.',
           'Slithery Fight는 고정 간격 가정을 충족하지 않는다: (33,1)/(29,25)가 M983514에서는 빈 쌍 21라운드에 21회 생성, M990346에서는 494라운드 비어도 0회. 이 지도는 단일 균등 간격 근사이며 확정 복원이 아니다(`heterogeneity.json`).', '',
           '| slug (`ladder_<slug>.map`) | 경기 | 간격 min/max: 전체 타일 수 |', '|---|---:|---|']
    for slug in a.TARGETS:
        vals=', '.join(k.replace(' ','/')+':'+str(v) for k,v in est[slug]['classes'].items());lines.append(f'| {slug} | {est[slug]["games"]} | {vals} |')
    lines+=['',
            '검증: 빈 MOVE는 r0 전멸. 각 지도 64시드에서 한 마리씩 양팀을 진주 없는 서로 다른 고리로 이동시켰고 나머지는 r0 사망시켰다. 384판 모두 r500 도달·섭취 0; 초기 몸/드롭 타일과 고리 경로는 비교에서 제외했다.',
            '비교 상태는 아직 첫 생성이 없고 몸·사망 드롭이 방문하지 않은 타일-라운드다(해당 구간 끝까지 진행한 경기만). L은 로컬 클래스별 실측 첫 생성 위험률을 래더의 이 노출에 곱한 기대 생성 수, R은 동일 노출의 실제 생성 수다.',
            '아래는 클래스별 경기당 생성 수: 위 간격 순서(0/0 제외), 각 항목 `로컬 원시 L→보정 L/R`. raw는 실제 no-eating 엔진 생성이며 보정의 상태/노출 차이를 명시적으로 반영했다.',
            '| slug | 0–100 | 101–300 |', '|---|---|---|']
    for slug in a.TARGETS:
        cells=[]
        for z in (0,1):
            entries=[checks[slug]['classes']['%d %d'%p]['phases'][z] for p in classes[slug]]
            cells.append('; '.join(f'{f(r["raw_local_per_game"])}→{f(r["local_per_game"])}/{f(r["ladder_per_game"])}' for r in entries))
        lines.append(f'| {slug} | {cells[0]} | {cells[1]} |')
    lines+=['', '| slug | 보정 0–100 L/R; 비율 | 보정 101–300 L/R; 비율 | 단순 접두 비율 0–100/101–300 | 전체 원시 0–100 L/R; 비율 |', '|---|---|---|---|---|']
    for slug in a.TARGETS:
        rs=checks[slug]['comparable_totals'];raw=checks[slug]['raw_total_0_100'];cells=[]
        for r in rs:cells.append(f'{f(r["local_per_game"])}/{f(r["ladder_per_game"])}; {r["ratio"]:.3f}'+(' **범위 밖**' if not .85<=r['ratio']<=1.15 else ''))
        prefix='/'.join(f'{r["prefix_ratio"]:.3f}' for r in rs)
        cells.append(prefix);cells.append(f'{f(raw["local_per_game"])}/{f(raw["ladder_per_game"])}; {raw["ratio"]:.3f}'+(' **범위 밖**' if not .85<=raw['ratio']<=1.15 else ''))
        lines.append(f'| {slug} | '+' | '.join(cells)+' |')
    lines+=['보정 비교는 5지도에서 두 구간 모두 ±15% 안이며, Slithery Fight 101–300은 1.402로 **실패**했다. 단순 접두의 후반은 Australia/Around UNSW/Slithery Fight/Schooltime #2가 범위 밖; 전체 원시는 Schooltime #1만 범위 안이다(래더의 반복 섭취와 no-eating 차이).',
            '비교 세부/384판 실측: `checks.json`, `checks/*/runs.json`; 최종 추정/불확실성: `estimates-renewal.json`; 입력 기보: `inventory.json`, `observations-complete.jsonl`. `validate.py`는 TILE의 두 숫자 외 모든 바이트 동일·미관측 타일 0/0·대칭·전수 포함을 확인한다.']
    lines[3:5]=[' '.join(lines[3:5])]
    lines[5:7]=[' '.join(lines[5:7])]
    lines.insert(lines.index('| slug | 0–100 | 101–300 |'),'')
    lines.insert(next(i for i,l in enumerate(lines) if l.startswith('보정 비교는')),'')
    assert len(lines)<=40,len(lines);(OUT/'README.md').write_text('\n'.join(lines)+'\n')
    print('README lines',len(lines),'engine games 384','adjusted failures',adjust_fail,'raw failures',raw_fail)

if __name__=='__main__':main()
