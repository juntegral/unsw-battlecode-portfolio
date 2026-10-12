# Scratch (diag-walk): a toy walker on an empty wrap-around board that moves by the terms main.cpp leaves when nothing scores:
# 0.2*(260-40*d) + 2*(80-d) for the path distance d from the step to the nearest tile it has never seen (main.cpp:5028,
# 5037-5046), plus the tie-break 0.25*((id*31+round*17+k*7)%5) (main.cpp:5361). Room and territory are the same in every
# direction for a dragon alone on open ground. Prints the share of steps onto its own last 12 tiles and the share that
# keep the direction, with the tie-break as written, with a fixed order instead, and with a small cost on turning.
# Usage: python3 data/analysis/ladder/dossier/work/wk_sim.py
import sys
sys.dont_write_bytecode = True
from collections import deque

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def walk(size, length, ident, rounds, mode, known, turn_cost=0.0, tread_cost=0.0):
    w = h = size
    seen = bytearray(w * h)
    if known:
        seen = bytearray([1]) * (w * h)
    body = deque([(size // 2) * w + size // 2 - k for k in range(length)])
    trail = deque([body[0]], maxlen=12)
    last = None
    n = re = keep = elig = 0

    def nearest(dest, blocked):
        if not seen[dest]:
            return 1
        d = {dest: 1}
        q = deque([dest])
        while q:
            z = q.popleft()
            if d[z] >= 14:
                return -1
            y, x = divmod(z, w)
            for dx, dy in STEP:
                t = ((y + dy) % h) * w + (x + dx) % w
                if t in d or t in blocked:
                    continue
                if not seen[t]:
                    return d[z] + 1
                d[t] = d[z] + 1
                q.append(t)
        return -1

    for rnd in range(1, rounds + 1):
        head = body[0]
        y, x = divmod(head, w)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                seen[((y + dy) % h) * w + (x + dx) % w] = 1
        blocked = set(body)
        best, best_score = None, -1e18
        for k, (dx, dy) in enumerate(STEP):
            dest = ((y + dy) % h) * w + (x + dx) % w
            if dest in blocked:
                continue
            d = nearest(dest, blocked)
            score = 0.0
            if d >= 0:
                score += max(0.0, 0.2 * (260 - 40 * d)) + 2 * max(0, 80 - d)
            if mode == 'bot':
                score += 0.25 * ((ident * 31 + rnd * 17 + k * 7) % 5)
            elif mode == 'fixed':
                score += 0.25 * k
            if last is not None and k != last:
                score -= turn_cost
            if dest in trail:
                score -= tread_cost
            if score > best_score:
                best, best_score = k, score
        if best is None:
            break
        dx, dy = STEP[best]
        dest = ((y + dy) % h) * w + (x + dx) % w
        if rnd > 12:
            n += 1
            re += int(dest in trail)
            if last is not None:
                elig += 1
                keep += int(best == last)
        body.appendleft(dest)
        body.pop()
        trail.append(dest)
        last = best
    return n, re, keep, elig


def main():
    print('board | length | rule | steps | onto own last 12 tiles | keeps direction')
    for known, name, size, rounds in ((False, 'never-seen ground all round (64x64, 150 rounds)', 64, 150),
                                      (True, 'everything already seen (any size)', 32, 150)):
        for length in (2, 3, 4, 6):
            for mode, tc, rc, label in (('bot', 0.0, 0.0, 'tie-break as written'), ('fixed', 0.0, 0.0, 'fixed order N<E<S<W'),
                                        ('bot', 1.5, 0.0, 'as written, turning costs 1.5'), ('bot', 0.0, 1.5, 'as written, own recent tile costs 1.5'),
                                        ('bot', 1.5, 1.5, 'as written, both cost 1.5')):
                tot = [0, 0, 0, 0]
                for ident in range(0, 40):
                    r = walk(size, length, ident, rounds, mode, known, tc, rc)
                    tot = [a + c for a, c in zip(tot, r)]
                print('%s | %d | %s | %d | %.1f%% | %.1f%%' % (name, length, label, tot[0], 100 * tot[1] / max(1, tot[0]), 100 * tot[2] / max(1, tot[3])))


main()
