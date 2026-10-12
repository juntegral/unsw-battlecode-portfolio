#include "heuristic.hpp"

int main() {
    auto [ct, game] = unswbc::init();
    heuristic::PortalMemory portals;
    while (unswbc::update(ct, game)) {
        portals.observe(ct);
        ct.make_move(heuristic::choose_h2(ct, portals));
        unswbc::end_turn();
    }
}
