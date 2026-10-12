// style.hpp — proxy3_swarm: the majority "N" style of the top teams (research/observations/top-summary-2026-09-29.md,
// top-decisions.md). 2+2 swarm growth, R4 trades by small pieces, stub escape when trapped, late sacrifices beside growing
// allies (R3), splitting to the end. v3 (research/experiments/proxies-v3.md): map spawn knowledge, R3/R4, px8 feeding.
// Every other proxy3 has the same pxcore.cpp and its own style.hpp.
#pragma once

namespace style {
constexpr const char* NAME = "swarm3";
constexpr unsigned SALT = 0x3A51u;          // per-style random salt (also the sonar tag; differs from v2 and px8)

// --- map knowledge (spawndb.hpp) ---
constexpr bool SPAWN_KNOW = true;           // recognise the known maps and value out-of-view spawn tiles by their gap range
constexpr double SPAWN_W = 1.0;             // scale of the expected pearl value
constexpr double EXP_FIRST = 0.75;          // a pearl spawned at the last known attempt is still there (decays per round)
constexpr double EXP_DECAY = 0.98;
constexpr double EXP_REGEN = 0.5;           // ... or a later one appeared: min(1, rounds since / mean gap) * this
constexpr double EXP_UNSEEN = 0.6;          // never-read tile: min(1, round / max gap) * this

// --- splitting ---
constexpr int GROW_START = 260;             // before: every dragon of length >= 4 splits (4 -> 2+2, longer -> halves)
constexpr double SPLIT_P_EARLY = 0.50;      // per-turn split probability of a length-4 dragon before GROW_START
constexpr double SPLIT_ENEMY_MULT = 1.6;    // ... times this with an enemy head in view (top: 41.0% vs 24.3%)
constexpr double SPLIT_P_MID = 0.50;        // ... from GROW_START (a length-4 dragon that eats first becomes a grower)
constexpr int GROWER_LEN = 5;               // from GROW_START a dragon this long stops 2+2 splitting ...
constexpr int HALVE_MAX_LEN = 6;            // ... and, up to this length, halves unless it is a local king
constexpr int KING_RADIUS = 14;             // a longer ally heard within this Manhattan distance means we are not the local king
constexpr double GROW_P = 0.15;             // per-turn chance that a length-4 local king keeps growing instead of splitting
constexpr double SPLIT_P_LATE = 0.40;       // per-turn 2+2 split probability of a length-4 dragon from SAC_START
constexpr int HALF_MIN_LEN = 6;             // before GROW_START longer dragons split in halves
constexpr int CHILD_ROOM = 3;               // a voluntary split needs this many free tiles around the tail (the child's start)
constexpr int STUB_KEEP = 2;                // trapped dragon of length >= 4 keeps this many head segments, the rest leaves reversed
constexpr int UNIT_SLACK = 0;               // voluntary splits stop this many units below the unit limit
constexpr int CROWD_UNITS = 32;             // 2+2 split rates times CROWD_MULT from this many team units (top: 23% vs 40%)
constexpr double CROWD_MULT = 0.6;
constexpr int CROWD_UNITS2 = 56;            // ... and times CROWD_MULT2 near the unit limit
constexpr double CROWD_MULT2 = 0.35;

// --- head-on rams: top rule R4 (small = length <= RAM_MAX_LEN) ---
constexpr int RAM_MAX_LEN = 4;              // only dragons this short ram
constexpr double R4_ALLY_GE = 0.70;         // an ally head in view, enemy as long or longer
constexpr double R4_ALLY_LT1 = 0.35;        // an ally head in view, enemy shorter, one enemy head in view
constexpr double R4_ALLY_LT = 0.15;         // ... several enemy heads in view
constexpr double R4_SOLO_GT = 0.50;         // no ally head in view, enemy longer
constexpr double R4_SOLO_EQ = 0.06;         // ... as long
constexpr double R4_SOLO_LT = 0.013;        // ... shorter
constexpr double RAM_SCALE = 1.0;           // style multiplier of the R4 rates
constexpr double R4_S2 = 0.80;              // two-step sprint ram: R4 rate times this (length >= 3)
constexpr double R4_S3 = 0.0;               // three-step sprint ram (length >= 4)
constexpr int RAM_BIG_LEN = 6;              // a big target (also at least twice our length) ...
constexpr double RAM_BIG_ADJ = 0.90;        // ... is rammed eagerly: adjacent,
constexpr double RAM_BIG_S2 = 0.80;         // two-step sprint,
constexpr double RAM_BIG_S3 = 0.50;         // three-step sprint
constexpr int RAM_MIN_UNITS = 2;            // never ram as the team's last dragon
constexpr bool HUNT = false;                // small pieces steer towards visible / reported enemy heads
constexpr double HUNT_W = 0.0;
constexpr double ELIM_MAP_HUNT_W = 0.25;     // v3: on known elimination-type maps small pieces steer towards seen or reported enemy heads ...
constexpr int ELIM_MAP_HUNT_UNITS = 6;      // ... while the team has at least this many units (enemy sightings go on sonar there)

// --- threat avoidance (mid and big dragons avoid enemy heads) ---
constexpr int THREAT_LEN = 5;
constexpr double THREAT1 = 3.0, THREAT2 = 1.2, THREAT3 = 0.4;
constexpr int KING_SAFE_LEN = 10;           // dragons this long weigh enemy reach more
constexpr double KING_SAFE_MULT = 1.5;

// --- late conversion ---
constexpr int SAC_START = 260;              // v2 exit sacrifices from here
constexpr int SAC_RAMP = 100;               // rounds to reach the full rate
constexpr double SAC_P = 0.015;             // per-turn probability at the full rate (any longer ally within reach)
constexpr double SAC_NEAR_P = 0.30;         // ... when an ally of BIG_RECV_LEN+ has its head within 2
constexpr int BIG_RECV_LEN = 6;             // direct feeding: receiver at least max(this, 2x our length), head within 2
constexpr double FEED_ADJ_P = 0.90;         // px8: our head next to a big receiver's / the king's head and not behind it
constexpr double FEED_FRONT_P = 0.55;       // ... within Chebyshev 2, not behind it
constexpr int R3_START = 250;               // top rule R3: a small piece dies beside a growing ally ...
constexpr int R3_LEN = 8;                   // ... at least this long
constexpr int R3_DIST = 3;                  // ... head within this Chebyshev distance, no enemy head in view
constexpr double R3_P_EARLY = 0.052;        // per turn before R3_LATE
constexpr double R3_P_LATE = 0.169;         // per turn from R3_LATE
constexpr int R3_LATE = 350;
constexpr bool R3_FRONT = true;            // v3: only where the receiver's head can take the pearls (not behind it)
constexpr int FEED_START = 330;             // v3 feeder: small pieces step towards the tile in front of a visible big ally's head ...
constexpr double FEED_W = 0.10;            // ... per step of distance (no enemy head in view)
constexpr bool LEAVE_PEARLS = true;         // late: do not take pearls near a clearly longer ally's head
constexpr int KING_RESERVE_R = 3;           // px8: ... within this Manhattan distance of a big ally's (or the king's) head
constexpr double RESERVE_MULT = 0.05;       // ... value multiplier
constexpr double SAC_KING_P = 0.0;          // K style: per-turn probability within KING_SAC_DIST of the king's head
constexpr double FOOD_W = 0.60;             // late: a dragon of BIG_RECV_LEN+ is drawn to shorter ally heads (they feed it)
constexpr int SAC_MAX_LEN = 4;              // small pieces sacrifice
constexpr int SAC2_START = 370;             // mid-size pieces too, next to a much longer ally
constexpr int SAC2_MAX_LEN = 12;
constexpr double SAC2_P = 0.10;
constexpr int SAC2_MARGIN = 3;              // ... at least this much longer
constexpr int MERGE_START = 440;            // from here the margin is 1: mid-size dragons merge into any longer neighbour
constexpr int SAC_RECV_DIST = 3;            // a longer ally head within this Chebyshev distance must be able to eat
constexpr int SAC_MIN_UNITS = 4;
constexpr double SAC_NOACT = 0.4;           // share of sacrifices by no action (the rest step into the own neck)
constexpr bool KING_GATHER = false;         // K style: non-kings walk to the king and sacrifice beside it
constexpr int KING_SAC_DIST = 4;
constexpr int KING_MIN_LEN = 8;             // K style: gather only toward a king at least this long; px8: "big ally" for pearl reserve
constexpr double GATHER_W = 0.0;
constexpr bool SAC_INTO_ALLY = false;       // die by stepping into a longer ally's body when one is adjacent
constexpr double TRAP_NOACT = 0.13;         // trapped piece that cannot split: share dying by no action (else a random blocked step)

// --- movement ---
constexpr int ROOM_EXTRA = 1;               // flood-fill room wanted = max(length + this, ROOM_MIN)
constexpr int SURVIVE_LEN = 2;              // dragons this long check that some path of more steps exists (v2: 5) ...
constexpr int SURVIVE_EXTRA = 0;            // ... clamp(length + this, SURVIVE_MIN_DEPTH, SURVIVE_DEPTH) steps
constexpr int SURVIVE_MIN_DEPTH = 6;
constexpr bool STUB_SURVIVE = true;         // a dead end counts as survivable when a stub split can leave it after eating ...
constexpr int STUB_GAIN = 2;                // ... at least this many pearls on the way (simulated)
constexpr int FOUNTAIN_SIM_GAP = 2;         // known spawn tiles with max gap <= this count as pearls on arrival in the simulation
constexpr int SURVIVE_DEPTH = 8;
constexpr int BIG_ROOM_LEN = 6;             // from this length the room wanted is 2*length + BIG_ROOM_EXTRA
constexpr int BIG_ROOM_EXTRA = 4;
constexpr int ROOM_MIN = 6;                 // pockets smaller than this get POCKET_PEN
constexpr double POCKET_PEN = 0.30;
constexpr bool ROOM_HEADS = true;           // room check: a tile next to another dragon's head may be taken before we arrive
constexpr double FOUNTAIN_V = 0.5;          // value of revisiting a tile seen to respawn within 40 rounds
constexpr double ROOM_PEN = 4.0;
constexpr double GAMMA = 0.80;              // per-step discount of pearl value
constexpr double GAMMA_EXP = 0.80;          // ... of expected pearls on known spawn tiles (rich far areas still pull)
constexpr double CONTEST_ENEMY_CLOSER = 0.35; // pearl value when an enemy head is closer (v2: 0.15 for any head)
constexpr double CONTEST_ENEMY_EQ = 0.80;   // ... about as close (v2: 0.55)
constexpr double EXPLORE_W = 0.25;          // value of reaching a stale or unseen tile (scaled down when pearls are known)
constexpr int STALE_AGE = 30;
constexpr double PORTAL_W = 0.35;           // value of reaching a portal whose far end is unknown
constexpr double PORTAL_ENTER = 0.30;       // score of stepping into such a portal
constexpr double PORTAL_BLIND_PEN = 0.10;   // stepping through a known portal whose exit tile is out of view
constexpr int BIG_LEN = 8;                  // px8: big dragons avoid unknown and blind portals
constexpr double BIG_PORTAL_BLIND_PEN = 2.0;
constexpr double BIG_PORTAL_UNKNOWN = -1.0;
constexpr double SPREAD_W = 0.15;           // per nearby ally head (Manhattan < 3)
constexpr double ALLY_HEAD_PEN = 0.15;      // stepping next to an ally head
constexpr int SPRINT_EAT_MAX_LEN = 6;       // ... only for dragons up to this length
constexpr double SPRINT_EAT_P = 0.30;       // sprint two steps onto a contested visible pearl (length >= 4)

// --- sonar ---
constexpr bool SONAR_ALL = true;            // own id, position, length and round on all four rays every turn
constexpr bool SONAR_ENEMY = false;         // one ray carries the nearest visible enemy head
constexpr bool INDICATOR = false;
}
