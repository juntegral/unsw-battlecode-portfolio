// proto.cpp — wire protocol 3.0.0 reader/writer.
//
// Parsing rules mirror the official helper.hpp (labels in order, whitespace tokens, '#' comments,
// blank lines skipped) but nothing here throws: a malformed block sets ok=false and parsing stops,
// so the caller can still emit a safe action. A blocking read before ENDTURN would end the turn with
// no action (suicide), so this reader only ever reads exactly the number of lines the block declares.
#include "proto.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <unistd.h>

namespace seed0 {

Reader::Reader() { buf_.resize(1 << 16); }

bool Reader::fill() {
    if (eof_) return false;
    if (pos_ > 0) { // compact
        if (end_ > pos_) memmove(buf_.data(), buf_.data() + pos_, end_ - pos_);
        end_ -= pos_; pos_ = 0;
    }
    if (end_ == buf_.size()) buf_.resize(buf_.size() * 2);
    for (;;) {
        ssize_t n = ::read(0, buf_.data() + end_, buf_.size() - end_);
        if (n > 0) { end_ += (size_t)n; return true; }
        if (n == 0) { eof_ = true; return false; }
        if (errno == EINTR) continue;
        eof_ = true; return false;
    }
}

bool Reader::nextLine(std::vector<std::string>& toks) {
    if (havePeek_) { toks = peek_; havePeek_ = false; return true; }
    for (;;) {
        // find newline
        size_t i = pos_;
        while (i < end_ && buf_[i] != '\n') i++;
        if (i >= end_) {
            if (!fill()) {
                if (pos_ >= end_) return false; // EOF, nothing left
                i = end_;                        // final unterminated line
            } else continue;
        }
        line_.assign(buf_.data() + pos_, i - pos_);
        pos_ = i < end_ ? i + 1 : i;
        // strip comments and CR
        size_t hash = line_.find('#');
        if (hash != std::string::npos) line_.erase(hash);
        toks.clear();
        size_t p = 0, n = line_.size();
        while (p < n) {
            while (p < n && (line_[p] == ' ' || line_[p] == '\t' || line_[p] == '\r')) p++;
            size_t s = p;
            while (p < n && line_[p] != ' ' && line_[p] != '\t' && line_[p] != '\r') p++;
            if (p > s) toks.emplace_back(line_, s, p - s);
        }
        if (!toks.empty()) return true;
    }
}

bool Reader::peekLine(std::vector<std::string>& toks) {
    if (!havePeek_) { if (!nextLine(peek_)) return false; havePeek_ = true; }
    toks = peek_; return true;
}

static inline bool toInt(const std::string& s, int& v) {
    if (s.empty()) return false;
    char* e = nullptr; long long x = strtoll(s.c_str(), &e, 10);
    if (e == s.c_str() || *e != 0) return false;
    v = (int)x; return true;
}
static inline bool toU64(const std::string& s, uint64_t& v) {
    if (s.empty()) return false;
    char* e = nullptr; unsigned long long x = strtoull(s.c_str(), &e, 10);
    if (e == s.c_str() || *e != 0) return false;
    v = (uint64_t)x; return true;
}
// -2 kelp, -1 open, >=0 portal id, INT32_MIN invalid
static inline int edgeTok(const std::string& s) {
    if (s == ".") return -1;
    if (s == "w") return -2;
    int v; if (toInt(s, v) && v >= 0) return v;
    return -2147483647 - 1;
}

bool Reader::readInit(InitBlock& out) {
    std::vector<std::string> t;
    int seen = 0;
    for (int guard = 0; guard < 16; guard++) {
        if (!peekLine(t)) return false;
        const std::string& L = t[0];
        if (L == "ROUND" || L == "ENDGAME") break; // block ended early; leave for readRound
        nextLine(t);
        if (L == "ID" && t.size() >= 2) { toInt(t[1], out.id); seen |= 1; }
        else if (L == "TEAM" && t.size() >= 2) { out.team = t[1][0] == 'B' ? 'B' : 'A'; seen |= 2; }
        else if (L == "MAP" && t.size() >= 3) { toInt(t[1], out.W); toInt(t[2], out.H); seen |= 4; }
        else if (L == "UNIT_LIMIT" && t.size() >= 2) { toInt(t[1], out.unitLimit); seen |= 8; break; }
        if (seen == 15) break;
    }
    if (out.W <= 0 || out.H <= 0) { out.W = out.W <= 0 ? 10 : out.W; out.H = out.H <= 0 ? 10 : out.H; }
    if (out.unitLimit <= 0) out.unitLimit = 64;
    out.ok = (seen & 4) != 0;
    return true;
}

bool Reader::readRound(RoundBlock& out) {
    std::vector<std::string> t;
    out.ok = false; out.endgame = false; out.msgs.clear(); out.parts.clear(); out.echoes = Echoes{};
    // Seek the ROUND header, discarding anything left over from an earlier truncated parse.
    for (;;) {
        if (!nextLine(t)) { out.endgame = true; return false; }
        if (t[0] == "ENDGAME") { out.endgame = true; return false; }
        if (t[0] == "ROUND" && t.size() >= 2) break;
    }
    if (!toInt(t[1], out.round)) return true; // ok=false
    auto labelled = [&](const char* label, int& v) -> bool {
        if (!nextLine(t) || t.size() < 2 || t[0] != label) return false;
        return toInt(t[1], v);
    };
    if (!nextLine(t) || t.size() < 2 || t[0] != "DIR") return true;
    { int d = dirFromCharSafe(t[1][0]); if (d < 0) return true; out.dir = d; }
    if (!labelled("LENGTH", out.length)) return true;
    if (!labelled("UNIT_COUNT", out.unitCount)) return true;
    int nmsgs = 0;
    if (!labelled("NUM_MSGS", nmsgs) || nmsgs < 0 || nmsgs > 100000) return true;
    out.msgs.reserve((size_t)nmsgs);
    for (int i = 0; i < nmsgs; i++) {
        if (!nextLine(t)) return true;
        uint64_t v; if (!toU64(t[0], v)) return true;
        out.msgs.push_back(v);
    }
    if (!nextLine(t)) return true;
    if (t[0] == "ECHOES") {
        if (t.size() != 6) return true;
        int k, a, ah, e, eh;
        if (!toInt(t[1], k) || !toInt(t[2], a) || !toInt(t[3], ah) || !toInt(t[4], e) || !toInt(t[5], eh)) return true;
        out.echoes = Echoes{k, a, ah, e, eh, true};
        if (!nextLine(t)) return true;
    }
    for (int i = 0; i < 49; i++) {
        if (i > 0 && !nextLine(t)) return true;
        if (t.size() != 4) return true;
        TileObs& o = out.tiles[i];
        int hp;
        if (!toInt(t[0], o.x) || !toInt(t[1], o.y) || !toInt(t[2], hp) || !toInt(t[3], o.pearlIn)) return true;
        o.pearl = hp != 0;
    }
    int nparts = 0;
    if (!labelled("DRAGON_BODIES", nparts) || nparts < 0 || nparts > 100000) return true;
    out.parts.reserve((size_t)nparts);
    for (int i = 0; i < nparts; i++) {
        if (!nextLine(t) || t.size() != 6) return true;
        PartObs p;
        p.team = t[0][0] == 'B' ? 'B' : 'A';
        int hf;
        if (!toInt(t[1], p.id) || !toInt(t[2], p.x) || !toInt(t[3], p.y) || !toInt(t[5], hf)) return true;
        p.dir = dirFromCharSafe(t[4][0]); if (p.dir < 0) return true;
        p.head = hf != 0;
        out.parts.push_back(p);
    }
    for (int r = 0; r < 8; r++) {
        if (!nextLine(t) || t.size() != 7) return true;
        for (int c = 0; c < 7; c++) { int v = edgeTok(t[c]); if (v == (-2147483647 - 1)) return true; out.hedge[r][c] = v; }
    }
    for (int r = 0; r < 7; r++) {
        if (!nextLine(t) || t.size() != 8) return true;
        for (int c = 0; c < 8; c++) { int v = edgeTok(t[c]); if (v == (-2147483647 - 1)) return true; out.vedge[r][c] = v; }
    }
    out.ok = true;
    return true;
}

void Writer::endTurn() {
    out_ += "PROTOCOL 3\nENDTURN\n";
    // One write for the whole turn (each write costs 2.5M points in the judge).
    const char* p = out_.data(); size_t left = out_.size();
    while (left > 0) {
        ssize_t n = ::write(1, p, left);
        if (n <= 0) { if (n < 0 && errno == EINTR) continue; break; }
        p += n; left -= (size_t)n;
    }
    out_.clear();
}

} // namespace seed0
