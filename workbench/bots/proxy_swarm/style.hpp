// style.hpp — proxy_swarm: the majority "N" style of the top teams (research/observations/top-summary-2026-09-29.md).
// 2+2 swarm growth, even head-on trades by small pieces, stub escape when trapped, late sacrifices near any longer ally
// (not gathered at the king), splitting to the end. Every other proxy has the same pxcore.cpp and its own style.hpp.
#pragma once

namespace style {
constexpr const char* NAME = "swarm";
constexpr unsigned SALT = 0x51A7u;          // per-style random salt

// --- splitting ---
constexpr int GROW_START = 260;             // before: every dragon of length >= 4 splits (4 -> 2+2, longer -> halves)
constexpr double SPLIT_P_EARLY = 0.50;      // per-turn split probability of a length-4 dragon before GROW_START
constexpr double SPLIT_P_MID = 0.50;        // ... from GROW_START (a length-4 dragon that eats first becomes a grower)
constexpr int GROWER_LEN = 5;               // from GROW_START a dragon this long stops 2+2 splitting ...
constexpr int HALVE_MAX_LEN = 6;            // ... and, up to this length, halves unless it is a local king
constexpr int KING_RADIUS = 14;             // a longer ally heard within this Manhattan distance means we are not the local king
constexpr double GROW_P = 0.15;              // per-turn chance that a length-4 local king keeps growing instead of splitting
constexpr double SPLIT_P_LATE = 0.40;       // per-turn 2+2 split probability of a length-4 dragon from SAC_START
constexpr int HALF_MIN_LEN = 6;             // before GROW_START longer dragons split in halves
constexpr int CHILD_ROOM = 3;              // a voluntary split needs this many free tiles around the tail (the child's start)
constexpr int STUB_KEEP = 2;                // trapped dragon of length >= 4 keeps this many head segments, the rest leaves reversed

// --- head-on rams (length classes as in the observations: small <= 4) ---
constexpr int RAM_MAX_LEN = 4;              // only dragons this short ram
constexpr double RAM_ADJ = 0.34;            // enemy head one step away, not longer than us
constexpr double RAM_ADJ_UP = 0.60;         // ... enemy longer than us
constexpr double RAM_S2 = 0.30;             // enemy head two steps away through a free tile (length >= 3 pays the sprint)
constexpr double RAM_S2_UP = 0.55;
constexpr double RAM_S3 = 0.0;              // three steps (length >= 4)
constexpr int RAM_BIG_LEN = 6;              // a big target (also at least twice our length) ...
constexpr double RAM_BIG_ADJ = 0.90;        // ... is rammed eagerly: adjacent,
constexpr double RAM_BIG_S2 = 0.80;         // two-step sprint,
constexpr double RAM_BIG_S3 = 0.50;         // three-step sprint
constexpr int RAM_MIN_UNITS = 2;            // never ram as the team's last dragon
constexpr bool HUNT = false;                // small pieces steer towards visible / reported enemy heads
constexpr double HUNT_W = 0.0;

// --- threat avoidance (mid and big dragons avoid enemy heads) ---
constexpr int THREAT_LEN = 5;
constexpr double THREAT1 = 3.0, THREAT2 = 1.2, THREAT3 = 0.4;

// --- late conversion ---
constexpr int SAC_START = 260;              // exit sacrifices from here
constexpr int SAC_RAMP = 100;                // rounds to reach the full rate
constexpr double SAC_P = 0.04;              // per-turn probability at the full rate (any longer ally within reach)
constexpr double SAC_NEAR_P = 0.45;         // ... when an ally of BIG_RECV_LEN+ has its head within 2
constexpr int BIG_RECV_LEN = 6;              // direct feeding: receiver at least max(this, 2x our length), head within 2
constexpr bool LEAVE_PEARLS = true;         // late: do not take pearls within 2 of a clearly longer ally's head
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
constexpr int KING_MIN_LEN = 8;             // K style: gather only toward a king at least this long
constexpr double GATHER_W = 0.0;
constexpr bool SAC_INTO_ALLY = false;       // die by stepping into a longer ally's body when one is adjacent
constexpr double TRAP_NOACT = 0.13;         // trapped piece that cannot split: share dying by no action (else a random blocked step)

// --- movement ---
constexpr int ROOM_EXTRA = 1;               // flood-fill room wanted = max(length + this, ROOM_MIN)
constexpr int SURVIVE_LEN = 5;              // dragons this long check that some path of SURVIVE_DEPTH more steps exists
constexpr int SURVIVE_DEPTH = 8;
constexpr int BIG_ROOM_LEN = 6;             // from this length the room wanted is 2*length + BIG_ROOM_EXTRA
constexpr int BIG_ROOM_EXTRA = 4;
constexpr int ROOM_MIN = 6;                 // pockets smaller than this get POCKET_PEN
constexpr double POCKET_PEN = 0.30;
constexpr bool ROOM_HEADS = true;           // room check: a tile next to another dragon's head may be taken before we arrive
constexpr double FOUNTAIN_V = 0.5;          // value of revisiting a tile seen to respawn within 40 rounds
constexpr double ROOM_PEN = 4.0;
constexpr double GAMMA = 0.80;              // per-step discount of pearl value
constexpr double EXPLORE_W = 0.25;          // value of reaching a stale or unseen tile (scaled down when pearls are known)
constexpr int STALE_AGE = 30;
constexpr double PORTAL_W = 0.35;           // value of reaching a portal whose far end is unknown
constexpr double PORTAL_ENTER = 0.30;       // score of stepping into such a portal
constexpr double PORTAL_BLIND_PEN = 0.10;   // stepping through a known portal whose exit tile is out of view
constexpr double SPREAD_W = 0.15;           // per nearby ally head (Manhattan < 3)
constexpr double ALLY_HEAD_PEN = 0.15;      // stepping next to an ally head
constexpr int SPRINT_EAT_MAX_LEN = 6;       // ... only for dragons up to this length
constexpr double SPRINT_EAT_P = 0.30;       // sprint two steps onto a contested visible pearl (length >= 4)

// --- sonar ---
constexpr bool SONAR_ALL = true;            // own id, position, length and round on all four rays every turn
constexpr bool SONAR_ENEMY = false;         // one ray carries the nearest visible enemy head
constexpr bool INDICATOR = false;
}
