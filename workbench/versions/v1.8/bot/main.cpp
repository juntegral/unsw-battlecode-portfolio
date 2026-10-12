// main.cpp — seed0: read init, then loop turns until EOF. Every turn emits a safe fallback MOVE, the
// intended action (last one wins), optional sonar, PROTOCOL 3 and ENDTURN in a single write.
// unsw-swarm v0: the engine layer. Each turn policy.hpp picks the engine from this process's map recognition (after
// ingest), that engine decides, and the indicator ends with " E=F" / " E=S" (ENGINE.md; engine.hpp).
#include <cstdio>
#include <string>

#include "engine.hpp"
#include "params.hpp"
#include "plan.hpp"
#include "policy.hpp"
#include "proto.hpp"
#include "world.hpp"

using namespace seed0;

int main() {
    Reader reader;
    Writer writer;
    InitBlock ib;
    if (!reader.readInit(ib)) return 0;
    World world;
    world.init(ib);
    Planner planner(world);          // FORTRESS: stack11's decision path (plan.cpp, FORTRESS_CONFIG)
    EngineSwarm swarm(planner);      // SWARM: the same planner with the row's swarm configuration (v1)
    PolicySelector policy;           // policy.hpp: the assignment table
    RoundBlock rb;
    int lastSonarDir = -1, lastSonarFrom = -1;
    for (;;) {
        if (!reader.readRound(rb)) break;   // EOF or ENDGAME
        world.ingest(rb);
        // attribute this turn's echoes to the single ray we sent last turn
        if (rb.echoes.present && lastSonarDir >= 0) {
            const Echoes& e = rb.echoes;
            if (e.enemyHead > 0) world.enemyHeadEchoDir[lastSonarDir] = world.round;
            if (e.enemy > 0 || e.enemyHead > 0) world.enemyEchoDir[lastSonarDir] = world.round;
            world.probeDir = lastSonarDir; world.probeRound = world.round;
            world.probeClear = (e.ally + e.allyHead + e.enemy + e.enemyHead) == 0;
            world.probeAlly = (e.ally + e.allyHead) > 0;   // stack8 px2
            world.probeFromT = lastSonarFrom; // the ray left our head as it stood after last turn's action
        }
        const MapPolicy& row = policy.get(world);
        Action a;
        if (row.engine == Engine::SWARM) a = swarm.decide(row, policy.config());
        else { planner.setConfig(&policy.config()); a = planner.decide(); }   // FORTRESS_CONFIG values; v1 5b rows add econW4; exp/portals: the Portals row
        if constexpr (P::Q1C_SIGHT_ON) {
            char note[80];
            snprintf(note, sizeof note, " qc%d,%d,%d,%d", world.enemyQueenBelievedAlive(), world.q1Sight.seen(), world.q1Sight.heard(), world.enemyQueenSeenRecently());
            a.indicator += note;
        }
        if constexpr (P::Q1B_BACKUP_ON) if (P::Q1_ON && P::Q1B_ON && world.round >= P::GATHER_BROADCAST && world.round < P::Q1B_LATE) {
            char note[48];
            snprintf(note, sizeof note, " qbk%d,%d", planner.q1GatherId(), planner.q1KeepTile());
            a.indicator += note;
        }
        // a well-formed fallback first: if the intended line were ever malformed, this one still applies
        if (a.safeDir >= 0) writer.move(std::string(1, DIRCH[a.safeDir]).c_str());
        if (a.kind == Action::SPLIT) {
            bool legal = a.splitSize >= 2 && world.myLen - a.splitSize >= 2 && world.unitCount < world.unitLimit;
            if (legal) writer.split(a.splitSize);
            else if (a.safeDir < 0) writer.move(std::string(1, DIRCH[world.myDir]).c_str());
        } else if (!a.dirs.empty()) {
            writer.move(a.dirs.c_str());
        }
        lastSonarDir = -1; lastSonarFrom = -1;
        if (P::SEND_SONAR && a.sonarDir >= 0) {
            uint64_t msg;
            if (a.relayId >= 0) msg = world.encodeKingMsg(a.relayId, a.relayRound, a.relayT, a.relayLen);
            else if (P::BELIEF_FIX_ON) {
                // v1 belief fix: report the state after this turn's action (the sonar is cast after it): head and length after the move or split
                int rt = world.headT, rl = world.myLen;
                if (a.kind == Action::SPLIT) rl -= a.splitSize;
                else if (!a.path.empty()) {
                    rt = a.path.back();
                    int eat = 0;
                    if constexpr (P::BODYMEM_ON) {
                        for (size_t i = 0; i < a.path.size(); i++) {
                            const int u = a.path[i];
                            if (world.tiles[u].seen == world.round && world.tiles[u].pearlSeen == world.round &&
                                std::find(a.path.begin(), a.path.begin() + i, u) == a.path.begin() + i) eat++;
                        }
                    } else for (int u : a.path) if (world.tiles[u].pearlSeen == world.round) eat++;
                    if constexpr (P::FREECOST_ON || P::BODYMEM_ON) rl += eat - P::paidSteps123(world.myLen, (int)a.dirs.size());
                    else {
                        const bool fs = P::Q2D_FREESTEP_ON || (P::Q2DQ_ON && world.myId <= 1);
                        rl += eat - (fs ? std::max(0, (int)a.dirs.size() - (world.myLen + 3) / 4) : (int)a.dirs.size() - 1);
                    }
                }
                msg = world.encodeMsg(a.hotT, rt, rl);
            } else msg = world.encodeMsg(a.hotT);
            if constexpr (P::Q2SIGHT_ON) {
                HeadSighting sight; int qt = -1;
                int ray = -1;
                if (world.headSightingToSend(sight, qt)) {
                    const int from = a.path.empty() ? world.headT : a.path.back();
                    const int facing = a.dirs.empty() ? world.myDir : dirFromChar(a.dirs.back());
                    ray = world.headSightingRay(from, facing, qt);
                }
                if (ray >= 0) {
                    const uint64_t report = world.encodeHeadSighting(sight);
                    for (int d = 0; d < 4; d++) writer.sonar(d, d == ray ? report : msg);
                    lastSonarDir = -2;
                    char note[112];
                    snprintf(note, sizeof note, " qst%d,%d,%d,%d,%d,%d", sight.enemy, sight.round, sight.t, std::min(sight.len, 127), ray, qt);
                    a.indicator += note;
                } else if (a.sonarAll) { for (int d = 0; d < 4; d++) writer.sonar(d, msg); lastSonarDir = -2; }
                else { writer.sonar(a.sonarDir, msg); lastSonarDir = a.sonarDir; lastSonarFrom = a.sonarFromT; }
            } else {
                if (a.sonarAll) { for (int d = 0; d < 4; d++) writer.sonar(d, msg); lastSonarDir = -2; } // several rays: no attribution
                else { writer.sonar(a.sonarDir, msg); lastSonarDir = a.sonarDir; lastSonarFrom = a.sonarFromT; }
            }
        }
        if constexpr (P::Q2SIGHT_ON) if (world.myId <= 1) {
            char note[112];
            snprintf(note, sizeof note, " qsn%d,%d", world.q2Sight.received(), world.q2Sight.accepted());
            a.indicator += note;
            for (const auto& s : world.q2Sight.heads()) {
                snprintf(note, sizeof note, " qsr%d,%d,%d,%d,%d", s.enemy, s.round, s.t, s.len, s.sender);
                a.indicator += note;
            }
            const double p1 = a.path.empty() ? 0.0 : world.sightingPrice(a.path.front());
            const double p2 = a.path.size() < 2 ? 0.0 : world.sightingPrice(a.path[1]);
            snprintf(note, sizeof note, " qsp%.0f,%.0f", p1, p2);
            a.indicator += note;
        }
        if constexpr (P::BODYMEM_ON) {
            if (a.kind == Action::SPLIT) {
                if (a.splitSize >= 2 && world.myLen - a.splitSize >= 2 && world.unitCount < world.unitLimit) {
                    while ((int)world.body.size() > world.myLen - a.splitSize) world.body.pop_back();
                    world.bodyMemory.history().clear();
                }
            } else if (!a.path.empty() && a.path.size() == a.dirs.size()) world.predictOwnMove(a.path);
        } else if constexpr (P::BODYMEM2_ON) {
            if (a.kind == Action::MOVE && a.path.size() > 1 && a.path.size() == a.dirs.size()) world.predictOwnMove(a.path);
        } else if constexpr (P::FREECOST_ON) {
            if (a.kind == Action::SPLIT) {
                if (a.splitSize >= 2 && world.myLen - a.splitSize >= 2 && world.unitCount < world.unitLimit)
                    while ((int)world.body.size() > world.myLen - a.splitSize) world.body.pop_back();
            } else if (!a.path.empty() && a.path.size() == a.dirs.size()) {
                world.predictOwnMove(a.path);
                uint32_t hash = 2166136261u; int unknown = 0;
                for (int t : world.body) { hash = (hash ^ (uint32_t)t) * 16777619u; if (t < 0) unknown++; }
                char note[96];
                snprintf(note, sizeof note, " fc%d,%d,%d,%d,%u", P::freeSteps123(world.myLen), P::paidSteps123(world.myLen, (int)a.dirs.size()), (int)world.body.size(), unknown, hash);
                a.indicator += note;
            }
        }
        // cand-mapid: the map recognition tag (" map=<Name>/<a|b|?>", " map=?", " map=none") on this process's first turn
        // and whenever its recognition changes (a split child decides later, or a contradiction turns a decision into none)
        if (P::MAPID_TAG) {
            int st = world.mapStateCode();
            if (st != world.mapTagState) { a.indicator += (a.indicator.empty() ? "" : " ") + world.mapTag(); world.mapTagState = st; }
            if (P::MAPID2_ON && world.mapNews) a.indicator += world.takeMapNewsTag();   // v1.6.1: " mg=<family>" " ms<k>" " mn" " mc"
        }
        // unsw-swarm v0: the engine that decided this turn, once per turn, after every other label (v1: the config's tag; 'S' also in the
        // SWARM_AS_FORTRESS identity build)
        if (P::ENGINE_TAG) { a.indicator += a.indicator.empty() ? "E=" : " E="; a.indicator += row.engine == Engine::SWARM ? 'S' : policy.config().tag; }   // v1: 'W' = 5b
        if (P::INDICATOR && !a.indicator.empty()) writer.indicator(a.indicator);
        writer.endTurn();
    }
    return 0;
}
