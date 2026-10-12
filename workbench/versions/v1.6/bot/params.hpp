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

// --- stack1 (2026-09-30): hypotheses from top-vs-top replays, each with its own indicator tag for the per-wave check
// (research/experiments/mech-stack1.md). Toggles: CONV_ON (M1), RAM_SMALL_ON (M2), KS_ON (M3); stack2 below: FRAG_ON, GRAB_ON; stack3: KS2_ON; stack4: TG_ON, ESC_SPLIT_ON, PX_ON, GX_ON, SPLIT_TAIL_ON; stack5: CSPLIT_ON, FGUARD_ON, COV_ON; stack7: FLOOR_ON, KCAP_ON; stack8: F2_ON, F2P_ON, PX2_ON, CLAIM_ALLY_ON, CLAIM_ENEMY_ON; stack9: LSPLIT_ON, FRAG_CAP_CSPLIT_ON (and COV_ON on); stack10: LNT_ON, UTAB_ON; stack11: GH_ON, KX_ON, LWK_ON. M1 conv (R3/K1, mass ledger H1): from CONV_START a small piece next to a big
// visible ally dies into its own neck so that ally eats the pearls. Tag "feed #<ally> d<dist> L<len> conv".
constexpr bool   CONV_ON = true;
constexpr int    CONV_START = 300;          // top winners start sacrificing about r300 (half done by r380)
constexpr int    CONV_MAX_LEN = 4;          // 79% of top sacrifices are length 2-3; the rule includes 4
constexpr int    CONV_ALLY_MIN = 8;         // the eater: a visible ally at least this long (47% of top drops go to >= 8)
constexpr int    CONV_ALLY_MARGIN = 4;      // and at least this much longer than us
constexpr int    CONV_MAX_DIST = 3;         // path distance from its head to ours (88% of top sacrifices: ally within 3)
constexpr int    CONV_MIN_UNITS = 3;        // keep two others alive
// M2 ram4 (B3): a piece of length <= RAM_SMALL_MAX_LEN rams an adjacent enemy head at least as long. Top winners do it
// on 43.6% of such turns (losers 32.0%, merge2 5.7%). Tag " ram4" on the TRADE label (+ " c1" when an ally head is
// within 3 of the enemy head, a collector for the pearls).
constexpr bool   RAM_SMALL_ON = false;       // W1 online (2026-09-30 12:00): off. 17 rams, pearls 9 to us vs 24 to them
constexpr int    RAM_SMALL_MAX_LEN = 4;
// Local check before the wave (37 games vs proxy4): without an ally near, the opponent ate 94 of the 99 pearls of the two
// bodies. Mass ledger H5: a trade pays only with a collector near. So ram only with a visible ally head within
// RAM_COLLECTOR_DIST of the enemy head.
constexpr bool   RAM_SMALL_NEED_COLLECTOR = true;
constexpr int    RAM_COLLECTOR_DIST = 3;
constexpr double RAM_SMALL_VALUE = 12.0;    // above an ordinary move's value (about 5-10), plus W_KILL per length gained
// M3 kingsafe (mass ledger H4): in the last KS_ROUNDS the king (our longest, >= KING_MIN_LEN) takes threats at the
// endgame weight whether or not we are ahead, enters no unexplored portal and pays KS_DEADEND_MULT times the dead-end
// penalty. Top winners' kings lose 0.3-0.7 length in r450-499, merge2's 3.8. Tag " ks" on the king's move label.
constexpr bool   KS_ON = false;              // W1 online: off. King loss after r450 2.2 > 1.0 a game; to be redesigned
constexpr int    KS_ROUNDS = 50;
constexpr double KS_DEADEND_MULT = 2.0;

// --- stack2 (2026-09-30): two more hypotheses, each with its own toggle and indicator tag (research/experiments/cand-stack2.md).
// With FRAG_ON and GRAB_ON both false the bot plays exactly as stack1 with the same M1-M3 switches.
// S1 frag (mass ledger H3, coverage for H2): from FRAG_START to FRAG_END a non-king dragon of length >= FRAG_MIN_LEN with no
// enemy head in view and a safe tail (wantSplit()'s child checks) splits off a FRAG_CHILD-segment child, so the team keeps
// small pieces that forage in our own territory and can later be fed to a big ally (stack1 conv). Top winners on 500-round
// maps hold 41.7 dragons at r300 and 27.4 at r400 (merge2 4.0 and 4.3), and their pieces of length <= 4 carry 92 length at
// r300; merge2 stops policy splits at GATHER_START and caps units at 3-5, so conv fired only 0.7 times a game locally.
// Tag "split<n> u<units> L<len> frag".
constexpr bool   FRAG_ON = true;
constexpr int    FRAG_START = 250;          // top winners' dragon count peaks about r230; conv (the feeding) starts at r300
constexpr int    FRAG_END = 420;            // the last pieces still get >= 80 rounds to forage and to be fed
constexpr int    FRAG_MIN_LEN = 7;          // the parent keeps >= 5 after the split
constexpr int    FRAG_CHILD = 2;            // 50% of top sacrifices are length 2 (29% length 3): the cheapest unit of coverage
constexpr int    FRAG_GAP = 15;             // rounds between two fragment splits of one dragon, so its pieces spread out
constexpr int    FRAG_KING_MEMORY = 40;     // non-king = an ally seen or heard within this many rounds is longer than us,
                                            // counted against UNIT_COUNT (Planner::longerAllyKnown): a king that wrongly
                                            // thinks it is not one cuts two segments off our longest every FRAG_GAP rounds
constexpr int    FRAG_FORAGE = 20;          // a piece born this recently does not convert yet: a coiled parent within
                                            // CONV_MAX_DIST would otherwise eat its new fragment back (2 segments for 1 pearl)
// Unit cap for fragment splits: tiles / FRAG_TILES_PER_UNIT, clamped. Top winners hold 27.4 dragons at r400 with 132 total
// length on 500-round maps (about 1,350 tiles each); merge2 holds 48 length (36% of that), so the same length per dragon is
// about 10 dragons, the H3 prediction (r400 count 4.3 -> >= 10), or one unit per ~135 tiles. The clamp gives the 512-tile maps
// one more unit than the rich policy cap (5) and keeps Schooltime (2,400 tiles) below a count our length cannot feed.
constexpr int    FRAG_TILES_PER_UNIT = 130; // Autarky 7, Portals 6, Schooltime 16, Slithery Fight 13, Trauma 8 (mean 10)
constexpr int    FRAG_CAP_MIN = 6;
constexpr int    FRAG_CAP_MAX = 16;
// S2 grab (mass ledger H5): a pearl that appears on a tile we saw pearl-free within GRAB_SEEN_GAP rounds, where no spawn attempt
// could have happened since, is a death drop (rules: a death turns every second segment into a pearl and leaves countdowns
// unchanged; a spawn needs its countdown to reach zero). For GRAB_ROUNDS rounds, our dragons within GRAB_REACH of it value it
// GRAB_VALUE times a pearl and drop the "enemy is closer" contest discount for it, so that we, not the opponent, collect the
// pearls of a head-on or of a death beside us. Top-vs-top, the ramming side eats 59-65% of the exchange pearls; merge2 eats
// 6.8 of 26.7 (25%), 22% when rammed. Not for the king (our longest, >= KING_MIN_LEN) in the last GRAB_KING_ROUNDS,
// whether or not stack1 M3 is on: the late king is not sent into contests.
// Tag " grab@<x>,<y>" on the move label: the fresh pearl this move eats or closes in on.
constexpr bool   GRAB_ON = true;
constexpr int    GRAB_ROUNDS = 6;           // a death drop stays fresh this many rounds after we first see it
constexpr int    GRAB_SEEN_GAP = 2;         // the tile was seen pearl-free this recently: the death happened beside us just now
constexpr int    GRAB_REACH = 6;            // path distance from our head over known edges (the 7x7 window reaches 6)
constexpr double GRAB_VALUE = 1.5;          // source value relative to an ordinary pearl
constexpr int    GRAB_KING_ROUNDS = 50;     // the late king's window (as KS_ROUNDS, but independent of KS_ON)

// --- stack3 (2026-09-30) M3v2 ks2: the late king models the full sprint reach of enemy heads. Replay study of our 14 king
// deaths by an enemy head from r400 (merge2 x3 + stack1, 280 games): 13 were sprints of 2-6 steps from Manhattan 3-6, 4 of
// them from outside the king's 7x7 view. merge2 caps an enemy head's reach at 4 (computeEnemyDistance). In the last
// KS2_ROUNDS the king (our longest, >= KING_MIN_LEN) also marks tiles an enemy head can reach with a sprint of up to
// KS2_REACH steps (length - 1; an unseen tail counts as long enough) and weighs them KS2_T5..T7. Its escapes never switch
// off by rammer trust. Tag " ks2" on the king's move label.
constexpr bool   KS2_ON = false;            // W3 online: off. ks2 fired (1,874 turns) but the late king was inside an enemy sprint reach on 27% of turns (gate <= 15%); tg (stack4) now covers the near field for every dragon
constexpr int    KS2_ROUNDS = 100;
constexpr int    KS2_REACH = 7;
constexpr double KS2_T5 = 7.0, KS2_T6 = 5.0, KS2_T7 = 3.0; // below T4 = 9 at distance 4

