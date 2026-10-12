---
name: codex-outsourcing
description: "User preference (2026-09-30 23:10 KST): outsource deep research and heavy study runs to Codex, so Claude stays on strategy and coordination; Claude prepares briefs and ingests results"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-30T14:10:39.057Z
---

User, 2026-09-30 about 23:10 KST: "앞으로 딥 리서치 같은 경우에는 codex에 외주를 맡기는 편이 더 나은것같아. 클로드에서 더 진지하고 전략적인 대화를 할 수 있게." For the next heavy study the user said: call Codex yourself if you can, otherwise hand me a script/prompt file, and prepare everything so you can pick up the result when it finishes.

- **Settings (user, 23:15): model gpt-6.1-sol, reasoning effort max.** These are the config.toml defaults. Still pass them explicitly: `-m gpt-6.1-sol -c 'model_reasoning_effort="max"'`.
- **The user also runs Codex in another window (Orca).** Before launching a brief the user already has, ask. On 2026-09-30 23:13 I started a duplicate of the foraging deep research the user was running in Orca, and had to kill it after 1 minute.
- **Broad-but-shallow work goes to Codex (user, 2026-10-01 03:25):** "코덱스는 많이 돌려도 되니까 사고를 요하는 작업이 아니지만 광범위한거는 걔한테 맡겨."
  - Full-population sweeps, extractors, tables and diagnostic tools go to Codex with effort high. Keep max effort for deep research.
  - Claude keeps strategy, integration, verification and short targeted replay reads.
- **Match effort to the task (user, 2026-10-01 02:52):** "클로드 최대한 그런 사고 쓰는게 아닌 단순업무 할때는 아껴야해".
  - Max reasoning is only for real research and design.
  - Simple work gets low or medium effort: smoke tests, file checks, mechanical edits, reruns. For Codex that is `-c 'model_reasoning_effort="low"'`; for Claude subagents or workflow agents, the lowest effort and short prompts.
  - The "never save tokens" rule is about research rigour: full populations and independent recounts. It does not mean burning effort on simple tasks.
- **Account:** the Codex CLI is logged in with ChatGPT as the user's own account. The plan is `prolite`, and the tokens last refreshed 2026-09-30 22:54 KST.
  - At 02:51, after the user refreshed, a test call worked again.
- **Usage limit (2026-10-01 02:45 KST):** the account hit its Codex limit ("try again at Oct 4th, 2026 2:30 AM"). Until then, research goes back to Claude subagents. Check a run's log for "usage limit" before relying on it.
- **Codex CLI works non-interactively on this machine.**
  - Binary: `~/.local/bin/codex`, version 0.159.2, config model gpt-6.1-sol.
  - Run form: `codex exec -C <repo> -s workspace-write --skip-git-repo-check -o <last-message file> "<brief>"`.
  - Live web search is a `--search` flag (listed under the top-level `codex --help`).
  - A read-only smoke test passed at 23:1x.
- **Brief pattern.** Write a self-contained brief file in the repo, for example `research/external/codex-brief-<topic>.md` or `codex-prompt-<topic>.md`. It must contain:
  - exact output paths and the format;
  - the game rules pointer;
  - our measured numbers;
  - the population and method rules (full population, recount key numbers);
  - a completion marker file written last.
- **After Codex finishes, Claude:**
  - verifies the key numbers (an independent recount agent if they drive a wave);
  - checks `git status` for stray edits;
  - commits;
  - integrates the results into the backlog and plans.

**Why:** Claude's context and attention should go to strategic conversation with the user and to wave decisions, not long research runs.
**How to apply:** deep research and long replay studies go to Codex, either launched by Claude via `codex exec` or handed to the user as a brief. Implementation agents that build wave candidates stay with Claude's own subagents unless the user says otherwise. Related: [[analysis-population-all-games]], [[heuristic-repo]].

