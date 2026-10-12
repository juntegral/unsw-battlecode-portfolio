#!/bin/zsh
# exp/portals: the patches, paths a/bot/... b/bot/... (git apply at the repo root):
#   portals.diff           bot/ at HEAD 40660cc (v1 final; exp/portals/bot-head) -> exp/portals/bot-v11 (the module rebased onto it)
#   portals-5497983.diff   bot/ at 5497983 (where the module was built and measured; exp/portals/bot-base) -> exp/portals/bot
#   portals-v1.1.diff      versions/v1.1/bot at d347ef6 -> exp/portals/bot-v111 (apply with: git apply --directory=versions/v1.1 ...)
# Each is checked to apply to its base, taken fresh from git.
cd "$(dirname "$0")"
mk() { T=$(mktemp -d); mkdir -p $T/a $T/b; cp -R $1 $T/a/bot; cp -R $2 $T/b/bot; rm -f $T/a/bot/.head; (cd $T && diff -ruN a/bot b/bot) > $3; rm -rf $T; }
mk bot-head bot-v11 portals.diff
mk bot-base bot portals-5497983.diff
T=$(mktemp -d); git -C ../.. archive d347ef6 versions/v1.1/bot | tar -x -C $T; mk $T/versions/v1.1/bot bot-v111 portals-v1.1.diff; rm -rf $T
cd ../..
chk() { T=$(mktemp -d); git archive $1 bot | tar -x -C $T; (cd $T && git init -q . && git apply --check "$OLDPWD/exp/portals/$2" && echo "$2 applies to bot/ at $1") || echo "$2 does NOT apply to bot/ at $1"; rm -rf $T; }
chk 40660cc portals.diff
chk 5497983 portals-5497983.diff
T=$(mktemp -d); git archive d347ef6 versions/v1.1/bot | tar -x -C $T; (cd $T && git init -q . && git apply --check --directory=versions/v1.1 "$OLDPWD/exp/portals/portals-v1.1.diff" && echo "portals-v1.1.diff applies to versions/v1.1/bot at d347ef6") || echo "portals-v1.1.diff does NOT apply"; rm -rf $T