// --- stack4 (2026-09-30): the top fixes of the failure study research/observations/mech-merge2-failures.md (section 10:
// 630 of our games against the elite + 8,734 top-vs-top games), each with its own toggle and indicator tag
// (research/experiments/cand-stack4.md). With TG_ON, ESC_SPLIT_ON, PX_ON, GX_ON and SPLIT_TAIL_ON all false (and KS2_ON as
// in stack3) the bot plays exactly as stack3 (checked on two local games by replay event hashes).
// tg (rank 1): close the gaps of the ordinary threat model (computeEnemyDistance) for every dragon, not only the late king.
// Of merge2's 248 rams on our L>=6 dragons, 34 came through tiles occupied at our decision (a tail that moved away before
// the killer did; 22 were our own new head on a tile our body held), 24 with a pearl eaten on the strike path and 21 by an
// L>=5 head whose tail we had not seen (estimated L4, reach 3). The field now (1) gives a distance to occupied tiles (a step
// onto a tile that empties has a threat) and lets the enemy pass our tail and the tails of dragons that move between us and
// it, (2) adds one step of reach to a head with a pearl beside it, (3) assumes an unseen tail is long enough for the full
// capped reach (World's length estimate is unchanged: with (3), counting what an unseen-tail head eats cannot change its
// capped reach). The trade side of the threat (who the head-on favours) keeps the old length, and childSafe() keeps the old
// field, so splits do not change with TG_ON. The reach cap stays at 4 (the study's killers: 1-4 steps in 239 of 248, 5+ in
// 9). Tag " tg" on the move label when some legal candidate's final tile (our head after the move) carries threat only the
// new model sees and the chosen move's final tile does not; " tgx" when the chosen move's does.
constexpr bool   TG_ON = true;
constexpr int    TG_UNSEEN_LEN = 5;         // an unseen tail: long enough to sprint the capped reach 4 (the old floor was 4)
// esc-split (rank 2): cornered (every single step threatened, no clean 2-step sprint) with a safe tail, split instead of
// sprinting. merge2's cornered turns: body length kept after 30 rounds 77% after a split, 59% / 49% after a 2 / 3-step
// sprint; with the tail >= 4 from every enemy head 102% vs 76% / 48%. Top winners split on 21% of cornered turns (95% kept).
// Cornered is judged with the reach we are sure of (a head in view, length <= 4 and shorter than us, reach = its visible
// segments - 1; see plan.cpp): with estimated reaches most firings were not cornered turns in the local check.
// Tag "esc-split<n> L<len>".
constexpr bool   ESC_SPLIT_ON = false;      // W4 online: off. It fired 0.24 a game (gate >= 0.3) and kept 54% of the body at +30 (gate >= 85%)
constexpr int    ESC_SPLIT_TAIL_DIST = 5;   // our tail at least this path distance from every enemy head seen within 3 rounds
// px (rank 4): avoid portal exits crowded by our own dragons. merge2: 55 non-desperate deaths on the crossing step with our
// own dragon at the exit (0.26 a game), 30 gathering deaths by collision with our own dragons, and a L74 king lost on a
// known portal crossed without a probe. A known portal whose exit is out of view costs PORTAL_HEAD_NEAR_PENALTY when an ally
// head was seen or heard within PX_ALLY_ROUNDS rounds within PX_ALLY_DIST of the exit, and from GATHER_BROADCAST (or at
// length >= PX_LONG_LEN) an unprobed first-step crossing costs PORTAL_DIRTY_PENALTY instead of PORTAL_UNPROBED_PENALTY.
// Tag " px" on the move label when some legal candidate's crossing pays a px penalty and the chosen move crosses none;
// " pxx" when it does.
constexpr bool   PX_ON = false;             // W4 online: off. Non-desperate crossing-step deaths against our own dragons 0.39 a game (gate <= 0.10; stack3 0.14); px avoided only 10%
constexpr int    PX_ALLY_ROUNDS = 20;
constexpr int    PX_ALLY_DIST = 6;
constexpr int    PX_LONG_LEN = 15;
// gx (rank 7): do not head for the king without the rounds to get there. merge2: gathering that started with fewer than 10
// rounds of slack (rounds left - distance) succeeded 4 of 31 times. Tag " gx" on the move label of a turn whose goal is off
// for this reason only.
constexpr bool   GX_ON = true;
constexpr int    GX_SLACK = 5;              // the goal counts only while its path distance + GX_SLACK < rounds left
// split tail (rank 6): a policy or insurance split only with no known enemy head (seen within 3 rounds) within
// SPLIT_TAIL_DIST of our tail, the child's head. merge2: a child born with an enemy head within 4 died within 30 rounds 43%
// of the time (5-8: 29%, 9+: 12%). Fragment splits (stack2 S1) keep their rule. Tag: the split label ends with " e<d>" (that
// distance, 99 = none known), and " sx" on the move label of a turn this rule stopped a policy split.
// Off for the stack4 wave. Local check (60 games vs proxy v4, stack3 1.15 policy splits a game): with an earlier esc-split
// trigger that fired 2 a game, policy splits were 0.60 with this on and 0.73 with it off (the extra units reach the policy
// cap sooner); with the final esc-split (0.47 a game) and this off, 1.07. This rule's own cut (about a fifth) would put the
// wave near the study's protection floor (0.9) untested, so it waits for a later wave.
constexpr bool   SPLIT_TAIL_ON = false;
constexpr int    SPLIT_TAIL_DIST = 5;

// --- stack5 (2026-09-30): territory coverage, the top two proposals of the territory study research/observations/
// top-territory.md (section 10; 8,431 top-vs-top games + our 840 elite-set games), each with its own toggle and indicator tag
// (research/experiments/cand-stack5.md). With CSPLIT_ON, FGUARD_ON, COV_ON and NOEXIT_SPARE_ON all false the bot plays exactly
// as stack4 with the same stack4 toggles (checked by replay event hashes on two local games).
// csplit (proposal 1): split to cover. Where a pearl is eaten is decided by whose head is nearer when it spawns: with the top
// winners' distance distribution merge2 would lose 20% of its own-territory pearls instead of 56% (study 2.1). merge2 holds
// 4 dragons at r100 (top winners 30 on 500-round maps, 21 on elimination maps) because its split rule is blocked by the unit
// cap (56% of blocked turns on 500-round maps), the king rule (18% / 38%) and length < 8 (18% / 45%) (study 7.4). Before
// CSPLIT_END a dragon of length >= CSPLIT_MIN_LEN splits off a CSPLIT_CHILD-segment child while the team has fewer units
// than the map-scaled target, with an enemy head in view too (top winners: 40% of splits on 500-round maps); only the
// child's spot is checked (a known, open tail, >= 2 exits, no enemy head within CSPLIT_TAIL_DIST of it).
// The king: a dragon of length >= KING_MIN_LEN splits only when a longer ally is known (frag's test), so the king keeps its
// length (merge2 holds Autarky and PD6 with it, and there early splits lose family length: E1 below). A shorter "king" is a
// piece: on maps that start with short dragons only (QoS, Trophy, Trauma: 2 of length 3-4) the king rule blocked 38% of
// merge2's turns and merge2 stayed at 2 dragons all game (study 8 A1); top winners' longest stays about 4 until r200.
// Tag "csplit<n> u<units> L<len> t<target>" (+ " v" with an enemy head in view, + " k" when we believe we are the longest).
constexpr bool   CSPLIT_ON = true;
constexpr int    CSPLIT_START = 1;          // not in round 0: every start dragon sees the team's start count (swarm8 S5)
constexpr int    CSPLIT_END = 250;          // S1 frag takes over from FRAG_START = 250 with its own cap (disjoint windows)
constexpr int    CSPLIT_MIN_LEN = 4;        // parent keeps >= 2 (4 -> 2+2: top winners' children are 76% length 2)
constexpr int    CSPLIT_CHILD = 2;
constexpr int    CSPLIT_GAP = 8;            // rounds between two csplits of one dragon, so its children spread out
// Target = map tiles / CSPLIT_TILES_PER_UNIT, clamped. The study's target is own-territory tiles / 20 (top winners hold 1.7-12.0
// dragons per 100 own tiles at r100, median 5.0); a team's territory is 38-50% of the map (report-all 8), and the bot cannot
// see it at the start, hence W*H/45 (the study's fallback): Autarky 21, Default 22, Devil/PD/Portals 11, QoS 19,
// Schooltime 53 -> 40, Slithery Fight 37, Trauma 25, Trophy 13 (top winners at r100: 23, 19, 30/15/26, 13, 44, 59, 17, 31).
// The clamp keeps room under the 64-unit limit for escape splits.
constexpr int    CSPLIT_TILES_PER_UNIT = 45;
constexpr int    CSPLIT_TARGET_MIN = 8;
constexpr int    CSPLIT_TARGET_MAX = 40;
constexpr int    CSPLIT_TAIL_DIST = 2;      // childSafe()'s near-tail rule (enemyDist_[tail] <= 2), measured so that it works
// E1 (research/observations/top-decisions-large.md 3.2): top-vs-top, a split of length >= 4 before r50 loses family length
// after 10 rounds on Autarky (-0.83), PD6 (-0.96), Slithery Fight (-0.55), Portals (-0.35) and PD10 (-0.29), and gains on
// Trauma (+1.37), Schooltime (+0.36), Devil (+0.30), Trophy (+0.27). Autarky, PD6, PD10 and Slithery Fight start each team
// with a long dragon (14, 11, 11, 25) and/or many dragons (6, 3, 5, 7). A start dragon that sees such a start (team units >=
// CSPLIT_SEED_UNITS, or a dragon of ours of length >= KING_MIN_LEN by round 2) makes no csplit before CSPLIT_SEED_START, nor does
// any dragon that before then is, or sees or hears, a dragon of ours of length >= KING_MIN_LEN (a child cannot see the start).
// Portals (3 of length 3) is not told apart from Devil (3 of length 4) this way; its pieces must eat to length 4 first.
constexpr int    CSPLIT_SEED_UNITS = 5;
constexpr int    CSPLIT_SEED_START = 50;
// F (proposal 2): fountain guard. Top winners lose 7% (500-round) / 6% (elimination) of their own fountain pearls and 22% / 20%
// outside fountains; merge2 loses 50% / 33% at fountains, and its heads are within 3 steps of only 22% of its own fountains
// at r100 (top winners 61% / 55%) (study 2.3, 3). Unguarded fountain pockets a few steps inside the border feed one raider for
// 100+ rounds (study 8: A2, A6, A8, A10, B5, B7). Before GATHER_START a dragon that is not the king (length >= KING_MIN_LEN and
// our longest) heads for the nearest known fountain of our side that no ally head (seen or heard within FG_ALLY_STALE rounds)
// guards within FG_GUARD_DIST, and holds its group: the goal field is 0 on the group's fountains and within FG_HOLD of them.
// Our side = nearer to this dragon's first head tile than the mirror image is (symmetry resolved). Tag " F<d>@<x>,<y>" on the
// move label: path distance to the group and the fountain chosen.
constexpr bool   FGUARD_ON = true;
constexpr int    FG_MIN_UNITS = 3;          // a team of one or two feeds freely
constexpr int    FG_ALLY_STALE = 20;        // an ally head this old (seen or heard) still guards (GATHER_STALE)
constexpr int    FG_GUARD_DIST = 3;         // the study's "guarded": a head within 3 steps
constexpr int    FG_GROUP_DIST = 3;         // fountains within this Manhattan distance of the chosen one form its group
constexpr int    FG_MAX_DIST = 20;          // only groups this near (path distance over known edges, bodies ignored)
constexpr int    FG_HOLD = 2;               // no pull within this distance of the group
constexpr double FG_W = 0.12;               // leaf penalty per tile beyond FG_HOLD (GATHER_W)
// cov (proposal 3): pieces of length <= COV_MAX_LEN keep sources of our side at contest factor >= COV_CONTEST when an enemy
// head is nearer (the contest discount is 0.15 today, so our pieces cede our territory where an enemy already stands: 53% /
// 55% of merge2's own-territory pearls spawn with an enemy head 3+ steps nearer; top winners 10% / 13%).
// Tag " cov" when the move ends on our side with no other ally head within 6 of its last tile.
// stack9 (W10, supply-chain proposal 3): on. csplit's density is there now (12.6 dragons at r100 on 500-round maps), yet the enemy is
// nearer to 27% (r100) and 37% (r250) of our territory's capacity (top winners 11%, losers 17%; supply-chain 3.2). Our side for cov is
// the recognised map's territory (the table side of our first head tile, World::mapTerrAt, as F2), else ourSide().
constexpr bool   COV_ON = true;             // off for W5-W9: the study expected little from it without csplit's density first
constexpr int    COV_MAX_LEN = 4;
constexpr double COV_CONTEST = 0.6;
// no-exit spare (a csplit companion; cand-swarm3 T0): a dragon with no exit dies "going forward"; when that tile holds an ally's
// head, the head to head kills the ally too. With csplit's pieces this became common in the local check (v1, 60 games vs proxy
// v4): our dragons died in head to heads with each other 3.8 times a game (stack4 0.6); 81 of the 226 deaths were such a
// no-exit mover (its victims account for most of the rest). Die elsewhere instead: an unexplored portal edge (it may still be
// open), else left or right if no ally head is there, else into our own neck (harms nobody). Tag "no-exit s".
constexpr bool   NOEXIT_SPARE_ON = true;
// --- cand-mapid (2026-09-30, research/experiments/cand-mapid.md): map and pearl-layout recognition (mapid.cpp, mapdb.hpp) ---
// Hypothesis #11: every process recognises the map and its layout from its own windows (edges, spawn flags, countdowns).
// MAPID_TAG writes " map=<Name>/<a|b|?>" (or " map=?", " map=none") on a process's first turn and on every change, for
// tools/mech_check.js (the gate: recognition matches the game's true map and layout). The tag changes no action.
constexpr bool   MAPID_TAG = true;
// Hypothesis #14 (one layout policy): bsplit = early splitting on Schooltime layout b. On b the first 100 rounds bring a third
// of a's pearls (108 vs 333) and the game turns into an elimination count war: top-vs-top (527 b / 539 a games),
// losers are eliminated in 39% of b games vs 9% on a, and winners hold more dragons (r100 16 vs losers 11, r200 42 vs 16).
// The b-specific elite habit: dragons of length 5-9 in rounds <= 166 split 22.4% of turns on b vs 6.5% on a (winners 23.8% vs
// losers 17.4%; on a the sign is the other way), 93.6% of b children are length 2, and length >= 4 dragons split 72% of turns
// before r50. Our bot holds 3 dragons on b (units r50 3, r100 3; merge2 lineage, 29 b games), eats 9 natural pearls in
// r0-99 (elite vs us 35) and is eliminated in 69% of b games. Schooltime a keeps the old policy (a within-wave control).
// Rule: this process has recognised Schooltime b (World::mapIs), round <= BSPLIT_END, length BSPLIT_MIN_LEN..BSPLIT_MAX_LEN,
// team units < BSPLIT_CAP: split off a BSPLIT_CHILD child when the ordinary policy does not split (the usual child-safety
// check childSafe() and move gates apply). Tag: the split label ends " bsp" ("split2 u<units> L<len> bsp").
constexpr bool   BSPLIT_ON = true;
constexpr int    BSPLIT_END = 166;          // R2's window (top-decisions-large: rounds <= 166)
constexpr int    BSPLIT_MIN_LEN = 4;        // E1/R1: length-4 pieces split 4 -> 2+2 (72% of turns before r50 on b)
constexpr int    BSPLIT_MAX_LEN = 9;        // R2: length 5-9; longer ones (C3) split 0.7% on b and stay as they are
constexpr int    BSPLIT_CHILD = 2;          // C4: 93.6% of b children are length 2
constexpr int    BSPLIT_CAP = 16;           // elite b winners hold 16 [14, 19] dragons at r100

