#!/usr/bin/env python3
"""patch_rules.py <bot dir> — add three decision rules learned from top-vs-top play (research/observations/top-decisions.md,
data/decisions/rules.md) to a base-px bot (pxcore.cpp + style.hpp). Each rule has its own switch in style.hpp.

  RULE_RAM (R4, b1 leaves): the probability of a head-on ram this turn (1 or 2 steps) follows the top teams' table
    by our length, the target's length, ally heads in view (aN) and enemy heads in view (eN):
      alone:            shorter 1.3%, equal 6%, longer 50% (eN <= 1) / 21%
      ally in view:     shorter 35.5% (L <= 3, eN <= 1) / 14.8% (L = 4) / 6.9% (aN = 1, eN >= 2) / 18.2% (aN >= 2)
                        equal or longer 70.7% (L <= 3, eN <= 2) / 30.5% (L = 4) / 25.9% (eN >= 3, aN <= 2) / 63%
    Big targets (px8 isBig) keep at least the px8 eager values. An ally whose head is in a closed pocket (our corridor
    fortress) does not count as an ally in view.
  RULE_SAC (R3, d1): a small piece sacrifices only beside a visible ally of length >= 8 (was: max(6, 2L) or any
    longer ally), never with an enemy head in view. Within Manhattan 3 of such an ally: 5.2%/turn from r250, 16.9% from
    r350. From SAC_START the px8 pulls stay on top (big receiver within Chebyshev 2, the king, feeding from the front),
    ramped as before, with the same length floor. Mid-size pieces keep the px8 rule with the same floor.
  RULE_ESCAPE (R8): a dragon of length >= 6 whose every free single step lies inside the reach of a shorter visible
    enemy head (path distance <= min(its length - 1, 3) over free tiles) sprints 2 or 3 steps to a free tile outside
    every such reach, choosing the end with the most room (2L + 4 wanted), 2 steps preferred over 3.
"""
import sys, os

d = sys.argv[1]
sp, cp = os.path.join(d, 'style.hpp'), os.path.join(d, 'pxcore.cpp')
s = open(sp).read(); c = open(cp).read()

def sub(text, old, new, what):
    assert text.count(old) == 1, 'anchor not unique or missing: ' + what
    return text.replace(old, new)

s = sub(s, '// --- movement ---\n', '''// --- px9c: decision rules learned from top-vs-top play (research/observations/top-decisions.md) ---
constexpr bool RULE_RAM = true;             // R4/b1: ram table by lengths, allies and enemies in view
constexpr bool RULE_SAC = true;             // R3: sacrifice only beside allies of length >= SAC_RECV_MIN, no enemy in view
constexpr int SAC_RECV_MIN = 8;
constexpr int SAC_EARLY_START = 250;
constexpr double SAC_EARLY_P = 0.052;       // per turn, r250-349, ally of SAC_RECV_MIN+ within Manhattan 3
constexpr double SAC_TOP_P = 0.169;         // per turn from r350
constexpr bool RULE_ESCAPE = true;          // R8: sprint out of the reach of shorter enemy heads when every step is exposed
constexpr int ESC_MIN_LEN = 6;

// --- movement ---
''', 'style movement')

# ---- R4: ram table ----
c = sub(c, '''            const Seen* e = seenById(nbId[d]); int el = e ? estLen(*e) : 2;
            double p = isBig(el) ? style::RAM_BIG_ADJ : el > L ? style::RAM_ADJ_UP : style::RAM_ADJ;''',
'''            const Seen* e = seenById(nbId[d]); int el = e ? estLen(*e) : 2;
            double p = style::RULE_RAM ? ramP(el, isBig(el), style::RAM_BIG_ADJ) : isBig(el) ? style::RAM_BIG_ADJ : el > L ? style::RAM_ADJ_UP : style::RAM_ADJ;''', 'ram 1')
