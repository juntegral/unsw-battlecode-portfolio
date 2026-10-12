import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)

rep("#include <cmath>\n", "#include <cmath>\n#include <cstdio>\n")

rep("""    struct Qdk {
        std::vector<int> parts;
        int reach = -1;""",
    """    struct Qdk {
        std::vector<int> parts;
        std::vector<int> last;
        int reach = -1;""")

a = s.index("    // QUEEN_DEAD_KNOWN: her head was in view last turn; now her cell holds a corpse pearl, or every cell")
b = s.index("    struct War {")
s = s[:a] + """    // QUEEN_DEAD_KNOWN: her head was in view last turn and no part of her is now. Proof 1: she could not have left her
    // cell (two long, nothing to eat) or every cell one move could reach is in view. 2: a corpse pearl lies on her head
    // cell. 3: she stepped once and died, a pearl on the stepped cell and one on her old body.
    void qdk_watch() {
        Qdk& state = qdk_state();
        int const seen = index_of(qh_foe_seen_pos);
        if (!qh_in_view && qh_foe_seen_round == round - 1 && qh_foe_dead_round < round && visible_parts(qh_foe_id) == 0 &&
            seen_round[seen] == round) {
            int pearls = 0;
            int rule = 0;
            if (state.reach >= 0 && ((state.reach == 1 && state.last.size() == 2) || qdk_ball(seen, state.reach, pearls))) {
                rule = 1;
            } else if (ct.get_id() > 1 && pearl_here[seen] != 0) {
                rule = 2;
            } else if (ct.get_id() > 1 && state.last.size() >= 3) {
                int const fresh = qh_ring(qh_foe_seen_pos, true) & qh_foe_seen_clear;
                auto const directions = Direction::get_direction_list();
                bool stepped = false;
                bool body = false;
                for (std::size_t k = 0; k < directions.size(); k++) {
                    int const at = step_index(qh_foe_seen_pos, directions[k]);
                    stepped = stepped || (at >= 0 && (fresh & (1 << k)) != 0 &&
                                          std::find(state.last.begin(), state.last.end(), at) == state.last.end());
                }
                for (int const cell : state.last) {
                    body = body || (cell != seen && seen_round[cell] == round && pearl_here[cell] != 0);
                }
                rule = stepped && body ? 3 : 0;
            }
            if (rule != 0) {
                qh_foe_dead_round = round;
                if (QDK_TRACE) {
                    qdk_log("rule", rule, static_cast<int>(state.last.size()));
                }
            }
        }
        state.reach = qh_in_view ? qdk_bound() : -1;
        state.last = state.parts;
        if (!qh_foe_dead()) {
            state.news = -1;
        } else if (state.news < 0) {
            state.news = round;
        }
    }

    void qdk_log(char const* what, int a, int b) const {
        char const* path = std::getenv("QDK_LOG");
        std::FILE* file = path ? std::fopen(path, "a") : nullptr;
        if (file) {
            std::fprintf(file, "%s %d %d %d %d %d\\n", what, round, ct.get_id(), length, a, b);
            std::fclose(file);
        }
    }

    void qdk_trace(int was) {
        Qdk& state = qdk_state();
        if (qh_foe_dead_round != was) {
            qdk_log("see", qh_foe_dead_round, 0);
        }
        if (qh_foe_dead() != state.told) {
            state.told = !state.told;
            qdk_log(state.told ? (real_queen() ? "knowq" : "know") : "unknow", qh_foe_dead_round, qh_round);
        }
    }

""" + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
