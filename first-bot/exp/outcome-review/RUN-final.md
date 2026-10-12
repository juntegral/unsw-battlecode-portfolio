# Final execution record and replay instructions

The coordinator authorized continuation without calling nice. Only one analysis
worker ran. Resource guards pause below memory_pressure free 10% or df -g / available
20 GiB. The reported parent niceness is 10; this continuation's measured child value
was 0. No priority change, network, upload, commit or credential access was attempted.

All original files and earlier output versions were preserved. New outputs are
exclusive-created. Do not run these commands again in place: existing outputs cause
failure. A rerun needs new script versions pointing to a new subdirectory under the
authorized output paths. Do not delete or overwrite the present artifacts.

The final dependency order, using one process at a time:

1. `prepare-v3.js --allow-inherited-10`: manifest and primary census from original caches.
2. `recount.js --allow-inherited-10`: first independent full official-update census.
3. `primary_extra.js --allow-inherited-10`: second full simulator census for births,
   all-life supply, exposure numerators/denominators and king deaths.
4. `recount-v2.js --allow-inherited-10`: corrected ally/enemy head cause semantics,
   full independent rerun; `audit_corrected_causes.py` verifies every king death.
5. `analyse-v4.py --allow-inherited-10`: freezes features/classes/original selection
   before models; outcomes, distributions, informative-stratum logistic fits and power.
6. `extend_analysis.py`, `elite_sensitivity.py`, `layout_sensitivity.py`: additional
   full-population descriptive estimates and explicitly exploratory sensitivities.
7. `add_current_cases.py`: selection-v2 (41 cases), after METHOD-CURRENT-CASES.md was
   written and before any selected replay deep reading.
8. `deep-read-v4.js --allow-inherited-10`: every selected replay, temporal lineage
   windows and detailed round/dragon events; `case_notes.py` records manual readings.
9. `audit_terminal.js`, `supplement_final.py`, `audit_classes.py`: all terminal rules,
   entire 10-game tie class, paired latest economy, independent classes and power.
10. `render_final.py`: Korean draft. Final QA and publication use new validation and
    publishing scripts; `finish-v2.py` writes SUMMARY.txt LAST.

JavaScript heavy commands ran with `node --max-old-space-size=1024`; Python ran with
`python3 -B` to avoid interpreter cache writes. No nice prefix was used. The
`--allow-inherited-10` flag is a retained authorization gate, not a statement about
the measured priority of the child process.

Separate outcome recounts: `metadata_ledger.py` reads indexes/game JSON and
`metadata_audit.js` independently enumerates results; `metadata_power.py` recounts
replicate noise and detection power. Their outputs remain available alongside the
full raw census. All actual data transformations use the final versions named here;
older staged prepare/analyse/render variants were not used to produce the report.
