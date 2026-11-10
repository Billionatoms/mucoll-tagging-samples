#!/bin/bash
# ---------------------------------------------------------------------------
# run_sim.sh -- simulate ONE chunk of SIM_EVENTS (25) generated events with ddsim.
#
# Usage:
#   MTS_SITE=<site> scripts/run_sim.sh <sample> <index> [options]
#     <sample>   bb_schannel | cc_schannel | qq_schannel | tc_signal
#     <index>    sim file index, e.g. 0 -> _00000
#   options:
#     --nevt N          simulate only the first N events of the chunk (tests)
#     --force           redo even if the output already exists
#     --keep-workdir    keep the scratch work directory for debugging
#
# Chunk <index> is events skip .. skip+SIM_EVENTS-1 of generator file j, where
#   per_file = EVENTS_PER_JOB / SIM_EVENTS,  j = index / per_file,
#   skip = (index % per_file) * SIM_EVENTS
# (generation/processes/<sample>/process.env). A chunk past the end of its file
# (Pythia dropped events, or a short test file) is reported and skipped.
#
# The chunk's events are copied into a file of their own (scripts/hepmc3_chunk.py):
# ddsim --skipNEvents starts one event late with HepMC3 input. ddsim runs in
# $IMAGE (MuSIC v2.5 dev) with sim_steering/sim_steer.py, the MuSIC_v2 geometry
# and seed SIM_SEED_BASE + <index>. The output is checked
# event by event against the HepMC3 file (scripts/check_sim.py) before it is
# published where scripts/run_job.sh --mode reco reads it:
#   $DATA_ROOT/<dir>/sim/sim_<q>_incl_<NNNNN>.slcio
#   $DATA_ROOT/<dir>/sim/sim_<q>_incl_<NNNNN>.json   (provenance)
# where <dir> is the sample's GEN_SAMPLE_DIRS entry in scripts/common.sh, e.g.
# s-channel/dijets/bb_dijets. The input is $GEN_ROOT/<dir>/gen/.
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=sim
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

NEVT=""; FORCE="${FORCE:-0}"; KEEP_WORKDIR="${KEEP_WORKDIR:-0}"; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --nevt) NEVT="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --keep-workdir) KEEP_WORKDIR=1; shift ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 2 ]] || die "usage: $0 <sample> <index> [--nevt N] [--force]"
SAMPLE="${POS[0]}"; INDEX="${POS[1]}"
[[ "$INDEX" =~ ^[0-9]+$ ]] || die "index must be a number"

