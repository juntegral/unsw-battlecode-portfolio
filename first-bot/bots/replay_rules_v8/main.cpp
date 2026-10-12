#define RR_YIELD 1
#define RR_REVERSE 1
#define RR_REVERSE_UNITS_DIV 2
#define RR_REVERSE_CONTINUE 1
#define RR_REVERSE_COOLDOWN 0
#include "helper.hpp"
#ifndef RR_REVERSE
#define RR_REVERSE 0        // cycle 16: reversal escape. 0 off (= v7), 1 no legal first step (R1a), 2 R1a + gate proves every checked move doomed (R1b)
#endif
#ifndef RR_REVERSE_MINLEN
#define RR_REVERSE_MINLEN 6  // only dragons of at least this length reverse (the stub left behind is 2 long)
#endif
#ifndef RR_HSWAP
#define RR_HSWAP 0        // cycle 15: learned-hazard optimistic swap at the final choice. 0 off (= v7), 1 fixed gap (HS-F), 2 expected-loss gap (HS-E)
#endif
#ifndef RR_HSWAP_HI
#define RR_HSWAP_HI 0.5    // swap only if the chosen first move has calibrated P(doomed within 15 rounds) >= this
#endif
#ifndef RR_HSWAP_LO
#define RR_HSWAP_LO 0.1    // ... to a first move with P <= this
#endif
#ifndef RR_HSWAP_GAP
#define RR_HSWAP_GAP 34.   // HS-F: largest score loss accepted (2 pearls); HS-E: points per expected unit of length saved
#endif
#ifndef RR_HSWAP_MINLEN
#define RR_HSWAP_MINLEN 6  // the model was trained on dragons of length >= 6
#endif
#if RR_HSWAP
#include "hazard.hpp"
#endif
#include <algorithm>
#include <cmath>
#include <limits>

