# Card loop

My files from the team's private repository: the loop that took idea cards from the GitHub board, built them behind
default-off switches, tested them and brought the decision back to a person. Only files whose every commit is mine
are here; the team's bot and my teammates' scripts are not.

| Path | What it is |
|---|---|
| `docs/LOOP.md`, `docs/LOOP.zh.md` | The specification: states, pick order, gates, result format |
| `docs/WORKFLOW.md` | The team workflow that preceded it |
| `work/loop/runner.py` | The poll loop over card labels |
| `work/loop/jobs.py` | Detached job supervisor with lease files |
| `work/loop/guard.py` | Hook that restricts what a card session may do |
| `work/loop/meow_control.py`, `late.py` | Consumer of confirmed requests from the Discord bot; late-estimate explainer |
| `work/loop/prompts/` | One prompt per step: clarify, build, look, verdict, decide, task |
| `work/loop/tests/` | Tests for the runner and its helpers |
| `work/board.py`, `fair_queue.py`, `card_names.py` | Board commands, fair rotation across authors, card short names |
| `work/card_*_check.py` | Completion checks written for individual cards |
| `candidates/` | Release candidate manifests the Discord bot turned into approval messages |
| `.github/ISSUE_TEMPLATE/` | The idea and task card templates |

Start with [`docs/LOOP.md`](docs/LOOP.md), or the [case study](../docs/case-studies/02-card-loop.md).
