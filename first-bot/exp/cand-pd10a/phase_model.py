#!/usr/bin/env python3
"""Prisoners Dilemma 통로 고리의 1차원 모형 (cand-pd10).

통로 x=14는 y=0..15다. y=0..3과 y=12..15는 양옆이 해초(막힌 칸)이고, y=4..11은 옆이 열려 있다.
끝마다 칸이 셋이다: 끝 칸(y=0/15), 샘물(y=1/14, 간격 1), 안쪽 칸(y=2/13).
  - 6마리 판본: 안쪽 칸도 간격 1 샘물이다.
  - 10마리 판본(서버): 안쪽 칸은 진주가 나지 않는다. 그 칸의 진주는 앞선 토막의 주검뿐이다.
고리 한 번(한쪽 끝 방문):
  - 길이 k로 태어난 사슬이 끝으로 간다. 안쪽 칸 진주(Pn)와 샘물(1)을 먹고 샘물 칸에서 막힌다: L = k + Pn + 1.
  - 자식은 늘 꼬리에서 태어난다. 꼬리의 끝 칸으로부터의 거리 T = L. T >= 12이면 반대쪽 막힌 칸에서 태어난다(안전).
    T < 12이면 옆이 열린 칸(y=4 또는 11)에서 태어난다(옆에서 박힐 수 있고, 옆으로 나갈 수 있다).
  - 보통 분열: 자식 L-2, 토막 2가 끝 칸 진주(Pe)를 먹고 죽는다. 토막 길이 3 이상이면 안쪽 칸에 주검 진주를 남긴다.
  - 주머니 먹기(pocket eat): 끝 칸 진주를 먼저 먹고(L+1) 다음 턴에 나눈다. 자식 L-1, 토막 2는 끝 칸에서 바로 죽는다.
    꼬리는 움직이지 않으므로 T는 그대로다.
정책:
  base : 늘 보통 분열(현재 봇).
  a    : 분열로 태어난 사슬만. 자식이 태어난 길이보다 짧아지면(열린 칸에서 태어났으면 +1까지) 주머니 먹기.
  b    : a와 같되 지도에 처음부터 있던 드래곤도 포함한다(처음 길이를 태어난 길이로 본다).
usage: python3 exp/cand-pd10a/phase_model.py
"""


def run(policy, version, visits=12):
    fountain_near = version == 6
    pn = [0, 1 if fountain_near else 0]  # 첫 방문(위): 안쪽 칸 y=2는 시작 머리 자리라 진주가 없다
    pe = [1, 1]                           # 0라운드 끝 칸 진주
    end, k, birth_len, exposed, map_dragon = 0, 11, 11, False, True  # 시작 드래곤: 길이 11, 머리 y=2
    d0 = 2                                 # 이번 끝에서 머리가 시작하는 거리(끝 칸 0, 샘물 1, 안쪽 칸 2)
    out = []
    for _ in range(visits):
        e = (pn[end] if d0 > 2 else 0) + (1 if d0 > 1 else 0)
        L = k + e
        T = L                               # 꼬리의 이번 끝으로부터의 거리
        child = L - 2
        eat = False
        if policy != 'base' and (not map_dragon or policy == 'b') and pe[end]:
            cap = birth_len + (1 if exposed else 0)
            if L + 1 - 2 <= cap:            # 봇의 조건: 먹고 나눈 자식이 상한 이하
                eat = True
        if eat:
            child = L - 1
            stub_len_at_death = 2
        else:
            stub_len_at_death = 2 + pe[end]
        new_pn = 1 if (stub_len_at_death >= 3 or fountain_near) else 0
        out.append((('위', '아래')[end], k, T, 'O' if T >= 12 else 'X', '먹기' if eat else '보통', child))
        pn[end], pe[end] = new_pn, 1
        d0 = 15 - T                         # 다음 끝에서 자식 머리의 거리
        end, k, birth_len, exposed, map_dragon = 1 - end, child, child, T < 12, False
    return out


def search(allow_eat, depth=12):
    """10마리 판본 전수 탐색: 방문마다 가능한 모든 선택(보통 분열의 자식 2..L-2, 끝 칸을 먼저 먹는 분열의 자식 2..L-1)."""
    from collections import deque
    # 상태: (끝, 도착 길이 k, 위 안쪽 진주, 아래 안쪽 진주, 이번 머리 시작 거리 d0)
    start = (0, 11, 0, 0, 2)
    seen = {start: 0}
    q = deque([start])
    walled = set()
    while q:
        st = q.popleft()
        end, k, pt, pb, d0 = st
        if seen[st] >= depth:
            continue
        pn = pt if end == 0 else pb
        e = (pn if d0 > 2 else 0) + (1 if d0 > 1 else 0)
        L = k + e
        T = L
        if st != start and T >= 12:
            walled.add((k, pt, pb))
        opts = [(c, 1 if (L - c) + 1 >= 3 else 0) for c in range(2, L - 1)]          # 보통: 토막이 끝 칸 진주를 먹고 죽는다
        if allow_eat:
            opts += [(c, 1 if (L + 1 - c) >= 3 else 0) for c in range(2, L)]       # 먹고 나눔: 토막은 끝 칸에서 바로 죽는다
        for c, npn in opts:
            ns = (1 - end, c, npn if end == 0 else pt, pb if end == 0 else npn, 15 - T)
            if ns not in seen:
                seen[ns] = seen[st] + 1
                q.append(ns)
    return len(seen), sorted(walled)


if __name__ == '__main__':
    import sys
    if '--search' in sys.argv:
        for allow in (False, True):
            n, w = search(allow)
            print(f"{'끝 칸 먼저 먹기 포함' if allow else '샘물 칸에서 나누기만'}: 도달 상태 {n}, 첫 방문 뒤 막힌 칸 탄생 상태(k, 위 안쪽, 아래 안쪽) {w}")
        sys.exit(0)
    for version in (6, 10):
        for policy in ('base', 'a', 'b'):
            seq = run(policy, version)
            x = sum(1 for s in seq if s[3] == 'X')
            print(f'{version}마리 {policy:4s} 열린 칸 탄생 {x}/{len(seq)}: ' + ' '.join(f'{e}k{k}T{T}{s}' + ('*' if kind == '먹기' else '') for e, k, T, s, kind, c in seq))
