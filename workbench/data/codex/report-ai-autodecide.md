Implemented AI-only verdict decisions with top-level thresholds, one automatic revision, terminal closure, candidate routing and the exact coin-flip note.
Added validated verdict.json fields, hidden result metadata and verdict-evidence recovery for existing tested AI ideas; human cards remain unchanged.
Automatic revisions preserve the verdict evidence in the build prompt and persist their limit across retries/restarts.
Verified Card #18's actual local raw files: 396/400 recorded-outcome pairs identical; updated runner logic schedules its one revision.
Added ≤10-line English/Chinese docs sections and branch, boundary, legacy and crash-recovery tests.
python3 -m unittest discover -s work/loop/tests: 66 tests passed; git diff --check passed.
No commit, push, GitHub call, or runner start/stop was performed; live issue/output state was not changed.
An already-running long-lived Python poller does not hot-reload runner.py; next-poll behavior requires the updated code to be loaded.
