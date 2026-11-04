#!/bin/bash
# ---------------------------------------------------------------------------
# run_gen.sh -- generate ONE HepMC3 file of one process, in the eventgen image.
#
# Usage:
#   MTS_SITE=<site> generation/run_gen.sh <sample> <job> [options]
#     <sample>   bb_schannel | cc_schannel | qq_schannel | tc_signal
#     <job>      generator job index, e.g. 0 -> _0000
#   options:
#     --events N        events in this job (default EVENTS_PER_JOB of the process;
#                       only for tests: scripts/run_sim.sh assumes EVENTS_PER_JOB)
#     --cores N         MadGraph cores (default SLURM_CPUS_PER_TASK or 1)
#     --force           redo even if the output already exists
#     --keep-workdir    keep the scratch work directory for debugging
#
# The process is defined by generation/processes/<sample>/ (proc.mg5,
# run_card.set, process.env); generation/gen_job.py runs MadGraph and Pythia
# inside $GEN_IMAGE. The seed is GEN_SEED_BASE + <job>.
#
# Output, published only if every check in gen_job.py passed:
#   $GEN_ROOT/<dir>/gen/gen_<q>_incl_<JJJJ>.hepmc3
#   $GEN_ROOT/<dir>/gen/gen_<q>_incl_<JJJJ>.json      (metadata + provenance)
#   $GEN_ROOT/<dir>/gen/gen_<q>_incl_<JJJJ>.cards.tgz (MadGraph cards, run banner,
#                                                      Pythia command file, logs)
# where <dir> is the sample's GEN_SAMPLE_DIRS entry in scripts/common.sh, e.g.
# s-channel/dijets/bb_dijets.
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=gen
source "$(dirname "${BASH_SOURCE[0]}")/../scripts/common.sh"

EVENTS=""; CORES="${SLURM_CPUS_PER_TASK:-1}"; FORCE="${FORCE:-0}"; KEEP_WORKDIR="${KEEP_WORKDIR:-0}"; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --events) EVENTS="$2"; shift 2 ;;
    --cores) CORES="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --keep-workdir) KEEP_WORKDIR=1; shift ;;
    -h|--help) sed -n '2,27p' "$0"; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 2 ]] || die "usage: $0 <sample> <job> [--events N] [--cores N] [--force]"
SAMPLE="${POS[0]}"; JOB="${POS[1]}"
[[ "$JOB" =~ ^[0-9]+$ ]] || die "job must be a number"

