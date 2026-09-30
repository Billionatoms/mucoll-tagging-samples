#!/bin/bash
# ---------------------------------------------------------------------------
# build_lctuple.sh -- build the LCTuple submodule inside the MuSIC container.
#
# Builds LCTuple/ into build/lctuple and installs into install/lctuple.
# Everything (configure, compile, install, checks) runs inside the container,
# because Marlin, ROOT and ilcutil come from the image and the library must
# match the Marlin that k4run loads at run time.
#
# On success it writes install/lctuple/BUILD_INFO (LCTuple commit, clean or
# dirty, image and its sha256). run_job.sh refuses to run unless that commit
# matches the submodule's current commit.
#
# Usage:  MTS_SITE=<site> scripts/build_lctuple.sh [-j N] [-k] [-H]
#           -j N   parallel compile jobs (default: nproc in the container)
#           -k     keep build/lctuple (incremental); default is a clean build
#           -H     skip hashing the image (hashing a 4 GB image on EOS is slow)
# ---------------------------------------------------------------------------
set -euo pipefail
MTS_TAG=build
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

JOBS=""; KEEP=0; HASH=1
while getopts "j:kHh" opt; do
  case "$opt" in
    j) JOBS="$OPTARG" ;;
    k) KEEP=1 ;;
    H) HASH=0 ;;
    h) sed -n '2,19p' "$0"; exit 0 ;;
    *) echo "usage: $0 [-j N] [-k] [-H]" >&2; exit 2 ;;
  esac
done

mts_load_site
[[ -f "$IMAGE" ]] || die "container image not found: $IMAGE"
[[ -f "$LCTUPLE_SRC/CMakeLists.txt" ]] \
  || die "LCTuple submodule is empty -- run: git submodule update --init"

COMMIT="$(git -C "$LCTUPLE_SRC" rev-parse HEAD)"
DIRTY=0
[[ -n "$(git -C "$LCTUPLE_SRC" status --porcelain --untracked-files=no)" ]] && DIRTY=1

info "site     : $MTS_SITE"
info "image    : $IMAGE"
info "source   : $LCTUPLE_SRC @ $COMMIT $([[ $DIRTY == 1 ]] && echo '(DIRTY)')"
info "build    : $LCTUPLE_BUILD"
info "install  : $LCTUPLE_INSTALL"
[[ "$DIRTY" == 1 ]] && ylw "[build] WARNING: uncommitted changes in LCTuple; run_job.sh will refuse this build unless ALLOW_DIRTY=1"

[[ "$KEEP" == 1 ]] || rm -rf "$LCTUPLE_BUILD" "$LCTUPLE_INSTALL"
mkdir -p "$LCTUPLE_BUILD"