// --- stack7 (2026-09-30): proposals 1 and 2 of the elimination study research/observations/our-eliminations.md (section 4; our
// 1,050 elite-set games + 10,171 top-vs-top games), each with its own toggle and indicator tag (research/experiments/cand-stack7.md).
// With FLOOR_ON and KCAP_ON both false the bot plays exactly as stack6 (checked by replay event hashes on two local games).
// We are eliminated in 81% of our elimination-map games. Our units stay at 2-4 while the opponent's grow to 30-60, and our losses are
// 1:1 head-on trades (study 1.2-1.4): with ten times the units the same trade erases only us. Top losers that survive, once down to
// <= 3 dragons (enemy >= 8), split 2.0 times in the next 20 rounds and 23-26% are back to >= 4 dragons 20 rounds later; our
// eliminated games split 0.5 times and 5% recover, although we hold the length to split (total 13.2, longest 7.1; study 2.6).
// Precedence in decide(): policy split -> frag -> bsp -> csplit -> kcap -> floor. One split per turn and one tag per split: kcap and
// floor fire only on turns the earlier rules leave (after csplit's window, a king csplit keeps whole, csplit's 8-round gap, its
// 2-exit child spot), so their gates are measured on firings that do not overlap csplit or bsp (study 4, "stack5와의 관계").
// Map gate (study 4, "지도 가르기"): both are off where our structure wins and early splits cost the elite too (E1, family length 10
// rounds after a split: Autarky -0.83, PD6 -0.96, Portals -0.35), that is on Autarky, Prisoners Dilemma (6 and 10 dragons) and
// Portals, and while this process has not recognised the map family (World::mapFamIs: off before recognition and on "map=none").
// The family is enough (both layouts of a family are on or off). kcap is also off on Slithery Fight (the study keeps it to maps whose
// start dragons are all of length <= 4; Slithery Fight starts each team with an L25).
// floor (proposal 1): from FLOOR_START, while the team has <= FLOOR_UNITS dragons (UNIT_COUNT, exact), a dragon of length >=
// FLOOR_MIN_LEN splits off a FLOOR_CHILD child, with enemy heads in view too; only the child's spot is checked (csplit's near-tail
// rule: a known tail, no enemy head within FLOOR_TAIL_DIST of it, >= FLOOR_MIN_EXITS exits). The king is included before GATHER_START;
// from then (the late gathering) only a dragon that knows a longer ally splits, and a lone dragon keeps the insurance split's length
// (SPLIT_FIRST_LEN). It ends at SPLIT_LAST_ROUND like every policy split. The move gate of every split stays (no pearl on the best
// first step, the best move unthreatened and safe, no enemy head within 2 of our head: the parent stands still on a split turn).
// Tag "split2 u<units> L<len> floor".
constexpr bool   FLOOR_ON = true;
constexpr int    FLOOR_START = 30;          // the top LS - LX unit gap opens from r30 (study 2.3: r10 0.00, r30 +0.61, r50 +1.38)
constexpr int    FLOOR_UNITS = 3;           // the study's low-unit state (<= 3 dragons)
constexpr int    FLOOR_MIN_LEN = 4;         // the parent keeps >= 2
constexpr int    FLOOR_CHILD = 2;           // top winners' children are length 2 in 76% / 90% (territory study)
constexpr int    FLOOR_TAIL_DIST = 2;       // no enemy head within this path distance of the child's head (our tail)
constexpr int    FLOOR_MIN_EXITS = 1;       // the study: one exit is enough for a 2-segment child
// kcap (proposal 2): before KCAP_END, while the team has fewer than KCAP_UNITS dragons, a dragon that believes it is our longest
// (World::iAmLongest) and is at least KCAP_LEN long splits off a KCAP_CHILD child (the child's spot as floor's). King kills are 16% of
// our eliminations (top eliminated losers 6%); our 91 kings lost were L12.3 on average, 74% by a sprint ram of a 4.7-long enemy, with
// 1.7 of our dragons left (study 1.3, 2.1). Our longest at r50 on elimination maps is 6.8 (top W 3.7, LS 3.8, LX 3.0; study 2.2).
// Tag "split2 u<units> L<len> kcap".
constexpr bool   KCAP_ON = true;
constexpr int    KCAP_LEN = 7;
constexpr int    KCAP_UNITS = 6;
constexpr int    KCAP_END = 250;            // csplit's window; frag and the king's growth take over from r250
constexpr int    KCAP_CHILD = 2;

