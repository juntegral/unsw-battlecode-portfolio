"""qmate-opus: add QUEEN_ROOM_MATES (off by default) to the work copy."""
p = '~/meow-redteam/solo/src/w-qmate/main.cpp'
s = open(p).read()
a = 'constexpr bool MATE_UNPIN = false;\n'
assert s.count(a) == 1
s = s.replace(a, a + 'constexpr bool QUEEN_ROOM_MATES = false;\n')
fn = '''    void keep_queen_room() {
        if (QUEEN_ROOM_MATES) {
            if (ct.get_id() <= 1 || turn_split != 0 || act_dirs.empty()) {
                return;
            }
            Position queen;
            int queen_seen = -1;
            for (auto const& tile : ct.get_tiles()) {
                auto const* part = tile.get_dragon();
                if (part && part->is_head() && part->get_team() == ct.get_team() && part->get_id() <= 1) {
                    queen = tile.get_position();
                    queen_seen = part->get_id();
                }
            }
            if (queen_seen < 0) {
                return;
            }
            int end = index_of(ct.get_position());
            for (Direction const direction : act_dirs) {
                end = step_index(position_of(end), direction);
                if (end < 0) {
                    return;
                }
            }
            bool beside = false;
            int room = 0;
            std::array<int, 4> sides{};
            int count = 0;
            for (Direction const direction : Direction::get_direction_list()) {
                int const next = step_index(queen, direction);
                sides[count++] = next;
                if (next < 0) {
                    continue;
                }
                beside = beside || next == end;
                auto const* tile = ct.get_tile(position_of(next));
                if (next != end && !(tile && tile->get_dragon())) {
                    room++;
                }
            }
            if (!beside || room >= 2) {
                return;
            }
            double best_score = SCORE_REJECT;
            int best = -1;
            auto const directions = Direction::get_direction_list();
            for (std::size_t k = 0; k < directions.size(); k++) {
                int const next = step_index(ct.get_position(), directions[k]);
                if (next < 0 || std::find(sides.begin(), sides.end(), next) != sides.end()) {
                    continue;
                }
                auto const* tile = ct.get_tile(position_of(next));
                if (!tile || tile->get_dragon()) {
                    continue;
                }
                double const score = score_step(position_of(next));
                if (score > best_score) {
                    best_score = score;
                    best = static_cast<int>(k);
                }
            }
            if (best < 0) {
                return;
            }
            turn_split = 0;
            act_dirs.assign(1, directions[best]);
            remember_path(act_dirs);
            ct.make_moves(act_dirs);
            ct.output_log("QROOM", round, ct.get_id(), room);
        }
    }

'''
a = '    Unpin* unpin_state() const {\n'
assert s.count(a) == 1
s = s.replace(a, fn + a)
a = '''            if (QUEEN_EXIT_STRICT) {
                keep_queen_exit(true);
            }
            if (QUEEN_CORRIDOR_GUARD > 0) {
                guard_queen_corridor();
            }
'''
print(s.count(a))
s = s.replace(a, a.replace('            if (QUEEN_CORRIDOR_GUARD', '            if (QUEEN_ROOM_MATES) {\n                keep_queen_room();\n            }\n            if (QUEEN_CORRIDOR_GUARD'))
a = '''        if (QUEEN_EXIT_STRICT) {
            keep_queen_exit(true);
        }
        if (QUEEN_CORRIDOR_GUARD > 0) {
            guard_queen_corridor();
        }
'''
print(s.count(a))
s = s.replace(a, a.replace('        if (QUEEN_CORRIDOR_GUARD', '        if (QUEEN_ROOM_MATES) {\n            keep_queen_room();\n        }\n        if (QUEEN_CORRIDOR_GUARD'))
a = '''            keep_queen_exit(true);
        }
        if (QUEEN_CORRIDOR_GUARD > 0) {
            head = ct.get_position();
'''
print(s.count(a))
s = s.replace(a, a.replace('        if (QUEEN_CORRIDOR_GUARD', '        if (QUEEN_ROOM_MATES) {\n            keep_queen_room();\n        }\n        if (QUEEN_CORRIDOR_GUARD'))
open(p, 'w').write(s)
