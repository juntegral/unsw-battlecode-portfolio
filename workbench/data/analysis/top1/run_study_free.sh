#!/bin/zsh
# Free-running driver for the top-team study. Replaces run_study_cont.sh (stopped while sub-session A ran).
# Waits for sub-session A, then alternates: resume the lead -> run the sub-session it asks for (NEXT_SUB)
# until the lead writes DONE. No deadline, no timeouts; only a runaway stop at MAX_SUBS sub-sessions.
U="~/01. Project/개인 프로젝트/unsw-swarm"; T="$U/data/analysis/top1"
B="~/01. Project/개인 프로젝트/battlecode"
SID="97432d25-be04-4d12-9524-9d47524e347a"
J="$T/study-cont.jsonl"
APID=91648
A_STARTED="2026-10-05 04:18:03"
MAX_SUBS=12

# session variables of whatever shell launched this driver must not leak into the study sessions
unset CLAUDECODE CLAUDE_CODE_ENTRYPOINT CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS CLAUDE_JOB_DIR CLAUDE_CODE_AGENT \
  CLAUDE_CODE_MESSAGING_SOCKET CLAUDE_CODE_MESSAGING_TOKEN CLAUDE_CODE_EXECPATH CLAUDE_CODE_SESSION_ID \
  CLAUDE_CODE_CHILD_SESSION CLAUDE_CODE_SESSION_ATTENDED CLAUDE_PID CLAUDE_EFFORT

# same environment as run_study.sh and run_study_cont.sh gave the sessions
export LOOP_GUARD="$B/work/loop/guard.py" CARD_LOOP_GUARD="$B/work/loop/guard.py" LOOP_TREE="$T" LOOP_OUT="$T" \
  LOOP_STEP=study CARD_LOOP_GAMES=0 LOOP_BATCH_LEASE=0

log() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$T/study.log"; }
now() { date '+%H:%M'; }
stop() { log "free STOPPED: $*"; exit 1; }
mtime() { /usr/bin/stat -f %m "$1"; }
size() { wc -c < "$1" 2>/dev/null | tr -d ' '; }
# written (non-empty) at or after epoch $2
fresh() { [[ -s "$1" ]] && (( $(mtime "$1") >= $2 )); }
a_alive() { [[ "$(ps -p $APID -o command= 2>/dev/null)" == "claude -p --model opus --effort max"* ]]; }

cd "$T" || exit 1

# lead <n> <message file>: resume the lead session with the message on stdin
lead() {
  local n=$1 msg=$2 before rc res
  [[ -s "$T/$msg" ]] || stop "lead step $n: $msg missing or empty"
  [[ -f "$J" ]] || : > "$J"
  before=$(wc -l < "$J" | tr -d ' ')
  log "free lead step $n start: lead resumed with $msg"
  claude -p --resume "$SID" --model opus --effort high --permission-mode bypassPermissions --settings "$B/work/loop/settings.json" --output-format stream-json --verbose < "$T/$msg" >> "$J" 2>&1
  rc=$?
  res=$(tail -n +$((before+1)) "$J" | grep '"type":"result"' | tail -1)
  log "free lead step $n end: lead exit=$rc $(echo "$res" | grep -oE '"(subtype|is_error|num_turns|duration_ms|session_id)":[^,}]*' | tr '\n' ' ')"
  (( rc == 0 )) || stop "lead step $n: lead exit code $rc"
  [[ -n "$res" ]] || stop "lead step $n: no result line in study-cont.jsonl"
  [[ "$res" == *'"is_error":true'* ]] && stop "lead step $n: lead result is an error"
  [[ "$res" == *"\"session_id\":\"$SID\""* ]] || stop "lead step $n: lead answered in a different session"
}

