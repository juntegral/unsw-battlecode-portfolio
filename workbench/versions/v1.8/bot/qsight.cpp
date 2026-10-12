#include "world.hpp"

namespace seed0 {
static constexpr uint64_t SIGHT_MAGIC = 0x21;
static constexpr uint64_t SIGHT_WHITEN = 0x9E3779B97F4A7C15ull;
static uint8_t sightChecksum(uint64_t v) {
    uint8_t crc = 0x93;
    for (int shift = 8; shift < 64; shift += 8) {
        crc ^= (v >> shift) & 255;
        for (int bit = 0; bit < 8; bit++) crc = (crc << 1) ^ ((crc & 128) ? 7 : 0);
    }
    return crc;
}

uint64_t World::encodeHeadSighting(const HeadSighting& s) const {
    if constexpr (P::Q2SIGHT_ON) {
        const uint64_t sender = myId & 2047, enemy = s.enemy & 2047, rnd = s.round & 127;
        const uint64_t x = s.t % geo.W, y = s.t / geo.W, len = std::clamp(s.len, 2, 127), team = myTeam == 'B';
        const uint64_t v = (SIGHT_MAGIC << 58) | (sender << 47) | (enemy << 36) | (rnd << 29) | (x << 23) | (y << 17) | (len << 10) | (team << 9);
        return (v | sightChecksum(v)) ^ SIGHT_WHITEN;
    }
    return 0;
}

bool World::decodeHeadSighting(uint64_t v, HeadSighting& s) const {
    if constexpr (P::Q2SIGHT_ON) {
        v ^= SIGHT_WHITEN;
        if (v >> 58 != SIGHT_MAGIC || (v & 256)) return false;
        const uint64_t sender = (v >> 47) & 2047, enemy = (v >> 36) & 2047, rnd = (v >> 29) & 127;
        const uint64_t x = (v >> 23) & 63, y = (v >> 17) & 63, len = (v >> 10) & 127, team = (v >> 9) & 1;
        const int age = ((round & 127) - (int)rnd + 128) & 127;
        if ((v & 255) != sightChecksum(v) || (team != (myTeam == 'B')) || sender <= 1 || sender == enemy ||
            x >= (uint64_t)geo.W || y >= (uint64_t)geo.H || len < 2 || age > P::Q2SIGHT_TTL || round - age < 0) return false;
        auto source = dragons.find((int)sender), target = dragons.find((int)enemy);
        if (source != dragons.end() && source->second.lastSeen >= 0 && source->second.team != myTeam) return false;
        if (target != dragons.end() && target->second.lastSeen >= 0 && target->second.team == myTeam) return false;
        s = {(int)sender, (int)enemy, round - age, geo.idx((int)x, (int)y), (int)len};
        return true;
    }
    return false;
}

bool World::headSightingToSend(HeadSighting& s, int& queenT) const {
    if constexpr (P::Q2SIGHT_ON) {
        s = {};
        if (myId <= 1 || !parsedOk || enemyHeadsNow.empty() || myId > 2047 || geo.W > 64 || geo.H > 64) return false;
        const Dragon* queen = nullptr;
        for (int id = 0; id <= 1; id++) {
            auto it = dragons.find(id);
            if (it != dragons.end() && it->second.team == myTeam && it->second.headT >= 0 && it->second.headSeen >= 0 && round - it->second.headSeen <= P::BELIEF_FRESH) queen = &it->second;
        }
        if (!queen) return false;
        queenT = queen->headT;
        std::vector<int> distance(geo.tiles(), -1), queue{queenT};
        distance[queenT] = 0;
        for (size_t i = 0; i < queue.size(); i++) for (int dir = 0; dir < 4; dir++) {
            const int u = across(queue[i], dir);
            if (u < 0 || distance[u] >= 0) continue;
            distance[u] = distance[queue[i]] + 1; queue.push_back(u);
        }
        int best = 1000000;
        for (int id : enemyHeadsNow) {
            if (id > 2047) continue;
            const Dragon& d = dragons.at(id);
            const int len = std::max(d.estLen, d.minLen), dist = distance[d.headT] < 0 ? 100000 : distance[d.headT];
            if (len < P::Q2SIGHT_MIN_LEN && dist > P::reach123(len)) continue;
            const int urgency = dist - P::reach123(len);
            if (s.enemy < 0 || urgency < best || (urgency == best && (len > s.len || (len == s.len && id < s.enemy)))) {
                best = urgency; s = {myId, id, round, d.headT, len};
            }
        }
        return s.enemy >= 0;
    }
    return false;
}

int World::headSightingRay(int from, int facing, int queenT) const {
    if constexpr (P::Q2SIGHT_ON) {
        int bestDir = -1, best = 1000000;
        for (int dir = 0; dir < 4; dir++) {
            int t = from, score = 1000000;
            for (int k = 1; k <= geo.W + geo.H; k++) {
                t = across(t, dir);
                if (t < 0 || t == from) break;
                if (k == 1) score = geo.manhattan(t, queenT) * 4 + (dir == opp(facing) ? 2 : 0);
                const int id = headOf[t];
                if (t == queenT || (id >= 0 && id <= 1 && dragons.count(id) && dragons.at(id).team == myTeam)) { score = -10000 + k; break; }
                bool queenBody = false;
                for (int q = 0; q <= 1; q++) {
                    auto it = dragons.find(q);
                    if (it != dragons.end() && it->second.team == myTeam && it->second.headSeen == round &&
                        std::find(it->second.chain.begin(), it->second.chain.end(), t) != it->second.chain.end()) queenBody = true;
                }
                if (queenBody) { score = -10000 + k; break; }
                if (occNow[t] == 2 || occNow[t] == 3) { if (score >= 0) score += 20000; break; }
            }
            if (score < best) { best = score; bestDir = dir; }
        }
        return bestDir;
    }
    return -1;
}

void World::buildSightingPrice() {
    if constexpr (P::Q2SIGHT_ON) {
        if (myId > 1) return;
        auto& heads = q2Sight.heads();
        heads.erase(std::remove_if(heads.begin(), heads.end(), [&](const HeadSighting& s) { return round - s.round > P::Q2SIGHT_TTL; }), heads.end());
        auto& price = q2Sight.price();
        price.assign(geo.tiles(), 0.0);
        std::vector<int> dist(geo.tiles()), queue;
        queue.reserve(geo.tiles());
        for (const auto& s : heads) {
            if (std::find(enemyHeadsNow.begin(), enemyHeadsNow.end(), s.enemy) != enemyHeadsNow.end()) continue;
            const int age = round - s.round, free = P::freeSteps123(s.len) * (age + 1), reach = free + s.len - 2;
            std::fill(dist.begin(), dist.end(), -1); queue.clear();
            dist[s.t] = 0; queue.push_back(s.t);
            for (size_t i = 0; i < queue.size(); i++) {
                const int t = queue[i], d = dist[t];
                price[t] = std::max(price[t], P::QUEEN_THREAT_MULT * (d <= free ? P::T3 : P::T4));
                if (d >= reach) continue;
                for (int dir = 0; dir < 4; dir++) {
                    const int u = across(t, dir);
                    if (u < 0 || dist[u] >= 0) continue;
                    dist[u] = d + 1; queue.push_back(u);
                }
            }
        }
    }
}

double World::sightingPrice(int t) const {
    if constexpr (P::Q2SIGHT_ON) return t >= 0 && t < (int)q2Sight.price().size() ? q2Sight.price()[t] : 0.0;
    return 0.0;
}
}
