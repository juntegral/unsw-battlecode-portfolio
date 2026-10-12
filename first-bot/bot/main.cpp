// main.cpp — seed0: read init, then loop turns until EOF. Every turn emits a safe fallback MOVE, the
// intended action (last one wins), optional sonar, PROTOCOL 3 and ENDTURN in a single write.
#include <cstdio>
#include <string>

#include "params.hpp"
#include "plan.hpp"
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
    Planner planner(world);
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
            world.probeFromT = lastSonarFrom; // the ray left our head as it stood after last turn's action
        }
        Action a = planner.decide();
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
            uint64_t msg = a.relayId >= 0 ? world.encodeKingMsg(a.relayId, a.relayRound, a.relayT, a.relayLen) : world.encodeMsg(a.hotT);
            if (a.sonarAll) { for (int d = 0; d < 4; d++) writer.sonar(d, msg); lastSonarDir = -2; } // several rays: no attribution
            else { writer.sonar(a.sonarDir, msg); lastSonarDir = a.sonarDir; lastSonarFrom = a.sonarFromT; }
        }
        if (P::INDICATOR && !a.indicator.empty()) writer.indicator(a.indicator);
        writer.endTurn();
    }
    return 0;
}
