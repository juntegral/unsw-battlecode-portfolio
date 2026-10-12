# usage: after.zsh <file that will contain "chain done"> <chain args...>
f=$1; shift
while ! grep -q "chain done" $f 2>/dev/null; do sleep 5; done
zsh "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/early-opus/chain.zsh" "$@"
