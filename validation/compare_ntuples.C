// ---------------------------------------------------------------------------
// compare_ntuples.C -- compare two LCTuple ntuple files leaf by leaf, value by
//                      value, for every tree they share.
//
// Use it as a regression test after changing LCTuple or the steering: run the
// same input through the old and the new setup and compare. Only the leaves
// you meant to change should differ.
//
//   root -l -b -q 'validation/compare_ntuples.C("new.root","old.root")'
//   root -l -b -q 'validation/compare_ntuples.C("new.root","old.root","JET_kt")'
//
// For every tree it prints the leaves present in only one file, the number of
// values compared and, per leaf, how many values differ. A leaf whose TYPE
// changed (for example daughters_Q, integer to float) shows up as differing
// values. NaN is treated as equal to NaN.
// ---------------------------------------------------------------------------
#include "TFile.h"
#include "TKey.h"
#include "TLeaf.h"
#include "TTree.h"
#include <cstdio>
#include <map>
#include <set>
#include <string>

long compareTree(TTree* ta, TTree* tb) {
  const char* tn = ta->GetName();
  std::set<std::string> na, nb;
  for (auto l : *ta->GetListOfLeaves()) na.insert(l->GetName());
  for (auto l : *tb->GetListOfLeaves()) nb.insert(l->GetName());
  for (auto& n : na) if (!nb.count(n)) printf("  %s: only in first : %s\n", tn, n.c_str());
  for (auto& n : nb) if (!na.count(n)) printf("  %s: only in second: %s\n", tn, n.c_str());
  if (ta->GetEntries() != tb->GetEntries()) {
    printf("  %s: entries differ, %lld vs %lld\n", tn, ta->GetEntries(), tb->GetEntries());
    return 1;
  }
  long nval = 0, ndiff = 0, ncommon = 0;
  std::map<std::string, long> bad;
  for (auto& n : na) if (nb.count(n)) ncommon++;
  for (Long64_t e = 0; e < ta->GetEntries(); e++) {
    ta->GetEntry(e); tb->GetEntry(e);
    for (auto& n : na) {
      if (!nb.count(n)) continue;
      TLeaf *la = ta->GetLeaf(n.c_str()), *lb = tb->GetLeaf(n.c_str());
      int len = la->GetLen();
      if (len != lb->GetLen()) { bad[n]++; ndiff++; continue; }
      for (int i = 0; i < len; i++) {
        nval++;
        double x = la->GetValue(i), y = lb->GetValue(i);
        if (!(x == y || (x != x && y != y))) { bad[n]++; ndiff++; }
      }
    }
  }
  printf("  %s: %lld entries, %ld common leaves, %ld values compared, %ld differ\n",
         tn, ta->GetEntries(), ncommon, nval, ndiff);
  for (auto& kv : bad) printf("     differs: %s (%ld)\n", kv.first.c_str(), kv.second);
  return ndiff;
}

void compare_ntuples(const char* fa, const char* fb, const char* tree = "") {
  TFile a(fa), b(fb);
  if (a.IsZombie() || b.IsZombie()) { printf("cannot open input files\n"); return; }
  long total = 0; int ntrees = 0;
  for (auto k : *a.GetListOfKeys()) {
    TObject* o = a.Get(k->GetName());
    if (!o->InheritsFrom(TTree::Class())) continue;
    if (std::string(tree).size() && std::string(tree) != k->GetName()) continue;
    TTree* tb = (TTree*)b.Get(k->GetName());
    if (!tb) { printf("  %s: missing in second file\n", k->GetName()); total++; continue; }
    total += compareTree((TTree*)o, tb); ntrees++;
  }
  printf("RESULT: %d tree(s) compared, %s\n", ntrees, total == 0 ? "identical" : "differences found");
}
