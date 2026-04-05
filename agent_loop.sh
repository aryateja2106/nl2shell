#!/usr/bin/env zsh
# ─────────────────────────────────────────────────────────────────────────────
# NL2Shell Autoresearch — Overnight Agent Loop
# Drives GitHub Copilot to iteratively improve train.py via lecoder-cgpu.
#
# Usage:
#   ./agent_loop.sh                        # default: 8 iterations, claude-sonnet-4
#   MAX_ITERATIONS=4 ./agent_loop.sh       # fewer iterations
#   COPILOT_MODEL=gpt-4.1 ./agent_loop.sh  # different model
#   DRY_RUN=1 ./agent_loop.sh              # plan only, skip GPU execution
#
# Prerequisites:
#   - copilot CLI authenticated  (copilot --version)
#   - lecoder-cgpu authenticated  (lecoder-cgpu status)
#   - HF_TOKEN set in environment
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_TSV="$PROJECT_DIR/results.tsv"
LOGS_DIR="$PROJECT_DIR/logs"
TRAIN_PY="$PROJECT_DIR/train.py"
PREPARE_PY="$PROJECT_DIR/prepare.py"

# Planning model — proposes and implements changes (big + smart)
PLAN_MODEL="${PLAN_MODEL:-claude-opus-4.5}"
# Review model — lightweight post-iteration analysis and retry hints
REVIEW_MODEL="${REVIEW_MODEL:-gpt-5.4-mini}"
# Legacy alias (still accepted)
if [[ -n "${COPILOT_MODEL:-}" ]]; then PLAN_MODEL="$COPILOT_MODEL"; fi

MAX_ITERATIONS="${MAX_ITERATIONS:-8}"
DRY_RUN="${DRY_RUN:-0}"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

# ── Helpers ───────────────────────────────────────────────────────────────────
log()  { echo -e "${CYAN}[loop]${RESET} $*"; }
ok()   { echo -e "${GREEN}[keep]${RESET} $*"; }
warn() { echo -e "${YELLOW}[warn]${RESET} $*"; }
fail() { echo -e "${RED}[fail]${RESET} $*"; }

die() { fail "$1"; exit 1; }

# ── Preflight ─────────────────────────────────────────────────────────────────
log "Checking prerequisites..."

command -v copilot >/dev/null 2>&1 || die "copilot CLI not found — run: brew install gh && gh extension install github/copilot"
command -v lecoder-cgpu >/dev/null 2>&1 || die "lecoder-cgpu not found — run: npm install -g lecoder-cgpu"

[[ -f "$TRAIN_PY" ]]   || die "train.py not found in $PROJECT_DIR"
[[ -f "$PREPARE_PY" ]] || die "prepare.py not found in $PROJECT_DIR"
[[ -f "$PROJECT_DIR/program.md" ]] || die "program.md not found in $PROJECT_DIR"

if [[ -z "${HF_TOKEN:-}" ]]; then
  warn "HF_TOKEN not set — model will not push to HuggingFace"
fi

mkdir -p "$LOGS_DIR"

# ── Init results.tsv ──────────────────────────────────────────────────────────
if [[ ! -f "$RESULTS_TSV" ]]; then
  echo -e "timestamp\titeration\tloss\teval_pass\ttrain_time_s\tscore\tstatus\tdescription" > "$RESULTS_TSV"
  log "Initialized $RESULTS_TSV"
fi

# ── Best score tracking ───────────────────────────────────────────────────────
get_best_score() {
  # Read last KEEP row's score from results.tsv (col 6, 1-indexed)
  awk -F'\t' '$7 == "KEEP" { best = $6 } END { print (best == "" ? "0" : best) }' "$RESULTS_TSV"
}

get_best_loss() {
  awk -F'\t' '$7 == "KEEP" { best = $3 } END { print (best == "" ? "9999" : best) }' "$RESULTS_TSV"
}

get_baseline_loss() {
  # First KEEP row's loss is the baseline for normalization
  awk -F'\t' 'NR==2 && $7 == "KEEP" { print $3; exit } END { if (!found) print "9999" }' "$RESULTS_TSV"
}

