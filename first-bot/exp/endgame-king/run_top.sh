#!/bin/bash
# Top-vs-top extraction in two passes: the 500-round maps first, then the elimination maps (same key snapshot, 21:10 KST).
cd "$(dirname "$0")/../.."
nice -n 10 node exp/endgame-king/extract.js top --jobs 3 --keys exp/endgame-king/top-keys-2126-r500.keys
nice -n 10 node exp/endgame-king/extract.js top --jobs 3 --keys exp/endgame-king/top-keys-2126-elim.keys
