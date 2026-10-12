# Scratch (diag-walk): compact index of the two per-game dossier files, one line per game for the side we follow
# (ours = team 1119 in per-game.jsonl, rank-1 = team 306 in target/per-game-top1.jsonl; relation 'us' in both).
# Keeps the dossier's own counts so wk_scan.py can be checked against them.
# Usage: python3 data/analysis/ladder/dossier/work/wk_index.py
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path

DOS = Path('data/analysis/ladder/dossier')
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def pick(path, who):
    out = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rg = r['ranges']
            keep = dict(who=who, game=r['game'], battle=r['battle'], replay=r['replay'], layout=r['layout_key'],
                        side=r['side'], result=r['result'], rating=r['opponent_rating'], last_round=r['last_round'],
                        cells=r['cells'], first_contact=r['first_enemy_head_in_view'])
            for name in ('0-100', '101-300'):
                c = rg[name]
                keep[name] = dict(turns=c['turns'], blind=c['no_view_pearl_turns'], moved=c['no_view_pearl_moved'],
                                  dither=c['dither'], keeps=c['keeps'], keeps_eligible=c['keeps_eligible'],
                                  pearls=c['pearls_eaten'], splits=c['splits'], hot=c['hot_turns'],
                                  seen=c['seen_tiles_end'])
            keep['seen50'] = rg['0-50']['seen_tiles_end']
            out.append(keep)
    return out


def main():
    rows = pick(DOS / 'per-game.jsonl', 'O') + pick(DOS / 'target/per-game-top1.jsonl', 'R')
    Path(OUT + 'wk_index.json').write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    for who in 'OR':
        sub = [r for r in rows if r['who'] == who]
        print(who, len(sub), len({r['layout'] for r in sub}))


main()
