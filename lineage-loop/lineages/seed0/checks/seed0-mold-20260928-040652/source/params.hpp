// params.hpp — every tunable in one place. Later waves adjust these; the seed values are reasoned
// from the rules and the design critique, not measured (see NOTES.md "unverified assumptions").
#pragma once

namespace seed0 { namespace P {

// --- pearl valuation ---
constexpr double GAMMA = 0.88;            // per-step discount on pearl value
constexpr double GAMMA_WAIT = 0.97;       // per-round discount while waiting for a known future spawn
constexpr double PEARL_DECAY = 0.985;     // per-round survival of a seen pearl (someone may eat it)
constexpr double SPAWN_CONF = 0.75;       // P(pearl) right after a predicted spawn we did not witness
constexpr double MIRROR_CONF = 0.80;      // factor applied to knowledge inferred through symmetry
constexpr double PRIOR_UNSEEN = 0.05;     // P(pearl) on a never-seen tile before any statistics
constexpr int    FOUNTAIN_MAX_GAP = 12;   // max reset-sample gap to call a tile a fountain
constexpr double FOUNTAIN_VALUE = 0.9;    // steady-state value of a fountain tile as a source
constexpr int    MAX_SOURCES = 20;        // per-turn cap on attract-field sources (CPU)
constexpr int    ATTRACT_RADIUS = 16;     // BFS radius per source
constexpr int    FUTURE_SPAWN_HORIZON = 120; // known spawns this far ahead still count as sources
constexpr double CONTEST_ENEMY_CLOSER = 0.15, CONTEST_ENEMY_ONE_CLOSER = 0.3, CONTEST_EQUAL = 0.9;
constexpr double CONTEST_ALLY_CLOSER = 0.15;
constexpr double EXPLORE_W = 0.35;        // value of revealing an unseen tile, times the map's pearl prior
constexpr double BLOCK_SPAWN_PENALTY = 0.5; // ending a turn on a tile whose spawn tick is next round

// --- safety ---
constexpr double AREA_TRAP_PENALTY = 60.0;  // reachable area < length + margin
constexpr int    AREA_MARGIN = 2;
constexpr double AREA_BONUS_PER_TILE = 0.04; // mild preference for open space (capped)
constexpr int    AREA_CAP_EXTRA = 16;        // flood-fill cap = max(2*len + this, AREA_CAP_MIN)
constexpr int    AREA_CAP_MIN = 96;
constexpr double AREA_DEADEND_PENALTY = 8.0;  // bounded region with no cycle that ends before round 500
constexpr double AREA_ROOM_PENALTY = 0.5;     // bounded region that has a cycle (a room we can circle in)
constexpr double AREA_FILL_PENALTY = 3.0;     // per tile by which the room we need exceeds the region
constexpr double AREA_FILL_RATIO = 1.5;       // room needed = ratio * len + AREA_FILL_MARGIN
constexpr int    AREA_FILL_MARGIN = 4;
constexpr double TAIL_REACH_BONUS = 1.5;
constexpr double HEAD_PATH_PENALTY = 1.5;    // tiles straight ahead of another dragon's head (k=1..3)
constexpr double PORTAL_STALE_PENALTY = 3.0; // known portal exit not seen recently (scaled by staleness/20 rounds)
constexpr double PORTAL_TIGHT_PENALTY = 2.0; // known portal exit with <= 1 free neighbour
constexpr double PORTAL_BLIND_PENALTY = 1.0; // exit tile not in view now: a head may have moved there
constexpr double PORTAL_HEAD_NEAR_PENALTY = 8.0; // a head (any team) was seen within 2 of the unseen exit recently
constexpr double PORTAL_GAMBLE_VALUE = 1.0;  // entering an unknown portal after a clean sonar probe
constexpr double DOOM_VALUE = -200.0;        // below this the best move is death within the horizon

// --- threat from enemy heads (d = path distance from the enemy head to the tile) ---
constexpr double T1 = 30.0;                        // adjacent: they can trade at will
constexpr double T2 = 24.0, T3 = 15.0, T4 = 9.0;   // sprint reach (needs Le >= d+1): the opponent decides the trade
constexpr double TRADE_BAD_FOR_THEM = 0.45;        // multiplier when the trade would favour us
constexpr double T_FAR_BAD_FOR_THEM = 0.2;         // same, at d >= 2
constexpr double PSEUDO_HEAD_MULT = 0.5;           // a higher-id enemy's tail may become a child head this round
constexpr double ENDGAME_THREAT_MULT = 2.0;        // last 30 rounds, when we are ahead on longest
constexpr double KING_THREAT_MULT = 1.5;           // the team's longest dragon (>= KING_MIN_LEN) is worth protecting
constexpr int    KING_MIN_LEN = 8;
constexpr int    ENDGAME_ROUNDS = 30;
constexpr double ECHO_LINE_PENALTY = 1.2;          // tiles on a line where sonar echoed an enemy head
constexpr int    ECHO_LINE_RANGE = 6;
constexpr int    ENEMY_MEMORY_ROUNDS = 8;          // remember an unseen enemy head this long

// --- trades (head-to-head) ---
constexpr double W_KILL = 4.0;            // reward per length difference when we trade up
constexpr int    KILL_MIN_DIFF = 3;
constexpr double KILL_MIN_RATIO = 2.0;
constexpr int    HUNT_MAX_LEN = 5;         // dragons this short are opportunistic hunters
constexpr double W_HUNT = 0.6;
constexpr double W_ESCORT = 0.08;          // per unit of the protected teammate's length
constexpr int    STRIKE_MAX_STEPS = 4;     // longest kill path searched (needs length >= steps + 1)
constexpr int    ENDGAME_ANY_TRADE_ROUND = 495; // from here a non-king trades into anything longer

// --- split policy ---
constexpr int SPLIT_LAST_ROUND = 450;
constexpr int SPLIT_FIRST_LEN = 5;         // insurance split when unit_count == 1
constexpr int SPLIT_FIRST_CHILD = 2;
constexpr int SPLIT_LEN = 8;               // later splits
constexpr int SPLIT_CHILD = 3;
constexpr int SPLIT_CAP_BASE = 3;          // further limited by map size: tiles/60 (base), tiles/50 (rich)
constexpr int SPLIT_CAP_RICH = 5;
constexpr int SPLIT_SMALL_MAP_TILES = 300; // below this, only dragons of SPLIT_LEN or more split at all
constexpr int SPLIT_MIN_CHILD_EXITS = 2;

// --- search / budget ---
constexpr int    DFS_DEPTH_MAX = 7;
constexpr int    DFS_DEPTH_MIN = 3;
constexpr long long DFS_NODE_BUDGET = 40000;   // deterministic primary limiter
constexpr long long POINTS_SOFT = 16'000'000;  // steady_clock ns == points in the judge
constexpr long long POINTS_HARD = 26'000'000;
constexpr double SPRINT_COST = 1.6;            // value of one lost segment
constexpr double UNKNOWN_EDGE_PENALTY = 0.3;   // stepping across an edge we have never seen
constexpr double JITTER = 0.002;               // deterministic per-dragon tie-break noise

// --- sonar ---
constexpr bool SEND_SONAR = true;
constexpr bool INDICATOR = true;
constexpr bool PROFILE = false;   // append per-phase point costs to the indicator (debug builds only)

}} // namespace seed0::P