c = sub(c, '''                double p = isBig(el) ? style::RAM_BIG_S2 : el > L ? style::RAM_S2_UP : style::RAM_S2;''',
'''                double p = style::RULE_RAM ? ramP(el, isBig(el), style::RAM_BIG_S2) : isBig(el) ? style::RAM_BIG_S2 : el > L ? style::RAM_S2_UP : style::RAM_S2;''', 'ram 2')
c = sub(c, '''    bool tryRam(Plan& out) {''', '''    // px9c R4/b1: ram probability from the top teams' table (see style.hpp); big targets keep the eager px8 value
    double ramP(int el, bool big, double bigP) const {
        int aN = 0, eN = 0;
        for (auto& v : vis) if (v.id != myId && v.head >= 0) { if (v.team != myTeam) eN++; else if (!pocketedNow(v.id)) aN++; }
        double p;
        if (aN == 0) p = el < L ? 0.013 : el == L ? 0.06 : (eN <= 1 ? 0.50 : 0.21);
        else if (el < L) p = eN <= 1 ? (L <= 3 ? 0.355 : 0.148) : (aN == 1 ? 0.069 : 0.182);
        else p = eN <= 2 ? (L <= 3 ? 0.707 : 0.305) : (aN <= 2 ? 0.259 : 0.63);
        return big ? std::max(p, bigP) : p;
    }
    bool tryRam(Plan& out) {''', 'tryRam head')

# ---- R3: sacrifice ----
c = sub(c, '''    bool wantSacrifice() {
        if (round < style::SAC_START || round > 496 || units <= style::SAC_MIN_UNITS) return false;''',
'''    // px9c R3: sacrifice beside allies of length >= SAC_RECV_MIN only, never with an enemy head in view (see style.hpp)
    bool wantSacrificeTop() {
        if (round < style::SAC_EARLY_START || round > 496 || units <= style::SAC_MIN_UNITS) return false;
        bool small = L <= style::SAC_MAX_LEN;
        bool mid = !small && round >= style::SAC2_START && L <= style::SAC2_MAX_LEN;
        if (!small && !mid) return false;
        for (auto& s : vis) if (s.team != myTeam && s.head >= 0) return false;
        bool late = round >= style::SAC_START;
        double ramp = late ? std::min(1.0, (round - style::SAC_START + 1) / (double)style::SAC_RAMP) : 0.0;
        int kid = -1, klen = 0, kt = -1, kr = -1;
        if (style::KING_GATHER && late) { kingInfo(kid, klen, kt, kr); if (kid == myId) return false; if (klen < style::KING_MIN_LEN) kid = -1; }
        double best = 0;
        for (auto& s : vis) {
            if (s.id == myId || s.team != myTeam || s.head < 0 || pocketedNow(s.id)) continue;
            int al = s.len, c = cheb(s.head, head), m = manh(s.head, head);
            if (al < style::SAC_RECV_MIN || al <= L) continue;
            int margin = round >= style::MERGE_START ? 1 : style::SAC2_MARGIN;
            if (mid && al < L + margin) continue;
            double q = 0;
            if (small && m <= 3) q = round < 350 ? style::SAC_EARLY_P : style::SAC_TOP_P;
            if (late) {
                double q2 = 0;
                if (c <= 2) q2 = small ? style::SAC_NEAR_P : style::SAC2_P;
                if (style::KING_GATHER && s.id == kid && m <= style::KING_SAC_DIST) q2 = std::max(q2, style::SAC_KING_P);
                if (c <= 2 && !behind(s.head, s.hdir, head)) q2 = std::max(q2, m <= 1 ? style::FEED_ADJ_P : style::FEED_FRONT_P);
                q = std::max(q, q2 * ramp);
            }
            best = std::max(best, q);
        }
        return best > 0 && rnd(77) < best;
    }
    bool wantSacrifice() {
        if (style::RULE_SAC) return wantSacrificeTop();
        if (round < style::SAC_START || round > 496 || units <= style::SAC_MIN_UNITS) return false;''', 'wantSacrifice')

# ---- R8: sprint escape ----
c = sub(c, '''        // 5. move (a contested pearl two steps away is worth a sprint)
        if (trySprintEat(p)) return p;''',
'''        // px9c R8: a long dragon sprints out of the reach of shorter enemy heads when every single step is exposed
        if (style::RULE_ESCAPE && L >= style::ESC_MIN_LEN && tryEscape(p)) return p;
        // 5. move (a contested pearl two steps away is worth a sprint)
        if (trySprintEat(p)) return p;''', 'decide escape')
