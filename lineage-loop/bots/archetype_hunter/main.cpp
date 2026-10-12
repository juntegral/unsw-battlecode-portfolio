#define ARCH_HUNTER 1 // generated from bots/archetype_swarm/main.cpp; edit that file, then regenerate
// Archetype practice opponent (never submitted): imitates online opponents observed in v5 games
// (experiments/archetypes/opponent-profile-dev.json, 171 dev games).
//   SWARM  : split off a 2-segment child at the per-action rates observed online below the unit limit (by team
//            unit count and length; parent length is mostly 4, a length-4 dragon splits on 10-20% of its actions); forage the nearest visible pearl; avoid cells next to other heads and pockets smaller than us.
//   HUNTER : SWARM plus ramming: a visible enemy head whose SEEN length is >= 1.5x ours (seen length under-counts
//            bodies leaving the view) reachable within 2 steps (3 if >= 2.5x) through free cells is rammed.
// Written from scratch (no replay-rules code) so it is not a lineage copy of our bot.
// Simplifications: portals are treated as walls; our own tail counts as occupied.
#include "helper.hpp"
#include <algorithm>
#include <map>
#include <queue>

#ifndef ARCH_HUNTER
#define ARCH_HUNTER 0
#endif

namespace arch {
using namespace unswbc;
constexpr char DIRS[4] = {'N', 'E', 'S', 'W'};

struct View {
    std::map<std::pair<int, int>, Tile const*> tiles;
    Tile const* at(Position p) const {
        auto it = tiles.find({p.x, p.y});
        return it == tiles.end() ? nullptr : it->second;
    }
};

// Destination one step from p in direction d, or nullopt if blocked (kelp, portal, outside view, occupied).
std::optional<Position> step(View const& v, Position p, int d, Position const* allow = nullptr) {
    Tile const* here = v.at(p);
    if (!here) return std::nullopt;
    Edge const& e = here->get_edge(Direction(DIRS[d]));
    if (!e.is_passable() || e.is_portal()) return std::nullopt;
    Position q = p.add_dir(Direction(DIRS[d]));
    Tile const* t = v.at(q);
    if (!t) return std::nullopt;
    if (t->get_dragon() && !(allow && allow->x == q.x && allow->y == q.y)) return std::nullopt;
    return q;
}

// Free cells reachable from start (inside the view), capped.
int area(View const& v, Position start, int cap) {
    std::queue<Position> q;
    std::map<std::pair<int, int>, bool> seen;
    q.push(start);
    seen[{start.x, start.y}] = true;
    int n = 1;
    while (!q.empty() && n < cap) {
        Position p = q.front(); q.pop();
        for (int d = 0; d < 4; d++) {
            auto r = step(v, p, d);
            if (!r || seen[{r->x, r->y}]) continue;
            seen[{r->x, r->y}] = true;
            q.push(*r);
            n++;
        }
    }
    return n;
}

// Shortest path (first moves) from start to target through free cells; target may be occupied (a head).
std::vector<int> path_to(View const& v, Position start, Position target, int max_len) {
    std::map<std::pair<int, int>, std::pair<std::pair<int, int>, int>> parent; // cell -> (prev, dir)
    std::queue<std::pair<Position, int>> q;
    q.push({start, 0});
    parent[{start.x, start.y}] = {{start.x, start.y}, -1};
    while (!q.empty()) {
        auto [p, dist] = q.front(); q.pop();
        if (p.x == target.x && p.y == target.y) {
            std::vector<int> dirs;
            std::pair<int, int> cur{p.x, p.y};
            while (parent[cur].second >= 0) { dirs.push_back(parent[cur].second); cur = parent[cur].first; }
            std::reverse(dirs.begin(), dirs.end());
            return dirs;
        }
        if (dist >= max_len) continue;
        for (int d = 0; d < 4; d++) {
            auto r = step(v, p, d, &target);
            if (!r || parent.count({r->x, r->y})) continue;
            parent[{r->x, r->y}] = {{p.x, p.y}, d};
            q.push({*r, dist + 1});
        }
    }
    return {};
}

void play(Controller& ct) {
    View v;
    for (auto const& t : ct.get_tiles()) v.tiles[{t.get_position().x, t.get_position().y}] = &t;
    Position head = ct.get_position();
    int len = ct.get_length();
    char team = ct.get_team().value;

    // Enemy heads and their seen lengths; every other head (allies too) is a collision risk.
    std::map<int, int> seen_len;
    std::vector<std::pair<Position, int>> enemy_heads; // position, id
    std::vector<Position> other_heads;
    for (auto const& t : ct.get_tiles())
        if (auto part = t.get_dragon()) {
            if (part->is_head() && part->get_id() != ct.get_id()) other_heads.push_back(t.get_position());
            if (part->get_team().value != team) {
                seen_len[part->get_id()]++;
                if (part->is_head()) enemy_heads.push_back({t.get_position(), part->get_id()});
            }
        }

    bool enemy_near = false;
    for (auto const& [pos, id] : enemy_heads) {
        int dx = std::abs(pos.x - head.x), dy = std::abs(pos.y - head.y);
        if (std::max(dx, dy) <= 3) enemy_near = true;
    }

#if ARCH_HUNTER
    // Ram a much bigger head within sprint reach.
    std::vector<int> best_ram;
    for (auto const& [pos, id] : enemy_heads) {
        int other = seen_len[id];
        int reach = 2 * other >= 5 * len ? 3 : 2 * other >= 3 * len ? 2 : 0;
        reach = std::min(reach, len - 1); // an n-step sprint needs length > n
        if (reach <= 0) continue;
        auto p = path_to(v, head, pos, reach);
        if (!p.empty() && (best_ram.empty() || p.size() < best_ram.size())) best_ram = p;
    }
    if (!best_ram.empty()) {
        std::vector<Direction> moves;
        for (int d : best_ram) moves.emplace_back(DIRS[d]);
        ct.make_moves(moves);
        return;
    }
#endif

    // Swarm: split at the per-action rate observed online BELOW the unit limit (at the limit nobody can split,
    // which is how their leaders grow late), by team unit count and length (v5 dev games, swarm + hunter
    // groups, 69 games). Deterministic pseudo-random draw from (dragon id, round) for reproducibility.
    if (len >= 4 && ct.can_split(2)) {
        static constexpr double RATE[3][3] = { // [units <30, 30-57, 58+][length 4, 5-7, 8+]
            {.199, .051, .024}, {.134, .057, .035}, {.103, .031, .024}};
        int round = unswbc::game->get_round_num();
        int units = ct.get_unit_count();
        double p = RATE[units < 30 ? 0 : units < 58 ? 1 : 2][len == 4 ? 0 : len <= 7 ? 1 : 2];
        unsigned h = unsigned(ct.get_id()) * 2654435761u ^ unsigned(round) * 40503u;
        h ^= h >> 15; h *= 2246822519u; h ^= h >> 13;
        if ((h % 10000) / 10000.0 < p) {
            ct.do_split(2);
            return;
        }
    }
    (void)enemy_near;

    // Forage: nearest visible pearl, avoiding pockets smaller than us and cells next to enemy heads.
    int best_dir = -1;
    long best_score = -1000000000;
    for (int d = 0; d < 4; d++) {
        auto q = step(v, head, d);
        if (!q) continue;
        int room = area(v, *q, len + 2);
        bool next_to_head = false;
        for (auto const& pos : other_heads)
            if (std::abs(pos.x - q->x) + std::abs(pos.y - q->y) == 1) next_to_head = true;
        int exits = 0;
        for (int e = 0; e < 4; e++) exits += step(v, *q, e).has_value() ? 1 : 0;
        int pearl_dist = 99;
        for (auto const& t : ct.get_tiles()) {
            if (!t.has_pearl()) continue;
            if (t.get_position().x == q->x && t.get_position().y == q->y) { pearl_dist = 0; break; }
            auto p = path_to(v, *q, t.get_position(), 8);
            if (!p.empty()) pearl_dist = std::min<int>(pearl_dist, p.size());
        }
        long score = 0;
        score += room >= len ? 100000 : room * 1000;
        score -= next_to_head ? 50000 : 0;
        score += 300 * std::min(exits, 3);
        score -= pearl_dist * 100;
        score += Direction(DIRS[d]).value == ct.get_dir().value ? 5 : 0; // keep heading when tied
        score -= d;                                                    // deterministic tie break
        if (score > best_score) { best_score = score; best_dir = d; }
    }
    if (best_dir < 0) best_dir = std::find(DIRS, DIRS + 4, ct.get_dir().value) - DIRS; // no legal move
    ct.make_move(Direction(DIRS[best_dir]));
}
}

int main() {
    unswbc::init();
    while (unswbc::update(*unswbc::ct, *unswbc::game)) {
        arch::play(*unswbc::ct);
        unswbc::end_turn();
    }
    return 0;
}