// --- stack8 (2026-09-30): refinements of two partially applied W5 pieces (F; the portal side effect of csplit), each with its own
// toggle and indicator tag (research/experiments/cand-stack8.md; failure classes over every F target and every portal crossing of
// the W5-W7 online sets, exp/cand-stack8/study.js + classify.js). With F2_ON, F2P_ON, PX2_ON, CLAIM_ALLY_ON and CLAIM_ENEMY_ON all false the bot
// plays exactly as stack7 (checked by replay event hashes on two local games).
// F2 (F target choice). W5+W6: 6,573 F targets (dragon x fountain), 72% in the designed situation; the misses are a tile outside our
// territory (13%: Portals 522, Slithery Fight 204; the mirror-side rule measures Manhattan distance from this dragon's first head
// tile, the territory is movement distance from the team's starting bodies through kelp and portals), another head of ours already
// within 3 (13%: in 214 of them we were nearer, so the old rule took it) and not a true fountain (1%). Of the designed targets, those
// 0-3 steps away when first tagged were reached in 94%, 4-6 in 27%, 7-10 in 7%, 11-20 in 5% (F's pull is FG_W a tile).
// With F2_ON: fountains and territory come from the recognised map (mapdb.hpp palettes, terrdb.hpp; World::mapFountAt/mapTerrAt,
// used once every table map left agrees on the tile, else the old rules; our side is the table side of our first head tile, since
// the server swaps the file's team letters in about half of the online games); a new target is at most FG2_MAX_DIST away, has no fresh
// ally head within FG_GUARD_DIST (any, not only a nearer one), and no fresh ally head of a non-king length nearer to it (Manhattan;
// ties to the lower id: two heads do not chase one fountain); a held target is kept while it stays within FG2_KEEP_DIST and no nearer
// ally head guards it (the old rule). Tag " F2" after the F tag when the target's fountain and side came from the table.
constexpr bool   F2_ON = true;
constexpr int    FG2_MAX_DIST = 6;          // new targets (designed targets 4-6 away were reached in 27%, 7+ in 6%)
constexpr int    FG2_KEEP_DIST = 9;         // hysteresis for the held target (a pearl may pull us a few steps off)
constexpr int    FG2_CLAIM_STALE = 5;       // a nearer ally claims a new target only if seen or heard this recently
// F2p (coordinator 18:0x; supply-chain study: "the F hold should release while the piece holds a live claim"): F must not pull a
// dragon away from a spawn it is the nearest head to. W5+W6: 26% of 49,287 F-tagged turns had a natural pearl within 7 (outside the
// target group) with us as the unique nearest head, 15% moved away from one, and the enemy ate 13% of those pearls (Slithery Fight
// 35%, Trauma 31%); on 500-round maps a child ate 29% of its claims on F-labelled turns, 43% without F (supply-chain). With F2P_ON the
// F pull is off for the turn (target kept) while this dragon holds a live claim (below; any length) outside FG_HOLD of the group
// that no known head is nearer to at this turn ([local v1, 18:38]: the claim's hysteresis is for cl / ce only).
// Tag " Fp@<x>,<y>" (the claimed pearl) after the F tag, which stays on the paused turn (the target is held).
constexpr bool   F2P_ON = false;          // W9 (2026-09-30 22:10): off, purpose did not move online
// Claims (supply-chain proposal, 18:07; exp/supply-chain/child_forage.js): a pearl (pearlProb >= 0.15) within CLAIM_REACH of our head
// (headDist_), seen within CLAIM_SEEN rounds, that no ally or enemy head is nearer to (SC.allyFar / SC.enemyFar, ties ours) is remembered as ours for CLAIM_ROUNDS
// while it stays (hysteresis: others may come nearer later). Computed when F2P_ON, CLAIM_ALLY_ON or CLAIM_ENEMY_ON is on.
// csplit children are rarely short of such claims (0.79 a child vs 0.85 for elite pieces on 500-round maps); the gap is who eats
// them: the child 39% (elite 48%), our longer dragons 18% (7%), the opponent 8% (0%); on elimination maps the opponent 18% (4%).
// cl (CLAIM_ALLY_ON): for a piece (length <= CLAIM_MAX_LEN) a claimed pearl is not ceded to a nearer LONGER ally (the contest cut
// CONTEST_ALLY_CLOSER stays for nearer allies of length <= CLAIM_MAX_LEN, siblings) and is worth max(v, p * CLAIM_VALUE).
// Tag " cl@<x>,<y>" when the move eats a claimed pearl or closes in on one (as grab).
// ce (CLAIM_ENEMY_ON): for a piece, a claimed pearl keeps at least CONTEST_EQUAL while the nearest enemy head is at most one step
// nearer than we are (SC.enemyFar >= headDist_ - 1); beyond that it is ceded as before. Tag " ce@<x>,<y>" when the move eats or
// closes in on such a claim with an enemy head within headDist_ + 1 of it.
constexpr bool   CLAIM_ALLY_ON = true;
constexpr bool   CLAIM_ENEMY_ON = false;  // W9 (2026-09-30 22:10): off, purpose did not move online
constexpr int    CLAIM_REACH = 6;
constexpr int    CLAIM_ROUNDS = 8;
constexpr int    CLAIM_SEEN = 2;            // [local v1, 18:38] a claim needs a pearl seen within this many rounds (not a predicted spawn)
constexpr int    CLAIM_MAX_LEN = 4;
constexpr double CLAIM_VALUE = 1.3;
// px2 (portal exits): W5+W6, 4,859 crossings, 291 bodies lost within 3 rounds (94.0%, protection floor 95%). The largest class is our
// own dragon on the exit tile (122: head 69, body 53); next come traps after the exit (93) and enemies at the exit (30). A known-portal
// crossing (not desperate, label v > -20) after last turn's probe from that tile through that portal stopped on a dragon of ours lost
// the body in 10% (echo ally, 410 crossings) and 19% (ally_head, 100) of cases, after a clean probe 3.6% (1,820); 97 of our 198
// crossing-step deaths against our own dragons followed such a probe. The dirty-probe penalty (PORTAL_DIRTY_PENALTY 8) did not stop
// them. With PX2_ON a crossing whose probe echoed our own dragon costs PX2_ALLY_PENALTY instead. Tag " px2" when some legal
// candidate paid it and the chosen move crosses none, " px2x" when the chosen move crosses it anyway.
constexpr bool   PX2_ON = false;  // W9 (2026-09-30 20:58): off; locally it did not keep dragons off ally-blocked exits (38% vs >=80%), cand-stack8.md
constexpr double PX2_ALLY_PENALTY = 30.0;   // judgement value: cross only when every other move is worse by 30 (desperate)

// --- stack9 (2026-09-30): the late piece pool, proposals 1, 4 and 3 of the supply-chain study research/observations/supply-chain.md
// (section 7; 11,743 top-vs-top games + our 1,259 elite-set games), each with its own toggle and indicator tag
// (research/experiments/cand-stack9.md). With LSPLIT_ON, FRAG_CAP_CSPLIT_ON and COV_ON (stack5 section) all false the bot plays exactly
// as stack8 (checked by replay event hashes on two local games).
// Our middle links (conv, feed, grab) decide and execute like the elite; what we lack is material, above all pieces after r250. On
// 500-round maps top winners give birth to 156 pieces a game in r250-499 (120 of them length-4 pieces re-splitting 2 + 2, 31 from
// parents of 5-7), stack5 8.7 and stack6 7.1 (nearly all escape splits); at r350 they hold 30.5 pieces, we 6.2 (study 4, 6). In stack8
// no rule splits a dragon of length 4-6 after r249 except the escape split: csplit ends at r249, frag needs length >= 7, the policy
// split length >= 8 (and stops at GATHER_START).
// Precedence in decide(): policy split -> frag -> bsp -> csplit -> kcap -> floor -> lsplit. One split per turn and one tag per split:
// lsplit is tried only on turns every earlier rule leaves (csplit and kcap end at r249, bsp at r166, frag needs length >= 7, the policy
// split length >= 8 or a lone dragon's insurance split, floor with <= 3 dragons on its maps comes first), so no earlier rule's decision
// changes on the turn it fires. fc changes frag's own cap only (frag keeps its place and its " frag" tag).
// lsplit (proposal 1): from LSPLIT_START to LSPLIT_END, while the team has fewer units (UNIT_COUNT) than csplit's target (clamp(W x H /
// CSPLIT_TILES_PER_UNIT, CSPLIT_TARGET_MIN, CSPLIT_TARGET_MAX); below top winners' r350 count on every map, study 6), a dragon of length
// LSPLIT_MIN_LEN..LSPLIT_MAX_LEN splits off an LSPLIT_CHILD child, at most once in LSPLIT_GAP rounds per dragon. csplit's king rule is
// kept (a dragon of length >= KING_MIN_LEN splits only when it knows a longer ally; it never binds at length <= 6), the child's spot is
// csplit's (csplitChildSafe: a known, open tail, >= SPLIT_MIN_CHILD_EXITS exits, no enemy head within CSPLIT_TAIL_DIST of it) and the move
// gate of every split stays (no pearl on the best first step, the best move unthreatened and safe, no enemy head within 2 of our head).
// Window (W10, coordinator 22:0x after the local check): r250-339, not the study's r250-429. The study keeps it on in the gathering window
// (top teams do not gather: study 1.2), but locally (proxy v4, a+b 120 games) about 60% of r250-429 firings came after GATHER_START:
// gatherers reaching within 3 of the king fell from 36-38% to 28% and the final king's line ate no more of our sacrifices (8.3 -> 8.7 a
// game); with LSPLIT_END = GATHER_START the reach was 37-38% and the line ate 11.0-12.1 (cand-stack9.md, [로컬 뒤]). Whether gathering
// itself should change is the endgame study's question. Tag "lsplit2 u<units> L<len> t<target>".
constexpr bool   LSPLIT_ON = true;
constexpr int    LSPLIT_START = 250;        // csplit's end (CSPLIT_END): the two windows do not overlap
constexpr int    LSPLIT_END = 340;          // GATHER_START (the study's end was 430; see above)
constexpr int    LSPLIT_MIN_LEN = 4;        // 4 -> 2 + 2: 120 of top winners' 156 late pieces a game
constexpr int    LSPLIT_MAX_LEN = 6;        // parents of 5-7 give 31; length >= 7 is frag's (FRAG_MIN_LEN)
constexpr int    LSPLIT_CHILD = 2;
constexpr int    LSPLIT_GAP = 8;            // CSPLIT_GAP: rounds between two lsplits of one dragon
// fc (proposal 4): frag's unit cap widened to csplit's target, cap = max(clamp(tiles / FRAG_TILES_PER_UNIT, FRAG_CAP_MIN, FRAG_CAP_MAX),
// csplit's target). frag pieces are the best late material (41-62% end in a sacrifice and 42-68% of their pearls go to a >= 8 ally;
// top winners' late children of 5-7 / 8+ parents: 30% / 44%, 20% / 36%) but fire 0.4-0.9 a game: csplit fills the old cap (6-16) before
// r250 (16.1-16.7 dragons at r250 on 500-round maps; study 2.2). Tag: the frag label ends " fc" when the split needed the wider cap
// (units >= the old cap).
constexpr bool   FRAG_CAP_CSPLIT_ON = true;

