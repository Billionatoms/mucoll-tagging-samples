# Simulation steering

`sim_steer.py` is the ddsim steering file that simulated the tagging samples. It was not
kept with the samples; ddsim stores the full steering file in the run header of every output
file (`SteeringFileContent`), and this copy was extracted from there unchanged.

## Provenance

| | |
|---|---|
| Source file | `MuSIC_v2_10TeV_samples/bb_dijet/m0_100/sim/sim_bb_m0_100_00000.slcio` |
| Made | 2025-04-03 11:50:43 UTC, user `gianelle`, HTCondor |
| Software | DD4hep v01-29, Geant4 11.1 (the versions in `MuonC_MuSICv2_v5_dev.sif`) |
| Extracted | 2026-10-15, pyLCIO run-header read in `MuonC_MuSICv2_v5_dev.sif` |
| sha256 of `sim_steer.py` | `72a1b743dec47b308706d38714ef6b2189f06d8b916d9aea39c73dece1a90bbf` |

The command line recorded in the same header:

    ddsim --steeringFile sim_steer.py --skipNEvents 0 --inputFiles gen.hepmc
          --outputFile sim_0.slcio --compactFile /usr/share/muonc-detector-geometry/MuSIC_v2/MuSIC_v2.xml

So the geometry, input and output paths written in `sim_steer.py` were overridden; the values above
are the ones used.

## Settings that matter

- Physics list `QGSP_BERT`, range cut 0.7 mm, detailed shower mode on.
- Random seed 42 in every job, per-event seeding off (`random.enableEventSeed = False`).
- 25 events per job, no vertex smearing, no crossing-angle boost.
- Closest public steering: MuonColliderSoft/ProductionConfig `simulation/001-Base/sim_steer.py`.

The header records `part.printStartTracking` and `part.printEndTracking` as `False`, while the file
sets them to `True`. Both only control logging.

Only this one sim file (bb_dijet, m0_100) was available locally, so the other eight samples are
assumed, not checked, to use the same steering. The run header of one file per sample on EOS would
confirm it.
