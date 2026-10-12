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
        else { planner.setConfig(&policy.config()); a = planner.decide(); }   // FORTRESS_CONFIG values; v1 5b rows add econW4
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
                    int eat = 0; for (int u : a.path) if (world.tiles[u].pearlSeen == world.round) eat++;
                    rl += eat - ((int)a.dirs.size() - 1);
                }
                msg = world.encodeMsg(a.hotT, rt, rl);
            } else msg = world.encodeMsg(a.hotT);
            if (a.sonarAll) { for (int d = 0; d < 4; d++) writer.sonar(d, msg); lastSonarDir = -2; } // several rays: no attribution
            else { writer.sonar(a.sonarDir, msg); lastSonarDir = a.sonarDir; lastSonarFrom = a.sonarFromT; }
        }
        // cand-mapid: the map recognition tag (" map=<Name>/<a|b|?>", " map=?", " map=none") on this process's first turn
        // and whenever its recognition changes (a split child decides later, or a contradiction turns a decision into none)
        if (P::MAPID_TAG) {
            int st = world.mapStateCode();
            if (st != world.mapTagState) { a.indicator += (a.indicator.empty() ? "" : " ") + world.mapTag(); world.mapTagState = st; }
        }
        // unsw-swarm v0: the engine that decided this turn, once per turn, after every other label (v1: the config's tag; 'S' also in the
        // SWARM_AS_FORTRESS identity build)
        if (P::ENGINE_TAG) { a.indicator += a.indicator.empty() ? "E=" : " E="; a.indicator += row.engine == Engine::SWARM ? 'S' : policy.config().tag; }   // v1: 'W' = 5b
        if (P::INDICATOR && !a.indicator.empty()) writer.indicator(a.indicator);
        writer.endTurn();
    }
    return 0;
}
