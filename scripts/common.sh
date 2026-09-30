# shellcheck shell=bash
# ---------------------------------------------------------------------------
# common.sh -- shared helpers, sourced by build_lctuple.sh, run_job.sh and the
#              batch wrappers. Not meant to be executed.
#
# Site selection:  MTS_SITE=local|artemis|lxplus   (default: local)
#   loads config/sites/$MTS_SITE.env, then config/site.local.env if present.
# ---------------------------------------------------------------------------

MTS_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Fixed layout inside the repo
LCTUPLE_SRC="$MTS_REPO/LCTuple"
LCTUPLE_BUILD="$MTS_REPO/build/lctuple"
LCTUPLE_INSTALL="$MTS_REPO/install/lctuple"
LCTUPLE_LIB="$LCTUPLE_INSTALL/lib/libLCTuple.so"
LCTUPLE_BUILD_INFO="$LCTUPLE_INSTALL/BUILD_INFO"
STEER_DIR="$MTS_REPO/Jet-tagging/reco_steering"
CONTAINER_LCTUPLE="/usr/lib64/libLCTuple.so"

SAMPLES=(bb_dijet cc_dijet qq_dijet)
MASSES=(m0_100 m100_1000 m1000_5000)

# --- logging ---------------------------------------------------------------
_c() { if [[ -t 1 ]]; then printf '\033[%sm%s\033[0m\n' "$1" "$2"; else printf '%s\n' "$2"; fi; }
red()  { _c 31 "$*"; }
grn()  { _c 32 "$*"; }
ylw()  { _c 33 "$*"; }
info() { echo "[${MTS_TAG:-mts}] $*"; }
die()  { red "[${MTS_TAG:-mts}][FATAL] $*" >&2; exit 1; }

# --- site config -----------------------------------------------------------
mts_load_site() {
  MTS_SITE="${MTS_SITE:-local}"
  local f="$MTS_REPO/config/sites/$MTS_SITE.env"
  [[ -f "$f" ]] || die "unknown site '$MTS_SITE' (no $f)"
  # shellcheck source=/dev/null
  source "$f"
  # shellcheck source=/dev/null
  [[ -f "$MTS_REPO/config/site.local.env" ]] && source "$MTS_REPO/config/site.local.env"
  : "${IMAGE:?IMAGE not set by site config}" "${DATA_ROOT:?}" "${OUT_ROOT:?}" "${RECO_ROOT:?}"
  NTUPLE_SUBDIR="${NTUPLE_SUBDIR:-ntuple}"
  OVERLAY="${OVERLAY:-none}"
  XRDCP="${XRDCP:-xrdcp}"
  XRDFS="${XRDFS:-xrdfs}"
}

# --- container -------------------------------------------------------------
mts_container_bin() {
  if command -v apptainer >/dev/null 2>&1; then echo apptainer
  elif command -v singularity >/dev/null 2>&1; then echo singularity
  else die "neither apptainer nor singularity found"; fi
}

# Bind list: the repo, every existing path in $BINDS, plus any extra paths given.
mts_bind_args() {
  local p seen=" " out=()
  for p in "$MTS_REPO" $BINDS "$@"; do
    [[ -e "$p" ]] || continue
    p="$(cd "$p" 2>/dev/null && pwd -P || echo "$p")"
    [[ "$seen" == *" $p "* ]] && continue
    seen+="$p "; out+=(-B "$p:$p")
  done
  printf '%s\n' "${out[@]}"
}

# mts_exec <bind paths...> -- <bash command string>
mts_exec() {
  local extra=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do extra+=("$1"); shift; done
  shift
  local binds; mapfile -t binds < <(mts_bind_args "${extra[@]}")
  "$(mts_container_bin)" exec --cleanenv "${binds[@]}" "$IMAGE" /bin/bash -l -c "$1"
}

