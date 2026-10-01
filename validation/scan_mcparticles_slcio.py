#!/usr/bin/env python3
"""
scan_mcparticles_slcio.py -- read the FULL MCParticle collection of every event
in sim or reco SLCIO files and check where the generator particles sit.

LCTuple writes only the first N MCParticles of each event (MCParticleMaxParticles).
That is safe only if the generator particles come first and there are fewer than
N of them. This script tests both, on the files themselves, without LCTuple.

Per event it records (one CSV row):
  ntot       particles in the collection
  ngen       particles with generatorStatus > 0, counted anywhere
  maxgen     highest index of a generator particle
  firstg4    index of the first particle with generatorStatus == 0
  gen_after  generator particles that sit after the first Geant4 one
  ngen_cap   generator particles with index < cap
  nnotsim    particles not flagged CreatedInSimulation (should equal ngen)

Needs pyLCIO, so run it inside the container:
  validation/in_container.sh python3 validation/scan_mcparticles_slcio.py \
      --cap 1000 --out scan.csv '/data/bb_dijet/m0_100/recoSig/*.slcio'
"""
import argparse, glob, sys

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("inputs", nargs="+", help="SLCIO files or quoted glob patterns")
p.add_argument("--cap", type=int, default=1000, help="the LCTuple cap to test against (default 1000)")
p.add_argument("--out", default=None, help="write one CSV row per event to this file")
p.add_argument("--max-events", type=int, default=-1, help="stop after this many events (default: all)")
p.add_argument("--collection", default="MCParticle")
args = p.parse_args()

import ROOT
from pyLCIO import IOIMPL

# The loop over ~10^5-10^6 particles per event is far too slow in Python.
ROOT.gInterpreter.Declare(r'''
#include "EVENT/LCCollection.h"
#include "EVENT/MCParticle.h"
std::vector<long> mts_mcscan(EVENT::LCCollection* c, long cap){
  long n=c->getNumberOfElements(), ngen=0, maxgen=-1, firstg4=-1, after=0, ncap=0, notsim=0;
  for(long i=0;i<n;i++){
    auto p=static_cast<EVENT::MCParticle*>(c->getElementAt(i));
    if(!p->isCreatedInSimulation()) notsim++;
    if(p->getGeneratorStatus()>0){ ngen++; maxgen=i; if(i<cap) ncap++; if(firstg4>=0) after++; }
    else if(firstg4<0) firstg4=i;
  }
  return {n,ngen,maxgen,firstg4,after,ncap,notsim};
}''')

files = sorted(f for pat in args.inputs for f in (glob.glob(pat) or [pat]))
out = open(args.out, "w") if args.out else None
if out:
    out.write("file,run,event,ntot,ngen,maxgen,firstg4,gen_after,ngen_cap,nnotsim\n")

nev = max_ngen = max_idx = n_after = n_trunc = n_mismatch = 0
for fn in files:
    r = IOIMPL.LCFactory.getInstance().createLCReader()
    r.setReadCollectionNames([args.collection])
    try:
        r.open(fn)
    except Exception as e:
        print(f"WARNING: cannot open {fn}: {e}", file=sys.stderr); continue
    for evt in r:
        ntot, ngen, maxgen, firstg4, after, ncap, notsim = ROOT.mts_mcscan(evt.getCollection(args.collection), args.cap)
        nev += 1
        max_ngen, max_idx = max(max_ngen, ngen), max(max_idx, maxgen)
        n_after += after > 0; n_trunc += maxgen >= args.cap; n_mismatch += ngen != notsim
        if out:
            out.write(f"{fn.split('/')[-1]},{evt.getRunNumber()},{evt.getEventNumber()},{ntot},{ngen},{maxgen},{firstg4},{after},{ncap},{notsim}\n")
        if nev == args.max_events:
            break
    r.close()
    if nev == args.max_events:
        break
if out:
    out.close()

print(f"files {len(files)}, events {nev}")
print(f"  largest generator record            : {max_ngen} particles, highest index {max_idx}")
print(f"  events with a generator particle after a Geant4 one : {n_after}")
print(f"  events where 'status > 0' != 'not created in simulation' : {n_mismatch}")
print(f"  events with a generator particle at index >= {args.cap} : {n_trunc}")
ok = n_after == 0 and n_trunc == 0 and n_mismatch == 0
print("RESULT:", "OK, a cap of %d keeps every generator particle in these files" % args.cap if ok else "PROBLEM, see the counts above")
sys.exit(0 if ok else 1)
