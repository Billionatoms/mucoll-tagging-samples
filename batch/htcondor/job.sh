#!/bin/bash
# HTCondor job: one file per job. Submitted by batch/htcondor/submit.sh, which
# sets MTS_REPO_DIR and MTS_SITE in the job environment.
# HTCondor copies this wrapper to the worker; the real work runs from the repo on AFS.
set -euo pipefail
exec "${MTS_REPO_DIR:?}/scripts/run_job.sh" "$@"
