import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)

rep("constexpr int QUEEN_HOLD_LEN = 0;\n",
    "constexpr int QUEEN_HOLD_LEN = 0;\nconstexpr int QUEEN_DEAD_KNOWN = 0;\nconstexpr bool QDK_TRACE = false;\n")

rep("        qh_in_view = false;\n\n        hear_exact(ct.get_id(), length, round, head, ct.get_dir());",
    "        qh_in_view = false;\n        if (QUEEN_DEAD_KNOWN > 0) {\n            qdk_state().parts.clear();\n        }\n\n        hear_exact(ct.get_id(), length, round, head, ct.get_dir());")

rep("""                    qh_foe_id = part->get_id();
                    if (part->is_head()) {""",
    """                    qh_foe_id = part->get_id();
                    if (QUEEN_DEAD_KNOWN > 0) {
                        qdk_state().parts.push_back(index);
                    }
                    if (part->is_head()) {""")

rep("""        if (!qh_in_view && qh_foe_seen_round == round - 1 && visible_parts(qh_foe_id) == 0 &&
            qh_corpse(qh_foe_seen_pos, qh_foe_seen_clear)) {
            qh_foe_dead_round = round;
        }
""",
    """        int const qdk_was = qh_foe_dead_round;
        if (!qh_in_view && qh_foe_seen_round == round - 1 && visible_parts(qh_foe_id) == 0 &&
            qh_corpse(qh_foe_seen_pos, qh_foe_seen_clear)) {
            qh_foe_dead_round = round;
        }
        if (QUEEN_DEAD_KNOWN > 0) {
            qdk_watch();
        }
        if (QDK_TRACE) {
            qdk_trace(qdk_was);
        }
""")

rep("""                       (QUEEN_HOLD_LEN > 0 && qh_foe_dead() && (round + static_cast<int>(k)) % 2 == 0)) {""",
    """                       (QUEEN_HOLD_LEN > 0 && qh_foe_dead() && (round + static_cast<int>(k)) % 2 == 0) ||
                       (QUEEN_DEAD_KNOWN > 0 && qh_foe_dead() && round - qdk_state().news < QUEEN_DEAD_KNOWN)) {""")

rep("""    struct War {
        std::vector<int> seen;""",
    """    struct Qdk {
        std::vector<int> parts;
        int reach = -1;
        int news = -1;
        bool told = false;
    };

    Qdk& qdk_state() const {
        static Qdk state;
        return state;
    }

    // Every cell within reach steps of from is in view now; counts the pearls there and those about to spawn.
    bool qdk_ball(int from, int reach, int& pearls) const {
        std::vector<int> cells{from};
        std::vector<int> depth{0};
        for (std::size_t q = 0; q < cells.size(); q++) {
            int const cell = cells[q];
            if (seen_round[cell] != round) {
                return false;
            }
            if (pearl_here[cell] != 0 || (pearl_timer[cell] >= 0 && pearl_timer[cell] <= QH_SPAWN_SLACK)) {
                pearls++;
            }
            if (depth[q] >= reach) {
                continue;
            }
            for (Direction const direction : Direction::get_direction_list()) {
                std::uint8_t const edge = edge_at(position_of(cell), direction);
                if (edge == EDGE_KELP) {
                    continue;
                }
                int const next = edge == EDGE_UNKNOWN ? -1 : step_index(position_of(cell), direction);
                if (next < 0) {
                    return false;
                }
                if (std::find(cells.begin(), cells.end(), next) == cells.end()) {
                    cells.push_back(next);
                    depth.push_back(depth[q] + 1);
                }
            }
        }
        return true;
    }

    // QUEEN_DEAD_KNOWN: the most steps her next move can have, or -1 when her whole body is not surely in view.
    int qdk_bound() const {
        int const parts = static_cast<int>(qdk_state().parts.size());
        if (parts < 2 || parts > 3) {
            return -1;
        }
        for (int const cell : qdk_state().parts) {
            if (on_view_edge(position_of(cell))) {
                return -1;
            }
            for (Direction const direction : Direction::get_direction_list()) {
                if (edge_at(position_of(cell), direction) == EDGE_PORTAL) {
                    return -1;
                }
            }
        }
        int const base = parts - 1;
        for (int reach = base; reach <= 2;) {
            int pearls = 0;
            if (!qdk_ball(index_of(qh_pos), reach, pearls)) {
                return -1;
            }
            if (base + pearls <= reach) {
                return reach;
            }
            reach = base + pearls;
        }
        return -1;
    }

    // QUEEN_DEAD_KNOWN: her head was in view last turn; now her cell holds a corpse pearl, or every cell
    // one move could have taken her to is in view without her.
    void qdk_watch() {
        Qdk& state = qdk_state();
        if (!qh_in_view && qh_foe_seen_round == round - 1 && qh_foe_dead_round < round && visible_parts(qh_foe_id) == 0) {
            int const seen = index_of(qh_foe_seen_pos);
            int pearls = 0;
            if (ct.get_id() > 1 && seen_round[seen] == round && pearl_here[seen] != 0) {
                qh_foe_dead_round = round;
                if (QDK_TRACE) {
                    ct.output_log("QDK", "rule-pearl", round, ct.get_id());
                }
            } else if (state.reach >= 0 && qdk_ball(seen, state.reach, pearls)) {
                qh_foe_dead_round = round;
                if (QDK_TRACE) {
                    ct.output_log("QDK", "rule-gone", round, ct.get_id(), state.reach);
                }
            }
        }
        state.reach = qh_in_view ? qdk_bound() : -1;
        if (!qh_foe_dead()) {
            state.news = -1;
        } else if (state.news < 0) {
            state.news = round;
        }
    }

    void qdk_trace(int was) {
        Qdk& state = qdk_state();
        if (qh_foe_dead_round != was) {
            ct.output_log("QDK", "see", round, ct.get_id(), length);
        }
        if (qh_foe_dead() != state.told) {
            state.told = !state.told;
            ct.output_log("QDK", state.told ? "know" : "unknow", round, ct.get_id(), length, real_queen() ? "queen" : "mate",
                          qh_foe_dead_round, qh_round);
        }
    }

    struct War {
        std::vector<int> seen;""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
