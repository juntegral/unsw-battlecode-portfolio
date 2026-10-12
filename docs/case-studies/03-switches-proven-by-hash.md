# Case study 3: default-off switches, proven by hash

## Problem

In the last 16 hours the team shipped 21 versions of the bot, about one every 46 minutes, with several AI builders
adding code to one 8,000-line C++ file in parallel. Under that pressure two questions had to have mechanical
answers: "is the thing we uploaded the thing we tested?" and "did this change touch anything it was not meant to?".

## The rule

1. Every new behaviour goes behind a compile-time constant that is **off by default**.
2. With every switch off, the build must be **byte-identical** to the previous program. The check is a hash of the
   binary. For the last two days the all-off hash was one fixed value, `92fb69564fbd`.
3. A version is **one source file plus a profile**, a text list of switch values. The repository default equals the
   live bot, so the team's main branch, local work and the server can be compared with a text diff.
4. If the compiler gives a different binary for equivalent code, equivalence is shown by replaying fixed games and
   comparing the replay files byte for byte.
5. An upload prints its plan and does nothing without `--confirm`; it refuses if the live bot is not the one the
   caller expects; afterwards the server copy and the active id are checked.

## Tooling

| Tool | Job |
|---|---|
| [`local-rig/solo/tools/mkbots.py`](../../local-rig/solo/tools/mkbots.py) | Builds a bot from a source and a list of switch values: `mkbots.py "name=CONST:value,..."` |
| [`final-bot/server_bot.py`](../../final-bot/server_bot.py), [`server_profile.txt`](../../final-bot/server_profile.txt) | Produces the exact uploaded source from the repository source plus the profile |
| [`workbench/tools/submit.js`](../../workbench/tools/submit.js) | Upload with plan, confirmation and expected-active check |
| [`workbench/archive/final-session-scripts/`](../../workbench/archive/final-session-scripts) | The last day as it ran: `one14.switches` to `one21.switches`, `up14.zsh` to `up21.zsh`, the check scripts |
| [`card-loop/work/loop/runner.py`](../../card-loop/work/loop/runner.py) | The same gate inside the card loop: a build with the new switch off must be replay-identical to the release |

## What it bought

- 21 live versions in 16 hours 19 minutes with no crash or timeout on record and no doubt about what was live.
- The hash caught a real break once: a builder's wrapper function and a rewritten condition changed the all-off
  binary. The work stayed out until it was fixed.
- Two harmful switches found on the last morning were removed by one-line edits to the profile.
- When two sources with the same values gave different binaries, eight replayed games differed only in the two
  bytes of the bot's name, which settled it in minutes.
- A server-side verification that reported failure, and an activation that none of our tools had made, were both
  caught by the post-upload check.

## What it did not buy

The discipline proves "this is the program we tested and nothing else changed". It does not prove "this is better".

- The last three versions went live with no online game of their own; they were checked only by local games
  identical to the version before, except where intended.
- Of the 49 values in the final profile, about eight have a comparison on record showing a gain of their own.
- The source grew to 8,657 lines with 423 constants, and interactions between switches were tested once, by
  leave-one-out.

## Takeaway

Decide the identity test before writing the first switch. It costs a few lines per change and it is what makes fast
iteration safe. Then spend the saved attention on the question the hash cannot answer.

Sources: [write-up 01, B1 and B2](../../writeup/01-playbook.md), [write-up 03](../../writeup/03-bot-design.md),
[write-up 04, section 3](../../writeup/04-tools.md).