10-03 ~19:50 KST user rule: until 10-04 08:00 KST, every concrete task goes to Codex: `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C <dir> -o <file>`. Brief lives in unsw-swarm/data/codex/. Claude only writes briefs, reviews, commits.
Model split (user 10-03): plain/mechanical work (scripts, wiring, formatting) → `-m gpt-6.1-sol`; work needing real judgment (analysis, verdict drafts, tricky design) → `-m gpt-6-astra -c model_reasoning_effort=high`. Parallel Codex jobs are fine; avoid two jobs editing the same file.
Pitfall (10-03): `codex exec` launched via Bash run_in_background hangs forever on "Reading additional input from stdin...". Always add `< /dev/null` (and nohup ... &). Check the log has a `model:` header within 20 s.
Pitfall (10-04): Codex editing work/loop/ in the live runner's checkout broke the runner, because the uncommitted prompt edits were read immediately (KeyError 'revision_evidence'). Run loop-code Codex jobs in a separate worktree, then commit to main and restart the runner.
Pitfall (10-04): a waiter like `zsh -c "while pgrep -f \"codex exec.*brief-X\"..."` matches its own command line and waits forever. Use `pgrep -f "^codex exec"`-style anchors, or wait on a PID.
Pitfall (10-04): after a Codex job, run `git status` for untracked new modules and run ALL checks BEFORE committing/restarting (chain with &&); a missed tools/pr_poll.py and stale fake-gh checks slipped through once.
Pitfall (10-04): `cmd | tail -1 && next` does NOT stop on failing tests (tail exits 0). Gate deploys with `if cmd | tail -1 | grep -q "^OK"; then ...` or check $pipestatus.

10-04 23:35 user rule: Codex accounts in order: <email> (Plus, Orca-managed home at ~/Library/Application Support/Orca/codex-accounts/910a88f2-.../home) FIRST; when it hits its usage limit, fall back to <email> (the default ~/.codex login, plan "prolite"). Use `unsw-swarm/tools/cx.sh <log> <codex exec args…>` for every Codex call (it closes stdin, logs which account ran to data/codex/accounts.log, and remembers a limit for 3 h). Until 23:35 all Codex work today ran on the second account.

10-05 02:28 user rule: never run gpt-6-astra at max effort (too many tokens for what it delivers); astra is high at most. Research goes to Sonnet 5.5 max instead of Codex max. See [[main-session-master-workbench]] for the current model table.

10-07 ~12:00 KST: the user noticed Codex was not being used where it should be and asked me to re-read the 10-06 handover. Its section 9 has a model table marked "keep exactly" that the 10-07 handover dropped: mechanical work (scripts, wiring, formatting) = Codex gpt-6.1-sol; tallies with a reference script, replay counts included = Codex gpt-6.1-sol low; work needing judgement (analysis, verdict drafts, tricky design) = Codex gpt-6-astra high, never max; simple checks = Codex low; thinking steps and the command-post session = Claude Opus 5.5 high; light steps = Sonnet medium; deep research only = Sonnet 5.5 max. From 01:00 to 12:00 KST that day there were no Codex calls while Opus did the hourly ladder analysis (166M cache-read), two overnight subagents and the #47 recount. The rule "meowbot answers in main, no subagents" never meant "no Codex". How to apply: before any tally, script or analysis in the main session, write a brief and send it to Codex (`tools/cx.sh <log> -m <model> -c model_reasoning_effort=<effort> -s workspace-write -C <unsw-swarm> "Follow the brief in ... exactly."`), read only the result file, and copy the table into every handover.

10-07 ~12:20 KST correction from the user, replacing the table above where they differ: "사고가 필요한거는 무조건 opus가 맞음. 그냥 기존 아스트라 업무도 6.1솔로 바꾸고…" So: anything that needs thinking (analysis, design, verdicts, interpreting results, implementation) is Claude Opus 5.5 high; Codex is gpt-6.1-sol only, for mechanical work, tallies whose metrics are already defined, and simple checks; gpt-6-astra is not used at all. He also asked whether xhigh is really needed, so default to high and justify any xhigh. I had just moved the ladder analysis to Codex astra on his "저대로 진행하면 돼" and he had me put it back on Opus 5.5 high (the 3-hour cadence stayed; that part is my reading of his earlier go-ahead).

