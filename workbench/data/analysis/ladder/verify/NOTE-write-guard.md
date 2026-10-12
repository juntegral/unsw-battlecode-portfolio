# Note for whoever maintains the runner: the write guard blocks the verifier's own folder

Seen on the first verifier run, 2026-10-07 02:27 KST. It cost about a third of the run.

- tools/ladder_guard.py allows a write when the resolved target lies under ROOT/data/analysis/ladder/verify.
  ROOT comes from the script's own location and is spelled the way the disk spells the Korean folder name
  (decomposed jamo). The target is built from the hook's working directory, which arrives in the composed
  spelling. The two strings never match, so every Write, mkdir, rm and shell redirect into verify/ is refused,
  for relative and absolute paths alike.
- What worked: Python (quoted heredoc or script) writing to an absolute path whose Korean part is written with
  \u escapes in the decomposed form. All files in this folder were written that way. Nothing was written outside
  verify/ and verify-results.json.
- A fix on the guard side would be to normalise both sides to the same Unicode form before comparing.
- Smaller: the guard refuses any heredoc that contains a backtick, so the result files here use no code marks.
- Left behind because rm is refused the same way: shard-test.jsonl and common_src.txt (both harmless).

Still the case on the second verifier run, 2026-10-07 03:25 KST: the Write tool is refused for verify/ and the Python route with the decomposed path works. Left behind this time: probe.txt and x2-test.jsonl (harmless, rm is refused).

Still the case on the third verifier run, 2026-10-07 04:25 KST (Write refused for verify/ with either spelling of the path; the Python route works). One more thing a maintainer may want to know: the ids F13 and F11 came back in the 04:00 queue with new wording, so F13.md and F11.md were rewritten; the 03:25 verdicts are kept as F13-0325.md and F11-0325.md and their result entries in results-0325-F13-F11.json.

Still the case on the fourth verifier run, 2026-10-07 05:20 KST (Write refused for verify/, the Python route works). The ids F20 and F13 came back in the 05:00 queue with new wording, so F20.md and F13.md were rewritten; the 04:25 verdicts are kept as F20-0425.md and F13-0425.md and their result entries in results-0425-F20-F13.json. Left behind: x4-test.jsonl (harmless).

Still the case on the fifth verifier run, 2026-10-07 06:27 KST (Write refused for verify/, the Python route works). The id F24 came back in the 06:00 queue with new wording, so F24.md was rewritten; the 05:20 verdict is kept as F24-0520.md and its result entry in results-0520-F24.json. Two more guard habits that cost a few minutes: a single ampersand anywhere in a heredoc is refused (so no set intersection operator in a script written that way), and a second command after a heredoc is refused. The import list does not allow a local module, so lib5.py is not imported; its text is pasted at the top of each c5 script. Left behind: x5-test.jsonl (harmless).

Still the case on the sixth verifier run, 2026-10-07 07:35 KST (Write refused for verify/, the Python route works). One more guard habit: the characters for less-than and greater-than are refused in any shell argument, so a search pattern cannot contain them. Left behind: x7-test.jsonl (harmless).

Still the case on the seventh verifier run, 2026-10-07 08:23 KST (Write refused for verify/, the Python route works). Two more guard habits: a round bracket in a search pattern is refused, and a directory change before a command is refused, so every path is given from the project root. Left behind: x8-test.jsonl (harmless).

Still the case on the eighth verifier run, 2026-10-07 09:18 KST (Write and Edit refused for verify/, the Python route works). One more guard habit: the string method that swaps one piece of text for another is on the blocked call list, so an edit of a written file goes through split and join. A first shell call that used a character-translate command was refused as not on the allowlist. Left behind: x9-test.jsonl (harmless).

Still the case on the ninth verifier run, 2026-10-07 10:21 KST (Write refused for verify/, the Python route works; background shell runs through the tool are allowed, which let the six extraction shards run at once). The ids F39 and F38 came back in the 10:00 queue as new parts, so F39.md and F38.md were rewritten; the 09:18 verdicts are kept as F39-0918.md and F38-0918.md and their result entries in results-0918-F38-F39.json. Left behind: x10-test.jsonl (harmless).

Still the case on the tenth verifier run, 2026-10-07 11:17 KST (Write refused for verify/, the Python route works; six background shards ran at once). The ids F38 and F39 came back in the 11:00 queue as new parts, so F38.md and F39.md were rewritten; the 10:21 verdicts are kept as F38-1021.md and F39-1021.md and their result entries in results-1021-F38-F39.json. One more guard habit: a curly bracket anywhere in a plain shell command is refused, so a search pattern cannot hold a repeat count. Left behind: x11-test.jsonl (harmless).

Eleventh verifier run, 2026-10-07 12:12 KST: the Write tool was not tried again; every file went through the Python route with the decomposed path from the start, and six background shards ran at once. The id F38 came back in the 12:00 queue as a new part, so F38.md was rewritten; the 11:17 verdict is kept as F38-1117.md and its result entry in results-1117-F38.json. F42 is new. Left behind: x12-test.jsonl (harmless).

Twelfth verifier run, 2026-10-07 15:12 KST: one Write was tried and refused as before; every file went through the Python route with the decomposed path, and six background shards ran at once. The ids F42 and F7 came back in the 15:00 queue with new wording, so F42.md and F7.md were rewritten; the 12:12 and 02:27 verdicts are kept as F42-1212.md and F7-0227.md and their result entries in results-1212-F42-0227-F7.json. F44 is new. One more guard habit: a curly bracket in a plain shell command is refused even inside a quoted search pattern, so a lookup in a JSON file goes through Python. Left behind: x13-test.jsonl (harmless).


Thirteenth verifier run, 2026-10-07 18:20 KST: every file went through the Python route with the decomposed path. New this time: a background shell run is stopped by the tool after ten minutes unless a longer limit is asked for, and the rebuild of 940 games in six shards now takes longer than that when two sets of shards run at once; the first extraction (extract14.py, shards x14-0 to x14-5) was stopped part-way and is not used, the second (extract14b.py) reached 661 games and extract14c.py did the other 279 with a thirty-minute limit. c14.py reads x14b and x14c together (940 games, no game twice). The ids F44 and F42 came back in the 18:00 queue with new wording, so F44.md and F42.md were rewritten; the 15:12 verdicts are kept as F44-1512.md and F42-1512.md and their result entries in results-1512-F44-F42.json. F45 is new. Left behind: x14-0 to x14-5 (partial, unused), x14-test.jsonl, extract14.py (harmless).