// --- stack10 (2026-09-30): proposals 1 and 2 of the economy-principles study research/observations/economy-principles.md (section 14;
// 12,566 top-vs-top games + our 1,259 elite-set games), each with its own toggle and indicator tag (research/experiments/cand-stack10.md).
// With LNT_ON and UTAB_ON both false the bot plays exactly as stack9 (checked by replay event hashes on two local games).
// lnt (proposal 1: E4 + decision rule B3; ram4 redesigned): trade by local numbers. d3 = ally heads in view - (enemy heads in view - 1)
// (the 7x7 view, Chebyshev 3 of our head; a trade target is always in view). Top-vs-top, the rammer's team eats 41% of the two bodies'
// pearls within 20 rounds at d8 <= -3 and 77% at >= +3 (net20 -0.12 -> +2.20). In B3 situations (length <= 4, an enemy head adjacent)
// top winners ram 14% of the time at d3 <= -2, 65% at +1 and 73% at >= +2 (30 of 31 big teams alike), and those rams keep 24% -> 80% of
// the pearls. We trade 38% of the time at d8 <= -3 (winners 11%) and keep 38% of our trade pearls; ram4 (W1) rammed 17 times, 14 of them
// locally outnumbered, and kept 6 of 35 pearls (its collector rule only checked "not alone").
//   ram branch: our length <= LNT_MAX_LEN, an enemy head seen this round one step away across an open edge (portals included), team units
//     >= LNT_MIN_UNITS, not the king, d3 >= LNT_MIN_D3: the trade value is max(old rules, RAM_SMALL_VALUE + W_KILL x (its proven length -
//     ours)). It takes ram4's place: RAM_SMALL_ON stays false and ram4's collector rule is not used. Tag " lnt<d3>" on the TRADE label
//     (" lnt<d3>o" when the old rules would have traded too).
//   veto: d3 <= LNT_VETO_D3 zeroes the value of any trade (every length; one step, sprint, kill path, and the hunting pull of short
//     dragons), except when the target's proven length is >= LNT_KINT_MIN_LEN and longer than our longest known (the enemy's likely
//     longest: the study's kint exception; top winners' rams of the opponent's longest (>= 8) net +9.47 even when outnumbered), and from
//     ENDGAME_ANY_TRADE_ROUND. Tags: " lntv<d3>" on a move turn whose best trade the veto removed (its value without the veto beat the
//     chosen move's), " kint" on a TRADE the veto would have removed but for the kint exception.
constexpr bool   LNT_ON = true;
// stack11 (coordinator, W11 verdict): lnt's ram branch only (lntRam: ram an adjacent enemy head when locally ahead, d3 >= LNT_MIN_D3; tag
// " lnt<d3>"). false = those turns fall back to stack9's trade rules; the veto (" lntv", with the kint >= 8 and r495 exceptions) stays. true = stack10.
constexpr bool   LNT_RAM_ON = false;            // W11 (2026-09-30 23:50): ram part off; online 46/52% pearl share, net20 −0.06 per trade; veto kept
constexpr int    LNT_MAX_LEN = 4;           // B3: length <= 4
constexpr int    LNT_MIN_D3 = 1;            // winners ram 65-73% from d3 = +1 (29% at 0)
constexpr int    LNT_VETO_D3 = -1;          // winners ram 14-16% at d3 <= -1, and such rams keep 24-35% of the pearls
constexpr int    LNT_D8_VETO = -3;          // v1 final (swarm rows but Slithery Fight): no trade at local balance d8 <= -3 (atlas: -0.1 to -1.25 a contact)
constexpr int    LNT_MIN_UNITS = 3;         // keep two others alive
constexpr int    LNT_KINT_MIN_LEN = 8;      // the veto's exception: a target this long (proven) and longer than our longest known
constexpr bool   LNT_KINT_NEED_LONGEST = false; // W11 (coordinator 22:29): the exception covers any target of proven length >= LNT_KINT_MIN_LEN.
                                            // true = the study's rule (also longer than our longest known). Evidence, the primary sample: W5-W8
                                            // online (280 games), our TRADE kills at d3 <= -1 of targets >= 8 netted +4.93 each (30 trades),
                                            // of targets < 8 -0.18 (28); top winners' rams of the opponent's longest (>= 8) net +9.47 outnumbered
// utab (proposal 2, E3): csplit's unit target from a table of top winners' median dragon counts per recognised layout instead of map
// tiles / 45 (R^2 of winners' r100 count over 15 layouts: area 0.14, fountain tiles 0.42, natural spawn flow 0.85; the area target is off
// by >= 1.5x on 8 of 15 layouts). Before UTAB_EARLY_END the winners' r50 median, then their r100 median (plan.cpp UTAB); before this
// process decided the map and layout (World::mapIs) or on "map=none", the area formula. The table values are not clamped to the area
// formula's 8-40 (the 64-unit limit still applies). Only csplit's target changes: lsplit and fc (stack9) keep the area formula in their
// own code, so UTAB_ON and LSPLIT_ON / FRAG_CAP_CSPLIT_ON switch independently; they interact only through the units present at r250.
// Tag: the csplit label's "t<target>" is followed by " tab".
constexpr bool   UTAB_ON = false;          // W11 (coordinator 22:50): off. Primary sample W5-W8: outside Portals the table changes csplit's
                                            // permission in <= 13% of r1-249 rounds; units are limited by length and survival, not by the target
constexpr int    UTAB_EARLY_END = 50;       // winners' r50 median before this round, their r100 median from it
constexpr bool   UTAB_PORTALS = false;      // W11 (coordinator 22:29): Portals keeps the area target (11), as in stack9. true = the study's
                                            // table (26). Evidence (stack8-based dev build, 120 local games): on Portals the table doubled our
                                            // r100 units and portal 3-round body survival fell from 94% to 90% (protection floor 95%)

// --- stack11 (2026-09-30): the three proposals of the endgame king study research/observations/endgame-king.md (section 7; our 21 elite
// sets, 1,469 games, + top-vs-top 500-round games), each with its own toggle and indicator tag (research/experiments/cand-stack11.md).
// With GH_ON, KX_ON and LWK_ON all false the bot plays exactly as stack10 (checked by replay event hashes on two local games).
// On 500-round maps our final king ends 20.4 shorter than top winners' (stack5-7), 17.5 of it in sacrifice pearls. Gathering supplies
// 57-76% of the line's sacrifice pearls but leaks: the team's longest at the start of gathering is the final king in 33%, and other own
// dragons eat 26-35% of the pearls of labelled feeds aimed at the line (merge2 20%). Our king lives next to enemy heads (52% of its
// r300-399 turns have one within Manhattan 6; top winners 32%) and we lose the team's longest to an enemy head after r340 in 13% of games
// (winners 5%); conv is blocked by an enemy head in view in 36-39% of its geometric states (winners 17%).
// gh (proposal 1): gatherers hold back at the king, and fresh drops beside a longer ally's head are left to it.
//   hold: the gathering leaf penalty (dfs) is GATHER_W x max(0, goal distance - GH_HOLD) instead of GATHER_W x goal distance (as F's
//     FG_HOLD). Tag " gh" on a gathering move turn whose goal distance at our head is <= GH_HOLD + 2.
//   drops: from GH_DROP_START, a fresh death drop (freshDrop) within Manhattan GH_DROP_R of the head of an ally seen this turn that is
//     longer than us is worth CONTEST_ALLY_CLOSER times a pearl wherever the planner values a pearl on it: the search's step value, its
//     attraction source (which loses grab's boost and tag for this dragon; the ally-closer discount applies at every distance), and the
//     first-step and sprint values of the candidates (a dragon beside the drop would otherwise take it on its first step). Whether a move
//     eats is unchanged (the body model). Tag " ghd@<x>,<y>" (the nearest such drop) on a move turn with one within 3 steps of our head.
// kx (proposal 2): from KX_START the king keeps away from enemy heads on the recognised fight maps (kxMapOn: Schooltime, Slithery Fight,
//   Trauma, Autarky; World::mapFamIs, off before recognition and on "map=none"). The king = length >= KING_MIN_LEN and no ally longer than
//   us with news (seen, heard or relayed) within KX_KING_FRESH rounds (kingFresh(); not gatherKing_, whose 100-round memory counts dead
//   allies: World::dragons is cleared only at init). kxDist_ = path distance over known edges (bodies ignored, as goalDist_) from the enemy
//   heads seen within KX_STALE rounds, up to KX_DIST; while a known enemy head is within KX_DIST of our head, the search's leaf pays
//   KX_W x (KX_DIST - kxDist_). Unlike stack1 ks and stack3 ks2 (threat weights on tiles inside the sprint reach of enemy heads long enough
//   to strike, r450 / r400 on; the king's position did not change), kx prices plain distance to every enemy head, pieces included (their
//   presence blocks conv and feed), from r300, as a pull over the whole search horizon. Tag " kx<d>" (d = kxDist_ at our head), and
//   " kxm" when the chosen move ends farther than d.
// lwk (proposal 3): the late window (from FEED_FIRST_ROUND) also feeds only the king class (an ally at least kingLen - 2 long, as the
//   gathering window's earlyOnlyKing), with kingLen taken from news of the last LWK_KING_FRESH rounds (not GATHER_KING_MEMORY: a dead
//   king's record would stop feeds to the new one). Tag " lwk" on a move turn whose feed the old late-window rule (any longer ally within
//   FEED_MAX_DIST) would have made.
constexpr bool   GH_ON = true;
constexpr int    GH_HOLD = 3;               // the study: no gathering pull within 3 of the goal (feeds reach 5)
constexpr int    GH_DROP_R = 2;             // drops within Manhattan 2 of a longer ally's head are left to it
constexpr int    GH_DROP_START = 300;       // CONV_START: the feeds (conv from r300, feed from r340) whose pearls the rule leaves to the target
constexpr bool   KX_ON = true;
constexpr int    KX_START = 300;            // the exposure gap is widest in r300-399 (52% vs 32%)
constexpr int    KX_DIST = 7;               // keep >= 7 from enemy heads (the exposure metric counts <= 6)
constexpr double KX_W = 0.4;                // leaf penalty per tile below KX_DIST (GATHER_W 0.12 moves gatherers 19 steps)
constexpr int    KX_STALE = 3;              // enemy heads seen this recently
constexpr int    KX_KING_FRESH = 20;        // GATHER_STALE: a longer ally with news this recent says we are not the king
constexpr bool   LWK_ON = false; // W12 (2026-10-01 00:03, coordinator): off before upload. Locally late-window feeds fell 3.0 -> 1.2/game and the line r450-499 sacrifice pearls 2.8 -> 2.0 (opposite of the hypothesis); cand-stack11.md
constexpr int    LWK_KING_FRESH = 20;       // GATHER_STALE: kingLen from news this recent in the late window

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

