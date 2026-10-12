"""Scratch (diag-topqueen): is the queen kept behind her own dragons? At the start of her turn every 4th round:
dq = torus Manhattan distance from her head to the nearest enemy head; rank = share of her side's other heads that are
nearer to an enemy head than she is (ties half). 0.5 = placed like any dragon, above = behind her swarm.
Also the same rank among her side's short dragons (length 4 or less) only.
Usage: python3 tq2_depth.py top3 <shard> <shards> | top1 <team> <shard> <shards> | online <label>
Writes tq2_depth-<tag>.jsonl: per game, per side, per band (r0-50, 51-100, 101-300, 301+): [n, sum rank, sum dq, sum median own, n short, sum rank short]."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STUDIED = (454, 157, 306, 70)


def band(r):
    return 0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3


def scan(path, own_letter, info):
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    heads, lens, teams = {}, {}, {}
    n = 0
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            heads[n] = (int(q[3]), int(q[4]))
            lens[n] = int(q[2])
            teams[n] = 0 if 'AB'[int(q[1])] == own_letter else 1
            n += 1
    bodies = {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
    queen = [min(i for i in teams if teams[i] == 0), min(i for i in teams if teams[i] == 1)]
    acc = [[[0, 0.0, 0, 0.0, 0, 0.0] for _ in range(4)] for _ in range(2)]
    rnd = -1

    def sample(s, q):
        hx, hy = bodies[q][0]
        en = [b[0] for i, b in bodies.items() if teams[i] != s]
        if not en:
            return
        def near(x, y):
            best = 999
            for ex, ey in en:
                dx = abs(x - ex)
                dy = abs(y - ey)
                d = min(dx, w - dx) + min(dy, h - dy)
                if d < best:
                    best = d
            return best
        dq = near(hx, hy)
        ds, short = [], []
        for i, b in bodies.items():
            if teams[i] == s and i != q:
                d = near(b[0][0], b[0][1])
                ds.append(d)
                if len(b) <= 4:
                    short.append(d)
        if not ds:
            return
        a = acc[s][band(rnd)]
        a[0] += 1
        a[1] += (sum(1 for d in ds if d < dq) + 0.5 * sum(1 for d in ds if d == dq)) / len(ds)
        a[2] += dq
        ds.sort()
        a[3] += ds[len(ds) // 2]
        if short:
            a[4] += 1
            a[5] += (sum(1 for d in short if d < dq) + 0.5 * sum(1 for d in short if d == dq)) / len(short)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            a = p.i32(0)
            if rnd % 4 == 0 and a == queen[teams[a]]:
                sample(teams[a], a)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(pt) for pt in p.pointer(z))
            teams[child] = 0 if 'AB'[p.u16(8)] == own_letter else 1
        elif k == 11:
            bodies.pop(p.i32(0))
    out = dict(info)
    out['acc'] = acc
    return out


def meta_job(rp, mp, team, src):
    meta = json.loads(mp.read_text())
    if team is None:
        team = meta['teamAId'] if meta['teamAId'] in STUDIED else meta['teamBId']
    if meta['teamAId'] == team:
        own, other = 'A', 'B'
    elif meta['teamBId'] == team:
        own, other = 'B', 'A'
    else:
        return None
    return (rp, own, dict(game=meta['id'], src=src, t=[meta['team' + own + 'Id'], meta['team' + other + 'Id']]))


def folder_jobs(folder, team, src):
    jobs = []
    for rp in sorted(folder.glob('M*.replay')):
        mp = folder / ('game-' + rp.stem[1:] + '.json')
        if mp.exists():
            j = meta_job(rp, mp, team, src)
            if j is not None:
                jobs.append(j)
    return jobs


def emit(tag, body):
    if tag == 'top3-0':
        Path(WORK + 'tq2_depth-top3-0.jsonl').write_text(body)
    elif tag == 'top3-1':
        Path(WORK + 'tq2_depth-top3-1.jsonl').write_text(body)
    elif tag == 't91-0':
        Path(WORK + 'tq2_depth-t91-0.jsonl').write_text(body)
    elif tag == 't264-0':
        Path(WORK + 'tq2_depth-t264-0.jsonl').write_text(body)
    elif tag == 't306-0':
        Path(WORK + 'tq2_depth-t306-0.jsonl').write_text(body)
    elif tag == 'agg8-q1':
        Path(WORK + 'tq2_depth-q1.jsonl').write_text(body)
    elif tag == 'agg7-m1':
        Path(WORK + 'tq2_depth-m1.jsonl').write_text(body)
    elif tag == 'agg7-m2':
        Path(WORK + 'tq2_depth-m2.jsonl').write_text(body)
    elif tag == 'agg7-m3':
        Path(WORK + 'tq2_depth-m3.jsonl').write_text(body)
    elif tag == 'top-l1':
        Path(WORK + 'tq2_depth-l1.jsonl').write_text(body)
    elif tag == 'top-l2':
        Path(WORK + 'tq2_depth-l2.jsonl').write_text(body)
    else:
        Path(WORK + 'tq2_depth-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'top3':
        base = Path('data/online/top3')
        who = {}
        upto = 0
        for a in sys.argv:
            if a.startswith('upto'):
                upto = int(a[4:])
        rows = [json.loads(line) for line in (base / 'index.jsonl').read_text().splitlines() if line.strip()]
        for r in (rows[:upto] if upto else rows):
            who[str(r['battle'])] = r['team']
        jobs = []
        for folder in sorted(x for x in base.iterdir() if x.is_dir()):
            if upto and folder.name not in who:
                continue
            jobs += folder_jobs(folder, who.get(folder.name), 'top3')
        shard, shards = int(sys.argv[2]), int(sys.argv[3])
        tag = 'top3-' + sys.argv[2]
    elif src == 'top1':
        team = int(sys.argv[2])
        jobs = []
        for line in Path('data/top1/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r['team'] == team:
                    folder = Path('data/online/top1') / str(r['battle'])
                    if folder.is_dir():
                        jobs += folder_jobs(folder, team, 'top1')
        shard, shards = int(sys.argv[3]), int(sys.argv[4])
        tag = 't' + sys.argv[2] + '-' + sys.argv[3]
    else:
        lab = sys.argv[2]
        jobs = folder_jobs(Path('data/online/smoke') / (lab + ('-old' if lab.startswith('top-l') else '-new')), 1119, lab)
        shard, shards = 0, 1
        tag = lab
    jobs = [j for n, j in enumerate(jobs) if n % shards == shard]
    if sys.argv[-1].startswith('limit'):
        jobs = jobs[:int(sys.argv[-1][5:])]
        tag = 'test'
    out, bad = [], []
    for n, (path, own, info) in enumerate(jobs):
        try:
            out.append(json.dumps(scan(path, own, info), separators=(',', ':')))
        except Exception as e:
            bad.append((info['game'], repr(e)[:200]))
        if n % 20 == 19:
            sys.stderr.write('%d %d bad %d\n' % (n + 1, len(jobs), len(bad)))
            sys.stderr.flush()
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
