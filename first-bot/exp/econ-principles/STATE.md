# econ-principles: state at the 18:55 KST sleep (written 18:42 KST)

Task: test E1–E9 (research/external/INTEGRATION-2026-09-30.md section 5) on all accumulated games. Output note:
research/observations/economy-principles.md (currently a DRAFT rendered from 9,860 of 12,566 top games + all 1,259 of ours).

## Running when the laptop slept (all incremental; they resume or can be restarted safely)
1. Top extraction (3 workers, nice): `node exp/econ-principles/extract.js top --name top-all --jobs 3`
   - log .cache/econ-principles/extract.log, output .cache/econ-principles/top-all.jsonl (one line per game; done games skipped on
     restart). Online sets (18) are complete: .cache/econ-principles/online-*.jsonl.
   - If the process died: just run the same command again (nice -n 10). A truncated last line is tolerated by every reader; to be
     clean, drop it first: `node -e "const f='.cache/econ-principles/top-all.jsonl';const fs=require('fs');const L=fs.readFileSync(f,'utf8').split('\n');const ok=L.filter(l=>{try{JSON.parse(l);return true}catch{return false}});fs.writeFileSync(f,ok.join('\n')+'\n')"`
2. Background waiter A (waits for "done" in the log): report.js > report.txt, cases.js > cases.txt, extract.js check > check.txt.
3. Background waiter B (waits for check.txt): approach.js (E7 attacker approach pass, round-500 top games + ours) and
   `approach.js summary` -> approach-summary.json.
4. Background waiter C (waits for check.txt): films of the final stage-3 picks -> scratchpad films-final.txt.
   If the waiters were lost, run by hand after the extraction ends:
   ```
   nice -n 10 node exp/econ-principles/report.js > exp/econ-principles/report.txt
   nice -n 10 node exp/econ-principles/cases.js > exp/econ-principles/cases.txt
   nice -n 10 node exp/econ-principles/extract.js check .cache/econ-principles/*.jsonl > exp/econ-principles/check.txt
   nice -n 10 node exp/econ-principles/approach.js --jobs 3 && node exp/econ-principles/approach.js summary
   ```

## Finish (after the passes)
- Film the final picks of cases.txt (classes "E4-top W d3≥+1 d8≥+1", "E4-top W d3≤−1 d8≤0", "E7 … (L king)") with film.js
  and update doc-films-b.md / doc-films-c.md if the picks changed (the current notes describe the 18:12 picks).
- Remove "DRAFT" from doc-verdicts.json, re-check the verdict wording against the final numbers, then
  `node exp/econ-principles/doc.js` (writes research/observations/economy-principles.md).

## Files
- Code: extract.js (per-event pass), report.js (tables + acc.json), cases.js, film.js, approach.js, doc.js.
- Note sources: doc-template.md, doc-proposals.md, doc-e7.md, doc-e9.md, doc-cases-{a,b,c}.md, doc-films-{b,c}.md, doc-verdicts.json.
- Saved partial tables: report-partial-1842.txt (9,860 top games), report.txt / cases.txt (partial until waiter A overwrites them).

## 20:37 KST (after wake)
- The laptop slept 18:55–20:34. The top extraction resumed by itself and was at 12,500 / 12,566 at 20:37.
- The 18:4x background waiters did not survive the stall. They were relaunched at 20:37 with the same steps: report / cases / check,
  then approach.js (3 workers, nice 15), then the stage-3 films.

## 21:0x KST: finished
- Top extraction done (12,566 games, errors 0). Checks over 13,825 games are all 0 (check.txt). The approach pass is done
  (2,677 games, checks 0) and approach-summary.json is written.
- Final report.txt, cases.txt and films are done. research/observations/economy-principles.md was rendered from the final data
  (no draft banner).
