// ---------------------------------------------------------------------------
// check_jet_constituents.C -- sanity checks on the jet constituent branches of
//                             JET_kt (daughters_*), over one or many files.
//
//   root -l -b -q 'validation/check_jet_constituents.C("/data/bb_dijet/m0_100/ntuple/*.root")'
//
// It reports, for the files matched by the pattern:
//   * events, jets and the largest number of constituents in a jet (the
//     arrays hold 200 per jet; more than that would be truncated)
//   * charged and neutral constituents. The charge is decoded whether
//     daughters_Q is the old integer branch holding float bits or a float.
//   * charged constituents with no track uncertainty (a charged constituent
//     without a track)
//   * neutral constituents with a non-zero track uncertainty. A neutral has no
//     track, so these are STALE values left over from an earlier event. Zero
//     with a fixed LCTuple; about 76% with the unfixed music10Tev one.
//
// It works on both branch naming schemes: daughters_trackVar{D0,Z0} (fixed)
// and daughters_trackSigma{D0,Z0} (before the fix).
//
// The [njet][200] arrays are read flattened: jet j, constituent k is element
// j*200 + k.
// ---------------------------------------------------------------------------
#include "TChain.h"
#include "TLeaf.h"
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>

void check_jet_constituents(const char* pattern, const char* tree = "JET_kt") {
  const int NJ = 200, NP = 200;
  TChain c(tree);
  if (c.Add(pattern) == 0 || c.GetEntries() == 0) { printf("no entries for %s\n", pattern); return; }
  c.GetEntry(0);

  const bool fixed = c.GetBranch("daughters_trackVarD0") != nullptr;
  const char* bd0 = fixed ? "daughters_trackVarD0" : "daughters_trackSigmaD0";
  const char* bz0 = fixed ? "daughters_trackVarZ0" : "daughters_trackSigmaZ0";
  if (!c.GetBranch(bd0)) { printf("no daughters_track uncertainty branches in %s\n", tree); return; }
  const bool qIsInt = std::string(c.GetLeaf("daughters_Q")->GetTypeName()) == "Int_t";

  static int njet, nd[NJ], qi[NJ * NP];
  static float qf[NJ * NP], ud0[NJ * NP], uz0[NJ * NP];
  c.SetBranchAddress("njet", &njet);
  c.SetBranchAddress("ndaughters", nd);
  if (qIsInt) c.SetBranchAddress("daughters_Q", qi); else c.SetBranchAddress("daughters_Q", qf);
  c.SetBranchAddress(bd0, ud0);
  c.SetBranchAddress(bz0, uz0);

  long jets = 0, charged = 0, neutral = 0, chargedNoTrack = 0, stale = 0, truncatedJets = 0;
  long qPlus = 0, qMinus = 0, qOther = 0;
  int maxConst = 0;
  for (Long64_t e = 0; e < c.GetEntries(); e++) {
    c.GetEntry(e);
    jets += njet;
    for (int j = 0; j < njet; j++) {
      maxConst = std::max(maxConst, nd[j]);
      if (nd[j] > NP) truncatedJets++;
      for (int k = 0; k < std::min(nd[j], NP); k++) {
        const int i = j * NP + k;
        float q;
        if (qIsInt) {
          // old files: float bits in an integer branch (+1 is 1065353216); a small integer is a real charge
          if (qi[i] > 1000 || qi[i] < -1000) memcpy(&q, &qi[i], sizeof(float)); else q = qi[i];
        } else q = qf[i];
        if (q == 0) { neutral++; if (ud0[i] != 0 || uz0[i] != 0) stale++; }
        else {
          charged++; if (ud0[i] == 0) chargedNoTrack++;
          if (q == 1) qPlus++; else if (q == -1) qMinus++; else qOther++;
        }
      }
    }
  }
  printf("%s\n", pattern);
  printf("  files %d, events %lld, jets %ld\n", c.GetNtrees(), c.GetEntries(), jets);
  printf("  uncertainty branches: %s (%s), daughters_Q stored as %s\n", bd0, fixed ? "fixed naming" : "pre-fix naming", qIsInt ? "integer" : "float");
  printf("  largest jet: %d constituents (array holds %d), jets over the limit: %ld\n", maxConst, NP, truncatedJets);
  printf("  charged %ld (+1: %ld, -1: %ld, other: %ld), neutral %ld\n", charged, qPlus, qMinus, qOther, neutral);
  printf("  charged without a track uncertainty: %ld\n", chargedNoTrack);
  printf("  neutral with a stale track uncertainty: %ld (%.1f%%)\n", stale, neutral ? 100. * stale / neutral : 0.);
  const bool ok = stale == 0 && truncatedJets == 0 && qOther == 0;
  printf("RESULT: %s\n", ok ? "OK" : "PROBLEM, see the counts above");
}
