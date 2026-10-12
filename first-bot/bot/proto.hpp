// proto.hpp — wire protocol 3.0.0 reader/writer. Never throws, never over-reads a block.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace seed0 {

inline int dirFromCharSafe(char c) {
    switch (c) { case 'N': return 0; case 'E': return 1; case 'S': return 2; case 'W': return 3; default: return -1; }
}

struct InitBlock {
    int id = 0;
    char team = 'A';
    int W = 0, H = 0;
    int unitLimit = 64;
    bool ok = false;
};

struct TileObs {
    int x = 0, y = 0;
    bool pearl = false;
    int pearlIn = -1; // rounds until next spawn attempt; -1 never
};

struct PartObs {
    char team = 'A';
    int id = 0;
    int x = 0, y = 0;
    int dir = 0;     // head: heading; body: direction toward the head
    bool head = false;
};

struct Echoes { int kelp = 0, ally = 0, allyHead = 0, enemy = 0, enemyHead = 0; bool present = false; };

struct RoundBlock {
    int round = 0;
    int dir = 0;      // our facing at start of turn
    int length = 0;
    int unitCount = 1;
    std::vector<uint64_t> msgs;
    Echoes echoes;
    TileObs tiles[49];              // row-major, row 0 = three north of head, col 0 = three west
    std::vector<PartObs> parts;
    // Edge tokens as read: hedge[r][c] r in 0..7 (north edge of window row r; r=7 is south edge of row 6),
    // vedge[r][c] c in 0..7 (west edge of window col c; c=7 is east edge of col 6). Value: -2 kelp, -1 open, >=0 portal id.
    int hedge[8][7];
    int vedge[7][8];
    bool ok = false;          // block fully and consistently parsed
    bool endgame = false;     // ENDGAME or EOF: stop
};

class Reader {
  public:
    Reader();
    // Reads the init block. Returns false at EOF.
    bool readInit(InitBlock& out);
    // Reads one round block. Returns false at EOF/ENDGAME (caller exits).
    bool readRound(RoundBlock& out);
  private:
    std::vector<char> buf_;
    size_t pos_ = 0, end_ = 0;
    bool eof_ = false;
    bool fill();
    // Next non-empty line split into tokens (comments after '#' removed). Returns false at EOF.
    bool nextLine(std::vector<std::string>& toks);
    bool peekLine(std::vector<std::string>& toks); // like nextLine but does not consume
    bool havePeek_ = false;
    std::vector<std::string> peek_;
    std::string line_;
};

class Writer {
  public:
    void move(const char* dirs) { out_ += "MOVE "; out_ += dirs; out_ += '\n'; }
    void split(int k) { out_ += "SPLIT "; out_ += std::to_string(k); out_ += '\n'; }
    void sonar(int dir, uint64_t v) { out_ += "SONAR "; out_ += "NESW"[dir & 3]; out_ += ' '; out_ += std::to_string(v); out_ += '\n'; }
    void indicator(const std::string& s) { out_ += "INDICATOR "; out_ += s; out_ += '\n'; }
    void log(const std::string& s) { out_ += "LOG "; out_ += s; out_ += '\n'; }
    // Appends PROTOCOL 3 and ENDTURN, writes everything in one write, clears.
    void endTurn();
    size_t size() const { return out_.size(); }
  private:
    std::string out_;
};

} // namespace seed0
