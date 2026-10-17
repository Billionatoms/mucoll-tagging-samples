# Simulation steering

`sim_steer.py` is the ddsim settings file that was used to simulate the tagging samples.
The original file was not kept with the samples. ddsim saves a full copy of its settings file
inside every output file, so this copy was taken from one of the simulated files, unchanged.

## Where it comes from

| | |
|---|---|
| Taken from | `MuSIC_v2_10TeV_samples/bb_dijet/m0_100/sim/sim_bb_m0_100_00000.slcio` |
| Simulated on | 3 April 2025 |
| Software | DD4hep v01-29 and Geant4 11.1, the same versions as in `MuonC_MuSICv2_v5_dev.sif` |
| Copied out on | 15 October 2026 |
| sha256 of `sim_steer.py` | `72a1b743dec47b308706d38714ef6b2189f06d8b916d9aea39c73dece1a90bbf` |

The simulated file also records the command that was run:

    ddsim --steeringFile sim_steer.py --skipNEvents 0 --inputFiles gen.hepmc
          --outputFile sim_0.slcio --compactFile /usr/share/muonc-detector-geometry/MuSIC_v2/MuSIC_v2.xml

The command sets its own detector geometry, input file and output file, so the paths written
inside `sim_steer.py` were not the ones used.

## Main settings

- Geant4 physics list `QGSP_BERT`, range cut 0.7 mm, detailed shower mode on.
- The same random seed, 42, in every job.
- 25 events per job.
- No smearing of the collision point.
- It is close to MuonColliderSoft/ProductionConfig `simulation/001-Base/sim_steer.py`.
