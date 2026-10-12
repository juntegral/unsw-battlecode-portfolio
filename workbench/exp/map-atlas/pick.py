"""pick.py — chooses the deep-read games: per class the game closest to the class medians (full-population rows)."""
import json, pathlib, statistics as st
O = pathlib.Path(__file__).resolve().parent / 'cache'
WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] + [f'cand-stack{i}-online' for i in range(1, 7)] + ['cand-stack6-online-r2'] + [f'cand-stack{i}-online' for i in range(7, 12)]
raw = [json.loads(l) for l in open(O / 'raw.jsonl')]
def cp(g, t, r, f='heads'): return g[t]['cp'].get(str(r), {}).get(f)
def typical(gs, feats):
    cols = [[fn(g) for g in gs] for fn in feats]
    cols = [c for c in cols if any(v is not None for v in c)]; feats = cols
    meds = [st.median([v for v in c if v is not None]) for c in cols]
    sds = [st.pstdev([v for v in c if v is not None]) or 1 for c in cols]
    best = min(range(len(gs)), key=lambda i: sum(((cols[j][i] if cols[j][i] is not None else meds[j]) - meds[j]) ** 2 / sds[j] ** 2 for j in range(len(feats))))
    return gs[best], meds
def lay(g): return g['map'] + '/' + g['layout']
picks = []
def top_class(L, elim, name):
    gs = [g for g in raw if g['src'] == 'top' and not g['stall'] and lay(g) == L and g['winner'] and ((g['endReason'] == 'teamEliminated') == elim)]
    W = lambda g: g['winner']; Lo = lambda g: 'B' if g['winner'] == 'A' else 'A'
    feats = [lambda g: cp(g, W(g), 100), lambda g: cp(g, Lo(g), 100), lambda g: g['rounds'] if elim else cp(g, W(g), 500, 'king'), lambda g: None if elim else cp(g, Lo(g), 500, 'king')]
    g, m = typical(gs, feats); picks.append((name, g['key'], len(gs), [round(x, 1) if x is not None else None for x in m]))
def our_class(L, won, name, elim=None):
    gs = [g for g in raw if g['src'] == 'online' and g.get('set') in WAVES and g['oppId'] != 545 and lay(g) == L and (g['winner'] == g['us']) == won and (elim is None or (g[g['us']]['cp']['500']['heads'] == 0) == elim)]
    if not gs: return
    U = lambda g: g['us']; E = lambda g: 'B' if g['us'] == 'A' else 'A'
    feats = [lambda g: cp(g, U(g), 100), lambda g: cp(g, E(g), 100), lambda g: g['rounds'], lambda g: cp(g, U(g), 500, 'king')]
    g, m = typical(gs, feats); picks.append((name, g['key'], len(gs), [round(x, 1) if x is not None else None for x in m]))
top_class('Devil/a', True, 'elite Devil/a elimination')
top_class('Trophy/a', True, 'elite Trophy elimination')
top_class('Slithery Fight/a', False, 'elite Slithery a 500-round')
top_class('Portals/a', False, 'elite Portals 500-round')
top_class('Schooltime/b', False, 'elite Schooltime b 500-round')
top_class('Autarky/a', True, 'elite Autarky elimination')
our_class('Autarky/a', True, 'our Autarky win')
our_class('Prisoners Dilemma/6', True, 'our PD6 win')
our_class('Devil/a', False, 'our Devil/a loss', True)
our_class('Slithery Fight/a', False, 'our Slithery a loss (500)', False)
our_class('Trauma/a', False, 'our Trauma loss eliminated', True)
our_class('Portals/a', True, 'our Portals win')
our_class('Portals/a', False, 'our Portals loss')
top_class('Queen Of Spades/a', True, 'elite QoS a elimination')
top_class('Schooltime/a', False, 'elite Schooltime a 500-round')
our_class('Default/a', False, 'our Default loss', True)
our_class('Schooltime/a', False, 'our Schooltime a loss eliminated', True)
for p in picks: print(p)
(O / 'picks.json').write_text(json.dumps(picks, ensure_ascii=False, indent=1))