compute_score() {
  local loss="$1" eval_pass="$2" baseline_loss="$3"
  python3 -c "
loss = float('$loss')
ep   = float('$eval_pass')
bl   = float('$baseline_loss')
if bl <= 0 or bl == 9999:
    bl = loss  # first run: baseline = self, score = 0.4 * ep/7
loss_norm = loss / bl if bl > 0 else 1.0
score = 0.60 * (1 - loss_norm) + 0.40 * (ep / 7)
print(f'{score:.4f}')
"
}

# ── Parse train output ────────────────────────────────────────────────────────
parse_loss() {
  # Matches "  Loss: 0.8234" from train.py output
  grep 'Loss:' "$1" | grep -oE '[0-9]+\.[0-9]+' | tail -1
}

parse_eval_pass() {
  # Count CMD lines that contain an actual command (non-empty after "CMD: ")
  grep -cE '^ +CMD: .+' "$1" || echo 0
}

parse_train_time() {
  grep 'Time:' "$1" | grep -oE '[0-9]+s' | grep -oE '[0-9]+' | tail -1
}

# ── Copilot prompt builder ────────────────────────────────────────────────────
build_copilot_prompt() {
  local iteration="$1"
  local best_score best_loss results_summary hint_section
  best_score="$(get_best_score)"
  best_loss="$(get_best_loss)"
  results_summary="$(tail -n 5 "$RESULTS_TSV" 2>/dev/null || echo '(no runs yet)')"

  # Inject hint from previous mini-review if available
  hint_section=""
  if [[ -n "$LAST_HINT" ]]; then
    hint_section="\n## Hint from previous review (mini-model suggestion)\n  ${LAST_HINT}\nConsider this hint when choosing your change, but use your own judgement."
  fi

  cat <<PROMPT
You are the NL2Shell autoresearch agent (iteration ${iteration} of ${MAX_ITERATIONS}).

## Your task
Propose and implement EXACTLY ONE improvement to train.py.
- Read program.md for policy and constraints.
- Read the current results summary below.
- Edit train.py with ONE targeted change.
- Do NOT run training, do NOT modify prepare.py.
- After editing, output a single line: CHANGE: <30-word description>

## Current best
  score: ${best_score}
  loss:  ${best_loss}

## Recent results (results.tsv tail)
${results_summary}
${hint_section}
## Project files
- program.md  — research policy (read this first)
- train.py    — the only file you may edit
- prepare.py  — IMMUTABLE, do not touch

Now read program.md, check recent results, and make your single best improvement to train.py.
PROMPT
}

# ── Main loop ─────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}NL2Shell Autoresearch Loop${RESET}"
echo -e "  Plan model:   ${PLAN_MODEL}"
echo -e "  Review model: ${REVIEW_MODEL}"
echo -e "  Iterations: ${MAX_ITERATIONS}"
echo -e "  Project:    ${PROJECT_DIR}"
echo -e "  DryRun:     ${DRY_RUN}"
echo ""

