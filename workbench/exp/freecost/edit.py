from pathlib import Path
root=Path('versions/v1.8/bot')
def edit(name,old,new):
 p=root/name
 t=p.read_text()
 assert t.count(old)==1,(name,old,t.count(old))
 p.write_text(t.replace(old,new))
edit('params.hpp','constexpr bool   Q2D_FREESTEP_ON = false; // 1.2.3 free-step moves for every dragon','''constexpr bool   Q2D_FREESTEP_ON = false; // 1.2.3 free-step moves for every dragon
constexpr bool   FREECOST_ON = false;    // 1.2.3 payment and body model without candidate expansion
constexpr int freeSteps123(int length) { return (length + 3) / 4; }
constexpr int paidSteps123(int length, int steps) { return steps > freeSteps123(length) ? steps - freeSteps123(length) : 0; }
constexpr int reach123(int length, int pearls = 0) { return freeSteps123(length) + length + pearls - 2; }''')
edit('plan.hpp','    int paidSteps(int x) const { return freeStepsOn() ? std::max(0, x - (w_.myLen + 3) / 4) : x - 1; }   // Q2d: segments an x-step move costs','''    int paidSteps(int x) const {
        if constexpr (P::FREECOST_ON) return P::paidSteps123(w_.myLen, x);
        else return freeStepsOn() ? std::max(0, x - (w_.myLen + 3) / 4) : x - 1;
    }''')
edit('plan.cpp','        int reach = std::min(le - 1, 4);','''        int reach = std::min(le - 1, 4);
        if constexpr (P::FREECOST_ON) reach = std::min(P::reach123(le), 4);''')
edit('plan.cpp','''            if (le2 < 99) for (int dir = 0; dir < 4; dir++) { int u = w_.across(d.headT, dir); if (u >= 0 && w_.pearlProb(u, w_.round) >= 0.5) { le2++; break; } }
            int reach2 = std::min(P::Q2B_SAFE_ON && queenFar_ && le2 < 99 ? (le2 + 3) / 4 + le2 - 2 : le2 - 1, P::KS2_REACH);''','''            int reach2;
            if constexpr (P::FREECOST_ON) {
                int food = 0;
                if (le2 < 99) for (int dir = 0; dir < 4; dir++) { int u = w_.across(d.headT, dir); if (u >= 0 && w_.pearlProb(u, w_.round) >= 0.5) { food = 1; break; } }
                reach2 = std::min(P::reach123(le2, food), P::KS2_REACH);
            } else {
                if (le2 < 99) for (int dir = 0; dir < 4; dir++) { int u = w_.across(d.headT, dir); if (u >= 0 && w_.pearlProb(u, w_.round) >= 0.5) { le2++; break; } }
                reach2 = std::min(P::Q2B_SAFE_ON && queenFar_ && le2 < 99 ? (le2 + 3) / 4 + le2 - 2 : le2 - 1, P::KS2_REACH);
            }''')
edit('plan.cpp','''        if (queenFar_ ? le2 - std::max(0, d2 - (le2 + 3) / 4) < 2 : le2 < d2 + 1) return 0.0;''','''        if constexpr (!P::FREECOST_ON) {
            if (queenFar_ ? le2 - std::max(0, d2 - (le2 + 3) / 4) < 2 : le2 < d2 + 1) return 0.0;
        } // Q2b's BFS already bounded payment using the starting length.''')
edit('plan.cpp','''                    if (freeStepsOn() ? w_.myLen + pe2 - paidSteps(3) < 2 : w_.myLen + pe2 - 1 < 3) continue; // the third step must be payable''','''                    if constexpr (P::FREECOST_ON) {
                        if (w_.myLen + pe2 - paidSteps(3) < 2) continue;
                    } else {
                        if (freeStepsOn() ? w_.myLen + pe2 - paidSteps(3) < 2 : w_.myLen + pe2 - 1 < 3) continue;
                    }''')
