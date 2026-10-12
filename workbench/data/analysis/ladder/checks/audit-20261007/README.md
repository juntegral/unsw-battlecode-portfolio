Independent recount used in the 2026-10-07 audit of rows.jsonl (see SCHEMA.md, "Audit").

    node batch.js 0 1                      # recount every ladder game -> recount-0.jsonl (about 15 minutes)
    python3 compare.py ../../rows.jsonl recount-0.jsonl     # every field, every game; prints disagreements
    python3 mapcheck.py                    # map geometry from the replay header, own edge handling
    python3 dumpgaps.py && node gapcheck.js 0 1 && python3 esteval.py   # local gap files vs server births

recount.js decodes with the official viewer (viewer2.js) and rebuilds the game with its own logic; it shares no
code with tools/ladder_replay.py. recount.jsonl is the result for the 625 games of 2026-10-07 01:27 KST.
