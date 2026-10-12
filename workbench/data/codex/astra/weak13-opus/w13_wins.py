"""Wins and early eating before / after PORTAL_SCOUT_MIN_LEN went live (one12), from early-rows.tsv and portal-rows.tsv.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_wins.py"""
import csv
D = 'data/codex/astra/weak13-opus/'
rows = list(csv.DictReader(open(D + 'early-rows.tsv'), delimiter='\t'))
prow = list(csv.DictReader(open(D + 'portal-rows.tsv'), delimiter='\t'))
print('rows of the three battles (early): set gid map ver n0 us49 us99 th49 th99 usN100 thN100 won')
for r in rows:
    if r['set'].startswith('b1'):
        print(' ', r['set'], r['gid'], r['map'], r['ver'], r['n0'], r['us49'], r['us99'], r['th49'], r['th99'], r['usN100'], r['thN100'], r['won'])
print('rows of the three battles (portal crossings r0-99): gid map ver queen short long them')
for r in prow:
    if r['set'].startswith('b1'):
        print(' ', r['gid'], r['map'], r['ver'], r['q'], r['short'], r['long'], r['them'])
aff = {'Trauma', 'Queen Of Spades', 'Portals', 'Default', 'Australia', 'Trophy'}
OLD, NEW = ('one8', 'one9', 'one10', 'one11'), ('one12', 'one13')
print()
print('online 15-game sets only (no ranked battles); affected6 =', sorted(aff))
for grp, name in ((True, 'affected6'), (False, 'other10')):
    for vs, lab in ((OLD, 'one8-11'), (NEW, 'one12-13')):
        g = [r for r in rows if r['ver'] in vs and r['set'].startswith('one') and ((r['map'] in aff) == grp)]
        print('%-10s %-9s games %3d wins %3d (%.0f%%) our eats r0-99 %.1f their %.1f' % (
            name, lab, len(g), sum(int(r['won']) for r in g), 100 * sum(int(r['won']) for r in g) / len(g),
            sum(int(r['us99']) for r in g) / len(g), sum(int(r['th99']) for r in g) / len(g)))
for m in sorted({r['map'] for r in rows}):
    line = '  %-16s' % m
    for vs, lab in ((OLD, 'one8-11'), (NEW, 'one12-13')):
        g = [r for r in rows if r['ver'] in vs and r['set'].startswith('one') and r['map'] == m]
        if g:
            line += ' | %s games %2d wins %2d eats %6.1f' % (lab, len(g), sum(int(r['won']) for r in g), sum(int(r['us99']) for r in g) / len(g))
    print(line)
print()
print('portal crossings r0-99 by our non-queens shorter than 4, all maps with portals, per game')
for vs, lab in ((OLD, 'one8-11'), (NEW, 'one12-13')):
    g = [r for r in prow if r['ver'] in vs and r['set'].startswith('one') and r['map'] not in ('Devil', 'Tower Defense', 'weakhold')]
    z = sum(1 for r in g if int(r['short']) == 0)
    print('  %-9s games %3d mean %.1f games with zero %d' % (lab, len(g), sum(int(r['short']) for r in g) / len(g), z))