// Independent replay-rules v8 candidate (cycle 16: reversal escape; cycle 15: learned-hazard optimistic swap (off); cycle 14: ally-protective gate; cycle 12: hard feasibility gate; cycle 11: split deadline). Only the official protocol helper is reused.
// Split tuning: below RR_SWARM living units every dragon may split (swarm / elimination insurance);
// at or above it, each dragon spends at most RR_BUDGET splits and then grows (longest-dragon tiebreak).
#ifndef RR_SWARM
#define RR_SWARM 8  // chosen by sweep-20260924T150853Z: fewest eliminations, 16/16 vs H2
#endif
#ifndef RR_BUDGET
#define RR_BUDGET 1
#endif
#ifndef RR_RAM
#define RR_RAM 1     // v5 (situation S2b): expected loss from enemy heads that can ram us within their sprint range
#endif
#ifndef RR_RAM_W
#define RR_RAM_W 34. // points per expected unit of length lost: 2 pearls (lost growth + longest-dragon tiebreak); sweep 17/34/51/85, see FEEDBACK
#endif
#ifndef RR_FREE_SPLIT
#define RR_FREE_SPLIT 0 // cycle 11 variant C: no per-dragon split budget (deadline + safety + map cap only)
#endif
#ifndef RR_GATE
#define RR_GATE 1        // v7 (cycle 12): never pick a move the bot's own optimistic model proves doomed if another is not
#endif
#ifndef RR_GATE_NODES
#define RR_GATE_NODES 1500 // node budget per verdict; beyond it the verdict is "unknown" and never blocks
#endif
#ifndef RR_GATE_MIN_H
#define RR_GATE_MIN_H 0     // minimum look-ahead in single steps (look-ahead = max(length+2, this), at most 40)
#endif
#ifndef RR_GATE_MINLEN
#define RR_GATE_MINLEN 5    // gate dragons of at least this length
#endif
#ifndef RR_GATE_UNKNOWN_OPEN
#define RR_GATE_UNKNOWN_OPEN 1 // diagnosis knob: 0 treats never-seen edges as kelp inside the gate model
#endif
#ifndef RR_GATE_OPT_VACATE
#define RR_GATE_OPT_VACATE 1   // diagnosis knob: 0 uses proven tails only (unproven chains never vacate)
#endif
#ifndef RR_APG
#define RR_APG 0          // cycle 14 closed (no promotion): 0 off, 1 protect every visible ally (reciprocal), 2 protect visible allies at least as long as me (priority)
#endif
#ifndef RR_APG_MINLEN
#define RR_APG_MINLEN 5   // protect allies whose visible body (from the head) is at least this long
#endif
#ifndef RR_APG_HIDDEN
#define RR_APG_HIDDEN 4   // cycle 14 dev 1: segments assumed beyond the view when an ally's visible chain runs out of view (no memory)
#endif
#ifndef RR_APG_UNKNOWN_OPEN
#define RR_APG_UNKNOWN_OPEN 1 // cycle 14 dev 2: 0 = never-seen edges are kelp in the ALLY model only (self gate unchanged)
#endif
#ifndef RR_APG_TRIES
#define RR_APG_TRIES 40     // cycle 14 dev 2: candidates checked for a sparing move when the chosen move harms an ally
#endif
#ifndef RR_GATE_TRIES
#define RR_GATE_TRIES 10   // alternatives checked, in score order
#endif
#ifndef RR_GATE_OCC
#define RR_GATE_OCC 1   // cpu-fix: O(1) body membership in the gate DFS (occupancy counts). Same DFS, verdicts and node counts
#endif
#ifndef RR_GATE_TURN_NODES
#define RR_GATE_TURN_NODES 8000 // cpu-fix: gate DFS nodes per turn over all verdicts (0 = no cap); a verdict gets min(RR_GATE_NODES, nodes left)
#endif
#ifndef RR_POCKET
#define RR_POCKET 1  // v3: penalise moves into a visible pocket smaller than our length
#endif
// cycle 19 (lever 1, next-lever/ANALYSIS.md 6.3): a dragon yields around a visibly longer own dragon. It leaves the pearls within
// RR_YIELD_RADIUS free steps of that dragon's head to it and keeps its own head out of that zone. The split, fallback, reversal and
// gate code is unchanged; only the scoring of search paths (1) or the pick among search paths before the gate (2) changes.
#ifndef RR_YIELD
#define RR_YIELD 0          // 0 off (= R1e2 exactly), 1 soft penalty (Y-S), 2 hard avoidance when a safe alternative exists (Y-H)
#endif
#ifndef RR_YIELD_MARGIN
#define RR_YIELD_MARGIN 2   // protect a visible ally head whose known length lb >= my LENGTH + margin (lb is a lower bound: never mutual)
#endif
#ifndef RR_YIELD_ABS
#define RR_YIELD_ABS 6      // ... and lb >= this (no yielding among tiny dragons)
#endif
#ifndef RR_YIELD_MEMORY
#define RR_YIELD_MEMORY 60  // rounds a remembered visible length (unproven chain) stays valid
#endif
#ifndef RR_YIELD_RADIUS
#define RR_YIELD_RADIUS 2   // zone = cells within this many steps of a protected head through visible free cells
#endif
#ifndef RR_YIELD_ENTER
#define RR_YIELD_ENTER 8.   // Y-S: points per path step that lands in a zone
#endif
#ifndef RR_YIELD_EAT
#define RR_YIELD_EAT 17.    // Y-S: points per zone pearl eaten on the path (cancels the 17-point growth reward)
#endif
#ifndef RR_YIELD_DSLACK
#define RR_YIELD_DSLACK 5.  // Y-H: extra danger (points) the replacement path may carry
#endif
namespace rr {
using namespace unswbc;
constexpr char DIRS[] = "NESW";
constexpr int UNKNOWN = -2, WALL = -1, OPEN = -3;
struct Cell {
    int seen = -1, owner = -1, team = -1, facing = 0, timer = -1, last_visit = -1000;
    bool head = false, pearl = false;
};
struct State {
    std::vector<int> body, eaten;
    int length = 0, gains = 0;
    bool complete = false;
};
struct Action { std::string moves; int split = 0; double score = -1e30;
#if RR_YIELD
    bool yz = false; double trap = 0., danger = 0.; // cycle 19: path lands in a yield zone; evaluate()'s trap and danger terms
#endif
};
struct Policy {
    int w, h, n, round = 0, uid = 0, team = 0, facing = 0, units = 0, limit = 64;
    int splits_done = 0; // v2: per-process split budget (each dragon is its own process)
    int born = -1; bool reborn = false; // analysis refinement: first round seen; born by reversal (first turn after round 0 with length >= 4)
    // cycle 11: observed foraging rate of this dragon (pearls per round over the last 60 rounds).
    // eaten = length change + segments spent on sprints and splits since the previous turn.
    int last_len = -1, last_round = -1, last_sprint = 0, last_split = 0, eaten_sum = 0;
    std::vector<int> eaten_window;
    double forage_rate() const {
        if (int(eaten_window.size()) < 10) return .08; // prior: 6.7-8.4 pearls per 100 moves online
        return std::min(.30, std::max(.02, double(eaten_sum) / eaten_window.size()));
    }
    // A 2-segment child can still catch up with the parent's post-split length before round 500.
    bool split_deadline_ok(int len, int r) const {
        return r + int((len - 4) / forage_rate()) + 10 <= 500;
    }
    void note_turn(int len, int r) {
        if (last_round == r - 1 && last_len >= 0) {
            int eaten = std::max(0, len - last_len + last_sprint + last_split);
            eaten_window.push_back(eaten); eaten_sum += eaten;
            if (eaten_window.size() > 60) { eaten_sum -= eaten_window.front(); eaten_window.erase(eaten_window.begin()); }
        }
        last_len = len; last_round = r; last_sprint = 0; last_split = 0;
    }
    void note_action(Action const& a) {
        last_sprint = a.moves.size() > 1 ? int(a.moves.size()) - 1 : 0;
        last_split = a.split;
    }
    std::vector<int> own_vacate; // v3: moves until a visible body segment (own unlinked or other dragon) leaves
    std::vector<int> opt_vacate; // v7: same ranks from the visible end of every chain, proven tail or not (a lower bound)
    mutable std::vector<Action> cands; // v7: every path the search scored, in search order
    bool gate_on = RR_GATE;
    int gate_budget = 0;
#if RR_GATE_OCC
    std::vector<int> gocc; // cpu-fix: gocc[p] = times cell p occurs in the gate DFS body (all zero outside verdict())
#endif
#if RR_GATE_TURN_NODES
    int gate_turn_left = RR_GATE_TURN_NODES; // DIAGNOSTIC ONLY (not the candidate): start full so a direct verdict() outside choose() is not capped at 0
#endif
    // cycle 14: visible allies to protect this turn (head-first visible body chain, escapable with my current body)
    struct Protected { int id; std::vector<int> body; int hidden = 0; }; // hidden: segments beyond the view (they leave first)
    std::vector<Protected> protect;
    std::unordered_map<int,std::pair<int,int>> ally_len; // cycle 14 dev 1: ally id -> (max visible length seen, round seen)
    std::vector<int> trail;      // v4: every cell our head entered, oldest first; the body is its last `length` cells
    mutable std::string dbg;     // RR_DEBUG builds only: per first-step option trace
    mutable std::pair<int,bool> last_room{-1,false};
    mutable double last_danger=0.;
#if RR_YIELD
    // cycle 19: yield zone of this turn (cells near protected ally heads), remembered visible ally lengths, current search path
    std::vector<char> yzone;
    bool yactive = false;
    int yprot = 0;
    std::unordered_map<int,std::pair<int,int>> ylen; // ally id -> (known length: exact if proven, else max visible chain, round)
    mutable double last_trap = 0.;
    mutable int ypath[3] = {0,0,0};
#endif
    std::vector<Cell> cells;
    std::vector<int> edges;
    std::unordered_map<int, std::vector<int>> portals;
    std::vector<double> threat;
    // v5: visible enemy heads. cap = sprint range (observed length - 1, or 6 if the tail is not proven visible);
    // dist = steps the head needs to reach each cell through free cells (255 = cannot within cap).
    struct Hunter { int vis = 0; std::vector<unsigned char> dist; };
    std::vector<Hunter> hunters;
    explicit Policy(int width, int height) : w(width), h(height), n(w*h), cells(n), edges(2*n, UNKNOWN), threat(n) {}
    int at(int x, int y) const { return ((y%h+h)%h)*w + (x%w+w)%w; }
    int adjacent(int p, int d) const {
        static constexpr int dx[] = {0,1,0,-1}, dy[] = {-1,0,1,0};
        return at(p%w+dx[d], p/w+dy[d]);
    }
    int edge_key(int p, int d) const {
        return d==0 ? p : d==2 ? adjacent(p,2) : n+(d==1 ? adjacent(p,1) : p);
    }
    void set_edge(int p, int d, int value) {
        int key = edge_key(p,d);
        edges[key] = value;
        if (value >= 0) {
            auto& pair = portals[value];
            if (std::find(pair.begin(),pair.end(),key)==pair.end()) pair.push_back(key);
        }
    }
    // Returns a destination, WALL, or UNKNOWN. Portal direction is unchanged.
    int step(int p, int d) const {
        int key = edge_key(p,d), edge = edges[key];
        if (edge==WALL || edge==UNKNOWN) return edge;
        if (edge==OPEN) return adjacent(p,d);
        auto it = portals.find(edge);
        if (it==portals.end() || it->second.size()!=2) return UNKNOWN;
        int other = it->second[0]==key ? it->second[1] : it->second[0];
        if ((other>=n)!=(key>=n)) return UNKNOWN;
        int q = other%n;
        return d==0 ? adjacent(q,0) : d==3 ? adjacent(q,3) : q;
    }
    bool fresh(int p) const { return p>=0 && cells[p].seen==round; }
    static bool contains(std::vector<int> const& values, int p) {
        return std::find(values.begin(),values.end(),p)!=values.end();
    }
    bool occupied(State const& s, int p) const {
        if (contains(s.body,p)) return true;
        if (!fresh(p) || cells[p].owner<0) return false;
        return cells[p].owner!=uid || !s.complete;
    }
    void observe(Controller const& ct, int r) {
        round=r; uid=ct.get_id(); team=ct.get_team().value; units=ct.get_unit_count(); limit=ct.unit_limit;
        facing=std::find(DIRS,DIRS+4,ct.get_dir().value)-DIRS;
        for (auto const& tile:ct.get_tiles()) {
            auto pos=tile.get_position(); int p=at(pos.x,pos.y); auto& c=cells[p];
            c.seen=round; c.pearl=tile.has_pearl(); c.timer=tile.get_pearl_time(); c.owner=-1; c.head=false; c.team=-1;
            if (auto part=tile.get_dragon()) {
                c.owner=part->get_id(); c.team=part->get_team().value; c.head=part->is_head();
                c.facing=std::find(DIRS,DIRS+4,part->get_dir().value)-DIRS;
            }
            for (int d=0;d<4;d++) {
                auto const& e=tile.get_edge(Direction(DIRS[d]));
                set_edge(p,d,!e.is_passable()?WALL:e.is_portal()?e.get_portal_id():OPEN);
            }
        }
        auto pos=ct.get_position(); cells[at(pos.x,pos.y)].last_visit=round;
        std::fill(threat.begin(),threat.end(),0.);
        hunters.clear();
#if RR_RAM
        for (int p=0;p<n;p++) if (fresh(p) && cells[p].head && cells[p].team!=team) {
            int id=cells[p].owner, vis=0; bool tail=false;
            for (int q=0;q<n;q++) if (fresh(q) && cells[q].owner==id) {
                vis++;
                bool pointed=false; // some visible segment of this dragon points at q
                for (int d=0;d<4 && !pointed;d++) { int z=step(q,d); if (z>=0 && fresh(z) && cells[z].owner==id && !cells[z].head && step(z,cells[z].facing)==q) pointed=true; }
                if (!pointed && (q!=p || vis==1)) { // an end of the visible chain: proven tail if its whole neighbourhood is seen
                    bool seen=true; for (int d=0;d<4;d++) { int z=step(q,d); if (z==UNKNOWN || (z>=0 && !fresh(z))) seen=false; }
                    if (seen && q!=p) tail=true;
                }
            }
            // A lone visible head is never a whole dragon (a sprint needs length > 2, so length >= 2 always):
            // its body is outside the view or beyond a portal, so its range is unknown.
            if (vis==1) tail=false;
            int cap=tail ? std::min(6,vis-1) : 6;
            if (cap<1) continue;
            Hunter hunter; hunter.vis=vis; hunter.dist.assign(n,255);
            std::vector<int> queue{p}; hunter.dist[p]=0;
            for (std::size_t i=0;i<queue.size();i++) {
                int x=queue[i]; if (hunter.dist[x]>=cap) continue;
                for (int d=0;d<4;d++) {
                    int q=step(x,d);
                    if (q<0 || hunter.dist[q]!=255) continue;
                    if (fresh(q) && cells[q].owner>=0) continue; // bodies (ours included) block the sprint
                    hunter.dist[q]=hunter.dist[x]+1; queue.push_back(q);
                }
            }
            hunters.push_back(std::move(hunter));
        }
#endif
        for (int p=0;p<n;p++) if (fresh(p) && cells[p].head && cells[p].team!=team) {
            for(int d=0;d<4;d++) {
                int q=step(p,d);
                if (q>=0 && fresh(q) && (cells[q].owner<0 || cells[q].owner==uid)) threat[q]+=1.;
            }
        }
    }
    State initial(Controller const& ct) const {
        State s; s.length=ct.get_length(); auto p=ct.get_position(); s.body.push_back(at(p.x,p.y));
        // Follow visible body links backwards. Partial/unknown tails are never assumed to vacate.
        while (int(s.body.size())<s.length) {
            int previous=-1;
            for (auto const& tile:ct.get_tiles()) {
                auto part=tile.get_dragon(); if(!part || part->get_id()!=uid || part->is_head()) continue;
                auto pos=tile.get_position(); int q=at(pos.x,pos.y);
                if (contains(s.body,q)) continue;
                if (step(q,cells[q].facing)==s.body.back()) { previous=q; break; }
            }
            if (previous<0) break;
            s.body.push_back(previous);
        }
        s.complete=int(s.body.size())==s.length;
        return s;
    }
    bool advance(State& s, int d, bool sprint) const {
        if (sprint && s.length<=2) return false;
        int q=step(s.body.front(),d);
        if (!fresh(q) || occupied(s,q)) return false;
        bool eat=cells[q].pearl && !contains(s.eaten,q);
        s.body.insert(s.body.begin(),q);
        if(eat) { s.eaten.push_back(q); s.length++; s.gains++; }
        else if(s.complete) s.body.pop_back();
        if(sprint) { s.length--; if(s.complete) s.body.pop_back(); }
        // Once the known head prefix covers the entire remaining length, the unseen suffix has vacated.
        if(!s.complete && int(s.body.size())>=s.length) { s.body.resize(s.length); s.complete=true; }
        return true;
    }
    int exits(State const& s) const {
        int result=0;
        for(int d=0;d<4;d++) { State next=s; result+=advance(next,d,false); }
        return result;
    }
    // v3 (situation S1): cells reachable from the head, letting our own body vacate from the tail as
    // time passes. Other bodies and unseen parts of our own body stay blocked. Returns {count, reachedUnknown}.
    // A pocket is only proven when the search stays inside the fresh 7x7 view.
    // shift: tail advance already applied along the evaluated path (1 per step, +1 per sprint step, -1 per pearl)
    std::pair<int,bool> room(State const& s, int shift=0) const {
        // v4: the search continues outside the view through remembered terrain. Outside the view only our
        // own body (known from the trail) blocks; an edge never seen counts as an escape (open).
        int need=s.length, count=1; bool open=false;
        std::vector<int> seen(n,-1), bodyIndex(n,-1), queue; queue.reserve(64);
        for(int i=0;i<int(s.body.size());i++) bodyIndex[s.body[i]]=i;
        queue.push_back(s.body.front()); seen[s.body.front()]=0;
        for(std::size_t i=0;i<queue.size() && count<need;i++) {
            int p=queue[i], t=seen[p];
            for(int d=0;d<4 && count<need;d++) {
                int q=step(p,d);
                if(q==WALL) continue;
                if(q==UNKNOWN) { if(edges[edge_key(p,d)]==UNKNOWN) open=true; continue; } // unseen edge vs unpaired portal
                if(seen[q]>=0) continue;
                // Segment i (from the head) of our body leaves after length-i moves; the length is known.
                if(bodyIndex[q]>=0) {
                    if(t+1<s.length-bodyIndex[q]) continue; // not yet vacated
                } else if(fresh(q) && cells[q].owner>=0) {
                    bool known=int(own_vacate.size())==n && own_vacate[q]>=0;
                    if(cells[q].owner==uid) { if(!s.complete && (!known || t+1<own_vacate[q]-shift)) continue; }
                    else if(!known || t+1<own_vacate[q]) continue; // other dragons: own path does not move them
                } else if(!fresh(q) && !s.complete) { open=true; continue; } // outside view, own body unknown
                seen[q]=t+1; queue.push_back(q); count++;
            }
        }
        return {count, open};
    }
    // v4: extend the trail from what we observe, not from what we intended: the previous head must appear in
    // the visible head-linked body prefix; the cells ahead of it are the steps just taken (sprints and portals
    // included). Otherwise restart from the visible prefix. A split keeps the head, so nothing is added.
    void sync_trail(std::vector<int> const& prefix) {
        if(!trail.empty())
            for(int i=0;i<int(prefix.size());i++) if(prefix[i]==trail.back()) {
                for(int j=i-1;j>=0;j--) trail.push_back(prefix[j]);
                if(trail.size()>4096) trail.erase(trail.begin(),trail.end()-2048);
                return;
            }
        trail.assign(prefix.rbegin(),prefix.rend());
    }
    double evaluate(State const& s, int steps) const {
        int start=s.body.front();
        int free=exits(s), viable=0;
        for(int d=0;d<4;d++) { State t=s; if(advance(t,d,false) && exits(t)>0) viable++; }
        // Bounded visible-space BFS: outside-window space is not declared safe.
        std::vector<int> distance(n,-1), queue; queue.reserve(64); queue.push_back(start); distance[start]=0;
        double food=0.; int frontier=0;
        for(std::size_t i=0;i<queue.size() && i<64;i++) {
            int p=queue[i], dist=distance[p];
#if RR_YIELD
            // cycle 19: pearls (and pearl timers) in a yield zone are left to the protected ally: not a food target
            if (dist>0 && cells[p].pearl && !contains(s.eaten,p) && !(yactive && yzone[p])) food=std::max(food,18./(dist+1));
            if (dist>0 && !cells[p].pearl && cells[p].timer>0 && cells[p].timer<=dist && !(yactive && yzone[p]))
                food=std::max(food,4./(dist+1));
#else
            if (dist>0 && cells[p].pearl && !contains(s.eaten,p)) food=std::max(food,18./(dist+1));
            if (dist>0 && !cells[p].pearl && cells[p].timer>0 && cells[p].timer<=dist)
                food=std::max(food,4./(dist+1));
#endif
            if(dist==6) continue;
            for(int d=0;d<4;d++) {
                int q=step(p,d);
                if (q==UNKNOWN) { frontier++; continue; }
                if(q<0 || occupied(s,q)) continue;
                if(!fresh(q)) { frontier++; continue; }
                if(distance[q]<0) { distance[q]=dist+1; queue.push_back(q); }
            }
        }
        double danger=threat[start]*(10.+std::min(20,s.length)*1.4);
#if RR_RAM
        // Hazard per visible enemy head, fitted on 64 dev games of v4 (tools/headon_miner.js): probability it rams us
        // before our next turn given its steps to our new head, split by whether we are at least twice its seen length.
        static constexpr double BIG[]={0,.175,.038,.018,.009,.009,.008}, SMALL[]={0,.01,.008,.007,.006,.002,.002};
        double ram=0.;
        for (auto const& hunter:hunters) { int k=hunter.dist[start]; if (k>=1 && k<=6) ram+=(s.length>=2*hunter.vis ? BIG : SMALL)[k]; }
        danger=std::max(danger, RR_RAM_W*s.length*ram);
#endif
        last_danger=danger;
        int age=round-cells[start].last_visit;
        double revisit=age<20 ? 5./(1+age) : 0.;
        double trap=(free==0?180.:viable==0?80.:0.);
#if RR_POCKET
        last_room={-1,false};
        if(s.length>=5) { auto [cnt,open]=room(s,2*steps-1-s.gains); last_room={cnt,open}; if(!open && cnt<s.length) trap+=90.+4.*(s.length-cnt); }
#endif
#if RR_YIELD
        last_trap=trap;
#endif
        return 17.*s.gains-20.*(steps-1)+food + 1.2*std::min(free,2)
            + .22*std::min(int(queue.size()),32) + .15*std::min(frontier,12)
            - danger - revisit - trap;
    }
    void search(State const& s, std::string path, Action& best) const {
        for(int d=0;d<4;d++) {
            State next=s;
            if(!advance(next,d,!path.empty())) continue;
            auto moves=path+DIRS[d]; double score=evaluate(next,int(moves.size()));
            if(moves.size()==1 && d==facing) score+=.025;
#ifdef RR_DEBUG
            if(moves.size()==1) dbg+=std::string(" ")+DIRS[d]+":"+std::to_string(int(score))+"/room"+std::to_string(last_room.first)+(last_room.second?"o":"c")+"/d"+std::to_string(int(last_danger));
#endif
            // Deterministic dragon-specific tie break prevents identical flank choices.
            score+=.001*((uid+d*3)%7);
#if RR_YIELD
            {
                int depth=int(moves.size()); ypath[depth-1]=next.body.front(); // the body may drop earlier path cells after sprints
                Action a{moves,0,score}; a.trap=last_trap; a.danger=last_danger;
                if(yactive) {
                    double pen=0.;
                    for(int i=0;i<depth;i++) if(yzone[ypath[i]]) { a.yz=true; pen+=RR_YIELD_ENTER; }
                    for(int e:next.eaten) if(yzone[e]) pen+=RR_YIELD_EAT;
#if RR_YIELD==1
                    a.score-=pen;   // Y-S: soft penalty in the path score (the gate's fallback order uses it too)
#endif
                    (void)pen;
                }
                cands.push_back(a);
                if(a.score>best.score) best=a;
            }
#else
            cands.push_back({moves,0,score});
            if(score>best.score) best={moves,0,score};
#endif
            if(moves.size()<3) search(next,moves,best);
        }
    }
    // v7 (cycle 12): hard feasibility gate. The model uses only the bot's own information and is optimistic: other dragons
    // never advance and their visible segments leave from the visible end of their chain (opt_vacate, a lower bound);
    // no bodies outside the view; unseen edges and unpaired portals are exits; pearls in view are eaten (the tail stays).
    // A move is refused only if it is proven doomed while another move is not; unknown (node budget) never blocks.
    bool gate_blocked(int q, int k) const {
        if(!fresh(q) || cells[q].owner<0 || cells[q].owner==uid) return false;
        auto const& vac = RR_GATE_OPT_VACATE ? opt_vacate : own_vacate;
        return int(vac.size())!=n || vac[q]<0 || vac[q]>k;
    }
    // 1 = can keep moving until single step `horizon` (or reaches an exit), 0 = proven doomed, -1 = unknown.
    int escape(std::vector<int>& body, std::vector<int>& eaten, int k, int horizon) {
        if(k>horizon) return 1;
        if(--gate_budget<0) return -1;
        int order[4]={0,1,2,3}, freeN[4]={-1,-1,-1,-1}, dest[4];
        for(int d=0;d<4;d++) {
            int q=step(body.front(),d); dest[d]=q;
            if(q==UNKNOWN && RR_GATE_UNKNOWN_OPEN) return 1;
#if RR_GATE_OCC
            if(q<0 || gocc[q]>0 || gate_blocked(q,k)) continue;
            int f=0; for(int e=0;e<4;e++) { int z=step(q,e); if((z==UNKNOWN && RR_GATE_UNKNOWN_OPEN) || (z>=0 && gocc[z]==0 && !gate_blocked(z,k+1))) f++; }
#else
            if(q<0 || contains(body,q) || gate_blocked(q,k)) continue;
            int f=0; for(int e=0;e<4;e++) { int z=step(q,e); if((z==UNKNOWN && RR_GATE_UNKNOWN_OPEN) || (z>=0 && !contains(body,z) && !gate_blocked(z,k+1))) f++; }
#endif
            freeN[d]=f;
        }
        std::stable_sort(order,order+4,[&](int a,int b){ return freeN[a]>freeN[b]; });
        bool unknown=false;
        for(int i=0;i<4;i++) {
            int d=order[i]; if(freeN[d]<0) continue; int q=dest[d];
            bool eat=fresh(q) && cells[q].pearl && !contains(eaten,q);
            int tail=body.back();
            body.insert(body.begin(),q); if(eat) eaten.push_back(q); else body.pop_back();
#if RR_GATE_OCC
            gocc[q]++; if(!eat) gocc[tail]--;
#endif
            int r=escape(body,eaten,k+1,horizon);
            body.erase(body.begin()); if(eat) eaten.pop_back(); else body.push_back(tail);
#if RR_GATE_OCC
            gocc[q]--; if(!eat) gocc[tail]++;
#endif
            if(r==1) return 1;
            if(r<0) unknown=true;
        }
        return unknown ? -1 : 0;
    }
    int verdict(State const& s, std::string const& moves) {
        State t=s;
        for(std::size_t i=0;i<moves.size();i++) { int d=int(std::find(DIRS,DIRS+4,moves[i])-DIRS); if(d>3 || !advance(t,d,i>0)) return 0; }
        if(!t.complete) return -1;
        std::vector<int> body=t.body, eaten=t.eaten; gate_budget=RR_GATE_NODES;
#if RR_GATE_TURN_NODES
        if(gate_turn_left<gate_budget) gate_budget=std::max(0,gate_turn_left);   // cpu-fix: per-turn node cap
        int budget0=gate_budget;
#endif
#if RR_GATE_OCC
        if(int(gocc.size())!=n) gocc.assign(n,0);
        for(int p:body) gocc[p]++;
        int v=escape(body,eaten,1,std::min(40,std::max(t.length+2,RR_GATE_MIN_H)));
        for(int p:body) gocc[p]--;
#else
        int v=escape(body,eaten,1,std::min(40,std::max(t.length+2,RR_GATE_MIN_H)));
#endif
#if RR_GATE_TURN_NODES
        gate_turn_left-=budget0-std::max(0,gate_budget);
#endif
        return v;
    }
    // cycle 14 (APG): can ally `vid` keep moving for `horizon` single steps in the optimistic static model, given my body
    // `mine` (my segment i leaves after mine.size()-i moves, as if I kept moving without blocking)? Other bodies stay and
    // leave from their visible chain ends; unseen cells hold no bodies; unseen edges and unpaired portals are exits.
    bool ally_blocked(int q, int k, std::vector<int> const& mine, int vid) const {
        for(int i=0;i<int(mine.size());i++) if(mine[i]==q) return int(mine.size())-i>k;
        if(!fresh(q) || cells[q].owner<0 || cells[q].owner==uid || cells[q].owner==vid) return false;
        return int(opt_vacate.size())!=n || opt_vacate[q]<0 || opt_vacate[q]>k;
    }
    int ally_dfs(std::vector<int>& body, std::vector<int>& eaten, std::vector<int> const& mine, int vid, int k, int horizon, int hidden) {
        if(k>horizon) return 1;
        if(--gate_budget<0) return -1;
        int order[4]={0,1,2,3}, freeN[4]={-1,-1,-1,-1}, dest[4];
        for(int d=0;d<4;d++) {
            int q=step(body.front(),d); dest[d]=q;
            if(q==UNKNOWN && RR_APG_UNKNOWN_OPEN) return 1;
            if(q<0 || contains(body,q) || ally_blocked(q,k,mine,vid)) continue;
            int f=0; for(int e=0;e<4;e++) { int z=step(q,e); if((z==UNKNOWN && RR_APG_UNKNOWN_OPEN) || (z>=0 && !contains(body,z) && !ally_blocked(z,k+1,mine,vid))) f++; }
            freeN[d]=f;
        }
        std::stable_sort(order,order+4,[&](int a,int b){ return freeN[a]>freeN[b]; });
        bool unknown=false;
        for(int i=0;i<4;i++) {
            int d=order[i]; if(freeN[d]<0) continue; int q=dest[d];
            bool eat=fresh(q) && cells[q].pearl && !contains(eaten,q);
            int tail=body.back(); bool popped=false, usedHidden=false;
            body.insert(body.begin(),q);
            if(eat) eaten.push_back(q); else if(hidden>0) usedHidden=true; else { body.pop_back(); popped=true; }
            int r=ally_dfs(body,eaten,mine,vid,k+1,horizon,usedHidden ? hidden-1 : hidden);
            body.erase(body.begin()); if(eat) eaten.pop_back(); if(popped) body.push_back(tail);
            if(r==1) return 1;
            if(r<0) unknown=true;
        }
        return unknown ? -1 : 0;
    }
    int ally_escape(Protected const& v, std::vector<int> const& mine) {
        std::vector<int> body=v.body, eaten; gate_budget=RR_GATE_NODES;
        return ally_dfs(body,eaten,mine,v.id,1,std::min(int(v.body.size())+v.hidden+2,40),v.hidden);
    }
    void build_protect(State const& s) {
        protect.clear();
#if RR_APG
        if(!s.complete) return;
        for(int p=0;p<n;p++) {
            if(!fresh(p) || !cells[p].head || cells[p].owner<0 || cells[p].owner==uid || cells[p].team!=team) continue;
            int id=cells[p].owner; std::vector<int> body{p};
            while(int(body.size())<64) {
                int prev=-1;
                for(int d=0;d<4 && prev<0;d++) { int z=step(body.back(),d);
                    if(z>=0 && fresh(z) && cells[z].owner==id && !cells[z].head && !contains(body,z) && step(z,cells[z].facing)==body.back()) prev=z; }
                if(prev<0) break;
                body.push_back(prev);
            }
            int vis=int(body.size());
            // cycle 14 dev 1: the chain end is the real tail only if every neighbour is visible (no hidden continuation)
            bool proven=true; for(int d=0;d<4;d++) { int z=step(body.back(),d); if(z==UNKNOWN || (z>=0 && !fresh(z))) proven=false; }
            auto& mem=ally_len[id]; if(vis>=mem.first || round-mem.second>60) mem={vis,round};
            int est = proven ? vis : std::max(vis+RR_APG_HIDDEN, round-mem.second<=60 ? mem.first : 0);
#ifdef RR_DEBUG
            dbg+=" ally"+std::to_string(id)+":vis"+std::to_string(vis)+":est"+std::to_string(est);
#endif
            if(est<RR_APG_MINLEN) continue;
            if(RR_APG==2 && !(est>s.length || (est==s.length && id<uid))) continue;
            Protected v{id,body,est-vis};
            int e0=ally_escape(v,s.body);
#ifdef RR_DEBUG
            dbg+=":e0="+std::to_string(e0);
#endif
            if(e0==1) protect.push_back(std::move(v)); // only allies that can escape now can be harmed
        }
#endif
    }
    // True if the path proves some protected ally unable to escape.
    bool harms(State const& s, std::string const& moves) {
        if(protect.empty()) return false;
        State t=s;
        for(std::size_t i=0;i<moves.size();i++) { int d=int(std::find(DIRS,DIRS+4,moves[i])-DIRS); if(d>3 || !advance(t,d,i>0)) return false; }
        for(auto const& v:protect) if(ally_escape(v,t.body)==0) return true;
        return false;
    }
#if RR_YIELD
    // cycle 19 (lever 1): protected allies are visible own dragon heads whose known length lb >= max(my LENGTH + RR_YIELD_MARGIN,
    // RR_YIELD_ABS). lb = the visible body chain from the head (exact when its tail is proven in view, which also resets the
    // memory: a reversal leaves a 2-long stub under the old id), else max(visible chain, max visible chain I saw within
    // RR_YIELD_MEMORY rounds). lb never exceeds the true length (up to stale memory), so two dragons never yield to each other.
    // The zone is every visible free cell within RR_YIELD_RADIUS steps (edges and portals as step()) of a protected head.
    void build_yield(State const& s) {
        yactive=false; yprot=0;
        if(int(yzone.size())!=n) yzone.assign(n,0); else std::fill(yzone.begin(),yzone.end(),0);
        for(int p=0;p<n;p++) {
            if(!fresh(p) || !cells[p].head || cells[p].owner<0 || cells[p].owner==uid || cells[p].team!=team) continue;
            int id=cells[p].owner; std::vector<int> body{p};
            while(int(body.size())<64) {
                int prev=-1;
                for(int d=0;d<4 && prev<0;d++) { int z=step(body.back(),d);
                    if(z>=0 && fresh(z) && cells[z].owner==id && !cells[z].head && !contains(body,z) && step(z,cells[z].facing)==body.back()) prev=z; }
                if(prev<0) break;
                body.push_back(prev);
            }
            int vis=int(body.size());
            bool proven=true; for(int d=0;d<4;d++) { int z=step(body.back(),d); if(z==UNKNOWN || (z>=0 && !fresh(z))) proven=false; }
            auto it=ylen.find(id);
            if(proven || it==ylen.end() || vis>=it->second.first || round-it->second.second>RR_YIELD_MEMORY) ylen[id]={vis,round};
            int lb=std::max(vis, ylen[id].first);
            if(proven) lb=vis;
#ifdef RR_DEBUG
            dbg+=" yally"+std::to_string(id)+":vis"+std::to_string(vis)+(proven?"p":"")+":lb"+std::to_string(lb);
#endif
            if(lb<s.length+RR_YIELD_MARGIN || lb<RR_YIELD_ABS) continue;
            yprot++;
            std::vector<int> q{p}, depth{0};
            for(std::size_t i=0;i<q.size();i++) {
                if(depth[i]>=RR_YIELD_RADIUS) continue;
                for(int d=0;d<4;d++) {
                    int z=step(q[i],d);
                    if(z<0 || !fresh(z) || cells[z].owner>=0 || contains(q,z)) continue;
                    q.push_back(z); depth.push_back(depth[i]+1); yzone[z]=1;
                }
            }
        }
        yactive=yprot>0;
#ifdef RR_DEBUG
        if(yactive) dbg+=" yield[prot="+std::to_string(yprot)+"]";
#endif
    }
#endif
#if RR_YIELD==2
    // cycle 19 (Y-H): the chosen search path lands in a yield zone -> take the best-scoring path that does not, has no more steps,
    // sets no trap (evaluate()'s trap term is 0) and adds at most RR_YIELD_DSLACK danger. None -> keep the chosen path. The gate
    // then checks the pick as usual; if it proves the pick doomed it falls back in score order (the original path first), so a
    // dragon never sacrifices itself for an ally.
    Action yield_hard(Action const& best) const {
        if(!yactive || !best.yz) return best;
        Action pick; bool found=false;
        for(auto const& a:cands) {
            if(a.yz || a.moves.size()>best.moves.size() || a.trap>0. || a.danger>best.danger+RR_YIELD_DSLACK) continue;
            if(!found || a.score>pick.score) { pick=a; found=true; }
        }
#ifdef RR_DEBUG
        dbg+=" yhard["+best.moves+(found?"->"+pick.moves:std::string("->none"))+"]";
#endif
        return found ? pick : best;
    }
#endif
    Action gated(State const& s, Action best, bool certain_death) {
        // The self gate (cycle 12) applies to dragons of length >= RR_GATE_MINLEN; shorter ones only get ally protection.
        bool self_gate = s.length>=RR_GATE_MINLEN;
        int v0=certain_death ? 0 : (self_gate ? verdict(s,best.moves) : 1);
#ifdef RR_DEBUG
        dbg+=" gate["+best.moves+"]="+std::to_string(v0)+"/b"+std::to_string(gate_budget)+" protect"+std::to_string(protect.size());
#endif
        bool best_harms = v0!=0 && harms(s,best.moves);
#ifdef RR_DEBUG
        dbg+=" harm"+std::to_string(best_harms);
#endif
        if(v0!=0 && !best_harms) return best;
        std::vector<Action> order=cands;
        std::stable_sort(order.begin(),order.end(),[](Action const& a,Action const& b){ return a.score>b.score; });
        int tries=0; Action self_only; bool have_self_only=false;
        bool all_doomed=(v0==0), exhausted=true; // cycle 16 (R1b)
        for(auto const& a:order) {
            if(a.moves==best.moves) continue;
            if(++tries>(best_harms ? RR_APG_TRIES : RR_GATE_TRIES)) { exhausted=false; break; }
            int va=self_gate ? verdict(s,a.moves) : 1;
            if(va!=0) all_doomed=false;
#ifdef RR_DEBUG
            dbg+=" alt["+a.moves+"]="+std::to_string(va);
#endif
            if(va==0) continue;
            if(!harms(s,a.moves)) {
#ifdef RR_DEBUG
                dbg+=" gate:"+best.moves+"->"+a.moves;
#endif
                return a;
            }
            if(!have_self_only) { self_only=a; have_self_only=true; }
        }
#if RR_REVERSE>=2
        // cycle 16 (R1b): my own optimistic model proves the chosen move and every other candidate doomed: reverse instead.
        if(v0==0 && all_doomed && exhausted && self_gate && s.length>=RR_REVERSE_MINLEN && units<limit) {
#ifdef RR_DEBUG
            dbg+=" reverse[R1b len="+std::to_string(s.length)+"]";
#endif
            return {"",s.length-2,-1e28};
        }
#endif
        // No candidate both keeps me safe and harms no protected ally: never sacrifice myself for an ally.
        if(v0!=0) return best;
        if(have_self_only) return self_only;
        return best;
    }
#if RR_HSWAP
    // cycle 15: optimistic replacement. Only when the final (gated) first move is very likely doomed and a first move that is
    // unlikely doomed scores almost as well. Never touches splits, fallbacks or the path evaluation (cycle 13 lesson).
    Action hswap(Controller const& ct, State const& s, Action best) {
        int da=int(std::find(DIRS,DIRS+4,best.moves[0])-DIRS); if(da>3) return best;
        auto p=hz::predict(hz::encode(ct,*unswbc::game));
#ifdef RR_DEBUG
        dbg+=" hz["+std::to_string(int(100*p[0]))+","+std::to_string(int(100*p[1]))+","+std::to_string(int(100*p[2]))+","+std::to_string(int(100*p[3]))+"]";
#endif
        if(p[da]<RR_HSWAP_HI) return best;
        std::vector<Action> order=cands;
        std::stable_sort(order.begin(),order.end(),[](Action const& a,Action const& b){ return a.score>b.score; });
        double maxgap = RR_HSWAP==1 ? RR_HSWAP_GAP : RR_HSWAP_GAP*s.length*double(p[da]);
        for(auto const& a:order) {
            if(a.moves.empty()) continue;
            if(a.score < best.score-maxgap) break;   // sorted by score: nothing later can qualify
            int d=int(std::find(DIRS,DIRS+4,a.moves[0])-DIRS);
            if(d>3 || d==da || p[d]>RR_HSWAP_LO) continue;
            double gap = RR_HSWAP==1 ? RR_HSWAP_GAP : RR_HSWAP_GAP*s.length*double(p[da]-p[d]);
            if(a.score < best.score-gap) continue;
            if(s.length>=RR_GATE_MINLEN && verdict(s,a.moves)==0) continue;   // never swap into a proven dead end
#ifdef RR_DEBUG
            dbg+=" hswap:"+best.moves+"->"+a.moves;
#endif
            return a;
        }
        return best;
    }
#endif
    Action choose(Controller const& ct, int r) {
        observe(ct,r); State s=initial(ct); Action best;
        if(born<0) { born=r; reborn = r>1 && s.length>=4; // r>1: a fresh test harness process at round 1 is not a reversal child (a real reversal child is born at round >= 2)
#if RR_REVERSE_CONTINUE
            if(reborn) splits_done=RR_BUDGET;
#endif
        }
        note_turn(s.length, r);
#if RR_GATE_TURN_NODES
        gate_turn_left=RR_GATE_TURN_NODES;
#endif
        // v4 (situation S1b): our whole body is the last `length` cells of our own trail, even outside the view.
        // Use it only when it agrees with the head and with every own segment we can see.
        sync_trail(s.body);
        if(!s.complete && int(trail.size())>=s.length) {
            std::vector<int> body(trail.rbegin(),trail.rbegin()+s.length);
            bool ok=std::equal(s.body.begin(),s.body.end(),body.begin());
            for(int q:body) if(fresh(q) && cells[q].owner!=uid) ok=false;
            for(int q=0;q<n && ok;q++) if(fresh(q) && cells[q].owner==uid && !contains(body,q)) ok=false;
            if(ok) { s.body=body; s.complete=true; }
        }
#ifdef RR_DEBUG
        dbg="trail"+std::to_string(trail.size())+" len"+std::to_string(s.length)+(s.complete?" complete":" partial")+" hunters";
        for(auto const& hh:hunters) dbg+=" v"+std::to_string(hh.vis);
#endif
        // v3: moves until a visible body segment leaves (-1 = treat as permanent).
        // Own segments not linked to the head are nearer our tail: rank each fragment from its tail end
        // (optimistic; our length is known). Other dragons: only fragments whose tail end is proven
        // (every neighbour visible, none of theirs behind it) are ranked; unknown fragments stay walls.
        own_vacate.assign(n,-1); opt_vacate.assign(n,-1);
        {
            std::vector<int> nxt(n,-1); std::vector<char> pointed(n,0);
            auto mine=[&](int p){ return cells[p].owner==uid; };
            auto cand=[&](int p){ return fresh(p) && cells[p].owner>=0 && !(mine(p) && (s.complete || contains(s.body,p))); };
            for(int p=0;p<n;p++) if(cand(p)) { int q=step(p,cells[p].facing);
                if(q>=0 && cand(q) && cells[q].owner==cells[p].owner) { nxt[p]=q; pointed[q]=1; } }
            for(int p=0;p<n;p++) if(cand(p) && !pointed[p]) {
                bool proven=mine(p);
                if(!proven) { proven=true; for(int d=0;d<4;d++) { int q=step(p,d); if(q==UNKNOWN || (q>=0 && !fresh(q))) proven=false; } }
                for(int x=p,k=1; x>=0 && opt_vacate[x]<0; x=nxt[x],k++) opt_vacate[x]=k;
                if(!proven) continue;
                for(int x=p,k=1; x>=0 && own_vacate[x]<0; x=nxt[x],k++) own_vacate[x]=k;
            }
        }
#if RR_YIELD
        build_yield(s);   // cycle 19: before the search, so evaluate() sees this turn's yield zone
#endif
        cands.clear();
        search(s,"",best);
        build_protect(s);
        // v2: any length >= 4 may split, but each dragon only once (last survivor excepted),
        // so the team still branches (Big Empty starts at length 7) and every dragon then grows
        // for the longest-dragon tiebreak instead of being cut back to 2 at length 4.
        // cycle 11: the fixed round<380 cutoff becomes a per-dragon deadline from its observed foraging rate.
        bool budget_ok = RR_FREE_SPLIT ? true : (units<RR_SWARM || splits_done<RR_BUDGET || units==1);
        if (s.complete && s.length>=4 && budget_ok
            && units<std::min(limit,std::max(2,n/12)) && split_deadline_ok(s.length, round)) {
            int parent=s.body.front(), tail=s.body.back(), child_exits=0;
            for(int d=0;d<4;d++) {
                int q=step(tail,d);
                if(fresh(q) && !occupied(s,q) && threat[q]<1.) child_exits++;
            }
            if(exits(s)>0 && child_exits>0 && threat[parent]<1. && threat[tail]<1.) { splits_done++; return {"",2,100.}; }
        }
        // Unknown portal exits are a last resort, never included in a guaranteed-safe sprint.
        int fallback=0; // 1 = unknown exit (optimistically an escape), 2 = head trade (certain death)
        for(int d=0;d<4;d++) {
            int q=step(s.body.front(),d);
            double score=-1e29;
            if(q==UNKNOWN || (q>=0 && !fresh(q))) score=-90.;
            else if(q>=0 && cells[q].head && cells[q].owner!=uid && cells[q].team!=team) score=-140.;
            if(score>best.score) { best={std::string(1,DIRS[d]),0,score}; fallback=score<-100. ? 2 : 1; }
        }
#if RR_REVERSE
        // cycle 16 (R1a): no search candidate (no legal first step) and no unknown exit: split off everything but head and neck.
        if(cands.empty() && fallback!=1 && s.length>=RR_REVERSE_MINLEN && units*RR_REVERSE_UNITS_DIV<limit
#if RR_REVERSE_CONTINUE
           && !(reborn && r-born<RR_REVERSE_COOLDOWN)
#endif
           && ct.can_split(s.length-2)) {
#ifdef RR_DEBUG
            dbg+=" reverse[R1a len="+std::to_string(s.length)+" fallback="+std::to_string(fallback)+"]";
#endif
            return {"",s.length-2,-1e28};
        }
#endif
#if RR_YIELD==2
        if(fallback==0 && !best.moves.empty()) best=yield_hard(best);   // cycle 19 (Y-H): a search path only, before the gate
#endif
#if RR_GATE
#ifdef RR_DEBUG
        if(!(s.complete && s.length>=RR_GATE_MINLEN)) dbg+=" nogate[complete="+std::to_string(s.complete)+" len="+std::to_string(s.length)+"]";
#endif
        if(gate_on && fallback!=1 && s.complete && !best.moves.empty() && (s.length>=RR_GATE_MINLEN || (fallback==0 && !protect.empty()))) best=gated(s,best,fallback==2);
#endif
#if RR_HSWAP
        if(fallback==0 && s.complete && s.length>=RR_HSWAP_MINLEN && best.split==0 && !best.moves.empty()) best=hswap(ct,s,best);
#endif
        if(best.moves.empty()) best.moves=std::string(1,DIRS[facing]);
        return best;
    }
};
}
int main() {
    unswbc::init();
    rr::Policy policy(unswbc::game->width,unswbc::game->height);
    while(unswbc::update(*unswbc::ct,*unswbc::game)) {
        auto a=policy.choose(*unswbc::ct,unswbc::game->get_round_num());
        policy.note_action(a);
#ifdef RR_DEBUG
        std::cout << "LOG " << policy.dbg << "\n";
#endif
        if(a.split) unswbc::ct->do_split(a.split);
        else { std::vector<unswbc::Direction> dirs; for(char d:a.moves) dirs.emplace_back(d); unswbc::ct->make_moves(dirs); }
        unswbc::end_turn();
    }
    return 0;
}