c = sub(c, '''    bool wantSplit(int& c) {''', '''    // px9c R8: exposure = inside the reach of a shorter visible enemy head (path distance over free tiles <=
    // min(its length - 1, 3)). When every free single step is exposed, sprint 2 (or 3) steps to an unexposed free tile.
    std::vector<uint8_t> expo; std::vector<int> escD;
    bool tryEscape(Plan& out) {
        if ((int)expo.size() != N) { expo.assign(N, 0); escD.assign(N, -1); }
        std::vector<int> marked; bool any = false;
        for (auto& s : vis) {
            if (s.team == myTeam || s.head < 0) continue;
            int reach = std::min(s.len - 1, 3); if (s.len >= L || reach < 1) continue;
            any = true;
            std::vector<int> qq(1, s.head), seenT(1, s.head); escD[s.head] = 0;
            for (size_t qi = 0; qi < qq.size(); qi++) {
                int t = qq[qi], k = escD[t];
                if (k >= 1 && !expo[t]) { expo[t] = 1; marked.push_back(t); }
                if (k >= reach) continue;
                for (int dd = 0; dd < 4; dd++) {
                    int u = across(t, dd);
                    if (u < 0 || escD[u] >= 0) continue;
                    if (u != head && (occKind[u] != 0 || bodyIdx[u] >= 0)) continue;
                    escD[u] = k + 1; qq.push_back(u); seenT.push_back(u);
                }
            }
            for (int t : seenT) escD[t] = -1;
        }
        bool result = false;
        if (any) {
            int nSingle = 0, nExp = 0;
            for (int d = 0; d < 4; d++) { if (nbKind[d] != NB_FREE) continue; nSingle++; if (expo[nb[d]]) nExp++; }
            if (nSingle > 0 && nExp == nSingle) {
                auto freeT = [&](int u) { return u >= 0 && u != head && occKind[u] == 0 && bodyIdx[u] < 0 && headId[u] < 0; };
                int need = L >= style::BIG_ROOM_LEN ? 2 * L + style::BIG_ROOM_EXTRA : L + style::ROOM_EXTRA;
                double bestV = -1; std::string bestDirs;
                for (int d1 = 0; d1 < 4; d1++) {
                    if (nbKind[d1] != NB_FREE || nbBlind[d1]) continue;
                    int u1 = nb[d1];
                    for (int d2 = 0; d2 < 4; d2++) {
                        if (d2 == opp(d1)) continue;
                        int u2 = across(u1, d2);
                        if (!freeT(u2) || u2 == u1) continue;
                        if (!expo[u2]) { double v = std::min(room(u2, need), need) + 0.5 + 0.01 * rnd(120 + d1 * 4 + d2); if (v > bestV) { bestV = v; bestDirs = std::string(1, DIRCH[d1]) + DIRCH[d2]; } }
                        if (L < 4) continue;
                        for (int d3 = 0; d3 < 4; d3++) {
                            if (d3 == opp(d2)) continue;
                            int u3 = across(u2, d3);
                            if (!freeT(u3) || u3 == u1 || expo[u3]) continue;
                            double v = std::min(room(u3, need), need) + 0.01 * rnd(140 + d1 * 16 + d2 * 4 + d3);
                            if (v > bestV) { bestV = v; bestDirs = std::string(1, DIRCH[d1]) + DIRCH[d2] + DIRCH[d3]; }
                        }
                    }
                }
                if (!bestDirs.empty() && bestV >= std::min(need, L + 1)) { out.kind = Plan::MOVE; out.dirs = bestDirs; out.tag = 'Z'; result = true; }
            }
        }
        for (int t : marked) expo[t] = 0;
        return result;
    }
    bool wantSplit(int& c) {''', 'tryEscape')

open(sp, 'w').write(s); open(cp, 'w').write(c)
print('patched', d)