# sub <prompt file>: one sub-session, the command from STUDY-PROMPT.md; sets SUB_REPORT for the lead
sub() {
  local f=$1 out="${1%.md}.out" t0 rc s e g changed=""
  t0=$(date +%s); s=$(now)
  SUBS=$((SUBS+1))
  log "free sub-session $SUBS start: $f -> $out"
  claude -p --model opus --effort max --permission-mode bypassPermissions --settings "~/01. Project/개인 프로젝트/battlecode/work/loop/settings.json" --output-format text < "$f" > "$out" 2>&1
  rc=$?; e=$(now)
  for g in "$T"/*.md(N); do
    [[ "${g:t}" == "$f" || "${g:t}" == free<->.md ]] && continue
    fresh "$g" $t0 && changed+="${g:t} "
  done
  [[ -n "$changed" ]] || changed="none "
  log "free sub-session $SUBS end: $f exit=$rc; $out $(size "$T/$out") bytes; .md files written during it: $changed"
  SUB_REPORT="Sub-session $f has finished (ran $s-$e KST, exit code $rc). What it printed is in $out ($(size "$T/$out") bytes). The .md files in this directory written while it ran: ${changed% }."
}

# ---- wait for sub-session A, started by the old driver
T0A=$(date -j -f '%Y-%m-%d %H:%M:%S' "$A_STARTED" +%s) || stop "cannot parse the start time of sub-session A"
log "free driver start (pid $$): waiting for sub-session A (pid $APID) to exit; no time limit"
while a_alive; do sleep 30; done
A_END=$(now)
if fresh "$T/deep-read.md" $T0A; then
  A_OUT="Its output file deep-read.md was written after 04:18 ($(size "$T/deep-read.md") bytes, last written $(date -r $(mtime "$T/deep-read.md") '+%H:%M') KST)"
else
  A_OUT="Its output file deep-read.md was NOT written after 04:18 (the file there is missing, empty or the earlier one)"
fi
log "free: sub-session A (pid $APID) has exited (seen at $A_END). $A_OUT; subA.out $(size "$T/subA.out") bytes"

# ---- loop: lead -> DONE, or NEXT_SUB -> sub-session -> lead
SUBS=1   # sub-session A counts
N=0
NUDGED=0
NEXT_MSG="Sub-session A (prompt subA.md) has finished. It started at 04:18 KST and had exited by $A_END KST. Its exit code is not known, because the driver was replaced while it ran. $A_OUT. What it printed is in subA.out ($(size "$T/subA.out") bytes)."
while true; do
  N=$((N+1)); msg="free$N.md"
  {
    print -r -- "$NEXT_MSG"
    if (( N == 1 )); then
      cat <<'EOF'

New terms from the user. They replace the limits in your prompt and in the earlier continuation message:
- The user has lifted the limits. There is no 08:30 deadline any more and no time budget for you or for sub-sessions; do not shorten or cut anything for time. Depth matters.
- You are no longer limited to three sub-sessions or to the fixed A, B, C order. Follow the method in your plan, and add steps where they make the study better: for example run the close read again or extend it if the time budget you gave it cut it short, extra sub-sessions for specific questions, another red-team round.
- How to get a sub-session: write a self-contained prompt file in this directory, then write its filename (one line) into a file named NEXT_SUB, and stop. A driver runs it at max effort and resumes you with the result. Do not start processes yourself.
- When the study is complete as in step 6 of your plan, write the outputs and touch DONE instead of writing NEXT_SUB.
- Unchanged: the goal, the protagonist (the rank-1 team of the snapshot), the rules in your prompt (read-only towards the outside, nothing posted anywhere). The safety hook still blocks uploads, battle requests, pushes and shell access to the loop's own files; use the Read tool where it says so.
EOF
    fi
  } > "$T/$msg"
  lead $N $msg

  if [[ -e "$T/DONE" ]]; then
    log "free finished; DONE=yes; sub-sessions in total: $SUBS; lead steps by this driver: $N"
    exit 0
  fi

  if [[ -e "$T/NEXT_SUB" ]]; then
    f=$(grep -m 1 '[^[:space:]]' "$T/NEXT_SUB" | tr -d '\r' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    rm -f "$T/NEXT_SUB"
    problem=""
    if [[ -z "$f" ]]; then problem="it was empty"
    elif [[ "$f" == */* ]]; then problem="'$f' is not a plain filename in this directory"
    elif [[ ! -f "$T/$f" || ! -s "$T/$f" ]]; then problem="the prompt file '$f' does not exist in this directory or is empty"
    fi
    if [[ -z "$problem" ]]; then
      log "free: lead asked for a sub-session with $f (NEXT_SUB removed)"
      (( SUBS >= MAX_SUBS )) && stop "RUNAWAY STOP: $SUBS sub-sessions have already run (limit $MAX_SUBS); the lead asked for another one ($f). Not started. Study left without DONE"
      sub "$f"
      NUDGED=0
      NEXT_MSG="$SUB_REPORT"
      continue
    fi
    log "free: NEXT_SUB not usable: $problem (NEXT_SUB removed)"
    why="The NEXT_SUB you wrote could not be used: $problem."
  else
    log "free: lead stopped without DONE and without NEXT_SUB"
    why="You stopped without writing NEXT_SUB or DONE."
  fi
  (( NUDGED )) && stop "the lead was asked once more and again wrote neither a usable NEXT_SUB nor DONE"
  NUDGED=1
  NEXT_MSG="$why Either write NEXT_SUB (one line: the filename of a sub-session prompt in this directory) and stop, or finish the study and touch DONE."
done
