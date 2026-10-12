#!/bin/bash
# Full-population top-vs-top pass (coordinator request, 22:45 KST): the 22:46 key snapshot, 500-round maps first, then the
# elimination maps. Effective niceness 15 (zsh runs background jobs at +5, the script adds 10), two workers (other agents' local games have priority). Games already cached are skipped.
cd "$(dirname "$0")/../.."
nice -n 10 node exp/endgame-king/extract.js top --jobs 2 --keys exp/endgame-king/top-keys-2246-r500.keys
echo "R500 PASS DONE $(date)"
nice -n 10 node exp/endgame-king/extract.js top --jobs 2 --keys exp/endgame-king/top-keys-2246-elim.keys
echo "ALL DONE $(date)"
