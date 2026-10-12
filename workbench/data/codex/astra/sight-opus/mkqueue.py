"""sight-opus: game queue, most informative first. Line = arm opp map seed side."""
maps = [('slithery_fight_1', 1), ('islands_1', 1), ('default_1', 1), ('trophy_1', 1), ('australia_1', 1),
        ('around_unsw_1', 1), ('slithery_fight_1', 2)]
out = []
for m, s in maps:
    out.append(('L', 'mD17', m, s, 0))
    for side in (0, 1):
        for arm in ('f8', 'e3'):
            out.append((arm, 'mD17', m, s, side))
for m, s in maps:
    for arm in ('L', 'f8', 'e3'):
        out.append((arm, 'm3base', m, s, 0))
for m, s in maps:
    for side in (0, 1):
        for arm in ('f4', 'f8e3'):
            out.append((arm, 'mD17', m, s, side))
print('\n'.join(' '.join(map(str, q)) for q in out))
