#!/bin/bash
# ---------------------------------------------------------------------------
# batch/slurm/submit_gensim.sh -- submit Slurm job arrays for event generation
# (generation/run_gen.sh) or simulation (scripts/run_sim.sh) of the samples this
# repo generates. Reconstruction and ntuples then go through batch/slurm/submit.sh
# with mass bin "incl", e.g.  batch/slurm/submit.sh bb_schannel incl --range 0-399
#
# Usage:
#   batch/slurm/submit_gensim.sh <gen|sim> <sample> --range A-B [options]
#     <sample>               bb_schannel | cc_schannel | qq_schannel | tc_signal
#     --range A-B            generator job indices (gen) or sim file indices (sim);
#                            with EVENTS_PER_JOB=10000 and 25 events per sim file,
#                            generator job j feeds sim files 400*j .. 400*j+399
#     --max-running N        array concurrency limit (default 100)
#     --site S               site config (default artemis)
#     --dry-run              print the sbatch commands only
#   Extra sbatch options in SBATCH_EXTRA override the defaults below, e.g.
#     SBATCH_EXTRA="--mem=48G --time=2-00:00:00" batch/slurm/submit_gensim.sh sim tc_signal --range 0-3
#
# Logs: logs/slurm/<stage>_<sample>_<jobid>_<task>.{out,err}
# Resources: gen 4 CPU, 8 GB, 2 h (100 events took 6 s for the s-channel processes
# and 33 s for tc_signal on the laptop); sim 1 CPU (ddsim is single-threaded),
# 8 GB, 4 h: on the laptop bb_schannel took 48 s start-up plus ~120 s and 4.9 GB
# per event, so ~50 min per 25 events. Artemis rejects time limits above its
# partition maximum; 4 h is what the earlier reco arrays used there. Check the
# time on a few tasks on Artemis before submitting thousands.
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=slurm
source "$(dirname "${BASH_SOURCE[0]}")/../../scripts/common.sh"

RANGE=""; MAXRUN=100; SITE=artemis; DRY=0; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --range) RANGE="$2"; shift 2 ;;
    --max-running) MAXRUN="$2"; shift 2 ;;
    --site) SITE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,27p' "$0"; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 2 ]] || die "usage: $0 <gen|sim> <sample> --range A-B [--max-running N] [--dry-run]"
STAGE="${POS[0]}"; SAMPLE="${POS[1]}"
[[ "$STAGE" == gen || "$STAGE" == sim ]] || die "stage must be gen or sim"
[[ "$RANGE" =~ ^[0-9]+-[0-9]+$ ]] || die "--range A-B is required"
[[ -n "${SLURM_JOB_ID:-}" ]] && die "do not run the submitter inside a Slurm job"

if [[ "$STAGE" == gen ]]; then RES=(--time=02:00:00 --cpus-per-task=4 --mem=8G)
else                           RES=(--time=04:00:00 --cpus-per-task=1 --mem=8G); fi

# Fail early (on the login node) rather than in hundreds of jobs.
MTS_SITE="$SITE" mts_load_site
mts_check_sample "$SAMPLE" "$GEN_BIN"
if [[ "$STAGE" == gen ]]; then [[ -f "${GEN_IMAGE:-}" ]] || die "GEN_IMAGE not found: ${GEN_IMAGE:-unset}"
else [[ -f "$IMAGE" ]] || die "IMAGE not found: $IMAGE"; fi

LOGDIR="$MTS_REPO/logs/slurm"; mkdir -p "$LOGDIR"
cmd=(sbatch --job-name="mts_${STAGE}_${SAMPLE}" --array="${RANGE}%${MAXRUN}"
     --nodes=1 --ntasks=1 "${RES[@]}"
     --output="$LOGDIR/${STAGE}_${SAMPLE}_%A_%a.out" --error="$LOGDIR/${STAGE}_${SAMPLE}_%A_%a.err"
     --export="ALL,MTS_REPO_DIR=$MTS_REPO,MTS_SITE=$SITE,MTS_SAMPLE=$SAMPLE,MTS_STAGE=$STAGE"
     ${SBATCH_EXTRA:-} "$MTS_REPO/batch/slurm/gensim_job.sh")
if [[ "$DRY" == 1 ]]; then echo "${cmd[*]}"; else "${cmd[@]}"; fi
