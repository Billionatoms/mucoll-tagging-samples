#!/bin/bash
# Slurm array task: one generator job or one sim file per task. Submitted by
# batch/slurm/submit_gensim.sh, which sets MTS_SITE, MTS_SAMPLE and MTS_STAGE.
set -euo pipefail
: "${MTS_SAMPLE:?}" "${MTS_STAGE:?}" "${SLURM_ARRAY_TASK_ID:?}"
# Slurm runs a copy of this script from its spool directory, so $0 does not
# point into the repo; the submitter passes the repo path in MTS_REPO_DIR.
REPO="${MTS_REPO_DIR:?}"
case "$MTS_STAGE" in
  gen) exec "$REPO/generation/run_gen.sh" "$MTS_SAMPLE" "$SLURM_ARRAY_TASK_ID" ;;
  sim) exec "$REPO/scripts/run_sim.sh" "$MTS_SAMPLE" "$SLURM_ARRAY_TASK_ID" ;;
  *) echo "unknown stage $MTS_STAGE" >&2; exit 2 ;;
esac
