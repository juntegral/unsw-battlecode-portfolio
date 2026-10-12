#pragma once
#include <vector>
namespace seed0 {
struct HeadSighting {
    int sender = -1, enemy = -1, round = -1, t = -1, len = 0;
};
template <bool ON> struct Q2SightState {
    std::vector<HeadSighting> heads_;
    std::vector<double> price_;
    int received_ = 0, accepted_ = 0;
    auto& heads() { return heads_; }
    const auto& heads() const { return heads_; }
    auto& price() { return price_; }
    const auto& price() const { return price_; }
    int& received() { return received_; }
    int& accepted() { return accepted_; }
};
template <> struct Q2SightState<false> {
    std::vector<HeadSighting>& heads();
    const std::vector<HeadSighting>& heads() const;
    std::vector<double>& price();
    const std::vector<double>& price() const;
    int& received();
    int& accepted();
};
}
