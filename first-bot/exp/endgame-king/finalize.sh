#!/bin/bash
# Regenerate every table and the text of research/observations/endgame-king.md after the full top pass (coordinator request,
# 2026-09-30 22:45). Order: elite value sheet (numbers_wl.js) -> before/after diff (diff_numbers.js) -> English tables
# (report.js, extra.js) -> Korean tables (doc.js) -> run texts (make_extra.py) -> narrative.py -> fill.js.
# usage: exp/endgame-king/finalize.sh [pass|ml (500-round lineage)] [pass|ml (elimination lineage)]
set -e
cd "$(dirname "$0")/../.."
LIN=${1:-pass}; ELIN=${2:-ml}
node exp/endgame-king/numbers_wl.js --lineage "$LIN" --elim-lineage "$ELIN" --out exp/endgame-king/numbers-wl.json
node exp/endgame-king/diff_numbers.js --old numbers-wl-old.json --new numbers-wl.json --md exp/endgame-king/changes.md --json exp/endgame-king/changes.json
node exp/endgame-king/report.js > /dev/null
node exp/endgame-king/extra.js > /dev/null
node exp/endgame-king/doc.js --lineage "$LIN" --elim-lineage "$ELIN" > exp/endgame-king/doc-tables.md
python3 exp/endgame-king/make_extra.py
python3 exp/endgame-king/narrative.py
node exp/endgame-king/fill.js exp/endgame-king/doc.filled.md "${OUT_DOC:-research/observations/endgame-king.md}"
node exp/endgame-king/wl_sheet.js > exp/endgame-king/wl-sheet.txt
echo "finalized $(date)"
