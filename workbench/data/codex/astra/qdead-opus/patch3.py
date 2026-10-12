import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)

rep("constexpr int QUEEN_DEAD_KNOWN = 0;\n", "constexpr int QUEEN_DEAD_KNOWN = 0;\nconstexpr bool QUEEN_HOLD_FEED = true;\n")
rep("        return QUEEN_MODE && queen_id >= 0 && id == queen_id && len >= 2 && len < 2 * QUEEN_HOLD_LEN &&",
    "        return QUEEN_HOLD_FEED && QUEEN_MODE && queen_id >= 0 && id == queen_id && len >= 2 && len < 2 * QUEEN_HOLD_LEN &&")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