edit('plan.cpp','''        int maxSteps = std::min(P::STRIKE_MAX_STEPS, freeStepsOn() ? (w_.myLen + 3) / 4 + w_.myLen - 2 : w_.myLen - 1);   // v1.8 Q2d: 1.2.3 reach''','''        int maxSteps = std::min(P::STRIKE_MAX_STEPS, freeStepsOn() ? (w_.myLen + 3) / 4 + w_.myLen - 2 : w_.myLen - 1);   // v1.8 Q2d: 1.2.3 reach
        if constexpr (P::FREECOST_ON) maxSteps = std::min(maxSteps, P::reach123(w_.myLen));''')
p=root/'plan.cpp'; t=p.read_text(); old='w_.myLen + c.pearls - ((int)c.dirs.size() - 1)'; assert t.count(old)==4
# Keep the original dispatch in the off instantiation.
start=t.index('            if constexpr (PT) cont = dfsPt(c.tiles.back()')
end=t.index('\n            v2[i] =',start)
legacy=t[start:end]
new=legacy.replace(old,'lenAfter')
t=t[:start]+'''            if constexpr (P::FREECOST_ON) {
                const int lenAfter = w_.myLen + c.pearls - paidSteps((int)c.dirs.size());
'''+ '\n'.join('    '+line for line in new.splitlines())+'''\n            } else {
'''+ '\n'.join('    '+line for line in legacy.splitlines())+'''\n            }'''+t[end:]
p.write_text(t)
edit('main.cpp','''                    const bool fs = P::Q2D_FREESTEP_ON || (P::Q2DQ_ON && world.myId <= 1);   // v1.8 Q2d / Q2dq
                    rl += eat - (fs ? std::max(0, (int)a.dirs.size() - (world.myLen + 3) / 4) : (int)a.dirs.size() - 1);   // v1.8 Q2d: 1.2.3 payment''','''                    if constexpr (P::FREECOST_ON) rl += eat - P::paidSteps123(world.myLen, (int)a.dirs.size());
                    else {
                        const bool fs = P::Q2D_FREESTEP_ON || (P::Q2DQ_ON && world.myId <= 1);
                        rl += eat - (fs ? std::max(0, (int)a.dirs.size() - (world.myLen + 3) / 4) : (int)a.dirs.size() - 1);
                    }''')
edit('main.cpp','''        // cand-mapid: the map recognition tag (" map=<Name>/<a|b|?>", " map=?", " map=none") on this process's first turn''','''        if constexpr (P::FREECOST_ON) {
            if (a.kind == Action::SPLIT) {
                if (a.splitSize >= 2 && world.myLen - a.splitSize >= 2 && world.unitCount < world.unitLimit)
                    while ((int)world.body.size() > world.myLen - a.splitSize) world.body.pop_back();
            } else if (a.path.size() == a.dirs.size()) world.predictOwnMove(a.path);
        }
        // cand-mapid: the map recognition tag (" map=<Name>/<a|b|?>", " map=?", " map=none") on this process's first turn''')
# Public helper: only linked by the on build, and no new object state.
edit('world.hpp','    void ingest(const RoundBlock& rb);','''    void ingest(const RoundBlock& rb);
    void predictOwnMove(const std::vector<int>& path);''')
edit('world.cpp','void World::updateOwnBody(const RoundBlock& rb) {','''void World::predictOwnMove(const std::vector<int>& path) {
    if constexpr (P::FREECOST_ON) {
        const int gratis = P::freeSteps123(myLen);
        for (size_t k = 0; k < path.size(); k++) {
            const int t = path[k];
            body.push_front(t);
            if (tiles[t].pearlSeen != round && !body.empty()) body.pop_back();
            if ((int)k >= gratis && !body.empty()) body.pop_back();
        }
    }
}

void World::updateOwnBody(const RoundBlock& rb) {''')
