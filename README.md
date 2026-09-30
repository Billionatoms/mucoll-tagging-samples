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
  based on iLCSoft `v02-09-MC` plus customised processors (see the MuSIC samples CodiMD page).
- Official samples: `/eos/experiment/muoncollider/data/EUS/samples/MuSIC_v2/JETtagging`.

## Clone

    git clone --recurse-submodules https://github.com/Billionatoms/mucoll-tagging-samples.git

## Licence

GPL-3.0, matching LCTuple.

`Jet-tagging/` is imported from MuonColliderSoft/Jet-tagging (no upstream licence at the time of import); credit belongs to its original authors.
