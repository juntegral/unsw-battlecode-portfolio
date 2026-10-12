#pragma once
namespace seed0 {
// Empty off states preserve the original object layout.
template <bool ON> struct Q1SightState {
    int seen_ = -1000, heard_ = -1000;
    int seen() const { return seen_; }
    int heard() const { return heard_; }
    void see(int r) { seen_ = r; }
    void hear(int r) { heard_ = r; }
};
template <> struct Q1SightState<false> {
    int seen() const { return -1000; }
    int heard() const { return -1000; }
    void see(int) {}
    void hear(int) {}
};
template <bool ON> struct Q1BackupState {
    int queen_ = -1;
    int queen() const { return queen_; }
    void setQueen(int t) { queen_ = t; }
};
template <> struct Q1BackupState<false> {
    int queen() const { return -1; }
    void setQueen(int) {}
};
}
