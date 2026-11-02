#!/usr/bin/env python3
"""Check one ddsim output against the HepMC3 events it was made from.

  check_sim.py <sim.slcio> <events.hepmc3> <skip> <n>

Runs inside the MuSIC image (pyLCIO). Event i of the sim file must be event
skip + i of the HepMC3 file: the stable generator particles (status 1) are
compared by count and PDG id. This catches a wrong --skipNEvents as well as
dropped or truncated events. Prints "OK events=<n>" on success.
"""
import collections
import sys

from pyLCIO import IOIMPL


def hepmc3_stable(path, skip, n):
    """Sorted PDG ids of the status-1 particles of events skip .. skip+n-1."""
    events, current, index = [], None, -1
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith("E "):
                if current is not None:
                    events.append(sorted(current))
                index += 1
                if index >= skip + n:
                    current = None
                    break
                current = [] if index >= skip else None
            elif current is not None and line.startswith("P "):
                parts = line.split()
                if parts[9] == "1":
                    current.append(int(parts[3]))
    if current is not None:
        events.append(sorted(current))
    return events


def main():
    sim, hepmc, skip, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    want = hepmc3_stable(hepmc, skip, n)
    if len(want) != n:
        sys.exit(f"HepMC3 file has {len(want)} events from {skip}, expected {n}")
    reader = IOIMPL.LCFactory.getInstance().createLCReader()
    reader.open(sim)
    got = []
    for event in reader:
        mcp = event.getCollection("MCParticle")
        got.append(sorted(p.getPDG() for p in mcp if p.getGeneratorStatus() == 1))
    reader.close()
    if len(got) != n:
        sys.exit(f"sim file has {len(got)} events, expected {n}")
    for i, (g, w) in enumerate(zip(got, want)):
        if g != w:
            diff = collections.Counter(w)
            diff.subtract(collections.Counter(g))
            sys.exit(f"event {i} (HepMC3 event {skip + i}): {len(g)} stable particles in sim, "
                     f"{len(w)} in HepMC3; differing PDG ids {dict(+diff)} / {dict(-diff)}")
    print(f"OK events={n}")


if __name__ == "__main__":
    main()
