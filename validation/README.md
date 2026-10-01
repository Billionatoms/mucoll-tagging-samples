# Validation scripts

Checks for the ntuples and the files they are made from. Each prints a `RESULT:` line.
Run them after changing LCTuple or the steering, and on a few files of every new production.

| Script | What it checks | Needs |
|---|---|---|
| `scan_mcparticles_slcio.py` | In the sim or reco files themselves: are the generator particles first in the `MCParticle` collection, and are there fewer than the LCTuple cap? | pyLCIO (container) |
| `scan_mcparticles_ntuple.py` | In the ntuples: is the generator record cut short by the cap (`MCParticleMaxParticles`)? | ROOT with RDataFrame |
| `check_jet_constituents.C` | Jet constituents: stale track uncertainties on neutrals, charged constituents without a track, largest jet against the 200 limit, charge values | ROOT |
| `compare_ntuples.C` | Two ntuple files, leaf by leaf and value by value | ROOT |
| `in_container.sh` | Runs any command inside the MuSIC container, using the site config | apptainer or singularity |

## Examples

    # generator particles in the reco files (inside the container)
    MTS_SITE=local validation/in_container.sh python3 validation/scan_mcparticles_slcio.py \
        --cap 1000 --out scan.csv '/data/bb_dijet/m0_100/recoSig/*.slcio'

    # truncation in the ntuples, all nine bins
    python3 validation/scan_mcparticles_ntuple.py --root /data --subdir ntuple_v2

    # jet constituents of one bin
    root -l -b -q 'validation/check_jet_constituents.C("/data/cc_dijet/m1000_5000/ntuple_v2/*.root")'

    # regression test: same input through the old and the new setup
    root -l -b -q 'validation/compare_ntuples.C("new.root","old.root")'

The ROOT scripts work with the host ROOT or the container one
(`validation/in_container.sh root -l -b -q '...'`).

## Reference results (MuSIC 10 TeV production, checked 30 Sep to 1 Oct 2026)

**Generator particles in the SLCIO files.** All 3000 `m0_100` reco events (bb, cc, qq): no generator
particle after a Geant4 one; largest generator record 236, 227 and 266 particles.

**Truncation at a cap of 1000**, `ntuple_v2`, 100k events per bin:

| bin | largest generator record | truncated events |
|---|---|---|
| bb, cc, qq `m0_100` | 310, 313, 308 | 0 |
| bb, cc, qq `m100_1000` | 650, 683, 731 | 0 |
| bb, cc, qq `m1000_5000` | over 1000 | 86, 29, 88 |

So the default cap of 1000 is too low for `m1000_5000`: set `MCParticleMaxParticles` higher for that bin.

**Jet constituents**, cc `m1000_5000`, 100 files: largest jet 141 constituents; no charged constituent
without a track; stale uncertainties on neutrals 77.7% with the unfixed LCTuple, 0% with the fixed one.

**Regression.** LCTuple at `6b3e625` reproduces the production `ntuple_v2` exactly. From `3c8a29e` on,
`daughters_Q` differs (stored as a float instead of float bits in an integer), and from `dbe3b5a` on,
stale `vttrchi` values are zero.
