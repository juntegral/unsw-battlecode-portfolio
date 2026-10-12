#!/bin/zsh
# Continues the top-team study as planned in STUDY-PROMPT.md: the driver starts the three
# sub-sessions; the same lead session is resumed between them. Strictly sequential.
U="~/01. Project/개인 프로젝트/unsw-swarm"; T="$U/data/analysis/top1"
B="~/01. Project/개인 프로젝트/battlecode"
SID="97432d25-be04-4d12-9524-9d47524e347a"
J="$T/study-cont.jsonl"
DEADLINE="Deadline unchanged: before 08:30 KST on 2026-10-05."

# session variables of whatever shell launched this driver must not leak into the study sessions
unset CLAUDECODE CLAUDE_CODE_ENTRYPOINT CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS CLAUDE_JOB_DIR CLAUDE_CODE_AGENT \
  CLAUDE_CODE_MESSAGING_SOCKET CLAUDE_CODE_MESSAGING_TOKEN CLAUDE_CODE_EXECPATH CLAUDE_CODE_SESSION_ID \
  CLAUDE_CODE_CHILD_SESSION CLAUDE_CODE_SESSION_ATTENDED CLAUDE_PID CLAUDE_EFFORT

# same environment as run_study.sh gave the lead
export LOOP_GUARD="$B/work/loop/guard.py" CARD_LOOP_GUARD="$B/work/loop/guard.py" LOOP_TREE="$T" LOOP_OUT="$T" \
  LOOP_STEP=study CARD_LOOP_GAMES=0 LOOP_BATCH_LEASE=0

log() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$T/study.log"; }
now() { date '+%H:%M'; }
stop() { log "cont STOPPED: $*"; exit 1; }
mtime() { /usr/bin/stat -f %m "$1"; }
# written (non-empty) at or after epoch $2
fresh() { [[ -s "$1" ]] && (( $(mtime "$1") >= $2 )); }

cd "$T" || exit 1

# lead <step> <message file>: resume the lead session with the message on stdin
lead() {
  local step=$1 msg=$2 before rc res
  [[ -s "$T/$msg" ]] || stop "step $step: $msg missing or empty"
  [[ -f "$J" ]] || : > "$J"
  before=$(wc -l < "$J" | tr -d ' ')
  log "cont step $step start: lead resumed with $msg"
  claude -p --resume "$SID" --model opus --effort high --permission-mode bypassPermissions --settings "$B/work/loop/settings.json" --output-format stream-json --verbose < "$T/$msg" >> "$J" 2>&1
  rc=$?
  res=$(tail -n +$((before+1)) "$J" | grep '"type":"result"' | tail -1)
  log "cont step $step end: lead exit=$rc $(echo "$res" | grep -oE '"(subtype|is_error|num_turns|duration_ms|session_id)":[^,}]*' | tr '\n' ' ')"
  (( rc == 0 )) || stop "step $step: lead exit code $rc"
  [[ -n "$res" ]] || stop "step $step: no result line in study-cont.jsonl"
  [[ "$res" == *'"is_error":true'* ]] && stop "step $step: lead result is an error"
  [[ "$res" == *"\"session_id\":\"$SID\""* ]] || stop "step $step: lead answered in a different session"
}

# sub <step> <letter> <output file>: one sub-session, the command from STUDY-PROMPT.md
sub() {
  local step=$1 x=$2 out=$3 t0 rc
  [[ -s "$T/sub$x.md" ]] || stop "step $step: sub$x.md missing or empty"
  t0=$(date +%s); SUB_START=$(now)
  log "cont step $step start: sub-session $x (sub$x.md -> $out)"
  claude -p --model opus --effort max --permission-mode bypassPermissions --settings "~/01. Project/개인 프로젝트/battlecode/work/loop/settings.json" --output-format text < "sub$x.md" > "sub$x.out" 2>&1
  rc=$?; SUB_RC=$rc; SUB_END=$(now)
  log "cont step $step end: sub-session $x exit=$rc; $out $(wc -c < "$T/$out" 2>/dev/null | tr -d ' ') bytes; sub$x.out $(wc -c < "$T/sub$x.out" | tr -d ' ') bytes"
  fresh "$T/$out" $t0 || stop "step $step: $out missing, empty or not written by sub-session $x"
}

# ---- step 0: keep the first run, refresh the metrics
log "cont step 0 start: preserve first run in run1/, refresh metrics"
if [[ -e "$T/run1" ]]; then
  log "cont step 0: run1/ already exists; first-run files not copied again"