ITERATION=0
LAST_HINT=""  # hint from previous mini-review, fed into next planning prompt
while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
  ITERATION=$((ITERATION + 1))
  TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  LOG_FILE="$LOGS_DIR/iter_${ITERATION}_$(date +%Y%m%d_%H%M%S).log"

  echo -e "\n${BOLD}━━━ Iteration ${ITERATION}/${MAX_ITERATIONS} ━━━${RESET}"

  # ── Step 1: Copilot edits train.py (PLAN_MODEL) ────────────────────────────
  log "Running Copilot plan (${PLAN_MODEL}) to propose change..."
  PROMPT="$(build_copilot_prompt "$ITERATION")"

  COPILOT_OUT=""
  if [[ "$DRY_RUN" == "1" ]]; then
    warn "DRY_RUN: skipping Copilot edit"
    CHANGE_DESC="dry-run-no-change"
  else
    COPILOT_OUT="$(
      copilot \
        --model "$PLAN_MODEL" \
        --allow-all-tools \
        --no-ask-user \
        --add-dir "$PROJECT_DIR" \
        --prompt "$PROMPT" \
        2>&1 | tee "${LOG_FILE}.copilot"
    )" || {
      warn "Copilot exited non-zero — continuing with unchanged train.py"
    }
    # Extract CHANGE: line from copilot output
    CHANGE_DESC="$(echo "$COPILOT_OUT" | grep 'CHANGE:' | sed 's/.*CHANGE:[[:space:]]*//' | head -1 || echo 'unspecified change')"
    log "Change: ${CHANGE_DESC}"
  fi

  # ── Step 2: Upload files to Colab ───────────────────────────────────────────
  if [[ "$DRY_RUN" == "1" ]]; then
    warn "DRY_RUN: skipping lecoder-cgpu upload"
  else
    log "Uploading train.py + prepare.py to Colab..."
    lecoder-cgpu copy "$TRAIN_PY" 2>&1 | tee -a "$LOG_FILE" \
      || { warn "Upload failed — skipping iteration"; continue; }
    lecoder-cgpu copy "$PREPARE_PY" 2>&1 | tee -a "$LOG_FILE" \
      || { warn "Upload failed — skipping iteration"; continue; }
  fi

  # ── Step 3: Run training on Colab ───────────────────────────────────────────
  TRAIN_LOG="${LOG_FILE}.train"
  if [[ "$DRY_RUN" == "1" ]]; then
    warn "DRY_RUN: skipping GPU training"
    # Fake output for testing
    echo "  Loss: 1.2345" > "$TRAIN_LOG"
    echo "  Time: 120s"  >> "$TRAIN_LOG"
    echo "  CMD: ls -la" >> "$TRAIN_LOG"
    echo "  CMD: find . -name '*.py'" >> "$TRAIN_LOG"
    echo "  CMD: tail -20 /var/log/syslog" >> "$TRAIN_LOG"
    echo "  CMD: tar -czf backup.tar.gz ~" >> "$TRAIN_LOG"
    echo "  CMD: lsof -i :8080" >> "$TRAIN_LOG"
    echo "  CMD: ps aux --sort=-%mem" >> "$TRAIN_LOG"
    echo "  CMD: find . -name '*.py' | xargs wc -l" >> "$TRAIN_LOG"
  else
    log "Running train.py on Colab GPU..."
    # Must pass HF_TOKEN inline — lecoder-cgpu run starts a fresh shell with no local env vars
    # Files upload to /content/, must use absolute path
    lecoder-cgpu run bash -c "HF_TOKEN='${HF_TOKEN}' python3 /content/train.py" 2>&1 | tee "$TRAIN_LOG" \
      || { warn "Training run failed — marking as DISCARD"; TRAIN_FAILED=1; }
  fi

  # ── Step 4: Parse results ───────────────────────────────────────────────────
  LOSS="$(parse_loss "$TRAIN_LOG")"
  EVAL_PASS="$(parse_eval_pass "$TRAIN_LOG")"
  TRAIN_TIME="$(parse_train_time "$TRAIN_LOG" || echo '0')"

  if [[ -z "$LOSS" ]]; then
    warn "Could not parse loss from training output — marking DISCARD"
    echo -e "${TIMESTAMP}\t${ITERATION}\tN/A\t${EVAL_PASS}\t0\t0\tDISCARD\t${CHANGE_DESC}" >> "$RESULTS_TSV"
    # Revert train.py
    git -C "$PROJECT_DIR" checkout train.py 2>/dev/null && log "train.py reverted"
    continue
  fi

  BASELINE_LOSS="$(get_baseline_loss)"
  SCORE="$(compute_score "$LOSS" "$EVAL_PASS" "$BASELINE_LOSS")"
  BEST_SCORE="$(get_best_score)"

  log "  loss=${LOSS}  eval_pass=${EVAL_PASS}/7  score=${SCORE}  best=${BEST_SCORE}"

  # ── Step 5: Keep or discard ─────────────────────────────────────────────────
  BEST_EVAL="$(awk -F'\t' '$7 == "KEEP" { best = $4 } END { print (best == "" ? "0" : best) }' "$RESULTS_TSV")"

  KEEP=0
  if python3 -c "exit(0 if float('$SCORE') > float('$BEST_SCORE') else 1)" 2>/dev/null; then
    if python3 -c "exit(0 if int('$EVAL_PASS') >= int('$BEST_EVAL') else 1)" 2>/dev/null; then
      KEEP=1
    else
      warn "eval_pass regressed (${EVAL_PASS} < ${BEST_EVAL}) — discarding"
    fi
  else
    warn "score did not improve (${SCORE} <= ${BEST_SCORE}) — discarding"
  fi

  if [[ $KEEP -eq 1 ]]; then
    ok "KEEP  score=${SCORE}  loss=${LOSS}  eval=${EVAL_PASS}/7"
    echo -e "${TIMESTAMP}\t${ITERATION}\t${LOSS}\t${EVAL_PASS}\t${TRAIN_TIME}\t${SCORE}\tKEEP\t${CHANGE_DESC}" >> "$RESULTS_TSV"
    # Commit the improvement
    git -C "$PROJECT_DIR" add train.py 2>/dev/null \
      && git -C "$PROJECT_DIR" commit -m "feat(train): iter ${ITERATION} — ${CHANGE_DESC}" 2>/dev/null \
      && log "Committed train.py (iter ${ITERATION})"
  else
    fail "DISCARD  score=${SCORE}  loss=${LOSS}  eval=${EVAL_PASS}/7"
    echo -e "${TIMESTAMP}\t${ITERATION}\t${LOSS}\t${EVAL_PASS}\t${TRAIN_TIME}\t${SCORE}\tDISCARD\t${CHANGE_DESC}" >> "$RESULTS_TSV"
    git -C "$PROJECT_DIR" checkout train.py 2>/dev/null && log "train.py reverted to last KEEP"

    # ── Mini-review (REVIEW_MODEL) ─────────────────────────────────────────
    # Lightweight post-discard analysis — suggests a hint for the next iteration
    if [[ "$DRY_RUN" != "1" && $ITERATION -lt $MAX_ITERATIONS ]]; then
      log "Running mini-review (${REVIEW_MODEL})..."
      REVIEW_PROMPT="NL2Shell autoresearch: iteration ${ITERATION} was DISCARDED.