// --- unsw-swarm v0 (2026-10-01): the engine layer (policy.hpp, engine.hpp, main.cpp; ENGINE.md) ---
// ENGINE_TAG appends " E=F" (FORTRESS) or " E=S" (SWARM) to every turn's indicator: the engine the assignment table chose
// for this turn. In v0 the SWARM engine forwards to FORTRESS, so " E=S" marks the dispatch, not a different behaviour.
// The label changes no action (tools/fingerprint.js skips indicator events).
constexpr bool ENGINE_TAG = true;

// --- unsw-swarm v1 (2026-10-01): belief integrity (both engines) and the swarm engine (versions/v1/VERSION.md, ENGINE.md §3) ---
// BELIEF_FIX_ON (coordinator 02:25; research/observations/bot-architecture-audit.md §4.1, §5.6 in legacy). Four faults of our beliefs:
//   1. sonar ids were cut to 8 bits (myId & 255; our ids reach 1,230-1,365 a game), and heard ids aliased seen ids in World::dragons;
//   2. dead dragons were never forgotten (World::dragons is cleared once, at init);
//   3. length lower bounds never decreased (minLen, maxAllyLenSeen: iAmLongest and teamLongestKnown were lifetime maxima);
//   4. "king" had five definitions (iAmLongest lifetime, gatherKing 100 rounds, kingFresh 20, the feed's 100-round kingLen - 2, the
//      split rules' 40-round longerAllyKnown).
// With the fix: message format 2 (World::encodeMsg / decodeMsg: an 11-bit id, round mod 128, length 7 bits, the post-action head and
// length), allies count only with news (seen, heard or relayed) within BELIEF_FRESH rounds, a length bound older than BELIEF_LEN_STALE
// rounds gives way to the current sighting, and one king class (World::iAmLongest over fresh allies) replaces the five definitions.
// false = stack11 exactly (benchmark/; checked with tools/fingerprint.js).
constexpr bool   BELIEF_FIX_ON = true;
constexpr int    BELIEF_FRESH = 20;          // rounds: an ally without news this recent is forgotten in every decision
constexpr int    BELIEF_LEN_STALE = 10;      // rounds: a length bound this old gives way to the current partial sighting
// BELIEF_TAG: every BELIEF_TAG_EVERY rounds the move label ends " bl<len>@<x>,<y> k<0|1>": the believed longest ally (its length and
// last known head; "bl0@-" none) and this dragon's own king verdict, under the active belief model (the lifetime memory with the fix
// off, fresh news with it on). For measuring belief accuracy against the true team longest in the replay. Changes no action.
constexpr bool   BELIEF_TAG = true;
constexpr int    BELIEF_TAG_EVERY = 5;
// SWARM_AS_FORTRESS: the identity build. true = the SWARM engine runs with the FORTRESS configuration (policy.hpp), so with
// BELIEF_FIX_ON false every map plays exactly as stack11 (the labels " E=S" and " bl" aside).
constexpr bool   SWARM_AS_FORTRESS = false;
// FORT_W4_ON (v1 final item 5b, coordinator 03:30): Autarky and PD6 play the FORTRESS with the W4-era economy (policy.hpp makeConfig): csplit, F / F2 /
// F2p, cov, lsplit, floor, kcap, fc, cl / ce compiled out (Planner::decideImpl<1>). false = those rows are stack11 (the identity builds).
constexpr bool   FORT_W4_ON = true;

// Swarm engine (engcfg.hpp holds the runtime switches; these are its constants).
// A explosion (sx): pf's rules (legacy/exp/cand-stack12): r1-99, length >= 4 splits off a 2-child every SX_GAP rounds while units <
// the map's head target (policy.hpp, <= unitLimit - SX_HEADROOM); no king rule, no E1 start block; child spot = csplitChildSafe +
// room (>= SX_ROOM free tiles reachable from the tail, none next to an enemy head).
constexpr int    SX_END = 100;
constexpr int    SX_GAP = 1;              // v1 final: the atlas split rate r0-49 is 0.6-0.8 per length >= 4 head-round on every swarm map (a 2-round gap caps it at 0.5)
constexpr int    SX_HEADROOM = 8;
constexpr int    SX_ROOM = 8;
// B re-split (sr): r100 to SR_END, length 4 -> 2 + 2 and 5-7 -> a 2-child, every SR_GAP rounds, while units < the phase-B target and
// (research transfer 17, coordinator 02:15) a service deficit exists: an own-side spawn group within SD_MAX_DIST that no ally owns,
// guards or claims besides ours; with fewer than SR_FLOOR_UNITS units the deficit is not required (survival splits).
constexpr int    SR_START = 100;
constexpr int    SR_END = 430;
constexpr int    SR_GAP = 2;
constexpr int    SR_FLOOR_UNITS = 8;
constexpr int    SR_SURVIVE_UNITS = 3;       // survival clause: stack7 floor's low-unit state (<= 3 dragons)
constexpr int    SR_MIN_LEN = 4, SR_MAX_LEN = 7;
// Dispersal (sd): replaces F in the swarm engine before the conversion clock. Target = the best own-side spawn group (the recognised
// map's spawn table, flow = 1 / mean gap, summed within FG_GROUP_DIST) that this dragon is uniquely nearest to (path distance over
// known edges against the ally heads' body-aware distance, ties to the lower id), else one no ally guards (FG_GUARD_DIST) or claims.
// Claims (research transfer 1 and 7): the regular sonar message's hotspot field carries our target; an ally's claim holds for SD_TTL
// rounds from its issue; a claim beats ours when its sender's estimated arrival is earlier, or equal with a lower id. Our held target
// is kept (lease) until SD_LEASE rounds pass, unless another's claim or ownership beats it by SD_HYST rounds.
constexpr int    SD_MAX_DIST = 16;
constexpr int    SD_TTL = 4;
constexpr int    SD_LEASE = 4;
constexpr int    SD_HYST = 2;
constexpr int    SD_ALLY_STALE = 3;          // (pre-cleanup build: ally heads this recent contested a group; now BELIEF_FRESH, coordinator 03:20)
constexpr int    SD_FALLBACK_K = 4;          // (03:20 build) uncovered fallback: hash(our id) mod k among the k nearest distinct uncovered groups; unused since 03:40
// SD_CONTEST_TIES (coordinator 04:00): a spawn group exactly as near to our head as to the nearest enemy head is ours unless the trade veto
// would apply there (symmetric maps: the central fountains are equidistant from both starts; the atlas: winners' r100 Voronoi share 0.58-0.98,
// 21-35% of their heads in enemy territory). false = a tie with an enemy head cedes the group. Shipped false (04:04, the coordinator's rule: ship
// it only if the centre head share rises on Slithery a and Schooltime a; 6-game check: 5 vs 6% and 13 vs 13%; exp/v1/report-ct-vs-fix.md).
constexpr bool   SD_CONTEST_TIES = false;
constexpr double SD_MIN_FLOW = 0.004;        // groups poorer than this (1 / 250 rounds) are not targets
// Spawn clearance (sc, research transfer 12): a step onto an own-side or neutral spawn tile whose next attempt comes while our body
// still covers it (within min(length, SC_WIN) rounds of the step) pays BLOCK_SPAWN_PENALTY (fortress: the head's next round only).
constexpr int    SC_WIN = 8;
// C local feed (sf): from the map's conversion clock a piece (length <= 4) dies beside the longest ally head in view that is longer
// (path distance <= CONV_MAX_DIST), a dragon of 5-7 beside one >= max(length + SF_MID_MARGIN, SF_MID_ALLY_MIN). No enemy head nearer
// to our head than the ally + 1, none within SF_ENEMY_R of the ally's head. Pickup queue (research transfer 3, 21): held (" sq#<id>")
// while SF_QUEUE_MAX or more pearls lie within Manhattan SF_QUEUE_R of the ally's head (it eats at most one per action).
constexpr int    SF_MID_MIN = 5, SF_MID_MAX = 7;
constexpr int    SF_MID_MARGIN = 4, SF_MID_ALLY_MIN = 8;
constexpr int    SF_ENEMY_R = 3;
constexpr int    SF_QUEUE_R = 2;
constexpr int    SF_QUEUE_MAX = 2;
// SF_PIECE_BIG_ONLY (k8; coordinator 03:30, kept 03:46 by its pre-registered rule): pieces too feed only an ally >= max(length + SF_MID_MARGIN,
// SF_MID_ALLY_MIN) (the mid-size rule). false = the task spec (a piece feeds the longest longer ally in view). Pre-cleanup local set: 75-80% of
// feeds went into recipients of length 3-4 and the final line's share of our r300+ sacrifice drops fell to 12-13% (v0 40%). Same 56 keys, k8 vs
// the post-cleanup build: final longest 14.6 vs 13.9, line share 20% vs 15%, recipients >= 8 49% vs 10%, wins 8 vs 5 (rule: keep unless final
// longest -2 or a lower line share).
constexpr bool   SF_PIECE_BIG_ONLY = true;