# --- configure, compile, install (inside the container) ---------------------
mts_exec -- "
  set -euo pipefail
  NJOBS='${JOBS}'; [ -n \"\$NJOBS\" ] || NJOBS=\$(nproc)
  cmake -S '$LCTUPLE_SRC' -B '$LCTUPLE_BUILD' \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_INSTALL_PREFIX='$LCTUPLE_INSTALL' \
        -DMarlin_DIR=/usr/lib64/cmake/Marlin \
        -DROOT_DIR=/usr/share/root/cmake \
        -DILCUTIL_DIR=/usr/lib64/cmake/ilcutil
  cmake --build '$LCTUPLE_BUILD' -j \"\$NJOBS\"
  cmake --install '$LCTUPLE_BUILD'
" || die "build failed"

# --- checks -------------------------------------------------------------------
echo; info "================ checks ================"
FAIL=0

# (a) the library exists and its symlink chain resolves
if [[ -L "$LCTUPLE_LIB" && -e "$LCTUPLE_LIB" ]]; then
  grn "[build] (a) OK  $(basename "$LCTUPLE_LIB") -> $(basename "$(readlink -f "$LCTUPLE_LIB")")"
else
  red "[build] (a) missing or broken: $LCTUPLE_LIB"; FAIL=1
fi

# (b) exported symbols, and no unresolved symbols against the container's libraries
if [[ -e "$LCTUPLE_LIB" ]]; then
  SYMS="$(mts_exec -- "nm -D --defined-only '$LCTUPLE_LIB'" 2>/dev/null || true)"
  missing=""
  for s in LCTuple JetBranches TrackBranches RecoParticleBranches MCParticleBranches; do
    grep -q "$s" <<< "$SYMS" || missing+=" $s"
  done
  [[ -z "$missing" ]] && grn "[build] (b) OK  expected symbols present" \
                      || { red "[build] (b) missing symbols:$missing"; FAIL=1; }
  if mts_exec -- "ldd -r '$LCTUPLE_LIB' 2>&1" | grep -q "undefined symbol"; then
    red "[build] (b) ldd -r reports undefined symbols"; FAIL=1
  else
    grn "[build] (b) OK  ldd -r: no undefined symbols"
  fi
fi

# (c) the fixes this repo depends on are compiled in (string literals, so grep -a)
if grep -qa 'MCParticleMaxParticles' "$LCTUPLE_LIB" 2>/dev/null; then
  grn "[build] (c) OK  MCParticleMaxParticles parameter present"
else
  red "[build] (c) MCParticleMaxParticles missing: not built from music10Tev-fixes?"; FAIL=1
fi

# (d) k4run loads this library through MARLIN_DLL and instantiates the processor.
#     The exit code plus the "Loading library <lib>" line is the test: grepping
#     for error strings misses both known failure modes.
PROBE="$LCTUPLE_BUILD/_loadprobe.py"
cat > "$PROBE" <<'EOF'
from Gaudi.Configuration import INFO
from Configurables import MarlinProcessorWrapper, ApplicationMgr
probe = MarlinProcessorWrapper("LoadProbe")
probe.ProcessorType = "LCTuple"
ApplicationMgr(TopAlg=[probe], EvtSel="NONE", EvtMax=0, ExtSvc=[], OutputLevel=INFO)
EOF
OUT="$(mts_exec -- "
  export MARLIN_DLL=\$(echo \$MARLIN_DLL | sed 's|$CONTAINER_LCTUPLE|$LCTUPLE_LIB|')
  cd '$LCTUPLE_BUILD'; k4run '$PROBE' 2>&1; echo __RC=\$?
" 2>&1 || true)"
RC="$(sed -n 's/^__RC=//p' <<< "$OUT" | tail -1)"
if [[ "${RC:-1}" != 0 ]]; then
  red "[build] (d) k4run load probe failed (exit ${RC:-?})"; grep -iE "ERROR|Failed" <<< "$OUT" | head -5; FAIL=1
elif ! grep -q "Loading library ${LCTUPLE_LIB}$" <<< "$OUT"; then
  red "[build] (d) k4run exited 0 but did not load $LCTUPLE_LIB (MARLIN_DLL substitution failed)"; FAIL=1
else
  grn "[build] (d) OK  k4run loaded the local build and created the LCTuple processor"
fi

[[ "$FAIL" == 0 ]] || { red "[build] CHECKS FAILED -- no BUILD_INFO written"; exit 1; }

# --- BUILD_INFO ---------------------------------------------------------------
IMAGE_SHA="skipped"
if [[ "$HASH" == 1 ]]; then info "hashing image (use -H to skip)"; IMAGE_SHA="$(sha256sum "$IMAGE" | cut -d' ' -f1)"; fi
cat > "$LCTUPLE_BUILD_INFO" <<EOF
lctuple_commit=$COMMIT
lctuple_dirty=$DIRTY
lctuple_describe=$(git -C "$LCTUPLE_SRC" describe --tags --always --dirty 2>/dev/null || echo unknown)
repo_commit=$(mts_git_desc "$MTS_REPO")
image=$IMAGE
image_sha256=$IMAGE_SHA
site=$MTS_SITE
built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
built_on=$(hostname)
EOF
echo; grn "[build] ALL CHECKS PASSED -- $LCTUPLE_LIB"
sed 's/^/    /' "$LCTUPLE_BUILD_INFO"