mts_load_site
mts_check_sample "$SAMPLE" "$GEN_BIN"
: "${GEN_ROOT:?GEN_ROOT not set by site config}"
# shellcheck source=/dev/null
source "$MTS_REPO/generation/processes/$SAMPLE/process.env"
(( EVENTS_PER_JOB % SIM_EVENTS == 0 )) || die "EVENTS_PER_JOB is not a multiple of SIM_EVENTS"
PER_FILE=$(( EVENTS_PER_JOB / SIM_EVENTS ))
IDX=$(( 10#$INDEX ))
JOB=$(( IDX / PER_FILE ))
SKIP=$(( (IDX % PER_FILE) * SIM_EVENTS ))
SEED=$(( SIM_SEED_BASE + IDX ))
Q="${SAMPLE%%_*}"
GEN_STEM="${Q}_${GEN_BIN}_$(printf '%04d' "$JOB")"
STEM="${Q}_${GEN_BIN}_$(printf '%05d' "$IDX")"
mts_sample_dirs "$SAMPLE" "$GEN_BIN"
GEN_DIR="$GEN_ROOT/$SAMPLE_DIR/gen"
IN_HEPMC="$GEN_DIR/gen_${GEN_STEM}.hepmc3"
OUT_DIR="$DATA_ROOT/$SAMPLE_DIR/sim"
OUT_SIM="$OUT_DIR/sim_${STEM}.slcio"
STEER="$MTS_REPO/sim_steering/sim_steer.py"
COMPACT=/usr/share/muonc-detector-geometry/MuSIC_v2/MuSIC_v2.xml

echo "========================================================================"
info "site $MTS_SITE | $SAMPLE index $IDX | gen file $GEN_STEM, skip $SKIP | seed $SEED | host $(hostname)"
info "input  : $IN_HEPMC"
info "output : $OUT_SIM"
echo "========================================================================"

if [[ "$FORCE" != 1 ]] && mts_exists "$OUT_SIM" && mts_exists "$OUT_DIR/sim_${STEM}.json" 0; then
  grn "[sim] SKIP: output already exists (use --force to redo)"; exit 0
fi
[[ -f "$IMAGE" ]] || die "container image not found: $IMAGE"

WORK="$(mktemp -d "$SCRATCH_ROOT/mts_sim_${STEM}_XXXXXX")"
cleanup() { if [[ "$KEEP_WORKDIR" == 1 ]]; then info "work dir kept: $WORK"; else rm -rf "$WORK"; fi; }
trap cleanup EXIT

# --- how many events this chunk has ----------------------------------------------
# The generator metadata is published last, so it marks a complete HepMC3 file.
mts_fetch "$GEN_DIR/gen_${GEN_STEM}.json" "$WORK/gen.json" \
  || die "no generator metadata for $GEN_STEM: generate it first (generation/run_gen.sh)"
GEN_EVENTS="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["events_hepmc3"])' "$WORK/gen.json")"
if (( SKIP >= GEN_EVENTS )); then
  ylw "[sim] SKIP: $GEN_STEM holds $GEN_EVENTS events, none from $SKIP on"; exit 0
fi
N=$(( GEN_EVENTS - SKIP < SIM_EVENTS ? GEN_EVENTS - SKIP : SIM_EVENTS ))
[[ -n "$NEVT" ]] && (( NEVT < N )) && N=$NEVT

if is_remote "$IN_HEPMC"; then
  info "staging input with $XRDCP"
  mts_fetch "$IN_HEPMC" "$WORK/full.hepmc3" || die "could not fetch $IN_HEPMC"
  IN_LOCAL="$WORK/full.hepmc3"
else
  [[ -f "$IN_HEPMC" ]] || die "input not found: $IN_HEPMC"
  IN_LOCAL="$IN_HEPMC"
fi
# ddsim --skipNEvents is off by one with HepMC3 input, so the chunk's events are
# copied into a file of their own and ddsim reads it from the start.
GOT="$(python3 "$MTS_REPO/scripts/hepmc3_chunk.py" "$IN_LOCAL" "$WORK/chunk.hepmc3" "$SKIP" "$N")" \
  || die "could not cut events $SKIP.. out of $IN_LOCAL"
[[ "$GOT" == "$N" ]] || die "cut $GOT events out of $IN_LOCAL from event $SKIP, expected $N"

# --- ddsim -------------------------------------------------------------------------
info "ddsim: $N events from event $SKIP"
START=$(date +%s)
set +e
mts_exec "$WORK" -- "
  cd '$WORK'
  ddsim --steeringFile '$STEER' --compactFile '$COMPACT' \
        --inputFiles '$WORK/chunk.hepmc3' --numberOfEvents $N \
        --random.seed $SEED --outputFile '$WORK/sim.slcio'
" > "$WORK/ddsim.log" 2>&1
RC=$?
set -e
WALL=$(( $(date +%s) - START ))
info "ddsim exit $RC, wall time ${WALL}s"

fail() {
  red "[sim] FAILED: $*" >&2
  echo "----- last 40 lines of the ddsim log -----" >&2; tail -40 "$WORK/ddsim.log" >&2
  exit 1
}
[[ "$RC" == 0 ]] || fail "ddsim exited with $RC"
[[ -s "$WORK/sim.slcio" ]] || fail "no sim file written"
CHECK="$(mts_exec "$WORK" "$(dirname "$IN_LOCAL")" -- \
  "python3 '$MTS_REPO/scripts/check_sim.py' '$WORK/sim.slcio' '$IN_LOCAL' $SKIP $N" 2>&1 | tail -1)" || true
[[ "$CHECK" == OK* ]] || fail "check against the HepMC3 file: $CHECK"
info "sim check: $CHECK"

# --- provenance and publish ----------------------------------------------------------
python3 - "$WORK/gen.json" "$WORK/sim.json" <<EOF
import json, sys
g = json.load(open(sys.argv[1]))
json.dump({"sample": "$SAMPLE", "index": $IDX, "stem": "$STEM", "events": $N,
           "input": "$IN_HEPMC", "input_sha256": g.get("hepmc3_sha256"), "skip": $SKIP,
           "gen_seed": g.get("seed"), "sim_seed": $SEED, "cross_section_pb": g.get("cross_section_pb"),
           "steering": "sim_steering/sim_steer.py", "steering_sha256": "$(sha256sum "$STEER" | cut -d' ' -f1)",
           "compact": "$COMPACT", "image": "$IMAGE", "site": "$MTS_SITE", "host": "$(hostname)",
           "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "wall_s": $WALL,
           "repo_commit": "$(mts_git_desc "$MTS_REPO")"}, open(sys.argv[2], "w"), indent=2)
EOF
mts_publish "$WORK/sim.slcio" "$OUT_SIM" || fail "could not publish $OUT_SIM"
mts_publish "$WORK/sim.json" "$OUT_DIR/sim_${STEM}.json" || fail "could not publish the provenance"
grn "[sim] SUCCESS $SAMPLE $STEM ($N events, ${WALL}s)"
