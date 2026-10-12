import sys,json,hashlib,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
import verify_maps as v
import rooms
OUT=Path(__file__).resolve().parent

def main():
    est=json.loads((OUT/'estimates-renewal.json').read_text());checks=json.loads((OUT/'checks.json').read_text());struct=json.loads((OUT/'structure-checks.json').read_text());inv=json.loads((OUT/'inventory.json').read_text());validation=json.loads((OUT/'validation.json').read_text())
    final=[]
    for s in struct:
        slug=s['file'][7:-4];data=(OUT/s['file']).read_bytes();loaded,diag=v.engine_load(data);base=v.state((OUT/'structure'/s['file']).read_text())
        assert all(loaded[k]==base[k] for k in ('size','walls','portals','dragons','edges','metadata'))
        assert est[slug]['classes']==validation['maps'][slug]['classes']
        saved=json.loads((OUT/'checks'/slug/'runs.json').read_text());assert saved['map_sha256']==hashlib.sha256(data).hexdigest();assert len(saved['runs'])==64;assert all(r['rounds']==499 and r['ate']==0 for r in saved['runs'])
        for ref in s['check']:
            expected=v.state(v.replay.load(v.ROOT/ref['replay']).root().text(0))
            assert all(loaded[k]==expected[k] for k in ('size','walls','portals','dragons','edges','metadata'))
            assert [c for c,p in loaded['tiles']]==[c for c,p in expected['tiles']]
        final.append(dict(slug=slug,sha256=hashlib.sha256(data).hexdigest(),two_replays=[r['replay'] for r in s['check']],structure_equal=True,TILE_coordinates_equal=True,intervals_restored=True,engine=diag))
    (OUT/'final-structure-checks.json').write_text(json.dumps(final,indent=2)+'\n')
    rooms.inspect();rs=json.loads((OUT/'stripes-rooms.json').read_text())
    assert len(rs)==12
    assert sorted(r['size'] for r in rs)==[1]*4+[3]*4+[4]*4
    lines=['# 래더 지도 3개: 구조 추출과 생성 간격 복원', '',
        '작성 '+subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()+f'; 기보 {inv["examined_files"]}개 전수 검색, 읽기 오류 {len(inv["errors"])}개, 중복 제외 837경기. maps2의 semantics.json과 동일한 추정·검증 코드를 재사용했다.',
        '첫 단계: 기보 r0 헤더 추출 → 1.2.7 WASM 초기화 → 각기 두 기보 대조. 둘째 단계: 전 경기의 생성·점유·미생성 검열로 갱신 모형 추정; TILE 간격 두 숫자 외 모든 바이트·대칭을 보존했다.',
        '각 지도 64시드(0–63), 총 192판에서 양편 한 마리씩 진주 없는 고리 이동, 나머지 r0 사망: 모두 r500 도달·섭취 0. 초기 몸/드롭·고리 타일은 비교에서 제외했다.',
        '보정 L/R은 로컬 클래스별 실측 첫 생성 위험률 × 래더의 아직 생성·방문·드롭 없는 타일-라운드 노출 / 같은 노출의 실제 생성 수다. 해당 구간 끝까지 진행한 경기만 비교했다.', '',
        '| 파일 slug (`ladder_<slug>.map`) | 크기 | A/B 마리 | 경기 | min/max: 전체 타일 수 | 두 기보 구조 | 보정 L/R 0–100 | 보정 L/R 101–300 |',
        '|---|---|---|---:|---|---|---|---|']
    for s in struct:
        slug=s['file'][7:-4];e=est[slug];c=checks[slug];vals=', '.join(k.replace(' ','/')+':'+str(n) for k,n in e['classes'].items());cells=[]
        for r in c['comparable_totals']:
            cells.append(f'{r["local_per_game"]:.2f}/{r["ladder_per_game"]:.2f}; '+(f'{r["ratio"]:.3f}'+(' **±15% 밖**' if not .85<=r['ratio']<=1.15 else '') if r['ratio'] is not None else '비율 없음(0/0)'))
        refs=', '.join(Path(r['replay']).stem for r in s['check'])
        lines.append(f'| {slug} | {s["size"][0]}×{s["size"][1]} | {s["dragons_per_side"]["A"]}/{s["dragons_per_side"]["B"]} | {e["games"]} | {vals} | {refs}: 모두 equal | '+ ' | '.join(cells)+' |')
    lines+=['', 'Tower Defense 101–300은 1.196으로 ±15% 밖이다. Portals 후반은 비교 생성 0/0이라 검증 비율이 없다. 전체 원시 0–100 비율(Stripes/Portals/Tower Defense)은 0.437/0.367/0.934: 앞 둘은 ±15% 밖이며 래더의 반복 섭취와 no-eating 차이를 포함한다.',
        'Stripes 출력의 작은 방 12개를 TILE 행·열린 변·포털 목적지로 직접 확인했다. 아래 좌표는 0부터 (x,y); 고리는 방 내부 변의 포털로 나갔다 돌아오는 구조, 막다른 방은 출입구 하나다. 무생성 고리 두 개도 포함했다.', '',
        '| 방 id | 타일 수·구조 | 타일 좌표 → min/max |', '|---|---|---|']
    for r in rs:
        groups=defaultdict(list)
        for t in r['tiles']:groups[tuple(t['interval'])].append(f'({t["x"]},{t["y"]})')
        desc='; '.join(','.join(cs)+f' → {par[0]}/{par[1]}' for par,cs in groups.items())
        lines.append(f'| {r["id"]} | {r["size"]}·'+('고리' if r['kind']=='loop' else '막다른 방')+f' | {desc} |')
    lines+=['세부: inventory.json·observations-complete.jsonl(전수 입력), estimates-renewal.json(추정·대안), structure-checks.json·final-structure-checks.json(구조), validation.json(TILE 외 동일), checks.json·checks/*/runs.json(보정·실측), stripes-rooms.json(방의 모든 변). 간격은 관측 추정이며 기보 RNG·첫 위상은 복원하지 않는다.']
    lines[2:4]=[" ".join(lines[2:4])]
    lines[3:5]=[" ".join(lines[3:5])]
    lines.insert(len(lines)-1, "")
    assert len(lines)<=30,len(lines)
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    checks['_method']=dict(engine='unswbc 1.2.7 WASM, seeds 0..63, 192 sequential runs',calibration='Same maps2 class-pooled first-birth hazards applied to untouched ladder risk tile-rounds; initial body/death drop and controller routes excluded; require game to reach phase end',outside_15_percent=[dict(slug=s,phase=r['phase'],ratio=r['ratio']) for s,c in checks.items() if s in est for r in c['comparable_totals'] if r['ratio'] is not None and not .85<=r['ratio']<=1.15],undefined=[dict(slug=s,phase=r['phase'],local=r['local'],ladder=r['ladder']) for s,c in checks.items() if s in est for r in c['comparable_totals'] if r['ratio'] is None])
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print('README lines',len(lines),'final structure equal ×2 for all three maps')
if __name__=='__main__':main()
