#pragma once

#include "helper.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <optional>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace heuristic {

using namespace unswbc;

struct EdgeKey {
    bool horizontal;
    int x;
    int y;
    constexpr bool operator==(EdgeKey const&) const = default;
};

class PortalMemory {
  public:
    void observe(Controller const& ct) {
        for (Tile const& tile : ct.get_tiles()) {
            for (Direction direction : Direction::get_direction_list()) {
                Edge const& edge = tile.get_edge(direction);
                if (!edge.is_portal())
                    continue;
                auto& known = portals_[edge.get_portal_id()];
                EdgeKey const key = edge_key(tile.get_position(), direction);
                if (std::find(known.begin(), known.end(), key) == known.end())
                    known.push_back(key);
            }
        }
    }

    std::optional<Position> exit_for(Controller const& ct, Direction direction) const {
        Tile const* here = ct.get_tile(ct.get_position());
        if (!here)
            return std::nullopt;
        Edge const& edge = here->get_edge(direction);
        if (!edge.is_portal())
            return ct.get_position().add_dir(direction);

        EdgeKey const entry = edge_key(ct.get_position(), direction);
        auto const found = portals_.find(edge.get_portal_id());
        if (found == portals_.end() || found->second.size() != 2)
            return std::nullopt;
        auto const partner = std::find_if(found->second.begin(), found->second.end(),
                                          [&](EdgeKey const& key) { return key != entry; });
        if (partner == found->second.end() || partner->horizontal != entry.horizontal)
            return std::nullopt;
        return beyond(*partner, direction);
    }

  private:
    std::unordered_map<int, std::vector<EdgeKey>> portals_;

    static EdgeKey edge_key(Position position, Direction direction) {
        auto const [width, height] = game->get_map_size();
        switch (direction.value) {
        case Direction::NORTH: return {true, position.x, position.y};
        case Direction::EAST:  return {false, wrap(position.x + 1, width), position.y};
        case Direction::SOUTH: return {true, position.x, wrap(position.y + 1, height)};
        default:               return {false, position.x, position.y};
        }
    }

    static int wrap(int value, int size) {
        return (value % size + size) % size;
    }

    static Position beyond(EdgeKey edge, Direction direction) {
        auto const [width, height] = game->get_map_size();
        switch (direction.value) {
        case Direction::NORTH: return {edge.x, wrap(edge.y - 1, height)};
        case Direction::EAST:  return {wrap(edge.x, width), edge.y};
        case Direction::SOUTH: return {edge.x, wrap(edge.y, height)};
        default:               return {wrap(edge.x - 1, width), edge.y};
        }
    }
};

struct Candidate {
    Direction direction;
    std::optional<Position> destination;
    int score;
};

inline std::array<Direction, 4> h1_order(Direction facing) {
    return {facing, facing.get_left(), facing.get_right(), facing.get_opposite()};
}

inline std::array<Direction, 4> h2_order(Direction facing) {
    return {facing.get_right(), facing, facing.get_left(), facing.get_opposite()};
}

inline Candidate base_candidate(Controller const& ct, PortalMemory const& portals,
                                Direction direction, int preference) {
    Candidate candidate{direction, std::nullopt, preference};
    Tile const* here = ct.get_tile(ct.get_position());
    if (!here)
        return candidate;

    Edge const& edge = here->get_edge(direction);
    if (!edge.is_passable()) {
        candidate.score -= 10000;
        return candidate;
    }

    candidate.destination = portals.exit_for(ct, direction);
    if (!candidate.destination) {
        candidate.score -= 300;
        return candidate;
    }

    Tile const* destination = ct.get_tile(*candidate.destination);
    if (!destination) {
        candidate.score -= 80;
        return candidate;
    }

    DragonPart const* dragon = destination->get_dragon();
    if (!dragon) {
        candidate.score += 100;
    } else if (!dragon->is_head()) {
        candidate.score -= 9000;
    } else if (dragon->get_team() == ct.get_team()) {
        candidate.score -= 8000;
    } else {
        candidate.score -= 40;
    }
    return candidate;
}

inline int visible_escape_space(Controller const& ct, Position start) {
    Tile const* first = ct.get_tile(start);
    if (!first || first->get_dragon())
        return 0;

    std::queue<Position> pending;
    std::unordered_set<Position, PositionHash> seen;
    pending.push(start);
    seen.insert(start);
    while (!pending.empty()) {
        Position const position = pending.front();
        pending.pop();
        Tile const* tile = ct.get_tile(position);
        if (!tile)
            continue;
        for (Direction direction : Direction::get_direction_list()) {
            Edge const& edge = tile->get_edge(direction);
            if (!edge.is_passable() || edge.is_portal())
                continue;
            Position const next = position.add_dir(direction);
            Tile const* next_tile = ct.get_tile(next);
            if (!next_tile || next_tile->get_dragon() || seen.contains(next))
                continue;
            seen.insert(next);
            pending.push(next);
        }
    }
    return static_cast<int>(seen.size());
}

inline Direction choose_h1(Controller const& ct, PortalMemory const& portals) {
    auto const order = h1_order(ct.get_dir());
    Candidate best{order.front(), std::nullopt, std::numeric_limits<int>::min()};
    for (int index = 0; index < 4; ++index) {
        Candidate candidate = base_candidate(ct, portals, order[index], 12 - index * 3);
        if (candidate.score > best.score)
            best = candidate;
    }
    return best.direction;
}

inline Direction choose_h2(Controller const& ct, PortalMemory const& portals) {
    auto const order = h2_order(ct.get_dir());
    Candidate best{order.front(), std::nullopt, std::numeric_limits<int>::min()};
    for (int index = 0; index < 4; ++index) {
        Candidate candidate = base_candidate(ct, portals, order[index], 12 - index * 3);
        if (candidate.destination) {
            if (Tile const* tile = ct.get_tile(*candidate.destination)) {
                if (tile->has_pearl())
                    candidate.score += 90;
                int const countdown = tile->get_pearl_time();
                if (countdown > 0 && countdown <= 4)
                    candidate.score += (5 - countdown) * 4;
                candidate.score += std::min(20, visible_escape_space(ct, *candidate.destination)) * 3;
            }
        }
        if (candidate.score > best.score)
            best = candidate;
    }
    return best.direction;
}

} // namespace heuristic
