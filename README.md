# mucoll-tagging-samples

Production of MuSIC 10 TeV flavour-tagging samples (bb, cc, qq dijets) for Muon Collider
b-tagging studies, using the `MuonC_MuSICv2_v5_dev` apptainer container.

## Components

| Path | What | Version |
|---|---|---|
| `LCTuple/` | Submodule: fork of [MuonColliderSoft/LCTuple](https://github.com/MuonColliderSoft/LCTuple), branch `music10Tev-fixes` | based on tag `MuSICv2-pre04` (045bccc) |
| `Jet-tagging/` | Reconstruction and ntuple steering, imported from [MuonColliderSoft/Jet-tagging](https://github.com/MuonColliderSoft/Jet-tagging) | upstream `main` at 03741b9 |

The container ships a precompiled LCTuple from the `music10Tev` branch (around tag `MuSICv2-pre03`).
The fork fixes bugs in that branch; the rebuilt library replaces the container one at run time
via `MARLIN_DLL`.

## Software base

- Containers: `/eos/experiment/muoncollider/software/MuonC_MuSICv2_v5.sif` and `MuonC_MuSICv2_v5_dev.sif`,
  based on iLCSoft `v02-09-MC` plus customised processors (see the MuSIC samples [CodiMD](https://codimd.web.cern.ch/IsLF65wBQ3iSvkYg3TDoQQ)).
- Official samples: `/eos/experiment/muoncollider/data/EUS/samples/MuSIC_v2/JETtagging`.

## Clone

    git clone --recurse-submodules https://github.com/Billionatoms/mucoll-tagging-samples.git

## Usage

Pick a site with `MTS_SITE` (`local`, `artemis`, `lxplus`; see `config/sites/`).
Personal path overrides go in `config/site.local.env` (git-ignored).

1. Build the patched LCTuple inside the container (once per site, and after every submodule bump):

       MTS_SITE=artemis scripts/build_lctuple.sh

2. Run one file locally, or test a site:

       MTS_SITE=local scripts/run_job.sh bb_dijet m0_100 0 --mode ntuple
       MTS_SITE=local scripts/run_job.sh bb_dijet m0_100 0 --mode reco --nevt 3

3. Submit whole bins:

       batch/slurm/submit.sh all all --mode reco                  # Artemis
       batch/htcondor/submit.sh bb_dijet m1000_5000 --mode ntuple # lxplus

   Add `--dry-run` to see what would be submitted, and start with `--range 0-4`.

`--mode reco` runs sim -> reco + ntuple; `--mode ntuple` reruns only LCTuple on existing reco files.
Jobs refuse to run if the LCTuple build does not match the pinned submodule commit, skip files
whose outputs already exist (`--force` to redo), validate the ntuple before publishing it, and stamp
it with a `mts_provenance` TNamed (repo and LCTuple commits, image hash, input, date).

## Licence

GPL-3.0, matching LCTuple.

`Jet-tagging/` is imported from MuonColliderSoft/Jet-tagging (no upstream licence at the time of import); credit belongs to its original authors.