// --- unsw-swarm v1.1 (2026-10-01, versions/v1.1/VERSION.md) ---
// A frontier allocation (swarm rows, sd): each tile's frontier bin f = d_own / (d_own + d_enemy) (frontdb.hpp, the spatial study's definition) and
// the elite winners' head share by bin (policy.hpp FRONT_POLICY). Deficit per bin = share x (allies counted + 1) - allies counted there (fresh news;
// a live claim counts at its group); sd takes, among the groups it may take, one in the bin with the largest positive deficit (v1's value inside
// the bin). Contest: a group is takeable when our path ETA <= the nearest enemy head's + SD_ENEMY_MARGIN (held target: + SD_HYST_ENEMY more) and the
// trade veto would not apply there. false = v1's rule (nearest known head, ties with enemies ceded).
constexpr bool   FRONTIER_ON = true;
constexpr int    SD_ENEMY_MARGIN = 1;
constexpr int    SD_HYST_ENEMY = 1;
// B king floor (swarm rows): the king class (fresh iAmLongest, length >= KING_MIN_LEN or round >= the conversion clock) pays, for the choice only,
// KF_FLOOR + KF_STEP x (KF_FLOOR_DIST - d) on a move ending at path distance d <= KF_FLOOR_DIST from an enemy head seen within KF_STALE rounds
// (known edges, bodies ignored), and KF_SOFT x (KF_TARGET - d) below KF_TARGET. Below the trap (60) and death penalties.
constexpr bool   KING_FLOOR_ON = true;
constexpr int    KF_FLOOR_DIST = 3, KF_TARGET = 6, KF_STALE = 3;
constexpr double KF_FLOOR = 20.0, KF_STEP = 10.0, KF_SOFT = 1.0;
// C king beacon (both engines): the believed king (fresh iAmLongest, length >= KING_MIN_LEN) casts its report on all four rays every
// KING_BEACON_EVERY rounds (not on a portal probe). FORTRESS before GATHER_BROADCAST (no relays yet): a non-king with news at most
// BEACON_RELAY_AGE rounds old of a longer fresh ally passes it on all four rays, at most once every KING_BEACON_EVERY rounds.
// false = v1 exactly (checked with tools/fingerprint.js on the fortress maps).
constexpr bool   KING_BEACON_ON = true;
// C2 length memory (lead 06:00, found by the Portals agent in exp/portals; both engines): v1's fix let a partial sighting (e.g. 12 of 42 segments in
// view) replace an ally's length once its evidence was BELIEF_LEN_STALE rounds old, so the second-longest believed itself the king. With this on, a
// sighting without the whole chain in view and a relayed report only raise a remembered length; it is lowered only by a whole chain in view, the
// dragon's own sonar report, or its expiry (BELIEF_FRESH rounds without news). false = v1 (the identity build turns this and the beacon off).
constexpr bool   BELIEF_LEN_KEEP_ON = true;
constexpr int    KING_BEACON_EVERY = 8;
constexpr int    BEACON_RELAY_AGE = 1;
// v1.1b (versions/v1.1/VERSION.md §5.2, after the local check; the SWARM engine only): a frontier sd target is held until arrival (within FG_HOLD)
// for at most SD_COMMIT_MAX rounds while it stays ours, and the search leaf pulls to it FG_W_FRONT a tile beyond FG_HOLD (v1: FG_W 0.12, the
// same as the gathering pull). Local check (112 paired swarm games, proxies): targets held 4.6 turns (v1.1 3.4), middle-bin heads r100 34% (28%).
constexpr int    SD_COMMIT_MAX = 30;
constexpr double FG_W_FRONT = 0.4;

// --- unsw-swarm exp/portals (2026-10-01): the Portals module (ptmod.cpp, ptmap.hpp; exp/portals/PLAN.md) ---
// Portals is solitaire: the two halves share no tile (movement BFS 240 / 240, no path), so our king500 depends on our play alone. Every
// switch below acts only in a process that recognised the Portals family (World::mapFamIs("Portals")); other maps are untouched.
// PT_ON: the Portals row gets its own planner instantiation (decideImpl<3>: policy.hpp makeConfig, main.cpp). false = FORTRESS as before.
constexpr bool   PT_ON = true;
// Conversion clock: stack1 conv from PT_CONV_START, central gathering (goal pull, feed on sight) from PT_GATHER_START (FORTRESS: 300 / 340).
constexpr int    PT_CONV_START = 300;
constexpr int    PT_GATHER_START = 340;
// Endgame (PT_ENDGAME_ON): from PT_ENDGAME_ROUND every non-king follows the king and the late feed runs down to PT_FEED_MIN_UNITS units
// (FORTRESS: gathering needs >= GATHER_FEED_UNITS units and length >= GATHER_FEED_MIN_LEN, the feed >= 3 units). The late window opens at
// 500 - (length + path distance + PT_FEED_SLACK) (FORTRESS FEED_SLACK 8): the king needs about length + distance rounds to eat the drops.
constexpr bool   PT_ENDGAME_ON = true;
constexpr int    PT_ENDGAME_ROUND = 430;
constexpr int    PT_FEED_MIN_UNITS = 2;
constexpr int    PT_FEED_SLACK = 10;
// King safety (PT_KING_SAFE_ON; the king class = iAmLongest and length >= KING_MIN_LEN): PT_KING_DEAD_PEN on every step onto a dead tile
// (ptmap DEAD: outside the 2-core, or a compartment of <= 8 tiles with one way out; first step and the look-ahead), PT_KING_BLIND_PEN on
// a first-step crossing whose exit is out of view without a clean probe from this tile last turn, while the king's head is outside the rooms
// (ptmap ROOM: in a room every way out is a portal crossing).
constexpr bool   PT_KING_SAFE_ON = true;
constexpr double PT_KING_DEAD_PEN = 40.0;
constexpr double PT_KING_BLIND_PEN = 12.0;
// Crossings near the king (PT_PIECE_PORTAL_ON): a non-king's crossing whose exit is out of view and within PT_NEAR_KING_DIST (+ the news
// age) of the king's head, known from news at most PT_KING_NEWS rounds old, pays PT_PIECE_NEAR_KING_PEN.
constexpr bool   PT_PIECE_PORTAL_ON = true;
constexpr int    PT_NEAR_KING_DIST = 2;
constexpr int    PT_KING_NEWS = 3;
constexpr double PT_PIECE_NEAR_KING_PEN = 12.0;
// PT_LEN_ON: the length memory (World::ptUpdateLens): an ally's length is the longest evidence of the last PT_LEN_MEMORY rounds unless its
// whole chain is in view; the king class, the gathering goal and the late feed read it (a partial sighting is a lower bound).
constexpr bool   PT_LEN_ON = true;
constexpr int    PT_LEN_MEMORY = 20;
// Endgame 2 (after V1: the second died but its drops rarely reached the king): PT_ENDFEED_ON = from PT_ENDGAME_ROUND a non-king feeds the
// king class (la >= king length - 2) on sight within FEED_MAX_DIST, without waiting for the late window; PT_KING_GRAB_ON = the late king
// keeps the fresh-drop pull (grab; FORTRESS turns it off in the last GRAB_KING_ROUNDS); PT_END_GATHER_W = the gathering leaf weight per
// tile from PT_ENDGAME_ROUND (FORTRESS GATHER_W 0.12).
constexpr bool   PT_ENDFEED_ON = true;
constexpr bool   PT_KING_GRAB_ON = true;
constexpr double PT_END_GATHER_W = 0.4;
// --- exp/portals v2 (PLAN-v2.md, 2026-10-01 06:30) ---
// A1 PT2_POCKET_ON: every dragon pays PT2_POCKET_PEN per step onto a pocket (ptmap POCKET: a one-tile compartment behind a portal; a head that
// enters cannot leave). V7 games: 50 pocket visits a game, each eating 0.5-1 pearl, most ending in an escape split whose stub dies there
// (net about -94 length a game before re-eaten drops), against U-rooms +130 and the corridor about -4.
constexpr bool   PT2_POCKET_ON = true;
constexpr double PT2_POCKET_PEN = 40.0;


// --- unsw-swarm v1.3 (versions/v1.3/VERSION.md) ---
// HV pocket harvest (swarm rows Trauma and Slithery a/b; research/observations/pocket-harvest.md §7): a non-king piece of length <= HV_START_LEN
// takes a fountain pocket (World::ensurePockets) with >= HV_MIN_FOOD pearls expected on arrival that no fresh ally head holds or claims and the
// enemy does not reach first; it approaches the mouth (sd claim channel, FG_W_FRONT pull), is scripted from HV_TRIGGER steps of the mouth
// (nearest food inside, legal steps only, no dead-end penalty), splits L-2 out once length >= 4 and it ate >= HV_EAT_SPLIT since entry (or no
// food is ahead) with a free exit at the tail; the length-2 parent goes on. Not from HV_LAST_ROUND, nor with fewer than ETA + depth + HV_SLACK
// rounds left. false = v1.2.
constexpr bool   HARVEST_ON = true;
constexpr int    HV_START_LEN = 3;
constexpr int    HV_MIN_FOOD = 2;
constexpr int    HV_TRIGGER = 2;
constexpr int    HV_EAT_SPLIT = 2;
constexpr int    HV_SLACK = 6;
constexpr int    HV_LAST_ROUND = 480;
// HV2 mouth queue (Trauma only; its two fountain pockets are width-1 corridors of 8 with 6 fountains): a second piece may take a pocket an ally
// is working (one family inside + one piece outside; another outside claim with a smaller or equal ETA holds the slot), waits within FG_HOLD of
// the mouth and enters only once no ally head is inside or on the mouth; its lease is HV2_WAIT rounds longer. false = HV's one family a pocket.
constexpr bool   HV2_ON = false;
constexpr int    HV2_WAIT = 20;
// KR king-news relay chain (both engines): a non-king passes news of a longer fresh ally that is at most KR_AGE rounds old and newer than the
// news it last passed on, on all four rays, at most once every KR_GAP rounds (KR_GAP_SW in the swarm engine). Replaces v1.1's one-shot beacon
// relay (FORTRESS before GATHER_BROADCAST). false = v1.2.
constexpr bool   KR_ON = false;
constexpr int    KR_AGE = 8;
constexpr int    KR_GAP = 2;
constexpr int    KR_GAP_SW = 4;

