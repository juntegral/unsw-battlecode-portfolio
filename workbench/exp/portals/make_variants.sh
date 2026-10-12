#!/bin/zsh
# exp/portals: build the screening variants from exp/portals/bot (params.hpp PT_* flags only; PLAN.md).
#   v1-end        PT_ENDGAME_ON only
#   v2-endsafe    PT_ENDGAME_ON + PT_KING_SAFE_ON (dead tiles, blind crossings) + PT_PIECE_PORTAL_ON, PT_KING_ROOM_ON false
#   v3-room       v2 + PT_KING_ROOM_ON, PT_LEN_ON false
#   v4-len        v3 + PT_LEN_ON; endgame 2 off
#   v5-full       v2 + PT_LEN_ON + endgame 2 (PT_ENDFEED_ON, PT_KING_GRAB_ON, PT_END_GATHER_W 0.4), room rule off (PLAN.md amendment 04:41)
#   v6-clock      v5 + PT_CONV_START 270, PT_GATHER_START 310
#   (v1-v6: PT_KING_BLIND_OUT_ONLY false, the code as screened)
#   v7-full2      v5 + PT_KING_BLIND_OUT_ONLY (PLAN.md amendment 04:47)
#   v8-clock2     v6 + PT_KING_BLIND_OUT_ONLY
#   (bot/ was then cleaned: the map loading and the room-from-round-0 rule removed, the blind rule always "outside rooms"; v7 = bot/ with
#    PT_KING_ROOM_LATE_ON false; the flags below for v1-v8 refer to the code as it was when they ran)
#   v9-late       bot/ (v7 + PT_KING_ROOM_LATE_ON, PLAN.md amendment 05:12)
#   decomposition after the decision (team lead 06:00, not a selection; from the final bot/):
#   d-null        every component off: the module's instantiation with FORTRESS values (must play as bot-base; fingerprint check)
#   d-lenonly     only the length memory
#   d-nolen       V7 without the length memory
cd "$(dirname "$0")"
set -e
mk() { rm -rf var/$1; mkdir -p var; cp -R bot var/$1; }
flag() { sed -i '' "s/^constexpr $2 *$3 = [^;]*;/constexpr $2   $3 = $4;/" var/$1/params.hpp; grep -q "^constexpr $2 *$3 = $4;" var/$1/params.hpp || { echo "flag edit failed $1 $3"; exit 1; }; }
only=${1:-all}
e2off() { flag $1 bool PT_ENDFEED_ON false; flag $1 bool PT_KING_GRAB_ON false; flag $1 double PT_END_GATHER_W 0.12; }
[ $only = all -o $only = v1-end ] && { mk v1-end;     flag v1-end bool PT_KING_SAFE_ON false; flag v1-end bool PT_PIECE_PORTAL_ON false; flag v1-end bool PT_KING_ROOM_ON false; flag v1-end bool PT_LEN_ON false; e2off v1-end; }
[ $only = all -o $only = v2-endsafe ] && { mk v2-endsafe; flag v2-endsafe bool PT_KING_ROOM_ON false; flag v2-endsafe bool PT_LEN_ON false; e2off v2-endsafe; }
[ $only = all -o $only = v3-room ] && { mk v3-room; flag v3-room bool PT_LEN_ON false; e2off v3-room; }
[ $only = all -o $only = v4-len ] && { mk v4-len; e2off v4-len; }
[ $only = all -o $only = v5-full ] && { mk v5-full; flag v5-full bool PT_KING_ROOM_ON false; flag v5-full bool PT_KING_BLIND_OUT_ONLY false; }
[ $only = all -o $only = v6-clock ] && { mk v6-clock; flag v6-clock bool PT_KING_ROOM_ON false; flag v6-clock int PT_CONV_START 270; flag v6-clock int PT_GATHER_START 310; flag v6-clock bool PT_KING_BLIND_OUT_ONLY false; }
[ $only = all -o $only = v7-full2 ] && { mk v7-full2; flag v7-full2 bool PT_KING_ROOM_ON false; }
[ $only = all -o $only = v8-clock2 ] && { mk v8-clock2; flag v8-clock2 bool PT_KING_ROOM_ON false; flag v8-clock2 int PT_CONV_START 270; flag v8-clock2 int PT_GATHER_START 310; }
[ $only = v9-late ] && mk v9-late
[ $only = v7-final ] && { mk v7-final; flag v7-final bool PT_KING_ROOM_LATE_ON false; }
nulls() { flag $1 bool PT_ENDGAME_ON false; flag $1 int PT_FEED_MIN_UNITS 3; flag $1 int PT_FEED_SLACK 8; flag $1 bool PT_KING_SAFE_ON false; flag $1 bool PT_PIECE_PORTAL_ON false;
           flag $1 bool PT_ENDFEED_ON false; flag $1 bool PT_KING_GRAB_ON false; flag $1 double PT_END_GATHER_W 0.12; }
[ $only = d-null ] && { mk d-null; nulls d-null; flag d-null bool PT_LEN_ON false; }
[ $only = d-lenonly ] && { mk d-lenonly; nulls d-lenonly; }
[ $only = d-nolen ] && { mk d-nolen; flag d-nolen bool PT_LEN_ON false; }
for v in v1-end v2-endsafe v3-room v4-len v5-full v6-clock v7-full2 v8-clock2 v9-late v7-final d-null d-lenonly d-nolen; do [ -d var/$v ] && { echo "== $v"; diff bot/params.hpp var/$v/params.hpp || true; }; done
