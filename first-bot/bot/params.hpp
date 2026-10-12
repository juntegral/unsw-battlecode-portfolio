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
// cand-portal1: a known exit is remembered like any other tile; the search and the flood fill already see a tight or
// dead-end exit through across(), so only the unseen-occupant risk stays (the old TIGHT 2.0 and STALE 3.0 are gone).
constexpr double PORTAL_STALE_PENALTY = 1.0; // known portal exit not seen recently (scaled by staleness/20 rounds)
constexpr double PORTAL_BLIND_PENALTY = 0.5; // exit tile not in view now: a head may have moved there
constexpr double PORTAL_HEAD_NEAR_PENALTY = 8.0; // a head (any team) was seen within 2 of the unseen exit recently

// --- unexplored portals (cand-portal1) ---
// An edge whose partner we have never seen is a frontier: it is an attraction source, a leaf of the search, and after a
// clean probe (one ray cast from the entry tile through the portal hit no dragon) a first-step candidate.
constexpr double FRONTIER_VALUE = 4.0;       // expected value behind an unexplored portal when hungry
constexpr double FRONTIER_FED_FRAC = 0.25;   // share of FRONTIER_VALUE right after eating
constexpr int    HUNGER_ROUNDS = 25;         // rounds without eating until the frontier counts in full
constexpr double FRONTIER_UNSEEN_GAIN = 2.5; // value x min(1, gain * share of the map this dragon has never seen)
constexpr int    FRONTIER_FADE_ROUNDS = 120; // value fades to 0 between 30+this and 30 rounds before the end
constexpr int    FRONTIER_MAX_SOURCES = 4;   // nearest frontiers that pull (field = the best one, not the sum)
constexpr double FRONTIER_COMMIT_MARGIN = 0.5; // enter after a clean probe when frontier - risk exceeds this
constexpr double BLIND_RISK = 0.8;           // expected cost of stepping into an unseen exit after a clean probe
constexpr double BLIND_RISK_PER_LEN = 0.05;  // + per segment: an unseen head beside the exit costs the whole dragon
constexpr int    BLIND_MIN_LEN = 3;          // L2 cannot escape-split out of a dead end
constexpr int    FRONTIER_BLOCK_ROUNDS = 6;  // a probe that hit a dragon: ignore that frontier this long
constexpr double BLIND_DESPERATE_PENALTY = 25.0; // an unexplored portal without a clean probe (or in the last rounds):
                                                 // still a legal step, chosen only when every other step is doomed
constexpr double PORTAL_UNPROBED_PENALTY = 4.0;  // known portal, exit out of view, no probe from here last turn
constexpr double PORTAL_DIRTY_PENALTY = 8.0;     // known portal, exit out of view, last turn's probe hit a dragon
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

// --- ram escape (cand-avoid6 = cand-avoid4 without the length bound: escapes and the trust switch only) ---
// A long dragon whose every single step is inside a shorter enemy head's reach may sprint 2 or 3 steps to a tile out of
// every reach. It does so only while it has no evidence that this opponent declines such trades: after RAMMER_TRUST
// turns on which it stood inside the exact reach of a shorter head and was not rammed, it behaves as before.
constexpr int    ESCAPE_MIN_LEN = 6;               // our dragons at least this long
constexpr int    RAMMER_TRUST = 4;                 // survived exact exposures after which escapes stop

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

// --- pocket eat (pd10): at a dead-end escape split, eat the pearl in front first when the child would otherwise
// come out shorter than this dragon was born (+1 if it was born on a tile open to the sides). A two-ended pocket loop
// then keeps its length, and the next child is born inside the walled part of the corridor instead of at its mouth.
constexpr bool POCKET_EAT = true;
constexpr bool POCKET_EAT_MAP_DRAGONS = false; // also map-given dragons (their initial length counts as birth length)
// (pd10d) a map-given dragon also uses the rule when its dead-end lane is poor: fewer than POCKET_LANE_YIELD tiles of
// the walled lane under its body (head backwards, both sides kelp) can spawn a pearl. A loop visit must win two pearls
// to pay for the two segments the split leaves behind; a poorer lane cannot keep the loop's length without the end pearl.
constexpr bool POCKET_MAP_LOW_YIELD = true;
constexpr int  POCKET_LANE_YIELD = 2;
// (pd10e) the rule is for pockets: the head and at least this many tiles behind it (itself included) are a walled lane
constexpr int  POCKET_MIN_LANE = 3;
constexpr int  POCKET_EXPOSED_BONUS = 1;       // extra child length allowed when this dragon was born exposed
constexpr int  POCKET_ENEMY_DIST = 4;          // no enemy head within this path distance of our head (enemyDist_ caps at 4)

// --- late consolidation (feeding the longest teammate) ---
constexpr int FEED_FIRST_ROUND = 430;       // never earlier
constexpr int FEED_MAX_DIST = 5;           // path distance from the longer teammate's head to ours
constexpr int FEED_SLACK = 8;              // start once round >= 500 - (L + dist + slack)

// --- gathering (c10): from GATHER_START the team concentrates length on its longest dragon ---
constexpr int    GATHER_BROADCAST = 300;    // from here every ray carries our message (all four directions)
constexpr int    GATHER_START = 340;        // from here: head for the king, feed on sight, no regular splits
constexpr int    GATHER_STALE = 20;         // ally position older than this (rounds) is ignored
constexpr int    GATHER_KING_MEMORY = 100;  // an ally heard to be longer within this many rounds means we are not the king
constexpr double GATHER_W = 0.12;           // leaf penalty per tile of path distance to the goal
constexpr int    GATHER_FEED_UNITS = 4;     // before the late window, feed only if this many units are alive (keeps 3)
constexpr int    GATHER_FEED_MIN_LEN = 4;   // before the late window, only feeders at least this long (an L2 gives one pearl)

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
