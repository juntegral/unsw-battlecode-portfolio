# Scratch (diag-stripes): compact round-by-round trace of one game (who is where, room entries, meals, splits, deaths).
# Usage: python3 data/analysis/ladder/dossier/work/st_trace.py <rows file> <game id> <first round> <last round>
import sys, json

gid, lo, hi = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
for line in open(sys.argv[1]):
    g = json.loads(line)
    if g['game'] == gid:
        break
w = g['w']
comp, size, loop = g['comp'], g['size'], g['loop']


def cls(c):
    s = size[comp[c]]
    return '' if s >= 48 else ('L%d' if loop[comp[c]] else 'D%d') % s


print('game', gid, g['result'], 'vs', g['rating'], 'ended', g['ended_by'], 'r', g['last_round'], 'our side', g['our_side'])
print('legend: id(o=ours,t=theirs,Q=queen) length x,y[room: L4 loop room, D3/D1 dead-end room]; marks: >portal step, *ate, S split(child id), X died(cause); m = a free portal step into a room with a pearl on its entry tile was open and not taken')
rows = {}
for t in g['turns']:
    if t['r'] < lo or t['r'] > hi:
        continue
    y, x = divmod(t['head'], w)
    marks = ''
    for n, c in enumerate(t['steps']):
        if t['dirs'][n][1]:
            marks += '>' + cls(c)
    if t['ate']:
        marks += '*' * t['ate']
    if t['split']:
        marks += 'S%d' % t['split'][0]
    if t['died']:
        marks += 'X(%s)' % t['died']
    miss = ''
    took = t['dirs'][0][0] if t['dirs'] else None
    for d, o in enumerate(t['opts']):
        if o and o[0] == 2 and o[2] < 48 and o[6] == 0 and o[4] and took != d:
            miss += 'm' + ('L%d' if o[3] else 'D%d') % o[2]
    end = t['steps'][-1] if t['steps'] else t['head']
    ey, ex = divmod(end, w)
    rows.setdefault(t['r'], []).append('%d%s%s L%d %d,%d%s->%d,%d%s %s%s' % (
        t['id'], 'o' if t['s'] == 'u' else 't', 'Q' if t['q'] else '', t['L'], x, y, cls(t['head']), ex, ey, cls(end), marks, miss))
snap = {s[0]: s for s in g['snaps']}
for r in sorted(rows):
    s = snap.get(r)
    print('r%-3d [ours %d dragons len %d | theirs %d len %d] ' % (r, s[1], s[2], s[4], s[5]) + ' ; '.join(rows[r]))
