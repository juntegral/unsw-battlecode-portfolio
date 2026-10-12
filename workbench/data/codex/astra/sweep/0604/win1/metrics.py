import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path(__file__).resolve().parent
counts = Counter()
moments = defaultdict(list)
def record(name, gid, turn):
    counts[name] += 1
    if len(moments[name]) < 12:
        moments[name].append(dict(game=gid,round=turn['round'],id=turn['id'],head=turn['head'],end=turn['end']))

for gid in range(1495464,1495468):
    game = json.loads((OUT/f'game-{gid}.json').read_text())
    w,h = game['dimensions']
    queen = game['queens']['us']
    def man(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    for turn in game['turns']:
        if not turn['ours']:
            continue
        if turn['round']<12 and turn['id']!=queen and turn['length']<=4 and turn['steps']:
            record('early_short_moving',gid,turn)
            if turn['dirs'][0]==turn['heading']:
                record('early_short_continued_heading',gid,turn)
        if turn['id']==queen and turn['steps'] and turn['near_mates'] and turn['own_count']>=12:
            mate=min(turn['near_mates'],key=lambda m:m[3])
            if mate[3]>3:
                record('queen_nearest_mate_4_6_movement',gid,turn)
                if man(turn['end'],mate[2])<mate[3]:
                    record('queen_toward_nearest_mate_4_6',gid,turn)
        if turn['nearby_pearls'] and turn['steps'] and turn['steps'][0] not in turn['nearby_pearls']:
            record('moving_past_adjacent_pearl',gid,turn)
        if turn['free'] and any(d[0]==turn['id'] and d[1]==4 for d in turn['deaths']):
            record('no_valid_action_with_free_exit',gid,turn)
            if 201<=turn['round']<=350:
                record('no_valid_action_with_free_exit_201_350',gid,turn)
        if turn['id']==queen and turn['split'] and turn['length']==4:
            record('queen_split_L4_to_2',gid,turn)
        if not turn['steps'] and not turn['split'] and turn['end'] is not None:
            record('stationary_survivor_no_split',gid,turn)

(OUT/'metrics.json').write_text(json.dumps(dict(counts=counts,moments=moments),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(counts=counts,moments=moments),ensure_ascii=False,indent=2))