Result: loss=${LOSS}  eval_pass=${EVAL_PASS}/7  score=${SCORE}  best_score=${BEST_SCORE}
Change attempted: ${CHANGE_DESC}

Recent results (last 5 rows of results.tsv):
$(tail -n 5 "$RESULTS_TSV")

In ONE sentence (max 20 words), what single hyperparameter or config change should the next iteration try?
Output only: HINT: <suggestion>"

      REVIEW_OUT="$(
        copilot \
          --model "$REVIEW_MODEL" \
          --no-ask-user \
          --prompt "$REVIEW_PROMPT" \
          2>/dev/null | grep 'HINT:' | sed 's/.*HINT:[[:space:]]*//' | head -1
      )" || true

      if [[ -n "$REVIEW_OUT" ]]; then
        log "Review hint → ${REVIEW_OUT}"
        echo "# iter ${ITERATION} hint: ${REVIEW_OUT}" >> "$LOGS_DIR/hints.log"
        LAST_HINT="$REVIEW_OUT"  # carry hint into next planning prompt
      fi
    fi
  fi
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}━━━ Autoresearch Complete ━━━${RESET}"
echo ""
echo "Results summary:"
column -t -s $'\t' "$RESULTS_TSV"
echo ""
FINAL_BEST="$(get_best_score)"
FINAL_LOSS="$(get_best_loss)"
echo -e "${GREEN}Best score: ${FINAL_BEST}  |  Best loss: ${FINAL_LOSS}${RESET}"
echo ""
echo "Logs: $LOGS_DIR"
echo "Results: $RESULTS_TSV"