# --- library guard ---------------------------------------------------------
# The installed library must have been built from the LCTuple commit the repo
# currently pins, from a clean tree. Set ALLOW_DIRTY=1 to downgrade to a warning
# while developing.
mts_bi() { sed -n "s/^$1=//p" "$LCTUPLE_BUILD_INFO" 2>/dev/null | head -1; }

mts_check_library() {
  [[ -e "$LCTUPLE_LIB" ]] || die "no LCTuple build at $LCTUPLE_LIB -- run scripts/build_lctuple.sh"
  [[ -f "$LCTUPLE_BUILD_INFO" ]] || die "missing $LCTUPLE_BUILD_INFO -- rebuild with scripts/build_lctuple.sh"
  local built dirty head
  built="$(mts_bi lctuple_commit)"; dirty="$(mts_bi lctuple_dirty)"
  if command -v git >/dev/null 2>&1 && git -C "$LCTUPLE_SRC" rev-parse HEAD >/dev/null 2>&1; then
    head="$(git -C "$LCTUPLE_SRC" rev-parse HEAD)"
    [[ "$built" == "$head" ]] || die "library built from LCTuple $built but the submodule is at $head -- rebuild"
  else
    ylw "[${MTS_TAG:-mts}] git not available: cannot compare the build with the submodule commit"
  fi
  if [[ "$dirty" != "0" ]]; then
    [[ "${ALLOW_DIRTY:-0}" == "1" ]] || die "library was built from a dirty LCTuple tree (set ALLOW_DIRTY=1 to override)"
    ylw "[${MTS_TAG:-mts}] WARNING: library built from a dirty LCTuple tree"
  fi
}

mts_git_desc() {  # <dir> -> "<sha>[-dirty]" or "unknown"
  if command -v git >/dev/null 2>&1 && git -C "$1" rev-parse HEAD >/dev/null 2>&1; then
    local s; s="$(git -C "$1" rev-parse HEAD)"
    [[ -n "$(git -C "$1" status --porcelain --untracked-files=no 2>/dev/null)" ]] && s+="-dirty"
    echo "$s"
  else echo unknown; fi
}

# --- local path or root:// URL ---------------------------------------------
is_remote() { [[ "$1" == root://* ]]; }
xrd_host()  { local u="${1#root://}"; echo "${u%%/*}"; }
xrd_path()  { local u="${1#root://}"; echo "/${u#*/}"; }

mts_exists() {  # non-trivial output already there?
  if is_remote "$1"; then
    "$XRDFS" "$(xrd_host "$1")" stat "$(xrd_path "$1")" >/dev/null 2>&1
  else
    [[ -f "$1" && $(stat -c%s "$1" 2>/dev/null || echo 0) -gt 10000 ]]
  fi
}

mts_fetch() {  # <src> <local dst>
  if is_remote "$1"; then "$XRDCP" -f -s "$1" "$2"; else cp -f "$1" "$2"; fi
}

# Copy to a temporary name, then rename, so an interrupted copy never leaves a
# file that looks complete.
mts_publish() {  # <local src> <dst>
  local src="$1" dst="$2"
  if is_remote "$dst"; then
    local h p; h="$(xrd_host "$dst")"; p="$(xrd_path "$dst")"
    "$XRDFS" "$h" mkdir -p "$(dirname "$p")" >/dev/null 2>&1 || true
    "$XRDCP" -f -s "$src" "root://$h/$p.part" \
      && "$XRDFS" "$h" mv "$p.part" "$p" \
      || { "$XRDFS" "$h" rm "$p.part" >/dev/null 2>&1 || true; return 1; }
  else
    mkdir -p "$(dirname "$dst")"
    cp -f "$src" "$dst.part" && mv -f "$dst.part" "$dst" || { rm -f "$dst.part"; return 1; }
  fi
}

mts_check_sample() {
  [[ " ${SAMPLES[*]} " == *" $1 "* ]] || die "unknown sample '$1' (expected: ${SAMPLES[*]})"
  [[ " ${MASSES[*]} "  == *" $2 "* ]] || die "unknown mass bin '$2' (expected: ${MASSES[*]})"
}