// --- unsw-swarm v1.6 (versions/v1.6/VERSION.md): the conversion module CONV2 (conv2.cpp) ---
// The swarm rows Slithery Fight a/b, Schooltime a and Trauma (policy.hpp makeConfig; research/observations/conversion-protocol.md §10, §12). From the
// conversion clock it replaces sf's recipient choice (main and late branches) with one recipient per process, the elected king K:
//   election (every turn): candidates are this dragon and the allies with news within BELIEF_FRESH rounds, at the C2 length memory's length
//     (max(estLen, minLen)); ties go to the lower id. The incumbent K stays until a candidate is CV2_H1 longer (before CV2_CAND), max(CV2_H2,
//     len / CV2_H2_DIV) longer (CV2_CAND to CV2_FREEZE) or max(CV2_H3, len / CV2_H3_DIV) longer (frozen, from CV2_FREEZE), or until its news is
//     older than BELIEF_FRESH rounds. A process whose K is itself never feeds.
//   feed: a piece or a mid (length < CV2_BIG) dies into its own neck when K's head is in view, K is >= length + CV2_MARGIN (no absolute floor: the
//     bootstrap of a short king on Trauma and Slithery b) and K can reach our head (the first drop) within CONV_MAX_DIST steps (K's front); a big
//     (>= CV2_BIG) only from CV2_FREEZE, into a K at least as long (the late merge), with the rounds K needs to walk its body (distance + length +
//     CV2_MERGE_SLACK <= 499 - round). sf's other conditions stay: not the escape stub, not a young piece, >= CONV_MIN_UNITS units, our head in the
//     2-core, no enemy head within SF_ENEMY_R of K's head nor nearer to our head than K + 1, the pickup queue (" sq#<id>").
//   pull: a dragon that may feed K (the same length gates; mids from CV2_CAND, bigs from CV2_FREEZE) with news of K's head at most CV2_PULL_FRESH
//     rounds old within the phase radius (CV2_R1 / CV2_R2 / CV2_R3 path steps over known edges, bodies ignored) gets a search leaf pull of
//     CV2_PULL_W a tile beyond CV2_HOLD of K's head. Not a pocket harvester (HV), not while another goal holds (sd, HV), not a young piece.
//   yield: a dragon whose K is another dragon leaves the fresh death drops within Manhattan CV2_YIELD_R of K's head (news at most 1 round old) to K
//     (stack11 gh's discount, CONTEST_ALLY_CLOSER) and pays CV2_FRONT_PEN on the tiles K can step to next (K's head seen this turn).
//   relay: the swarm engine's every-other-turn relay carries this process's K (v1.3: the longest fresh ally).
// Tags: " ck#<id>" this process's K (" ck=" it is K itself), " cp<d>" pulled at path distance d, " cy<n>" n drops left to K; the feed's label is
// "feed #<K> d<d> L<len> cv2 k<K's length>" (+ " m" for a big's merge). false = v1.3 (event-identical, tools/fingerprint.js's hash).
constexpr bool   CONV2_ON = true;
constexpr int    CV2_CAND = 350;            // the king candidate's stronger hysteresis from here (Codex §10.1: "r350 잠정 왕")
constexpr int    CV2_FREEZE = 400;          // the recipient id is frozen from here (Codex: "r400 수령 ID 안정화"); the bigs' merge and pull start
constexpr int    CV2_H1 = 2;                // hysteresis before CV2_CAND (length steps)
constexpr int    CV2_H2 = 3, CV2_H2_DIV = 5;
constexpr int    CV2_H3 = 6, CV2_H3_DIV = 3;   // frozen: K gives way only to a much longer dragon (an escape split's child) or to staleness
constexpr int    CV2_MARGIN = 2;            // a piece or a mid feeds a K at least this much longer (Codex: "recipient > donor"; k8's floor 8 dropped)
constexpr int    CV2_BIG = 8;               // a donor this long is a big: it merges into K from CV2_FREEZE (Codex: "elected king >= donor")
constexpr int    CV2_MERGE_SLACK = 6;       // a big merges only with round + distance + length + slack <= 499
constexpr int    CV2_R1 = 10, CV2_R2 = 16, CV2_R3 = 24;   // the pull radius (path steps to K's head) before CV2_CAND, to CV2_FREEZE, after
constexpr int    CV2_PULL_FRESH = 6;        // news of K's head at most this old pulls
constexpr double CV2_PULL_W = 0.3;          // leaf penalty a tile beyond CV2_HOLD (sd FG_W_FRONT 0.4, gathering GATHER_W 0.12)
constexpr int    CV2_HOLD = 3;              // no pull within this path distance of K's head (the feed reaches CONV_MAX_DIST = 3)
constexpr int    CV2_YIELD_R = 4;           // fresh drops within this Manhattan distance of K's head are left to K
constexpr double CV2_FRONT_PEN = 2.0;       // soft penalty on the tiles K can step to next (dragons whose K is another)
// v1.6b (versions/v1.6/VERSION.md §6): the four changes after the v1.6 local set, each on its own switch
constexpr bool   CV2_RELAY_K = false;       // true = v1.6 (the relay carries this process's K); false = v1.3's relay (the longest fresh ally), which
                                            // spreads the team's maximum past a region whose processes elected a local K
constexpr bool   CV2_YIELD_ALL = true;      // the yield covers every pearl within CV2_YIELD_R of K's head (not only fresh drops), and a fresh drop seen
                                            // there stays reserved for K CV2_LEASE rounds (also after K moves on); a yielded tile costs CV2_YIELD_PEN
constexpr int    CV2_LEASE = 12;
constexpr double CV2_YIELD_PEN = 0.5;
constexpr bool   CV2_KING_GRAB = true;      // the late king keeps grab (fresh drops x GRAB_VALUE within GRAB_REACH) on conv2 rows (its gifts)
constexpr bool   CV2_HV_YIELD = true;       // from CV2_FREEZE a pocket harvester still approaching (outside the pocket) gives way to the pull
constexpr int    CV2_KMIN = 8;              // a piece or a mid feeds (and is pulled to) a K of at least this length (k8's floor) unless the bootstrap
                                            // holds (v1.6g G2: our units <= CV2_BOOT_UNITS; v1.6b: Trauma's row)
constexpr int    CV2_MERGE_MAX = 12;        // a big merges into K only up to this length (Codex: "relay L5-12"); longer ones stay as the backup
constexpr bool   CV2_PORTAL_SAFE = true;    // a crossing whose known exit is out of view and within CV2_PORTAL_NEAR + K's news age of K's head costs
                                            // CV2_PORTAL_PEN (the Portals module's rule), and the pull field does not pass portals
constexpr int    CV2_PORTAL_NEAR = 2;
constexpr double CV2_PORTAL_PEN = 12.0;
// v1.6g (versions/v1.6/VERSION.md §8): map-independent CONV2. Every rule reads runtime state only (round, our unit count, lengths, positions, news);
// the rows choose the clock (the swarm rows' own, the Unknown row's 335, FORTRESS-late CV2_FORT_START).
constexpr bool   CV2_ALL_SWARM = true;      // G1: every SWARM row runs CONV2 (the Unknown row too); false = v1.6b's SE rows only
constexpr int    CV2_BOOT_UNITS = 12;       // G2: the recipient floor of pieces and mids is 0 (the bootstrap) while our units <= this, else CV2_KMIN
                                            // (Trauma's median heads r250 / r350 are 12 / 9; Slithery and Schooltime 18-48)
constexpr bool   CV2_LEN_MEM = true;        // G3: a process without C2 (unknown maps, before recognition) reads lengths from CONV2's own memory: per
constexpr int    CV2_LEN_MEMORY = 20;       //   ally the largest evidence of the last CV2_LEN_MEMORY rounds; a whole chain in view or its newer direct report
                                            //   replaces it
constexpr double CV2_PULL_W_BIG = 0.6;      // G4: the leaf pull of a big that may merge (CV2_BIG..CV2_MERGE_MAX); a merge gives K 4-6 pearls
constexpr bool   CV2_FORT_ON = false;       // G5: the default FORTRESS config (unknown maps, PD undecided, PD b) runs CONV2 from CV2_FORT_START in its own
constexpr int    CV2_FORT_START = 400;      //   instantiation decideImpl<5> (Autarky / PD a and Portals keep theirs); off = v1.3's FORTRESS
// evaluation only (exp/gen's construction; false in the shipped build): an unknown map (World::mapNone) runs SWARM with the Unknown row, and
// recognition forced off (the known maps as unseen ones)
constexpr bool   CV2_EVAL_UNKNOWN_SWARM = false;
constexpr bool   CV2_EVAL_MAPID_OFF = false;
// v1.6g+H0 (versions/v1.6/VERSION.md §12): CONV2's length reading; both off = v1.6g
constexpr bool   CV2_EVIDENCE_LEN = true;   // H0: CONV2 reads an ally's evidence length (minLen: sightings, direct reports, relays), never estLen's sprint
                                            // guess (World: >= 4 for a dragon at the edge of the view; with C2 it never comes down)
constexpr int    CV2_LEN_CONFIRM = 8;       // H0b: a length below CV2_KMIN whose exact evidence (a whole chain in view, a direct report: World::lenRoundOf)
                                            // is older than this many rounds gives way to the visible part when the head is in view now; 0 = off

}} // namespace seed0::P
