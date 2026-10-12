# Known map: room check for long dragons = hard L+KNOWN_ROOM_EXTRA, soft up to 2L+4. usage: python3 patch_room.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
old = """        int need = L >= style::BIG_ROOM_LEN ? 2 * L + style::BIG_ROOM_EXTRA : L + style::ROOM_EXTRA, cap = std::max(need, style::ROOM_MIN);
        int rm = room(s, cap);"""
new = """        int need = L >= style::BIG_ROOM_LEN ? 2 * L + style::BIG_ROOM_EXTRA : L + style::ROOM_EXTRA, cap = std::max(need, style::ROOM_MIN);
        double pocketPen = style::POCKET_PEN;
        // px3b: with the true geometry a long dragon needs room for its body (hard) and prefers room to turn (soft);
        // 2L+4 as a hard need kept kings out of the mazes where the pearls are
        if (mapIdx >= 0 && L >= style::BIG_ROOM_LEN) { need = L + style::KNOWN_ROOM_EXTRA; pocketPen = style::KNOWN_SOFT_PEN; }
        int rm = room(s, cap);"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """        else if (rm < cap) sc -= style::POCKET_PEN * (cap - rm) / (double)cap; // a small closed pocket: mild"""
new = """        else if (rm < cap) sc -= pocketPen * (cap - rm) / (double)cap; // a small closed pocket: mild"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "constexpr bool USE_MAPDB = true;"
assert old in s
s = s.replace(old, """constexpr bool USE_MAPDB = true;
constexpr int KNOWN_ROOM_EXTRA = 4;         // known map, length >= BIG_ROOM_LEN: hard room need L + this ...
constexpr double KNOWN_SOFT_PEN = 1.0;      // ... and a soft penalty up to this while the room is below 2L + BIG_ROOM_EXTRA""", 1)
open(p, 'w').write(s)
print('patched', d)
