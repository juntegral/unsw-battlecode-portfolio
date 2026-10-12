# px4: all mass to the king (sacrifice only beside the king once one is known; late merge of big non-kings),
# gather from GATHER_START, king reports stale after KING_STALE rounds. usage: python3 patch_kingonly.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
old = s[s.index("    bool wantSacrifice() {"):s.index("    double scoreDir(")]
new = '''    bool wantSacrifice() {
        if (round < style::SAC_START || round > 496 || units <= style::SAC_MIN_UNITS) return false;
        int kid = -1, klen = 0, kt = -1, kr = -1;
        if (style::KING_GATHER) { kingInfo(kid, klen, kt, kr); if (kid == myId) return false; if (klen < style::KING_MIN_LEN) kid = -1; }
        // px4: with a known king, all mass goes to the king: no diffuse feeding of other allies, and late even big dragons merge
        bool kingOnly = style::KING_ONLY && kid >= 0 && klen > L;
        bool small = L <= style::SAC_MAX_LEN;
        bool mid = !small && round >= style::SAC2_START && L <= style::SAC2_MAX_LEN;
        bool large = !small && !mid && kingOnly && round >= style::MERGE_START && 500 - round >= L + style::MERGE_SLACK;
        if (!small && !mid && !large) return false;
        double ramp = std::min(1.0, (round - style::SAC_START + 1) / (double)style::SAC_RAMP);
        // feed a longer ally whose head is close: directly (big receiver within 2, or the king) or diffusely (any longer
        // ally within SAC_RECV_DIST, the N style's nearby mid-size eaters)
        double best = 0;
        for (auto& s : vis) {
            if (s.id == myId || s.team != myTeam || s.head < 0) continue;
            bool isKing = kid >= 0 && s.id == kid;
            if (kingOnly && !isKing) continue;
            int al = s.len, c = cheb(s.head, head);
            int margin = round >= style::MERGE_START ? 1 : style::SAC2_MARGIN; // late: merge into any longer neighbour
            if (al <= L || (mid && al < L + margin)) continue;
            double q = 0;
            bool bigRecv = al >= std::max(style::BIG_RECV_LEN, 2 * L) || (mid && al >= L + margin);
            if (c <= 2 && bigRecv) q = small ? style::SAC_NEAR_P : style::SAC2_P;
            else if (c <= style::SAC_RECV_DIST) q = small ? style::SAC_P : 0.0;
            if (isKing && manh(s.head, head) <= style::KING_SAC_DIST) q = std::max(q, style::SAC_KING_P);
            // px2: feed from the front: our pearls land where the receiver's head can take them next
            if ((bigRecv || isKing) && c <= 2 && !behind(s.head, s.hdir, head))
                q = std::max(q, manh(s.head, head) <= 1 ? style::FEED_ADJ_P : style::FEED_FRONT_P);
            if (large) q = (isKing && c <= 2 && !behind(s.head, s.hdir, head)) ? style::FEED_FRONT_P : 0.0;
            best = std::max(best, q * ramp);
        }
        return best > 0 && rnd(77) < best;
    }

'''
s = s.replace(old, new)
# king reports go stale sooner
rep("""            if (nw.round < round - 40 || nw.t < 0) continue;
            if (nw.len > klen || (nw.len == klen && id < kid)) { kid = id; klen = nw.len; kt = nw.t; kround = nw.round; }""",
"""            if (nw.round < round - style::KING_STALE || nw.t < 0) continue;
            if (nw.len > klen || (nw.len == klen && id < kid)) { kid = id; klen = nw.len; kt = nw.t; kround = nw.round; }""")
# gathering starts before the sacrifices
rep("""        bool late = round >= style::SAC_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;""",
"""        bool late = round >= style::GATHER_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "constexpr double BIG_PORTAL_UNKNOWN = -1.0;"
assert old in s
s = s.replace(old, """constexpr double BIG_PORTAL_UNKNOWN = -1.0;
// --- px4: all mass to the king ---
constexpr bool KING_ONLY = true;            // with a known king (>= KING_MIN_LEN, longer than us) sacrifice only beside the king
constexpr int MERGE_SLACK = 6;              // from MERGE_START any non-king merges into the king if 500 - round >= L + this
constexpr int GATHER_START = 320;           // non-kings walk to the king from here (sacrifices start at SAC_START)
constexpr int KING_STALE = 25;              // a king report older than this is ignored""", 1)
open(p, 'w').write(s)
print('patched', d)
