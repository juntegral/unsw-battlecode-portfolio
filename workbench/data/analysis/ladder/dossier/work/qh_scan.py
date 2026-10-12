"""Scratch (diag-queenhit): for every turn of our queen in the agg7-m* and sr51-bob1 replays, rebuild what she could
know (7x7 view, remembered edges, ghosts), the hit/pay rings as map_hits() in sr51-bot/main.cpp draws them, the
single-step candidates as pick_direction() sees them, what she did, and what killed her.
Usage: python3 data/analysis/ladder/dossier/work/qh_scan.py   (writes qh_turns.jsonl, qh_fates.json next to it)"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay as LR
from collections import deque, defaultdict
from pathlib import Path

replay = LR.replay
SMOKE = Path('data/online/smoke')
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSES = ('wall', 'own body', 'another body', 'head-on', 'no action')
QS_PAY_REACH = 3
GHOST_ROUNDS = 3
QUEEN_MIN_CELLS = 600


def true_reach(n):
    return (n + 3) // 4 + n - 2


class Game:
    def __init__(self, label, path, meta):
        self.label, self.meta = label, meta
        self.root = replay.load(path).root()
        text = self.root.text(0)
        lines = text.splitlines()
        self.W, self.H = map(int, lines[0].split()[1:3])
        W = self.W
        self.bodies, self.teams, raw = {}, {}, []
        for line in lines:
            q = line.split()
            if not q:
                continue
            if q[0] == 'DRAGON':
                i = len(self.bodies)
                self.bodies[i] = deque(int(q[4 + 2 * k]) * W + int(q[3 + 2 * k]) for k in range(int(q[2])))
                self.teams[i] = int(q[1])
            elif q[0] == 'EDGE':
                raw.append(tuple(map(int, q[1:4])))
        self.edges = LR.canonical_edges(W, self.H, raw)
        self.portals = defaultdict(list)
        for e, (k, p) in self.edges.items():
            if k == 2:
                self.portals[p].append(e)
        self.own = int(meta['teamAId'] != 1119)
        self.Q = min(i for i in self.bodies if self.teams[i] == self.own)
        self.EQ = min(i for i in self.bodies if self.teams[i] != self.own)
        self.known = set()
        self.seen = set()
        self.ghost = {}
        self.pearls = set()
        self.pearl_mem = set()

    def eid(self, c, d):
        return LR.edge_id(self.W, self.H, c % self.W, c // self.W, d)

    def adj(self, c, d):
        x, y = c % self.W, c // self.W
        return ((y + STEP[d][1]) % self.H) * self.W + (x + STEP[d][0]) % self.W

    def kind(self, c, d):
        return self.edges.get(self.eid(c, d), (0, -1))[0]

    def exit_of(self, c, d):
        e = self.eid(c, d)
        pid = self.edges[e][1]
        pair = self.portals[pid]
        partner = pair[0] if pair[1] == e else pair[1]
        row, x = divmod(partner, self.W + 1)
        y = row // 2
        return ((y - (d == 0)) % self.H) * self.W + (x - (d == 3)) % self.W, partner

    def true_step(self, c, d):
        k = self.kind(c, d)
        if k == 1:
            return -1
        if k == 2:
            return self.exit_of(c, d)[0]
        return self.adj(c, d)

    def bot_step(self, c, d):
        """step_index() with the queen's remembered edges: unknown edge = open, portal with unseen partner = shut."""
        e = self.eid(c, d)
        if e not in self.known:
            return self.adj(c, d)
        k = self.edges.get(e, (0, -1))[0]
        if k == 1:
            return -1
        if k == 2:
            ex, partner = self.exit_of(c, d)
            return ex if partner in self.known else -1
        return self.adj(c, d)

    def gap(self, a, b, n):
        d = abs(a - b)
        return min(d, n - d)

    def cheb(self, a, b):
        return max(self.gap(a % self.W, b % self.W, self.W), self.gap(a // self.W, b // self.W, self.H))

    def man(self, a, b):
        return self.gap(a % self.W, b % self.W, self.W) + self.gap(a // self.W, b // self.W, self.H)

    def true_dist(self, src, blocked, limit):
        dist = {src: 0}
        q = deque([src])
        while q:
            c = q.popleft()
            if dist[c] >= limit:
                continue
            for d in range(4):
                n = self.true_step(c, d)
                if n < 0 or n in dist or n in blocked:
                    continue
                dist[n] = dist[c] + 1
                q.append(n)
        return dist

    def record(self, rnd):
        W, H, Q = self.W, self.H, self.Q
        body = list(self.bodies[Q])
        head, L = body[0], len(body)
        hx, hy = head % W, head // W
        view = set(((hy + dy) % H) * W + (hx + dx) % W for dx in range(-3, 4) for dy in range(-3, 4))
        for c in view:
            for d in range(4):
                self.known.add(self.eid(c, d))
        self.seen |= view
        occupied = {}
        for i, b in self.bodies.items():
            for k, c in enumerate(b):
                occupied[c] = (i, k)
        vis = defaultdict(list)
        for c in view:
            if c in occupied and occupied[c][0] != Q:
                vis[occupied[c][0]].append(c)
        blocked = set(c for cs in vis.values() for c in cs)
        own_time = dict((c, L - k + 1) for k, c in enumerate(body))
        tail = body[-1]
        ring_block = blocked | set(c for c in body if c != tail)
        enemies = []
        hit, pay = set(), set()
        hit_w, pay_w = set(), set()
        arr, arr_w = {}, {}
        hit_head = pay_head = False
        for c in view:
            if c in self.pearls:
                self.pearl_mem.add(c)
            else:
                self.pearl_mem.discard(c)
        for i in sorted(vis):
            b = self.bodies[i]
            if self.teams[i] == self.own or b[0] not in view:
                continue
            seen_parts = len(vis[i])
            g = self.ghost.get(i)
            parts = max(seen_parts, g[1]) if g and rnd - g[0] <= GHOST_ROUNDS else seen_parts
            self.ghost[i] = (rnd, parts)
            if i == self.EQ:
                enemies.append(dict(id=i, head=b[0], L=len(b), seen=seen_parts, queen=True))
                continue
            cut = any(self.gap(c % W, hx, W) == 3 or self.gap(c // W, hy, H) == 3 for c in vis[i])
            free = max(1, (parts + 3) // 4)
            size = max(parts, seen_parts + 1, 3) if cut else parts
            full = (size + 3) // 4 + size - 2
            reach = max(free, min(full, QS_PAY_REACH))
            size_w = max(parts, seen_parts + 1, 4) if cut else parts
            reach_w = max(free, min((size_w + 3) // 4 + size_w - 2, QS_PAY_REACH))
            bd, hb = self.spread(b[0], ring_block, head, None, reach + free * 6)
            for c, s in bd.items():
                if s <= free:
                    hit.add(c)
                    hit_w.add(c)
                if s <= reach:
                    pay.add(c)
                a = 1 if s <= reach else 1 + (s - reach + free - 1) // free
                if a < arr.get(c, 99):
                    arr[c] = a
            if hb <= free:
                hit_head = True
            elif hb <= reach:
                pay_head = True
            bw, hw = self.spread(b[0], ring_block, head, self.pearl_mem, reach_w + free * 6)
            for c, s in bw.items():
                if s <= reach_w:
                    pay_w.add(c)
                a = 1 if s <= reach_w else 1 + (s - reach_w + free - 1) // free
                if a < arr_w.get(c, 99):
                    arr_w[c] = a
            enemies.append(dict(id=i, head=b[0], L=len(b), seen=seen_parts, parts=parts, cut=cut, free=free, reach=reach,
                                reach_w=reach_w, queen=False, treach=true_reach(len(b))))
        risk = lambda c: 2 if c in hit else 1 if c in pay else 0
        is_queen_static = W * H > QUEEN_MIN_CELLS
        # true danger: every enemy head near her, true length, true edges, bodies as they stand (her tail moves off)
        all_block = set(occupied) - {tail}
        danger = defaultdict(list)
        near = []
        for i, b in self.bodies.items():
            if self.teams[i] == self.own or self.man(b[0], head) > 14:
                continue
            tr = true_reach(len(b))
            dist = self.true_dist(b[0], all_block - {b[0]}, min(max(tr, 3), 8) + 1)
            dh = min((dist[n] + 1 for n in (self.true_step(head, d) for d in range(4)) if n in dist), default=99)
            near.append((dh, i, len(b), b[0], b[0] in view))
            for c, s in dist.items():
                if 0 < s <= tr:
                    danger[c].append((i, s, len(b)))
            if len(b) >= 4:
                cr = true_reach(len(b) - 2)
                dist2 = self.true_dist(b[-1], all_block - {b[-1]}, min(cr, 8))
                for c, s in dist2.items():
                    if 0 < s <= cr:
                        danger[c].append((-i - 1, s, len(b) - 2))
        cands = []
        for d in range(4):
            k = self.kind(head, d)
            if k == 1:
                cands.append(dict(d=d, kind='kelp'))
                continue
            t = self.true_step(head, d)
            entry = dict(d=d, kind='portal' if k == 2 else 'open', dest=t)
            who = occupied.get(t)
            entry['occ'] = None if who is None else ('own' if who[0] == Q else 'ally' if self.teams[who[0]] == self.own else 'enemy') + ('H' if who[1] == 0 else 'B')
            entry['enterable'] = who is None
            if who is None:
                entry['risk'] = risk(t)
                entry['closed'] = self.closed(t, L, own_time, blocked, tail, is_queen_static)
                entry['danger'] = sorted(danger.get(t, []))[:4]
                entry['pearl'] = t in self.pearls
                entry['risk_w'] = 2 if t in hit_w else 1 if t in pay_w else 0
                entry['arr'] = arr.get(t, 99)
                entry['arr_w'] = arr_w.get(t, 99)
                entry['kelp'] = sum(1 for d2 in range(4) if self.kind(t, d2) == 1)
                entry['ah'] = self.ahead(head, t, arr, blocked, own_time) if k != 2 else None
                entry['ah_w'] = self.ahead(head, t, arr_w, blocked, own_time) if k != 2 else None
                entry['exits'] = sum(1 for d2 in range(4) if self.kind(t, d2) == 0 and self.adj(t, d2) != head and self.adj(t, d2) not in blocked)
            cands.append(entry)
        sprint2 = False
        for c1 in cands:
            if not c1.get('enterable') or c1['kind'] != 'open':
                continue
            for d2 in range(4):
                if self.kind(c1['dest'], d2) != 0:
                    continue
                n2 = self.adj(c1['dest'], d2)
                if n2 in view and n2 not in occupied and risk(n2) == 0:
                    sprint2 = True
        scored = [c for c in cands if c.get('enterable') and not (c['kind'] == 'portal' and is_queen_static)]
        open0 = any(c['risk'] == 0 and not c['closed'] for c in scored)
        open1 = any(c['risk'] == 1 and not c['closed'] for c in scored)
        risky = any(c['risk'] > 0 for c in scored)
        local = {}
        for i, b in self.bodies.items():
            if any(self.cheb(c, head) <= 6 for c in b):
                local[i] = (self.teams[i] == self.own, list(b))
        return dict(game=self.meta['id'], label=self.label, map=self.meta['mapName'], cells=W * H, W=W, H=H, round=rnd,
                    head=head, L=L, body=body, enemies=enemies, hit_head=hit_head, pay_head=pay_head, cands=cands,
                    sprint2=sprint2, open0=open0, open1=open1, risky=risky, hit_blocked=risky and not open0,
                    hit=sorted(hit), pay=sorted(pay - hit), pay_w=sorted(pay_w - pay - hit), near=sorted(near)[:5], local=local,
                    pearls=sorted(c for c in self.pearls if c in view), own_danger=sorted(danger.get(head, []))[:4],
                    danger=dict((str(c), sorted(v)[:3]) for c, v in danger.items() if self.man(c, head) <= 3),
                    head_kelp=sum(1 for d2 in range(4) if self.kind(head, d2) == 1),
                    n_own=sum(1 for i in self.bodies if self.teams[i] == self.own),
                    n_enemy=sum(1 for i in self.bodies if self.teams[i] != self.own))

    def spread(self, source, ring_block, head, pearls, limit):
        """Budget an enemy head needs to stand on each tile: steps, less one for each pearl eaten on the way when pearls is given."""
        b = {source: 0}
        dq = deque([source])
        bd = {}
        head_b = 99
        while dq:
            c = dq.popleft()
            bc = b[c]
            if bc >= limit:
                continue
            for d in range(4):
                n = self.bot_step(c, d)
                if n == head:
                    head_b = min(head_b, bc + 1)
                if n < 0 or n in ring_block:
                    continue
                t = bc + 1
                if t < bd.get(n, 99):
                    bd[n] = t
                nb = t - (1 if pearls is not None and n in pearls else 0)
                if nb < b.get(n, 99):
                    b[n] = nb
                    if nb == bc:
                        dq.appendleft(n)
                    else:
                        dq.append(n)
        return bd, head_b

    def ahead(self, head, first, arr, blocked, own_time, K=6):
        """Enemy turns she is sure to stay out of reach of the heads she sees, walking one tile a turn from first."""
        if arr.get(first, 99) <= 1:
            return 0
        best = [1]

        def go(c, i, path):
            if i > best[0]:
                best[0] = i
            if i >= K:
                return
            for d in range(4):
                e = self.eid(c, d)
                if e in self.known and self.edges.get(e, (0, -1))[0] != 0:
                    continue
                n = self.adj(c, d)
                if n in blocked or n in path or i + 1 < own_time.get(n, 0) or arr.get(n, 99) <= i + 1:
                    continue
                go(n, i + 1, path + [n])
                if best[0] >= K:
                    return
        go(first, 1, [head, first])
        return best[0]

    def closed(self, t, L, own_time, blocked, tail, no_portal):
        need = L + 2
        steps = {t: 1}
        q = deque([t])
        room = 0.0
        while q:
            c = q.popleft()
            s = steps[c]
            room += 1.0 if c in self.seen else 0.5
            if c == tail or room >= need:
                return False
            for d in range(4):
                e = self.eid(c, d)
                if no_portal and e in self.known and self.edges.get(e, (0, -1))[0] == 2:
                    continue
                n = self.bot_step(c, d)
                if n < 0 or n in steps or n in blocked or s + 1 < own_time.get(n, 0):
                    continue
                steps[n] = s + 1
                q.append(n)
        return True

    def scan(self):
        W, Q = self.W, self.Q
        tile = lambda z: replay.point(z)[1] * W + replay.point(z)[0]
        rnd, actor = 0, None
        rec, turns, fate = None, [], None
        turn_start, used, dirs, action = {}, 0, [], None
        trace = []
        snap = {}

        def close():
            if rec is not None and 'end' not in rec:
                alive = Q in self.bodies
                rec['end'] = self.bodies[Q][0] if alive else None
                rec['L_after'] = len(self.bodies[Q]) if alive else 0
                rec['path'] = list(trace)
                rec['action'] = action
        for ev in self.root.pointer(3):
            k = ev.u16(0)
            if k not in (0, 1, 3, 4, 9, 10, 11):
                continue
            p = ev.pointer(0)
            if k == 0:
                if actor == Q:
                    close()
                rnd, actor = p.i32(0), None
            elif k == 1:
                if actor == Q:
                    close()
                actor = p.i32(0)
                used, dirs, action = 0, [], None
                turn_start = dict(head=self.bodies[actor][0], L=len(self.bodies[actor]), body=list(self.bodies[actor]))
                if actor == Q:
                    rec = self.record(rnd)
                    rec['hit_after'] = None
                    turns.append(rec)
                    trace = []
                    snap = dict((i, (b[0], len(b))) for i, b in self.bodies.items())
            elif k == 4:
                a = p.pointer(0)
                kind = a.u16(0) if a else 2
                dirs = list(a.pointer(0)) if a and kind == 0 and a.pointer(0) is not None else []
                action = dict(kind=('move', 'split', 'none')[min(kind, 2)], dirs=[int(x) for x in dirs])
            elif k == 3:
                c = tile(p.pointer(0))
                if p.u32(0):
                    self.pearls.add(c)
                else:
                    self.pearls.discard(c)
            elif k == 9:
                i = p.i32(0)
                hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
                b = self.bodies[i]
                if b[0] != hd:
                    b.appendleft(hd)
                    if i == actor:
                        used += 1
                        if i == Q:
                            trace.append(hd)
                while len(b) > 1 and b[-1] != tl:
                    b.pop()
            elif k == 10:
                parent, child = p.i32(0), p.i32(4)
                for z, i in enumerate((parent, child)):
                    self.bodies[i] = deque(tile(pt) for pt in p.pointer(z))
                    self.teams[i] = p.u16(8)
                if parent == Q and rec is not None:
                    rec['split_child'] = len(self.bodies[child])
            elif k == 11:
                i, reason = p.i32(0), p.u16(4)
                if i == Q:
                    b = list(self.bodies[i])
                    fate = dict(round=rnd, L=len(b), body=b, cause=CAUSES[min(reason, 4)], mover=actor == Q,
                                turn_index=len(turns) - 1 if turns else None)
                    if actor != Q:
                        then = snap.get(actor)
                        crossed, at = False, turn_start['head']
                        for dd in dirs:
                            if self.kind(at, int(dd)) == 2:
                                crossed = True
                            nx = self.true_step(at, int(dd))
                            if nx < 0:
                                break
                            at = nx
                        fate['rammer'] = dict(id=actor, start=turn_start['head'], L=turn_start['L'], body=turn_start['body'],
                                              steps=used + 1, dirs=[int(x) for x in dirs], existed=then is not None,
                                              then_head=then[0] if then else None, then_len=then[1] if then else None,
                                              portal=crossed, is_enemy_queen=actor == self.EQ, enemy=self.teams[actor] != self.own)
                        if turns:
                            turns[-1]['hit_after'] = actor
                    else:
                        fate['dirs'] = [int(x) for x in dirs]
                        fate['used'] = used
                    close()
                self.bodies.pop(i)
        if actor == Q:
            close()
        final = dict(alive=Q in self.bodies, L=len(self.bodies.get(Q, ())), last_round=rnd)
        return turns, fate, final


def main():
    out_turns, fates = [], []
    for label in LABELS:
        folder = SMOKE / (label + '-new')
        if not folder.exists():
            print('missing label', label)
            continue
        for rp in sorted(folder.glob('M*.replay')):
            gid = int(rp.stem[1:])
            mp = folder / ('game-%d.json' % gid)
            if not mp.exists():
                continue
            meta = json.loads(mp.read_text())
            g = Game(label, rp, meta)
            turns, fate, final = g.scan()
            own = 'ab'[g.own]
            out_turns.extend(turns)
            fates.append(dict(game=gid, label=label, map=meta['mapName'], cells=g.W * g.H, W=g.W, H=g.H, Q=g.Q,
                              result='win' if meta.get('winner') == own else 'draw' if meta.get('winner') is None else 'loss',
                              opponent=meta['team' + 'AB'[1 - g.own] + 'Name'], fate=fate, final=final, turns=len(turns)))
            print(label, gid, meta['mapName'], g.W, g.H, 'Q', g.Q, 'turns', len(turns), 'fate',
                  None if fate is None else (fate['round'], fate['cause'], fate['mover'], fate['L']), flush=True)
    Path(OUT + 'qh_turns.jsonl').write_text(''.join(json.dumps(t, separators=(',', ':')) + '\n' for t in out_turns))
    Path(OUT + 'qh_fates.json').write_text(json.dumps(fates, separators=(',', ':')) + '\n')
    print('turns', len(out_turns), 'games', len(fates))


main()
