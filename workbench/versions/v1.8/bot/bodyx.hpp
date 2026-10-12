#pragma once
#include <algorithm>
#include <cstdint>
#include <deque>

namespace seed0 {
template <bool Enabled> struct BodyTransition123T {
    std::deque<int> body;
    int gratis, steps = 0, removed = 0, pearls = 0;
    explicit BodyTransition123T(const std::deque<int>& initial, int length)
        : body(initial), gratis((length + 3) / 4) {}
    char check(int tile) const {
        if (steps >= gratis && body.size() <= 2) return 'A';
        if (tile < 0) return 'W';
        if (std::find(body.begin(), body.end(), tile) != body.end()) return 'S';
        return 0;
    }
    char advance(int tile, bool eat) {
        if (char reason = check(tile)) return reason;
        body.push_front(tile);
        if (eat) pearls++;
        else { body.pop_back(); removed++; }
        if (steps >= gratis) { body.pop_back(); removed++; }
        steps++;
        return 0;
    }
};
using BodyTransition123 = BodyTransition123T<true>;
template <typename Body> uint32_t bodyHash123(const Body& body) {
    uint32_t hash = 2166136261u;
    for (int t : body) hash = (hash ^ static_cast<uint32_t>(t)) * 16777619u;
    return hash;
}
}
