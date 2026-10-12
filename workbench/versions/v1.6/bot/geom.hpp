// geom.hpp — directions, wrapped coordinates, edge/portal conventions.
#pragma once
#include <cstdint>

namespace seed0 {

// Direction order matches the protocol's sonar order and edge arrays: N, E, S, W.
enum Dir : int { N = 0, E = 1, S = 2, W = 3 };
constexpr int DX[4] = {0, 1, 0, -1};
constexpr int DY[4] = {-1, 0, 1, 0};
constexpr char DIRCH[5] = "NESW";
inline constexpr int opp(int d) { return (d + 2) & 3; }
inline constexpr int leftOf(int d) { return (d + 3) & 3; }
inline constexpr int rightOf(int d) { return (d + 1) & 3; }
inline int dirFromChar(char c) {
    switch (c) { case 'N': return N; case 'E': return E; case 'S': return S; case 'W': return W; default: return -1; }
}

// Edge state as seen from a tile. UNKNOWN until observed. Kelp blocks; a portal leads to its partner edge.
enum EdgeKind : uint8_t { EDGE_UNKNOWN = 0, EDGE_OPEN = 1, EDGE_KELP = 2, EDGE_PORTAL = 3 };

struct Geo {
    int W = 1, H = 1;
    inline int wrapX(int x) const { x %= W; return x < 0 ? x + W : x; }
    inline int wrapY(int y) const { y %= H; return y < 0 ? y + H : y; }
    inline int idx(int x, int y) const { return y * W + x; }
    inline int tiles() const { return W * H; }
    inline int stepIdx(int t, int d) const {
        int x = t % W, y = t / W;
        return idx(wrapX(x + DX[d]), wrapY(y + DY[d]));
    }
    // Shortest wrapped distance along one axis.
    inline int dx(int a, int b) const { int d = b - a; if (d > W / 2) d -= W; if (d < -W / 2) d += W; return d; }
    inline int dy(int a, int b) const { int d = b - a; if (d > H / 2) d -= H; if (d < -H / 2) d += H; return d; }
    inline int cheb(int t1, int t2) const {
        int ax = abs(dx(t1 % W, t2 % W)), ay = abs(dy(t1 / W, t2 / W));
        return ax > ay ? ax : ay;
    }
    inline int manhattan(int t1, int t2) const { return abs(dx(t1 % W, t2 % W)) + abs(dy(t1 / W, t2 / W)); }
    static inline int abs(int v) { return v < 0 ? -v : v; }
};

} // namespace seed0
