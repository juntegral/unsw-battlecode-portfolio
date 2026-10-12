# px8: pearls around any visible big ally (>= KING_MIN_LEN and >= our length + 3) are reserved strongly (x RESERVE_MULT)
# within KING_RESERVE_R, from SAC_START - 20; does not depend on knowing which dragon is the king. usage: python3 patch_reserve.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
old = """        if (round >= style::SAC_START) {
            for (auto& v : vis) {
                if (v.id == myId || v.team != myTeam || v.head < 0 || v.len < L + 3) continue;
                for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) {
                    if (std::abs(dx) + std::abs(dy) > 2) continue;
                    leave[wy(v.head / W + dy) * W + wx(v.head % W + dx)] = 1;
                }
            }
        }"""
new = """        if (round >= style::SAC_START - 20) {
            for (auto& v : vis) {
                if (v.id == myId || v.team != myTeam || v.head < 0 || v.len < L + 3) continue;
                bool big = v.len >= style::KING_MIN_LEN;             // px8: any visible big ally, known king or not
                if (!big && round < style::SAC_START) continue;
                const int R = big ? style::KING_RESERVE_R : 2; const uint8_t lvl = big ? 2 : 1;
                for (int dy = -R; dy <= R; dy++) for (int dx = -R; dx <= R; dx++) {
                    if (std::abs(dx) + std::abs(dy) > R) continue;
                    uint8_t& c = leave[wy(v.head / W + dy) * W + wx(v.head % W + dx)];
                    if (c < lvl) c = lvl;
                }
            }
        }"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
print('patched', d)