else
  mkdir "$T/run1" || stop "step 0: cannot create run1/"
  for f in REPORT.md SUMMARY-ko.md card-draft.md hypotheses.md redteam.md deep-read.md DONE study.jsonl; do
    [[ -e "$T/$f" ]] || stop "step 0: first-run file $f missing"
    cp -p "$T/$f" "$T/run1/$f" && cmp -s "$T/$f" "$T/run1/$f" || stop "step 0: copy of $f failed"
  done
  rm "$T/DONE"
  log "cont step 0: first run copied to run1/ ($(ls "$T/run1" | tr '\n' ' ')); DONE removed"
fi
t0=$(date +%s)
N=$(find "$U/data/online/top1" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
python3 ../../../tools/top_metrics.py
rc=$?
(( rc == 0 )) || stop "step 0: top_metrics.py exit code $rc"
fresh "$T/games.csv" $t0 || stop "step 0: games.csv missing, empty or not refreshed"
log "cont step 0 end: metrics refreshed; data/online/top1 holds $N battle folders; $(grep -E '"(games|top_games|own_games|rank1_team_id|rank1_name|errors)"' "$T/run.json" | tr -d ' \n')"

# ---- step 1: lead updates subA.md if needed
cat > "$T/cont1.md" <<EOF
Continuation of your study session. What has changed:
- The user now allows the sub-sessions. A driver script (run_study_cont.sh, outside your session) starts them for you, one at a time, with the exact command from the "How to call a sub-session" section of your prompt. Do not try to start any process yourself.
- Your earlier single-session results (REPORT.md, SUMMARY-ko.md, card-draft.md, hypotheses.md, redteam.md, deep-read.md, DONE, study.jsonl) are saved in run1/. They count as your own first notes, not as sub-session output. The same files are still in this directory (DONE was removed); each sub-session's output file replaces the one of the same name, and the driver checks that it was written during that sub-session.
- The metrics were just refreshed (python3 ../../../tools/top_metrics.py): ../../online/top1/ holds $N battle folders (175 when you started).
- The protagonist stays the rank-1 team of the snapshot, as your prompt defines it.
- It is $(now) KST. $DEADLINE

Your step now: update subA.md if the refreshed data changes which games to read (keep it self-contained; output file deep-read.md). Then stop. The driver starts sub-session A next and resumes you when it has finished.
EOF
lead 1 cont1.md
[[ -s "$T/subA.md" ]] || stop "step 1: subA.md missing or empty"

# ---- step 2: sub-session A
sub 2 A deep-read.md

# ---- step 3: lead checks A, writes subB.md
t0=$(date +%s)
cat > "$T/cont2.md" <<EOF
Sub-session A has finished (ran $SUB_START-$SUB_END KST, exit code $SUB_RC). Its output is deep-read.md; what it printed is in subA.out.

Your step now, as your plan says: check its work against the data. Then write subB.md (self-contained; Method step 4; output file hypotheses.md) and stop. Do not start any process yourself; the driver starts sub-session B next and resumes you when it has finished.

It is $(now) KST. $DEADLINE
EOF
lead 3 cont2.md
fresh "$T/subB.md" $t0 || stop "step 3: subB.md missing, empty or not written in this step"

# ---- step 4: sub-session B
sub 4 B hypotheses.md

# ---- step 5: lead checks B, writes subC.md
t0=$(date +%s)
cat > "$T/cont3.md" <<EOF
Sub-session B has finished (ran $SUB_START-$SUB_END KST, exit code $SUB_RC). Its output is hypotheses.md; what it printed is in subB.out.

Your step now, as your plan says: check its work against the data. Then write subC.md (self-contained; Method step 5, the red team; output file redteam.md) and stop. The red team must recount from the data and must not rely on your first-run run1/redteam.md. Do not start any process yourself; the driver starts sub-session C next and resumes you when it has finished.

It is $(now) KST. $DEADLINE
EOF
lead 5 cont3.md
fresh "$T/subC.md" $t0 || stop "step 5: subC.md missing, empty or not written in this step"

# ---- step 6: sub-session C
sub 6 C redteam.md

# ---- step 7: lead checks C, decides and writes the report
t0=$(date +%s)
cat > "$T/cont4.md" <<EOF
Sub-session C has finished (ran $SUB_START-$SUB_END KST, exit code $SUB_RC). Its output is redteam.md; what it printed is in subC.out. All three sub-sessions have now been used.

Your step now, as your plan says: check its work against the data. Then do Method step 6 as written in your prompt: decide, write REPORT.md, card-draft.md and SUMMARY-ko.md, then touch DONE. Also add to SUMMARY-ko.md a short section on what changed compared with the first run in run1/ and why.

It is $(now) KST. $DEADLINE
EOF
lead 7 cont4.md
for f in REPORT.md card-draft.md SUMMARY-ko.md; do
  fresh "$T/$f" $t0 || stop "step 7: $f missing, empty or not written in this step"
done
[[ -e "$T/DONE" ]] && (( $(mtime "$T/DONE") >= t0 )) || stop "step 7: DONE not written"
log "cont finished; DONE=yes"
