"""Scratch (diag-aahsplit): metadata index of every game on disk with a studied team; writes as_index.jsonl.
Usage: python3 as_index.py"""
import json
from pathlib import Path
from collections import Counter

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
FOCUS = (454, 157, 306, 70, 1119)
ROOTS = ('data/online/top3', 'data/online/top1', 'data/online/smoke/agg8-q1-new', 'data/online/smoke/agg7-m1-new',
         'data/online/smoke/agg7-m2-new', 'data/online/smoke/agg7-m3-new')


def main():
    extra = [str(p) for p in sorted(Path('data/online/smoke').glob('top-l*')) if p.is_dir()]
    seen = set()
    out = []
    cnt = Counter()
    for root in ROOTS + tuple(extra):
        for mp in sorted(Path(root).rglob('game-*.json')):
            try:
                m = json.loads(mp.read_text())
            except ValueError:
                continue
            gid = m.get('id')
            if gid is None:
                continue
            rp = mp.with_name('M%d.replay' % gid)
            if not rp.exists() or (root, gid) in seen:
                continue
            seen.add((root, gid))
            if m.get('teamAId') not in FOCUS and m.get('teamBId') not in FOCUS:
                continue
            for team in (m.get('teamAId'), m.get('teamBId')):
                if team in FOCUS:
                    cnt[root, team] += 1
            out.append(json.dumps(dict(src=root, path=str(rp), gid=gid, a=m.get('teamAId'), b=m.get('teamBId'),
                                       an=m.get('teamAName'), bn=m.get('teamBName'), ae=m.get('teamAElo'), be=m.get('teamBElo'),
                                       map=m.get('mapName'), at=m.get('completedAt'), win=m.get('winner'),
                                       ranked=m.get('ranked'), size=rp.stat().st_size), ensure_ascii=False))
    Path(WORK + 'as_index.jsonl').write_text('\n'.join(out) + '\n')
    print(len(out), 'games')
    for k, v in sorted(cnt.items()):
        print(k, v)


main()
