#!/bin/bash
# ---------------------------------------------------------------------------
# run_job.sh -- process ONE file of one sample and mass bin.
#
# Used directly for local runs and by the Slurm and HTCondor wrappers.
#
#   --mode reco    sim -> reco slcio + ntuple (full reco_steer_jets.py chain)
#   --mode ntuple  existing reco slcio -> ntuple only (ntuple_only.py)
#
# Usage:
#   MTS_SITE=<site> scripts/run_job.sh <sample> <mass> <index> [options]
#     <sample>   bb_dijet | cc_dijet | qq_dijet
#     <mass>     m0_100 | m100_1000 | m1000_5000
#     <index>    file index, e.g. 0 -> _00000
#   options:
#     --mode reco|ntuple   (default reco)
#     --nevt N             events to process (default -1 = all)
#     --force              redo even if the outputs already exist
#     --keep-workdir       keep the scratch work directory for debugging
#
# Paths come from config/sites/$MTS_SITE.env; any of DATA_ROOT, RECO_ROOT,
# OUT_ROOT may be a local path or a root:// URL. Remote inputs are staged to the
# work directory with xrdcp; remote outputs are copied back with xrdcp.
#
# Each job runs k4run in its own work directory (with a conf/ symlink the
# steering needs), so nothing is written into the repo.
#
# The ntuple is validated before it is published (k4run exit code, the local
# LCTuple library was loaded, JET_kt and TrueJets filled, nmcp present) and gets
# a TNamed "mts_provenance" (JSON: repo and LCTuple commits, image, input, ...).
# On any failure nothing is published and the job exits non-zero.
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=job
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

MODE=reco; NEVT=-1; FORCE="${FORCE:-0}"; KEEP_WORKDIR="${KEEP_WORKDIR:-0}"; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --nevt) NEVT="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --keep-workdir) KEEP_WORKDIR=1; shift ;;
    -h|--help) sed -n '2,31p' "$0"; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 3 ]] || die "usage: $0 <sample> <mass> <index> [--mode reco|ntuple] [--nevt N] [--force]"
SAMPLE="${POS[0]}"; MASS="${POS[1]}"; INDEX="${POS[2]}"
[[ "$MODE" == reco || "$MODE" == ntuple ]] || die "--mode must be reco or ntuple"
[[ "$INDEX" =~ ^[0-9]+$ ]] || die "index must be a number"

