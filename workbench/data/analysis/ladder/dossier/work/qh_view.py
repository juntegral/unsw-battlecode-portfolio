"""Scratch (diag-queenhit): print the last turns of our queen in one game from qh_turns.jsonl, with a map of the
tiles around her head (edges from the replay's map text). Usage: python3 .../qh_view.py <game> [turns back=2] [radius=5]
Legend: Q/q our queen head/body, E/e enemy head/body, X rammer head, H/h ally head/body, * pearl, ! hit ring, + pay ring,
. free tile in her view, , tile outside her 7x7 view, | - kelp, : ~ portal."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay as LR
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
SMOKE = Path('data/online/smoke')
DN = 'NESW'


def main():
    gid = int(sys.argv[1])
    back = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    R = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    fate = [f for f in json.loads((WORK / 'qh_fates.json').read_text()) if f['game'] == gid][0]
    turns = []
    with (WORK / 'qh_turns.jsonl').open() as fh:
        for line in fh:
            if ('"game":%d,' % gid) in line:
                turns.append(json.loads(line))
    W, H = fate['W'], fate['H']
    text = LR.replay.load(SMOKE / (fate['label'] + '-new') / ('M%d.replay' % gid)).root().text(0)
    raw = [tuple(map(int, l.split()[1:4])) for l in text.splitlines() if l.startswith('EDGE ')]
    edges = LR.canonical_edges(W, H, raw)
    kind = lambda c, d: edges.get(LR.edge_id(W, H, c % W, c // W, d), (0, -1))[0]
    f = fate['fate']
    print('GAME', gid, fate['label'], fate['map'], '%dx%d' % (W, H), 'cells', fate['cells'], 'vs', fate['opponent'], fate['result'], 'Q id', fate['Q'], 'turns', fate['turns'])
    ram = None
    if f:
        ram = f.get('rammer')
        print(' FATE round', f['round'], f['cause'], 'mover' if f['mover'] else 'hit', 'L', f['L'], 'body', [(c % W, c // W) for c in f['body']])
        if ram:
            print(' RAMMER id', ram['id'], 'L', ram['L'], 'start', (ram['start'] % W, ram['start'] // W), 'steps', ram['steps'], 'dirs', ''.join(DN[d] for d in ram['dirs']),
                  'existed at her turn', ram['existed'], 'then', None if ram['then_head'] is None else (ram['then_head'] % W, ram['then_head'] // W), 'len then', ram['then_len'],
                  'enemy queen' if ram['is_enemy_queen'] else '', '' if ram['enemy'] else 'OWN TEAM', 'body', [(c % W, c // W) for c in ram['body']])
    for t in turns[-back:]:
        head = t['head']
        hx, hy = head % W, head // W
        rel = lambda c: (((c % W - hx + W // 2) % W) - W // 2, ((c // W - hy + H // 2) % H) - H // 2)
        print('--- round', t['round'], 'head', (hx, hy), 'L', t['L'], 'body', [rel(c) for c in t['body']], 'own/enemy alive', t['n_own'], t['n_enemy'])
        for e in t['enemies']:
            print('   enemy head', e['id'], 'at', rel(e['head']), 'L', e['L'], 'seen', e['seen'], 'QUEEN (no ring)' if e['queen'] else 'parts %d cut %s free %d reach %d true reach %d' % (e['parts'], e['cut'], e['free'], e['reach'], e['treach']))
        print('   nearest enemy heads (steps to her head, id, L, in view):', [(n[0], n[1], n[2], rel(n[3]), n[4]) for n in t['near']])
        for c in t['cands']:
            if c['kind'] == 'kelp':
                print('   ', DN[c['d']], 'kelp')
            elif not c['enterable']:
                print('   ', DN[c['d']], c['kind'], rel(c['dest']), 'blocked by', c['occ'])
            else:
                print('   ', DN[c['d']], c['kind'], rel(c['dest']), 'risk', c['risk'], 'closed' if c['closed'] else 'open', 'pearl' if c['pearl'] else '', 'true danger (id, steps, L; negative id = child off that tail)', c['danger'])
        print('   open0', t['open0'], 'open1', t['open1'], 'hit_blocked', t['hit_blocked'], 'hit_head', t['hit_head'], 'pay_head', t['pay_head'], 'own tile true danger', t['own_danger'])
        a = t.get('action')
        print('   ACTION', None if a is None else (a['kind'], ''.join(DN[d] for d in a['dirs'])), 'path', [rel(c) for c in t.get('path', [])], 'end', None if t.get('end') is None else rel(t['end']),
              'L after', t.get('L_after'), 'split child', t.get('split_child'), 'hit after by', t['hit_after'])
        tiles = {}
        for i, (own, b) in t['local'].items():
            for k, c in enumerate(b):
                if int(i) == fate['Q']:
                    ch = 'Q' if k == 0 else 'q'
                elif own:
                    ch = 'H' if k == 0 else 'h'
                else:
                    ch = ('X' if ram and int(i) == ram['id'] else 'E') if k == 0 else 'e'
                tiles[c] = ch
        hit, pay, pearls = set(t['hit']), set(t['pay']), set(t['pearls'])
        for dy in range(-R, R + 1):
            top, mid = '', ''
            for dx in range(-R, R + 1):
                c = ((hy + dy) % H) * W + (hx + dx) % W
                kn, kw = kind(c, 0), kind(c, 3)
                top += '+' if False else ' '
                top += '-' if kn == 1 else '~' if kn == 2 else ' '
                mid += '|' if kw == 1 else ':' if kw == 2 else ' '
                inview = abs(dx) <= 3 and abs(dy) <= 3
                ch = tiles.get(c)
                if ch is None:
                    ch = '!' if c in hit else '+' if c in pay else '*' if c in pearls else '.' if inview else ','
                mid += ch
            print('      ' + top)
            print('      ' + mid)


main()
