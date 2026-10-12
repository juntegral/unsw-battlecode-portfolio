import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
import re
from pathlib import Path
import op_scan
import op_tab

ARMS = ['m4bq_vb', 'm5r0_vb', 'm5og_vb', 'm5op_vb']
HERE = Path(__file__).resolve().parent


def main():
    rows = [op_tab.rows(a) for a in ARMS]
    dirs = [{d.name for d in (op_scan.RUNS/a).iterdir() if d.is_dir()} for a in ARMS]
    expected = sorted(set.union(*dirs[1:]))
    games = sorted(set.intersection(*(set(r) for r in rows)))
    assert len(expected) == len(games) == 16
    assert expected == games == sorted(set.intersection(*dirs))
    assert len({g.split('-seed')[0] for g in games}) == 8
    assert all('-seed1-side' in g for g in games)
    outcomes, issues = {}, []
    for arm, records in zip(ARMS, rows):
        outcomes[arm] = {}
        for game in expected:
            d = op_scan.RUNS/arm/game
            missing = [f for f in ('game.replay', 'result.txt') if not (d/f).exists()]
            assert not missing, (arm, game, missing)
            root = op_scan.load(d/'game.replay').root()
            result = root.pointer(4)
            assert result.bit(0), (arm, game, 'unfinished')
            winner = result.u16(6) if result.u16(4) == 1 else None
            txt = (d/'result.txt').read_text().strip()
            match = re.search(r'\bwinner=(\d+)\b', txt)
            assert match and int(match[1]) == winner, (arm, game, txt)
            rounds = re.search(r'\brounds=(\d+)\b', txt)
            assert rounds and int(rounds[1]) == records[game]['rounds'] + 1
            side = records[game]['side']
            assert result.pointer(side).i32(12) == records[game]['q_end']
            meta = json.loads((d/'result.json').read_text())
            assert not meta.get('bot_errors') and not meta.get('error') and not meta.get('crash'), (arm, game, meta)
            outcomes[arm][game] = '무승부' if winner is None else '승' if winner == side else '패'
        print(arm, len(games), '완료·결과 대조 통과', flush=True)
    buf = io.StringIO()
    sys.argv = ['op_tab.py', *ARMS]
    with contextlib.redirect_stdout(buf):
        op_tab.main()
    table = [line for line in buf.getvalue().splitlines() if line.startswith('|')]
    reference = [line for line in (Path.home()/'meow-redteam/solo/src/w-open/op_table_pack.txt').read_text().splitlines() if line.startswith('|')]
    assert len(table) == len(reference) == 17
    assert [l.split('|')[1].strip() for l in table] == [l.split('|')[1].strip() for l in reference]
    for actual, old in zip(table[2:], reference[2:]):
        ac, oc = actual.split('|'), old.split('|')
        assert ac[2] == oc[2] and ac[5] == oc[3], (actual, old)
    out = ['# Round-0 split 단독 집계', '',
           '`m4bq_vb`: baseline/live; `m5r0_vb`: baseline + SPLIT_ROUND0; `m5og_vb`: SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6; `m5op_vb`: guard 없이 HEADING_TIE를 더한 pack. 상대는 plain main이다.', '',
           '원본 `op_scan.py`·`op_tab.py`를 변경 없이 실행했다. 숫자는 기보에서 읽었다. 시점은 라운드 종료이며, 일찍 끝난 판은 최종 상태를 이후 시점에도 유지한다. 평균·조건부 분모는 원본 집계 정의를 따른다.', '',
           *table, '',
           '표에 사용한 공통 16판(8지도 × seed 1 × 양편): m4bq_vb 16판, m5r0_vb 16판, m5og_vb 16판, m5op_vb 16판; 총 64개 기보. 공통 집합의 누락·실패 없음. 기보 완료 여부, result.txt의 winner·rounds, 최종 여왕 길이가 일치하며 result.json에 봇 오류가 없다. 스캔된 전체 기보는 arm 순서대로 64·16·16·16개이며, baseline의 공통 집합 밖 48판은 표에서 제외했다.', '',
           '판별 결과(승 = 기보 winner가 해당 arm의 side와 같음):', '']
    for game in games:
        out.append('- ' + game + ': ' + '; '.join(f'{arm} {outcomes[arm][game]}' for arm in ARMS))
    out += ['', '## 4줄 요약', '',
            'baseline → SPLIT_ROUND0 단독에서 길이 4+ 시작 드래곤의 r0 분열은 2/14 → 12/14, 시작 드래곤 첫 분열 평균은 12.8 → 12.4, r0–5 사망·초기 새끼 10라운드 내 사망은 4·6 → 2·2이며, guard/HEADING_TIE arm은 각각 14/14·14/14와 2·2·2·2다.',
            '머릿수·총 길이·누적 섭취·r40까지 사망 평균은 SPLIT_ROUND0 단독부터 달라졌다: baseline/단독/guard/HEADING_TIE의 r20 값은 머릿수 6.0/7.0/7.1/7.8, 총 길이 16.1/18.6/18.2/19.4, 섭취 11.7/13.8/13.8/15.0이고, r40까지 사망 평균은 6.9/8.0/7.1/8.9다.',
            '포털 r20 통과 판은 baseline/단독/guard/HEADING_TIE에서 전체 시작 계보 6/8/9/6·비여왕 계보 3/5/5/3으로 단독부터 달라지고, r10은 각각 4/4/4/4·3/3/3/3이다; 길이 2·적 머리 4칸 이내 여왕 차례는 baseline과 단독이 3회(3판)로 같으며 guard에서 6회(4판), HEADING_TIE에서 49회(8판)로 달라진다.',
            '여왕 첫 분열·길이·생존·4+ 차례 분열·r40까지 사망도 단독부터 달라졌다: baseline/단독/guard/HEADING_TIE에서 첫 분열 평균 9.1/8.9/7.0/6.1, r40 길이 2.8/3.1/2.6/1.9, r40·r100·r150 생존 13·8·5/14·10·7/14·6·5/12·7·6, 4+ 차례 분열 48/281·50/257·53/116·57/69, r40까지 사망 3/2/2/4판이다.']
    (HERE.parent/'out-r0.md').write_text('\n'.join(out)+'\n')
    (HERE/'r0-audit.json').write_text(json.dumps(dict(games=games, outcomes=outcomes, issues=issues), ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