mts_load_site
mts_check_sample "$SAMPLE" "$MASS"
Q="${SAMPLE%%_*}"
SUFFIX="$(printf '%05d' "$((10#$INDEX))")"
STEM="${Q}_${MASS}_${SUFFIX}"
BIN="$SAMPLE/$MASS"

OUT_TUPLE="$OUT_ROOT/$BIN/$NTUPLE_SUBDIR/tuples_${STEM}.root"
if [[ "$MODE" == reco ]]; then
  STEER_FILE=reco_steer_jets.py
  INPUT="$DATA_ROOT/$BIN/sim/sim_${STEM}.slcio"
  OUT_RECO="$OUT_ROOT/$BIN/recoSig/reco_${STEM}.slcio"
else
  STEER_FILE=ntuple_only.py
  INPUT="$RECO_ROOT/$BIN/recoSig/reco_${STEM}.slcio"
  OUT_RECO=""
fi

echo "========================================================================"
info "site $MTS_SITE | mode $MODE | $BIN | index $SUFFIX | nevt $NEVT | host $(hostname)"
info "input  : $INPUT"
info "ntuple : $OUT_TUPLE"
[[ -n "$OUT_RECO" ]] && info "reco   : $OUT_RECO"
echo "========================================================================"

# --- skip if already done ----------------------------------------------------
if [[ "$FORCE" != 1 ]] && mts_exists "$OUT_TUPLE" && { [[ -z "$OUT_RECO" ]] || mts_exists "$OUT_RECO"; }; then
  grn "[job] SKIP: outputs already exist (use --force to redo)"; exit 0
fi

[[ -f "$IMAGE" ]] || die "container image not found: $IMAGE"
[[ -f "$STEER_DIR/$STEER_FILE" ]] || die "steering file not found: $STEER_DIR/$STEER_FILE"
mts_check_library

# --- work directory ------------------------------------------------------------
WORK="$(mktemp -d "$SCRATCH_ROOT/mts_${STEM}_${MODE}_XXXXXX")"
cleanup() { if [[ "$KEEP_WORKDIR" == 1 ]]; then info "work dir kept: $WORK"; else rm -rf "$WORK"; fi; }
trap cleanup EXIT
ln -s "$STEER_DIR/conf" "$WORK/conf"      # steering uses sys.path 'conf' and conf/... paths

# --- stage input ---------------------------------------------------------------
if is_remote "$INPUT"; then
  info "staging input with $XRDCP"
  mts_fetch "$INPUT" "$WORK/input.slcio" || die "could not fetch $INPUT"
  IN_LOCAL="$WORK/input.slcio"
else
  [[ -f "$INPUT" ]] || die "input not found: $INPUT"
  IN_LOCAL="$INPUT"
fi

# --- run -----------------------------------------------------------------------
ARGS="--input '$IN_LOCAL' --tupleout '$WORK/tuples.root' --nevt $NEVT"
[[ "$MODE" == reco ]] && ARGS+=" --overlay $OVERLAY --output '$WORK/reco.slcio' --root '$WORK/aida'"

START=$(date +%s)
set +e
mts_exec "$WORK" "$(dirname "$IN_LOCAL")" -- "
  cd '$WORK'
  export MARLIN_DLL=\$(echo \$MARLIN_DLL | sed 's|$CONTAINER_LCTUPLE|$LCTUPLE_LIB|')
  k4run '$STEER_DIR/$STEER_FILE' $ARGS
" > "$WORK/k4run.log" 2>&1
RC=$?
set -e
WALL=$(( $(date +%s) - START ))
info "k4run exit $RC, wall time ${WALL}s"

fail() {
  red "[job] FAILED: $*" >&2
  echo "----- last 40 lines of the k4run log -----" >&2; tail -40 "$WORK/k4run.log" >&2
  exit 1
}
[[ "$RC" == 0 ]] || fail "k4run exited with $RC"
grep -q "Loading library ${LCTUPLE_LIB}$" "$WORK/k4run.log" \
  || fail "the local LCTuple library was not loaded (MARLIN_DLL substitution failed)"
[[ -s "$WORK/tuples.root" ]] || fail "no ntuple written"
[[ "$MODE" == ntuple || -s "$WORK/reco.slcio" ]] || fail "no reco slcio written"

# --- validate the ntuple and stamp provenance ------------------------------------
cat > "$WORK/provenance.json" <<EOF
{"mode": "$MODE", "sample": "$SAMPLE", "mass": "$MASS", "index": "$SUFFIX", "nevt": $NEVT,
 "input": "$INPUT", "site": "$MTS_SITE", "host": "$(hostname)",
 "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "wall_s": $WALL,
 "repo_commit": "$(mts_git_desc "$MTS_REPO")",
 "lctuple_commit": "$(mts_bi lctuple_commit)", "lctuple_describe": "$(mts_bi lctuple_describe)",
 "lctuple_built_at": "$(mts_bi built_at)",
 "image": "$IMAGE", "image_sha256": "$(mts_bi image_sha256)", "overlay": "$OVERLAY"}
EOF
cat > "$WORK/check.py" <<'EOF'
import json, sys, ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
path, prov = sys.argv[1], sys.argv[2]
f = ROOT.TFile.Open(path, "UPDATE")
if not f or f.IsZombie():
    sys.exit("cannot open ntuple")
n = {}
for name in ("JET_kt", "TrueJets"):
    t = f.Get(name)
    if not t or t.GetEntries() == 0:
        sys.exit(f"tree {name} missing or empty")
    n[name] = t.GetEntries()
if n["JET_kt"] != n["TrueJets"]:
    sys.exit(f"entry mismatch {n}")
if not f.Get("TrueJets").GetBranch("nmcp"):
    sys.exit("TrueJets has no nmcp branch")
text = json.dumps(dict(json.load(open(prov)), entries=n["TrueJets"]))
f.cd(); ROOT.TNamed("mts_provenance", text).Write("", ROOT.TObject.kOverwrite); f.Close()
print(f"OK entries={n['TrueJets']}")
EOF
CHECK="$(mts_exec "$WORK" -- "python3 '$WORK/check.py' '$WORK/tuples.root' '$WORK/provenance.json'" 2>&1 | tail -1)" || true
[[ "$CHECK" == OK* ]] || fail "ntuple validation: $CHECK"
info "ntuple check: $CHECK"

# --- publish -------------------------------------------------------------------------
if [[ -n "$OUT_RECO" ]]; then
  mts_publish "$WORK/reco.slcio" "$OUT_RECO" || fail "could not publish $OUT_RECO"
fi
mts_publish "$WORK/tuples.root" "$OUT_TUPLE" || fail "could not publish $OUT_TUPLE"
grn "[job] SUCCESS $BIN $SUFFIX ($MODE, ${CHECK#OK }, ${WALL}s)"