**2026-10-08 18:5x KST update (user):** after I spawned three Opus builder subagents for new bot switches he asked why, and said "가능하면 빌드 자체는 그냥 코덱으로 넘기길 원했는데". Standing preference: the build grind (running games, waiting, counting scripts, tables, mechanical edits from a ready diff) goes to Codex; Claude/Opus keeps only the part that needs thinking (reading the bot source to choose a mechanism, the edit, judging replays). **How to apply:** split every build job that way from the start, and say the size and the reason before spawning Claude subagents, even when tokens are "free" ([[claude-usage-budget]]).

**2026-10-09 00:49 KST update (user):** "사고도 그냥 이제 아스트라도 돌려도 됨. 아스트라까지 최대한 이용해서 진행하자. 아스트라에서도 한 8배럭 돌려. 나 초기화권 많음" and "지금 만약 가설 돌릴만한 자리가 부족하면 거기서 돌려도 된다는 말임." This lifts his 10-07 ban ("사고는 무조건 opus, 아스트라 빡통"): thinking work (hypothesis analysis, design) may go to Codex `gpt-6-astra` (`-c model_reasoning_effort=high`), about 8 in parallel, when Claude capacity is short. Reason: Claude weekly limit was at 17% with 14 hours to the deadline; he has Codex limit resets to spare. Launch: `tools/cx.sh data/codex/<log> -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-astra-<name>.md exactly."` from unsw-swarm; common notes `data/codex/astra/ASTRA-COMMON.md`; Codex cannot play games (sandbox refuses nice), so games are started by Claude. My own caution: Astra's reports were unreliable once (10-07 queen stats), so check a key number or run a local test before acting on one.

10-09 01:45 fact: sessions started inside Orca inherit `CODEX_HOME` = the Orca home (<email>, Plus), so a bare `codex exec` is NOT the juntegral login. `unsw-swarm/tools/cx.sh` was fixed that night to call the second account with `CODEX_HOME="$HOME/.codex"` (<email>, prolite). Before saying which account is in use, check the `CODEX_HOME` of the running `codex exec` process and which login it holds; `data/codex/accounts.log` labels alone were wrong once.

**2026-10-09 10:54 KST update (user), current model split:** "사고가 필요한 경우에는 opus5.5랑 astra, 비교적 단순한 경우에는 sonnet5.5랑 6.1sol을 사용하는거만 명심해줘." Thinking work (analysis, design, builders that must read the bot source) = Claude Opus 5.5 or Codex gpt-6-astra (both high); simpler work (counting, tables, scripts, mechanical checks) = Claude Sonnet 5.5 or Codex gpt-6.1-sol. Said while lifting token saving for the last four hours before the deadline ("토큰을 아끼지 말아줘", Claude subagents welcome again). He said it right after declining one Codex launch of mine; that launch was an Astra builder, so my reading is that the note was a reminder, not a correction of that call.

**2026-10-09 11:2x KST (user):** Codex is on its last limit: no need to save it, keep using it; when its usage runs out, move that work into Claude and run it on Sonnet 5.5 in volume ("소넷으로 물량전", his view: Sonnet 5.5 thinks well enough). How to apply: check `unsw-swarm/data/codex/accounts.log` and the job log for a usage-limit line when a Codex job ends early, then relaunch the same brief as a Sonnet subagent instead of waiting.

**2026-10-09 11:26 KST (user), refinement of the line above:** once Codex is used up, every subagent runs on Sonnet 5.5, including the ones I add when a new question or improvement widens the work ("사고 자체는 소넷도 충분"); Opus only for the few jobs that need deep thinking. Until Codex runs out, carry on as now.
