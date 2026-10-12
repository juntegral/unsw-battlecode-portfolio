import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
from pathlib import Path
import op_tab

HERE = Path(__file__).resolve().parent


def main():
    audit = json.loads((HERE/'audit.json').read_text())
    out = ['# Opening pack + guard 집계', '',
           'A: plain main 상대, `m4bq_vb`(baseline/live) → `m5op_vb`(HEADING_TIE 포함 pack, guard 없음) → `m5og_vb`(SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6).',
           'B: queen hunter 상대, `m3b7qk_vh`(baseline) → `m5og_vh`.', '',
           '집계는 원본 `op_scan.py`·`op_tab.py`를 그대로 복사해 실행했다. 숫자는 기보에서 읽었고, `result.txt`는 완료·승자·라운드 일치 확인에 사용했다. 시점은 원본 도구대로 라운드 종료 시점이며, 일찍 끝난 판은 최종 상태를 이후 시점에 유지한다. 평균과 조건부 분모도 원본 도구대로다.', '']
    sets = {}
    for label, group in audit.items():
        arms, games = group['arms'], group['candidates']
        assert not group['issues'], group['issues']
        raw = [op_tab.rows(a) for a in arms]
        shared = sorted(set.intersection(*(set(a) for a in raw)))
        assert shared == games
        sets[label] = [[a[g] for g in games] for a in raw]
        for arm, rows in zip(arms, raw):
            for game in games:
                old, checked = rows[game]['qdeath'], group['data'][arm][game]['death']
                assert bool(old) == bool(checked)
                if old:
                    assert (old[0], old[2]) == (checked['round'], checked['length'])
        buf = io.StringIO()
        sys.argv = ['op_tab.py', *arms]
        with contextlib.redirect_stdout(buf):
            op_tab.main()
        table = [line for line in buf.getvalue().splitlines() if line.startswith('|')]
        assert len(table) == 17, len(table)
        reference = [line for line in (Path.home()/'meow-redteam/solo/src/w-open/op_table_pack.txt').read_text().splitlines() if line.startswith('|')]
        assert [line.split('|')[1].strip() for line in table] == [line.split('|')[1].strip() for line in reference] if label == 'A' else len(table) == len(reference)
        if label == 'A':
            assert all(a.split('|')[1:4] == b.split('|')[1:4] for a, b in zip(table, reference))
        out += [f'## Table {label}', '', *table, '',
                f'근거 판: {len(games)}개 지도·시드·진영 조합({len(games)//2}지도 × seed 1 × 양편); arm당 {len(games)}판, 총 {len(games)*len(arms)}개 기보. 누락·실패: 없음. 모든 `result.txt`의 winner와 rounds가 완료된 기보와 일치한다.', '',
                '판별 승패(승 = 기보 winner가 해당 arm의 side와 같음):', '']
        for game in games:
            out.append('- ' + game + ': ' + '; '.join(f"{arm} {group['data'][arm][game]['outcome']}" for arm in arms))
        out.append('')
        if label == 'B':
            out += ['여왕 사망 전수(각 arm의 우리 여왕; 전체 라운드):', '',
                    '`rammed`는 다른 머리의 차례에 head 충돌로 사망, `ran into a head`는 여왕 자신의 차례에 head 충돌로 사망이다. `boxed in`은 wall/own/body 충돌을 묶은 표기이며 원시 원인을 함께 적었다(다른 선택지가 없었다는 판정은 하지 않았다). 마지막 분열의 거리는 분열 이벤트 직후 여왕 머리와 당시 살아 있는 적 머리의 최소 toroidal Manhattan 거리이며, ≤6을 “예”로 센다. 분열이 없으면 해당 없음이다.', '']
            for game in games:
                for arm in arms:
                    d = group['data'][arm][game]['death']
                    if not d:
                        continue
                    split = d['last_split']
                    if split:
                        flag = '예' if split['within6'] else '아니오'
                        distance = split['nearest'] if split['nearest'] is not None else '적 머리 없음'
                        tail = f"마지막 분열 r{split['round']}, 적 머리 ≤6 {flag}, 최소 거리 {distance}"
                    else:
                        tail = '마지막 분열 없음, 적 머리 ≤6 해당 없음'
                    detail = {0: 'wall', 1: 'own', 2: 'body', 3: 'head'}.get(d['reason'], str(d['reason']))
                    out.append(f"- {arm} {game}: r{d['round']}, 길이 {d['length']}, {d['cause']} ({detail}; actor #{d['actor']}, team {d['actor_team']}); {tail}.")
            out.append('')
    (HERE/'tables-draft.md').write_text('\n'.join(out)+'\n')
    print(json.dumps({label: [{'q_r40': op_tab.m([r['q_r40'] for r in rs]),
                             'q_alive': [sum(r[f'q_r{k}'] > 0 for r in rs) for k in (40,100,150)],
                             'r0split': sum(x == 0 for r in rs for x,L in zip(r['first_split'],r['starters']) if L >= 4),
                             'hunts': sum(r['q2hunt'] for r in rs),
                             'n_r20': op_tab.m([r['n_r20'] for r in rs]),
                             'pearls_r20': op_tab.m([r['pearls_r20'] for r in rs]),
                             'portal': [sum(r[key] for r in rs) for key in ('portal_r10','portal_r20','portal_nq_r10','portal_nq_r20')]}
                            for rs in rows] for label, rows in sets.items()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
