# Known map: keep the portal curiosity of the unknown-map bot: a portal whose far side we have never seen attracts small
# dragons like an unknown portal did (bfsPortal / PORTAL_ENTER). Requires patch_map.py. usage: python3 patch_curious.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
rep("""            for (int dd = 0; dd < 4; dd++) {
                int u = across(t, dd);
                if (u == -2 && k + 1 < bfsPortal) bfsPortal = k + 1;""",
"""            for (int dd = 0; dd < 4; dd++) {
                int u = across(t, dd);
                if (u == -2 && k + 1 < bfsPortal) bfsPortal = k + 1;
                if (mapIdx >= 0 && u >= 0 && ek[t * 4 + dd] == E_PORTAL && seenR[u] < 0 && k + 1 < bfsPortal) bfsPortal = k + 1; // px3e""")
rep("""        if (nbKind[d] == NB_PORTAL_UNKNOWN) return""",
"""        if (mapIdx >= 0 && L < style::BIG_LEN && nbKind[d] == NB_FREE && ek[head * 4 + d] == E_PORTAL && seenR[s] < 0) return style::PORTAL_ENTER + 0.01 * rnd(90 + d); // px3e: never-seen far side
        if (nbKind[d] == NB_PORTAL_UNKNOWN) return""")
open(p, 'w').write(s)
print('patched', d)
