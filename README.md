# mucoll-tagging-samples

Production of MuSIC 10 TeV flavour-tagging samples (bb, cc, qq dijets) for Muon Collider
b-tagging studies, using the `MuonC_MuSICv2_v5_dev` apptainer container.

## Components

| Path | What | Version |
|---|---|---|
| `LCTuple/` | Submodule: fork of [MuonColliderSoft/LCTuple](https://github.com/MuonColliderSoft/LCTuple), branch `music10Tev-fixes` | based on tag `MuSICv2-pre04` (045bccc) |
| `Jet-tagging/` | Reconstruction and ntuple steering, imported from [MuonColliderSoft/Jet-tagging](https://github.com/MuonColliderSoft/Jet-tagging) | upstream `main` at 03741b9 |
| `sim_steering/` | The ddsim steering that simulated the samples, extracted from a sim file's run header | see `sim_steering/README.md` |

**Known limitation of the reco steering: stiff tracks are lost.** The tracking settings are the upstream
defaults, the same as for the official VBF training samples, and they keep reco jets at about half the
truth-jet energy in these 10 TeV samples:

- `FilterTrk` (`reco_steer_jets.py`) and `FilterTracksCone` (`conf/tracking.py`) leave `MaxPt` at the
  `FilterTracks` default of 1000 GeV (`music10Tev` branch of MarlinTrkProcessors, commit `692194c7`),
  which removes every track above 1 TeV $p_T$.
- `CKF_Chi2CutOff` stays at 10. At 10, tracks of a few hundred GeV and up lose their tracker hits after
  the vertex detector and are then removed by `MinNdf`.

Lifting `MaxPt` and raising the cut-off to 100 was tried on 10 Nov 2026 (commit `70023c4`): on 100
full-sim tc events the charged jet energy went from 0.48 to 0.73 of truth and the jet response from 0.51
to 0.65. It was undone on 13 Nov 2026, as agreed in the supervisor meeting that day: above 1 TeV, with
the beam-induced background in the event, fake tracks far outnumber real ones, and the cut was tuned with
the detector full of BIB hits, which signal-only simulation does not show. Any change has to be agreed
with the people who tune the MuSIC tracking. The calorimeter calibration was not changed either: with the
HCAL outside the solenoid, Pandora's default clustering and track-cluster association cuts cannot span
the coil gap, so a charged hadron's HCAL shower is left as a neutral hadron and a correct hadronic scale
would double count. Anything reconstructed with commit `70023c4` in place used the changed tracking and
does not match the other samples.

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

Checks for the outputs (generator record truncation, stale values, file-to-file comparison) are in
`validation/`, see `validation/README.md`.

## New samples

The s-channel dijets (`bb_schannel`, `cc_schannel`, `qq_schannel`) and the $\mu^+\mu^- \to tc$
signal (`tc_signal`) are generated and simulated here, then go through the same reco and ntuple
chain with mass bin `incl`. See `generation/README.md`.

## Licence

GPL-3.0, matching LCTuple.

`Jet-tagging/` is imported from MuonColliderSoft/Jet-tagging (no upstream licence at the time of import); credit belongs to its original authors.
