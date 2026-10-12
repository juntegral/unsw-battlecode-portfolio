Updated work/board.py on juntegral to follow docs/LOOP.md.
next selects ready cards by author priority and age, prints all paginated comments; --state lists cards.
state replaces stale status/legacy labels, preserves descriptive labels, posts optional notes, and updates heartbeat.
ready/claim use state; ask posts “Questions before we build” and sets needs-info.
report validates the opening three-line summary and appends a small tag footer using fetched origin/main.
migrate defaults to preview; --apply converts safe loop:ready cards and leaves review-required/conflicting cards unchanged.
heartbeat and remove remain unchanged; the docstring lists all commands.
Validation: python3 -m py_compile, git diff --check, and 12 mocked CLI tests passed.
Tests covered parsing, priority, comments, transitions, repeated states, reports, questions, migration, and heartbeat/remove.
No real gh/network calls, commits, or pushes were made.
