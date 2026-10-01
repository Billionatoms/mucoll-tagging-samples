#!/bin/bash
# ---------------------------------------------------------------------------
# validation/in_container.sh -- run a command inside the MuSIC container.
#
# Uses the same site config as the production scripts (MTS_SITE, default
# local). The repo, the current directory, the site's BINDS and every
# argument that is an existing path (or whose directory exists) are bound.
#
#   MTS_SITE=local validation/in_container.sh python3 validation/scan_mcparticles_slcio.py ...
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=validation
source "$(dirname "${BASH_SOURCE[0]}")/../scripts/common.sh"
[[ $# -gt 0 ]] || { sed -n '2,10p' "$0"; exit 2; }
mts_load_site
[[ -f "$IMAGE" ]] || die "container image not found: $IMAGE"

extra=("$PWD")
for a in "$@"; do
  a="${a%%\**}"                       # strip a trailing glob, keep its directory
  if   [[ -d "$a" ]]; then extra+=("$a")
  elif [[ -e "$a" ]]; then extra+=("$(dirname "$a")")
  elif [[ "$a" == */* && -d "$(dirname "$a")" ]]; then extra+=("$(dirname "$a")")
  fi
done
cmd="cd $(printf '%q' "$PWD") &&"; for a in "$@"; do cmd+=" $(printf '%q' "$a")"; done
mts_exec "${extra[@]}" -- "$cmd"