mts_load_site
mts_check_sample "$SAMPLE" "$GEN_BIN"
: "${GEN_IMAGE:?GEN_IMAGE not set by site config}" "${GEN_ROOT:?GEN_ROOT not set by site config}"
PDIR="$MTS_REPO/generation/processes/$SAMPLE"
# shellcheck source=/dev/null
source "$PDIR/process.env"
EVENTS="${EVENTS:-$EVENTS_PER_JOB}"
[[ "$EVENTS" =~ ^[0-9]+$ && "$EVENTS" -gt 0 ]] || die "--events must be a positive number"
SEED=$(( GEN_SEED_BASE + 10#$JOB ))
Q="${SAMPLE%%_*}"
STEM="${Q}_${GEN_BIN}_$(printf '%04d' "$((10#$JOB))")"
mts_sample_dirs "$SAMPLE" "$GEN_BIN"
OUT_DIR="$GEN_ROOT/$SAMPLE_DIR/gen"
OUT_HEPMC="$OUT_DIR/gen_${STEM}.hepmc3"

UFO_ARGS=(); UFO_BIND=()
if [[ -n "${UFO_RESTRICT_BASE:-}" ]]; then
  : "${TC_UFO:?TC_UFO not set by site config}"
  [[ -d "$TC_UFO" ]] || die "UFO directory not found: $TC_UFO"
  UFO_ARGS=(--ufo "$TC_UFO"); UFO_BIND=("$TC_UFO")
fi

echo "========================================================================"
info "site $MTS_SITE | $SAMPLE job $JOB | $EVENTS events | seed $SEED | $CORES cores | host $(hostname)"
info "output : $OUT_HEPMC"
echo "========================================================================"

if [[ "$FORCE" != 1 ]] && mts_exists "$OUT_HEPMC" && mts_exists "$OUT_DIR/gen_${STEM}.json"; then
  grn "[gen] SKIP: output already exists (use --force to redo)"; exit 0
fi
[[ -f "$GEN_IMAGE" ]] || die "generator image not found: $GEN_IMAGE"

WORK="$(mktemp -d "$SCRATCH_ROOT/mts_gen_${STEM}_XXXXXX")"
cleanup() { if [[ "$KEEP_WORKDIR" == 1 ]]; then info "work dir kept: $WORK"; else rm -rf "$WORK"; fi; }
trap cleanup EXIT
mkdir -p "$WORK/job" "$WORK/home" "$WORK/tmp" "$WORK/cache"

# The image points TMPDIR and the caches at /work, which only exists under
# Docker; here they go into the job's own work directory.
START=$(date +%s)
set +e
IMAGE="$GEN_IMAGE" mts_exec "$WORK" "${UFO_BIND[@]}" -- "
  export HOME='$WORK/home' TMPDIR='$WORK/tmp' XDG_CACHE_HOME='$WORK/cache' \
         PYTHONPYCACHEPREFIX='$WORK/cache/pycache' MPLCONFIGDIR='$WORK/cache/mpl'
  cd '$WORK/job'
  python3 '$MTS_REPO/generation/gen_job.py' --process-dir '$PDIR' --events $EVENTS \
      --seed $SEED --cores $CORES --work '$WORK/job' ${UFO_ARGS[*]}
" > "$WORK/gen.log" 2>&1
RC=$?
set -e
WALL=$(( $(date +%s) - START ))
info "gen_job exit $RC, wall time ${WALL}s"
if [[ "$RC" != 0 ]]; then
  red "[gen] FAILED" >&2; tail -30 "$WORK/gen.log" >&2
  for f in "$WORK"/job/logs/*.log; do [[ -f "$f" ]] && { echo "----- tail $f" >&2; tail -15 "$f" >&2; }; done
  exit 1
fi
tail -1 "$WORK/gen.log"

# --- provenance, then publish --------------------------------------------------
# Hashing the 1 GB image in every job is slow on a shared filesystem, so a
# <image>.sha256 file next to it (sha256sum output) is used when present.
if [[ -f "$GEN_IMAGE.sha256" ]]; then IMAGE_SHA="$(cut -d' ' -f1 "$GEN_IMAGE.sha256")"
else IMAGE_SHA="$(sha256sum "$GEN_IMAGE" | cut -d' ' -f1)"; fi
IMAGE_REV="$("$(mts_container_bin)" inspect --labels "$GEN_IMAGE" 2>/dev/null \
  | sed -n 's/^org.opencontainers.image.revision: //p')"
python3 - "$WORK/job/metadata.json" "$WORK/meta.json" <<EOF
import json, sys
m = json.load(open(sys.argv[1]))
m.update(sample="$SAMPLE", job=$((10#$JOB)), stem="$STEM", site="$MTS_SITE", host="$(hostname)",
         date="$(date -u +%Y-%m-%dT%H:%M:%SZ)", wall_s=$WALL, cores=$CORES,
         repo_commit="$(mts_git_desc "$MTS_REPO")", image="$GEN_IMAGE",
         image_sha256="$IMAGE_SHA", eventgen_commit="$IMAGE_REV")
json.dump(m, open(sys.argv[2], "w"), indent=2)
EOF
( cd "$WORK/job" && tar czf "$WORK/cards.tgz" mg5_commands.txt run_banner.txt pythia.cmnd \
    mg5_proc/Cards logs ) || die "could not pack the cards"
mts_publish "$WORK/cards.tgz" "$OUT_DIR/gen_${STEM}.cards.tgz" || die "could not publish the cards"
mts_publish "$WORK/job/events.hepmc3" "$OUT_HEPMC" || die "could not publish $OUT_HEPMC"
# The metadata goes last: run_sim.sh reads it, so its presence marks a complete file.
mts_publish "$WORK/meta.json" "$OUT_DIR/gen_${STEM}.json" || die "could not publish the metadata"
grn "[gen] SUCCESS $SAMPLE $STEM (${WALL}s)"
