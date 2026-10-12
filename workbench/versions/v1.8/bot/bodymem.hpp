#pragma once
#include <deque>

namespace seed0 {
template <bool Enabled> struct BodyMemoryState {
    std::deque<int> history_;
    auto& history() { return history_; }
};
template <> struct BodyMemoryState<false> {
    std::deque<int>& history();
};
}
