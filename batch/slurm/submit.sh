#!/bin/bash
# ---------------------------------------------------------------------------
# batch/slurm/submit.sh -- submit Slurm job arrays that call scripts/run_job.sh.
#
# Usage:
#   batch/slurm/submit.sh <sample|all> <mass|all> [options]
#     --mode reco|ntuple     (default reco)
#     --range A-B            file indices (default 0-3999)
#     --max-running N        array concurrency limit (default 100; a Lustre
#                            read throttle as much as a CPU limit)
#     --nevt N               events per file (default -1 = all)
#     --site S               site config (default artemis)
#     --dry-run              print the sbatch commands only
#   Extra sbatch options can be passed in SBATCH_EXTRA, e.g.
#     SBATCH_EXTRA="--partition=long --account=epp" batch/slurm/submit.sh all all
#
# Logs: logs/slurm/<mode>_<sample>_<mass>_<jobid>_<task>.{out,err}
# Resources per mode are set below (reco: 4 h, 4 CPU, 8 GB; ntuple: 30 min,
# 1 CPU, 4 GB -- 25 events take about 10 s in ntuple mode).
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=slurm
source "$(dirname "${BASH_SOURCE[0]}")/../../scripts/common.sh"

MODE=reco; RANGE=0-3999; MAXRUN=100; NEVT=-1; SITE=artemis; DRY=0; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --range) RANGE="$2"; shift 2 ;;
    --max-running) MAXRUN="$2"; shift 2 ;;
    --nevt) NEVT="$2"; shift 2 ;;
    --site) SITE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 2 ]] || die "usage: $0 <sample|all> <mass|all> [--mode reco|ntuple] [--range A-B] ..."
[[ "$MODE" == reco || "$MODE" == ntuple ]] || die "--mode must be reco or ntuple"
[[ "$RANGE" =~ ^[0-9]+-[0-9]+$ ]] || die "--range must look like 0-3999"
[[ -n "${SLURM_JOB_ID:-}" ]] && die "do not run the submitter inside a Slurm job"

if [[ "$MODE" == reco ]]; then RES=(--time=04:00:00 --cpus-per-task=4 --mem=8G)
else                           RES=(--time=00:30:00 --cpus-per-task=1 --mem=4G); fi

samples=("${POS[0]}"); [[ "${POS[0]}" == all ]] && samples=("${SAMPLES[@]}")
masses=("${POS[1]}");  [[ "${POS[1]}" == all ]] && masses=("${MASSES[@]}")

# Fail early (on the login node) rather than in thousands of jobs.
MTS_SITE="$SITE" mts_load_site
[[ "$DRY" == 1 ]] || mts_check_library

LOGDIR="$MTS_REPO/logs/slurm"; mkdir -p "$LOGDIR"
for s in "${samples[@]}"; do
  for m in "${masses[@]}"; do
    mts_check_sample "$s" "$m"
    cmd=(sbatch --job-name="mts_${MODE}_${s%%_*}_${m}" --array="${RANGE}%${MAXRUN}"
         --nodes=1 --ntasks=1 "${RES[@]}"
         --output="$LOGDIR/${MODE}_${s}_${m}_%A_%a.out" --error="$LOGDIR/${MODE}_${s}_${m}_%A_%a.err"
         --export="ALL,MTS_REPO_DIR=$MTS_REPO,MTS_SITE=$SITE,MTS_SAMPLE=$s,MTS_MASS=$m,MTS_MODE=$MODE,MTS_NEVT=$NEVT"
         ${SBATCH_EXTRA:-} "$MTS_REPO/batch/slurm/job.sh")
    if [[ "$DRY" == 1 ]]; then echo "${cmd[*]}"; else "${cmd[@]}"; fi
  done
done
