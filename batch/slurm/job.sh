#!/bin/bash
# Slurm array task: one file per task. Submitted by batch/slurm/submit.sh,
# which sets MTS_SITE, MTS_SAMPLE, MTS_MASS, MTS_MODE and MTS_NEVT.
set -euo pipefail
: "${MTS_SAMPLE:?}" "${MTS_MASS:?}" "${MTS_MODE:?}" "${SLURM_ARRAY_TASK_ID:?}"
# Slurm runs a copy of this script from its spool directory, so $0 does not
# point into the repo; the submitter passes the repo path in MTS_REPO_DIR.
REPO="${MTS_REPO_DIR:?}"
exec "$REPO/scripts/run_job.sh" "$MTS_SAMPLE" "$MTS_MASS" "$SLURM_ARRAY_TASK_ID" \
     --mode "$MTS_MODE" --nevt "${MTS_NEVT:--1}"
