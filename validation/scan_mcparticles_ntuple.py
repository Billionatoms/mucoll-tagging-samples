#!/usr/bin/env python3
"""
scan_mcparticles_ntuple.py -- check the stored MCParticle block in LCTuple ntuples
for a generator record cut short by the cap.

The ntuple holds the first nmcp particles of each event. An event is flagged as
truncated when nmcp equals the cap AND the last stored particle is still a
generator particle (mcgst > 0): the generator record then runs past the cap.

Per input it prints: events, the cap (--cap, or the largest nmcp seen), the largest generator
count, events with a generator particle after a Geant4 one inside the stored
block, truncated events, and the pile-up check (events with a generator count
in the 50 below the cap, against events sitting exactly at the cap; a count at
the cap far above the tail means the record overflows).

Needs ROOT with RDataFrame (host or container):
  python3 validation/scan_mcparticles_ntuple.py '/data/bb_dijet/m1000_5000/ntuple/*.root'
  python3 validation/scan_mcparticles_ntuple.py --root /data --subdir ntuple_v2     # all nine bins
"""
import argparse, os, sys

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("inputs", nargs="*", help="ROOT files or quoted glob patterns, one sample per argument")
p.add_argument("--root", help="sample root: scans <root>/<sample>/<mass>/<subdir>/*.root for all nine bins")
p.add_argument("--subdir", default="ntuple", help="ntuple directory name under each bin (default ntuple)")
p.add_argument("--tree", default="TrueJets", help="tree holding the MC branches (default TrueJets)")
p.add_argument("--cap", type=int, default=0, help="the MCParticleMaxParticles the ntuples were made with (default: the largest nmcp seen)")
p.add_argument("--threads", type=int, default=8)
args = p.parse_args()

inputs = list(args.inputs)
if args.root:
    inputs += [f"{args.root}/{s}_dijet/{m}/{args.subdir}/*.root"
               for s in ("bb", "cc", "qq") for m in ("m0_100", "m100_1000", "m1000_5000")]
if not inputs:
    p.error("give input patterns or --root")

import ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
ROOT.EnableImplicitMT(args.threads)
ROOT.gInterpreter.Declare(r'''
using RVI = ROOT::RVec<int>;
int mts_ngen(const RVI& g){ int k=0; for(auto x:g) if(x>0) k++; return k; }
int mts_genafter(const RVI& g){ bool seen=false; int k=0; for(auto x:g){ if(x<=0) seen=true; else if(seen) k++; } return k; }
''')

def label(pat):          # <sample>/<mass> from .../<sample>/<mass>/<subdir>/<files>
    parts = [x for x in os.path.dirname(pat).split("/") if x]
    return "/".join(parts[-3:-1]) if len(parts) >= 3 else pat

print(f"{'sample':24s} {'events':>8s} {'cap':>6s} {'max gen':>8s} {'gen after G4':>13s} {'truncated':>10s} {'cap-50..cap-1':>14s} {'at cap':>7s}")
bad = 0
for pat in inputs:
    try:
        df = ROOT.RDataFrame(args.tree, pat)
        cap = args.cap or int(df.Max("nmcp").GetValue())
    except Exception as e:
        print(f"{label(pat):24s} cannot read: {str(e).splitlines()[0][:60]}"); bad += 1; continue
    d = df.Define("ng", "mts_ngen(mcgst)").Define("ga", "mts_genafter(mcgst)")
    r = [d.Count(), d.Max("ng"), d.Filter("ga>0").Count(),
         d.Filter(f"nmcp=={cap} && mcgst[{cap - 1}]>0").Count(),
         d.Filter(f"ng>={cap - 50} && ng<{cap}").Count(), d.Filter(f"ng=={cap}").Count()]
    ROOT.RDF.RunGraphs(r)
    v = [int(x.GetValue()) for x in r]
    print(f"{label(pat):24s} {v[0]:8d} {cap:6d} {v[1]:8d} {v[2]:13d} {v[3]:10d} {v[4]:14d} {v[5]:7d}", flush=True)
    bad += (v[2] > 0) + (v[3] > 0)
print("RESULT:", "OK, no generator record is cut by the cap" if bad == 0 else "PROBLEM, truncated or mis-ordered events found (see table)")
sys.exit(0 if bad == 0 else 1)
