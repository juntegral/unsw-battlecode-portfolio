"""Battle b1536232 (seat B, one18): per-game line + our queen's last turns. Run from ROOT."""
import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/codex/astra/stuck-opus', 'data/codex/astra/skku']
import json, glob, os
import o1_scan, analyze
def reach(L): return (L + 3) // 4 + max(0, L - 2)
for mp in sorted(glob.glob('data/online/live-one1/b1536232/game-*.json')):
    j = json.load(open(mp)); gid = j['id']; rp = os.path.join(os.path.dirname(mp), f'M{gid}.replay')
    if not os.path.exists(rp): print(gid, 'no replay yet'); continue
    sc = o1_scan.scan('b1536232', rp, j); d = analyze.details(rp, j); W, H = d['W'], d['H']; q = d['queens']
    def gap(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); return min(dx, W - dx) + min(dy, H - dy)
    def cnt(r, s): return len({t['id'] for t in d['turns'] if t['r'] == r and t['s'] == s})
    def eats(r, s): return sum(t['eat'] for t in d['turns'] if t['r'] <= r and t['s'] == s)
    qd = {x['s']: x for x in d['deaths'] if x['id'] in q}
    print('==', gid, j['mapName'], W * H, 'seat', 'A' if j['teamAId'] == 1119 else 'B', 'bot', sc['bot'], sc['result'], sc['how'], 'last r', sc['last'], 'ends us/them N,T,L,Q', [list(x[:4]) for x in sc['ends']],
          '| p100', eats(100, 0), eats(100, 1), 'n100', cnt(100, 0), cnt(100, 1), 'n50', cnt(50, 0), cnt(50, 1), '| queen ids', q, '| their queen died r', qd[1]['r'] if 1 in qd else None)
    x = qd.get(0)
    if not x: print('   our queen alive at end'); continue
    a = x.get('attack') or {}; qt = d['qturn'][0]; last = qt[-1]
    selfd = a.get('id') == x['id']
    print('   OUR queen died r', x['r'], 'L', x['L'], 'reason', x['reason'], 'at', x['head'], 'their queen alive then', x.get('enemy_queen_alive'), 'our units', last['units'])
    if selfd:
        print('   own move: turn start', a.get('h'), 'path', a.get('path'), 'dirs', a.get('dirs'))
    else:
        foe = next((f for f in last['foes'] if f['id'] == a.get('id')), None)
        print('   rammed by id', a.get('id'), 'L', a.get('L'), 'from', a.get('h'), 'gap', a.get('distance'), 'steps', a.get('steps'), 'paid', a.get('paid'), 'portal', a.get('portal'), 'seen at her last turn', bool(foe),
              '| gap at her last turn start', gap(tuple(last['h']), tuple(foe['h'])) if foe else None, 'rammer reach', reach(foe['L']) if foe else None, 'her last step', last['h'], '->', x['head'])
    for t in d['turns']:
        if t['id'] == q[0] and x['r'] - 4 <= t['r'] <= x['r']: print('     turn', t['r'], 'L', t['L'], 'path', t['path'], 'eat', t['eat'], 'split', t['split'])
    for rec in qt[-4:]:
        print('     view r', rec['r'], 'h', rec['h'], 'L', rec['L'], 'foes(id,L,head,gap)', [(f['id'], f['L'], tuple(f['h']), gap(tuple(rec['h']), tuple(f['h']))) for f in rec['foes']], 'pearls', len(rec['pearls']), 'units', rec['units'])
    # local board at her last turn: her body, foes, own cells in view
    rec = qt[-1]; hx, hy = rec['h']; cells = {}
    for z, bb in rec['bodies'].items():
        z = int(z); mine = z == q[0]
        for k, c in enumerate(bb):
            c = tuple(c)
            ch = ('Q' if k == 0 else 'q') if mine else None
            if ch is None:
                foe_ids = {f['id'] for f in rec['foes']}
                ch = ('E' if k == 0 else 'e') if (z in foe_ids or any(z == int(t) for t in [])) else ('A' if k == 0 else 'a')
            cells[c] = ch
    for p in rec['pearls']: cells.setdefault(tuple(p), '*')
    print('     board at her last turn start (Q queen, E foe head whose head is in view, A/a other bodies in view incl. foes with head out of view, * pearl):')
    for dy in range(-3, 4):
        print('       ' + ''.join(cells.get(((hx + dx) % W, (hy + dy) % H), '.') for dx in range(-3, 4)))
