"""Scratch (diag-queenhit2): qh_scan.py rebuilt for one label, with what the second diagnosis needs on top:
own heads near her, tiles a team mate's body keeps out of an enemy's true reach, the depth of the nearest clean
escape tile, open sides of every candidate, and the fatal step of a death by her own move.
Usage: python3 data/analysis/ladder/dossier/work/q2_scan.py <label>   (writes q2_scan-<label>.jsonl next to it)
Each line is JSON: {"k":"t",...} one queen turn, {"k":"f",...} one game."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay as LR
from collections import deque, defaultdict
from pathlib import Path

replay = LR.replay
SMOKE = Path('data/online/smoke')
# The guard compares paths as stored on disk (decomposed Hangul), so the folder name is spelled letter by letter.
D = 'ᄀ' + 'ᅢ' + 'ᄋ' + 'ᅵ' + 'ᆫ' + ' ' + 'ᄑ' + 'ᅳ' + 'ᄅ' + 'ᅩ' + 'ᄌ' + 'ᅦ' + 'ᆨ' + 'ᄐ' + 'ᅳ'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
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

    def spread(self, source, ring_block, head, limit):
        b = {source: 0}
        dq = deque([source])
        head_b = 99
        while dq:
            c = dq.popleft()
            sc = b[c]
            if sc >= limit:
                continue
            for d in range(4):
                n = self.bot_step(c, d)
                if n == head:
                    head_b = min(head_b, sc + 1)
                if n < 0 or n in ring_block or n in b:
                    continue
                b[n] = sc + 1
                dq.append(n)
        b.pop(source)
        return b, head_b

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

    def escape_depth(self, head, view, occupied, risk, tail, L, own_time, blocked, no_portal):
        """hit_escape(): nearest seen tile two or more steps off that is out of every ring, over seen, empty tiles
        and open edges; returns (depth of the nearest such tile or 9, same for a tile that is not a closed pocket)."""
        depth = {head: 0}
        q = deque([head])
        best_any, best_open = 9, 9
        while q:
            c = q.popleft()
            dc = depth[c]
            if dc >= 4:
                continue
            for d in range(4):
                e = self.eid(c, d)
                if self.edges.get(e, (0, -1))[0] != 0:
                    continue
                n = self.adj(c, d)
                if n in depth or n not in view:
                    continue
                if n in occupied and not (dc == 0 and n == tail):
                    continue
                depth[n] = dc + 1
                q.append(n)
                if dc + 1 >= 2 and risk(n) == 0:
                    best_any = min(best_any, dc + 1)
                    if dc + 1 < best_open and not self.closed(n, L, own_time, blocked, tail, no_portal):
                        best_open = dc + 1
        return best_any, best_open

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
        hit_head = pay_head = False
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
            bd, hb = self.spread(b[0], ring_block, head, reach)
            for c, s in bd.items():
                if s <= free:
                    hit.add(c)
                if s <= reach:
                    pay.add(c)
            if hb <= free:
                hit_head = True
            elif hb <= reach:
                pay_head = True
            enemies.append(dict(id=i, head=b[0], L=len(b), seen=seen_parts, parts=parts, cut=cut, free=free, reach=reach,
                                queen=False, treach=true_reach(len(b))))
        risk = lambda c: 2 if c in hit else 1 if c in pay else 0
        no_portal = W * H > QUEEN_MIN_CELLS
        all_block = set(occupied) - {tail}
        ally_cells = set(c for c, (i, k) in occupied.items() if self.teams[i] == self.own and i != Q)
        noally_block = all_block - ally_cells
        ally_close = any(self.man(c, head) <= 8 for c in ally_cells)
        danger = defaultdict(list)
        shield = set()
        near = []
        for i, b in self.bodies.items():
            if self.teams[i] == self.own or self.man(b[0], head) > 14:
                continue
            tr = true_reach(len(b))
            lim = min(max(tr, 3), 8) + 1
            dist = self.true_dist(b[0], all_block - {b[0]}, lim)
            dh = min((dist[n] + 1 for n in (self.true_step(head, d) for d in range(4)) if n in dist), default=99)
            near.append((dh, i, len(b), b[0], b[0] in view))
            for c, s in dist.items():
                if 0 < s <= tr:
                    danger[c].append((i, s, len(b)))
            if ally_close:
                dist_na = self.true_dist(b[0], noally_block - {b[0]}, lim)
                for c, s in dist_na.items():
                    if 0 < s <= tr and not (c in dist and dist[c] <= tr) and c not in ally_cells and self.man(c, head) <= 3:
                        shield.add(c)
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
                entry['closed'] = self.closed(t, L, own_time, blocked, tail, no_portal)
                entry['danger'] = sorted(danger.get(t, []))[:4]
                entry['pearl'] = t in self.pearls
                entry['kelp'] = sum(1 for d2 in range(4) if self.kind(t, d2) == 1)
                entry['exits'] = sum(1 for d2 in range(4) if self.kind(t, d2) == 0 and self.adj(t, d2) != head and self.adj(t, d2) not in blocked)
                entry['shield'] = t in shield
                entry['edist'] = min((self.man(t, e['head']) for e in enemies if not e['queen']), default=99)
            cands.append(entry)
        esc_any, esc_open = self.escape_depth(head, view, occupied, risk, tail, L, own_time, blocked, no_portal)
        scored = [c for c in cands if c.get('enterable') and not (c['kind'] == 'portal' and no_portal)]
        open0 = any(c['risk'] == 0 and not c['closed'] for c in scored)
        open1 = any(c['risk'] == 1 and not c['closed'] for c in scored)
        risky = any(c['risk'] > 0 for c in scored)
        allies = sorted((self.man(b[0], head), i, len(b)) for i, b in self.bodies.items()
                        if self.teams[i] == self.own and i != Q and self.man(b[0], head) <= 6)
        local = {}
        for i, b in self.bodies.items():
            if any(self.cheb(c, head) <= 6 for c in b):
                local[i] = (self.teams[i] == self.own, list(b))
        return dict(k='t', game=self.meta['id'], label=self.label, map=self.meta['mapName'], cells=W * H, W=W, H=H, round=rnd,
                    head=head, L=L, body=body, enemies=enemies, hit_head=hit_head, pay_head=pay_head, cands=cands,
                    esc_any=esc_any, esc_open=esc_open, open0=open0, open1=open1, risky=risky, hit_blocked=risky and not open0,
                    any_enterable=bool(scored), hit=sorted(hit), pay=sorted(pay - hit), near=sorted(near)[:5], local=local,
                    allies=allies, shield=sorted(shield), pearls=sorted(c for c in self.pearls if c in view),
                    danger=dict((str(c), sorted(v)[:3]) for c, v in danger.items() if self.man(c, head) <= 3),
                    head_kelp=sum(1 for d2 in range(4) if self.kind(head, d2) == 1),
                    n_own=sum(1 for i in self.bodies if self.teams[i] == self.own),
                    n_enemy=sum(1 for i in self.bodies if self.teams[i] != self.own))

    def scan(self):
        W, Q = self.W, self.Q
        tile = lambda z: replay.point(z)[1] * W + replay.point(z)[0]
        rnd, actor = 0, None
        rec, turns, fate = None, [], None
        turn_start, used, dirs, action = {}, 0, [], None
        trace = []
        snap = {}
        occ_start = {}

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
                    occ_start = {}
                    for i, b in self.bodies.items():
                        for z, c in enumerate(b):
                            occ_start[c] = (i, z)
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
                        at = b[0]
                        dd = int(dirs[used]) if used < len(dirs) else None
                        fate['dirs'] = [int(x) for x in dirs]
                        fate['used'] = used
                        fate['at'] = at
                        if dd is not None:
                            e = self.eid(at, dd)
                            target = self.true_step(at, dd)
                            who = occ_start.get(target) if target >= 0 else None
                            now = None
                            for j, bb in self.bodies.items():
                                if target >= 0 and target in bb:
                                    now = (j, list(bb).index(target), len(bb))
                            fate['fatal'] = dict(dir=dd, edge=self.kind(at, dd), known=e in self.known, target=target,
                                                 occ_start=None if who is None else (who[0], who[1], self.teams[who[0]] == self.own),
                                                 occ_now=None if now is None else (now[0], now[1], now[2], self.teams[now[0]] == self.own, now[0] == self.EQ),
                                                 in_view=target >= 0 and self.cheb(target, turn_start['head']) <= 3)
                    close()
                self.bodies.pop(i)
        if actor == Q:
            close()
        final = dict(alive=Q in self.bodies, L=len(self.bodies.get(Q, ())), last_round=rnd)
        return turns, fate, final


def main():
    label = sys.argv[1]
    folder = SMOKE / (label + '-new')
    if not folder.exists():
        print('missing label', label)
        return
    lines = []
    for rp in sorted(folder.glob('M*.replay')):
        gid = int(rp.stem[1:])
        mp = folder / ('game-%d.json' % gid)
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text())
        g = Game(label, rp, meta)
        turns, fate, final = g.scan()
        own = 'ab'[g.own]
        for t in turns:
            lines.append(json.dumps(t, separators=(',', ':')))
        lines.append(json.dumps(dict(k='f', game=gid, label=label, map=meta['mapName'], cells=g.W * g.H, W=g.W, H=g.H, Q=g.Q,
                                     result='win' if meta.get('winner') == own else 'draw' if meta.get('winner') is None else 'loss',
                                     opponent=meta['team' + 'AB'[1 - g.own] + 'Name'], fate=fate, final=final, turns=len(turns)),
                                separators=(',', ':')))
        print(label, gid, meta['mapName'], g.W, g.H, 'turns', len(turns), 'fate',
              None if fate is None else (fate['round'], fate['cause'], fate['mover'], fate['L']), flush=True)
    text = ''.join(x + '\n' for x in lines)
    if label == 'agg8-q1':
        Path(WORK + 'q2_scan-agg8-q1.jsonl').write_text(text)
    elif label == 'agg8-q2':
        Path(WORK + 'q2_scan-agg8-q2.jsonl').write_text(text)
    elif label == 'agg7-m1':
        Path(WORK + 'q2_scan-agg7-m1.jsonl').write_text(text)
    elif label == 'agg7-m2':
        Path(WORK + 'q2_scan-agg7-m2.jsonl').write_text(text)
    elif label == 'agg7-m3':
        Path(WORK + 'q2_scan-agg7-m3.jsonl').write_text(text)
    print('written', label, len(lines))


main()
