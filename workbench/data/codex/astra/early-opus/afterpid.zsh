# usage: afterpid.zsh "<pid> <pid>" <chain args...>   (waits for my own earlier games to end)
for p in ${=1}; do while kill -0 $p 2>/dev/null; do sleep 3; done; done
shift
zsh "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/early-opus/chain.zsh" "$@"
