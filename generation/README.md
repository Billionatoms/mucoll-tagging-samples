# Event generation and simulation of new samples

The official MuSIC samples come as simulated files. The samples here are generated and simulated by
this repo, then reconstructed and ntupled by the unchanged chain (`scripts/run_job.sh`):

| sample | process | MadGraph process |
|---|---|---|
| `bb_schannel` | s-channel $b\bar b$ dijets | `mu+ mu- > b b~` |
| `cc_schannel` | s-channel $c\bar c$ dijets | `mu+ mu- > c c~` |
| `qq_schannel` | s-channel light dijets | `mu+ mu- > jl jl`, jl = u, d, s |
| `tc_signal` | $\mu^+\mu^- \to t\bar c + \bar t c$ through $O_{lequ}^{(1)}$ | `mu+ mu- > t c~ NP=1`, `mu+ mu- > t~ c NP=1` |

All at $\sqrt{s} = 10$ TeV with fixed-energy beams, as the official VBF samples. Each sample has a
single bin, `incl`.

## Chain

```text
generation/run_gen.sh <sample> <j>   eventgen.sif     MadGraph -> LHE -> Pythia -> gen/gen_<q>_incl_<jjjj>.hepmc3
scripts/run_sim.sh <sample> <i>      MuSIC v2.5 dev   ddsim, 25 events        -> sim/sim_<q>_incl_<iiiii>.slcio
scripts/run_job.sh <sample> incl <i> MuSIC v2.5 dev   reco + ntuple (unchanged)
```

Generator job *j* holds `EVENTS_PER_JOB` events (10,000). Sim file *i* takes events
`skip .. skip+24` of generator file `i / 400`, with `skip = (i % 400) * 25`, so one generator file
feeds sim files `400 j .. 400 j + 399`, and reco file *i* is made from sim file *i*.

On Artemis:

    batch/slurm/submit_gensim.sh gen bb_schannel --range 0-9        # 100,000 events
    batch/slurm/submit_gensim.sh sim bb_schannel --range 0-3999     # their 4,000 sim files
    batch/slurm/submit.sh bb_schannel incl --range 0-3999           # reco + ntuple

Start each stage with a few tasks and `--dry-run`.

## Processes

Each `processes/<sample>/` holds:

| file | what |
|---|---|
| `proc.mg5` | the MadGraph commands up to `output` |
| `run_card.set` | the cuts written into the run card |
| `process.env` | events per generator job, events per sim job, seed bases; for `tc_signal` the UFO restriction |

The beams (`lpp = 0`, `ebeam = 5000`), the seed and the event count are set by `gen_job.py` for all
processes. The Pythia settings are those of mucoll-production (`docs/04-pythia.md` there): ISR and
FSR on, MPI off, QED radiation off leptons on, all decays inclusive.

**Cuts.** The s-channel samples use the cuts of the official VBF samples, read off the hard-process
quarks of their HepMC files (`event_analysis/hepmc2root` on cernbox, all three mass bins):

| sample | pT | \|eta\| | Delta R(q,q) |
|---|---|---|---|
| `bb_schannel` | > 5 GeV | none | none |
| `cc_schannel`, `qq_schannel` | > 5 GeV | < 5 | > 0.4 |

The quarks are back to back with about 5 TeV each, so only the |eta| < 5 edge is ever reached, far
outside the tracker. `tc_signal` keeps the mucoll-production cuts (pT(c) > 20 GeV, |eta| < 5).

**tc model.** SMEFTsim `general_MwScheme` from
[tqllmumucollidermcgen](https://gitlab.cern.ch/dojones/tqllmumucollidermcgen) at 1798a76, as vendored
in mucoll-production. It is 39 MB, so it is not in this repo: the site config points `TC_UFO` at a
copy, and every job checks it against `processes/tc_signal/ufo.sha256` before copying it into the
job and deriving the restriction that keeps `clequ1Re2232` free.

`clequ1Re2232 = 1` with $\Lambda = 1$ TeV is a normalisation, as in mucoll-production, not a
benchmark. The process has no Standard Model tree diagram, so with `NP=1` the events do not depend on
the coefficient (the top width is fixed in the restriction at 1.33 GeV); only the cross-section
does, exactly as $C^2$. Pick the physical value in the analysis:

$$\sigma(t\bar c + \bar t c) = 1161\ \text{pb} \times (C \cdot 1\ \text{TeV}^2)^2$$

The 1161 pb (100-event test, 2 November 2026) agrees to 0.04% with
$2 \times \tfrac34\, s/(16\pi\Lambda^4)$ from Aké et al., eq. (5)
([arXiv:2311.09488](https://arxiv.org/abs/2311.09488)), so `clequ1Re2232` is their
$C^{lequ1}_{13}$ with $\Lambda = 1$ TeV.

| benchmark at 10 TeV, 10 ab⁻¹ | $C$ [TeV⁻²] | $C^{-1/2}$ | $\sigma$ | events |
|---|---|---|---|---|
| Aké et al., Table 2: 1000 events, no tagging or backgrounds | $2.9 \times 10^{-4}$ | 59 TeV | 0.098 fb | 980 |
| Glioti, Marzocca, Wulzer, Fig. 2 ([arXiv:2509.08132](https://arxiv.org/abs/2509.08132)): 68% CL single-operator projection, read off the plot | $\approx 1 \times 10^{-4}$ | $\approx 100$ TeV | 0.012 fb | 116 |

Glioti et al. use the down-quark mass basis; before comparing with them, check their index order,
conjugate counting and CKM rotation against `clequ1Re2232` (the restriction has the CKM off).

## Checks

A generator job fails, and publishes nothing, unless MadGraph's run banner shows every requested
run-card value (beams, seed, event count, cuts), the LHE file has the requested number of events,
and Pythia lost at most 1% of them. Cuts MadGraph applied without being asked are recorded as
`cuts_not_requested` in the metadata.

A sim job fails unless ddsim succeeds and every event of the output has the same stable generator
particles as the HepMC3 event it should come from (`scripts/check_sim.py`).

ddsim's `--skipNEvents` is not used. With HepMC3 input, DD4hep 1.29 starts one event late: asked
to skip 25, it simulated events 26 and 27, which this check caught on the first test. Each sim job
instead copies its 25 events into a file of its own (`scripts/hepmc3_chunk.py`) and ddsim reads it
from the start. mucoll-production found the same behaviour in DD4hep 1.37.

## Cost

Measured on the laptop for `bb_schannel` (2 November 2026, MuSIC v2.5 dev): 48 s start-up,
about 120 s per event, 4.9 GB peak memory, about 260 MB of sim output per event. A 25-event sim
file is therefore about 50 minutes and 6.5 GB. Generation is negligible: 100 events in 7 s.

## Seeds

Generator job *j* uses `GEN_SEED_BASE + j` for both MadGraph and Pythia; sim file *i* uses
`SIM_SEED_BASE + i` for Geant4. The bases differ per sample (`process.env`), so no two jobs share a
seed and every file can be remade.

## Containers

- `eventgen.sif`: the eventGen image (`eventgen:dev`) converted with
  `apptainer build eventgen.sif docker-daemon://eventgen:dev`. The image sets `TMPDIR` and its caches
  under `/work`, which only exists under Docker; `run_gen.sh` moves them into the job's work
  directory. Put `sha256sum eventgen.sif > eventgen.sif.sha256` next to it, or every job hashes the
  1 GB image itself.
- `MuonC_MuSICv2_v5_dev.sif` for ddsim (DD4hep 1.29, reads `.hepmc3` directly), as for reco.

## Outputs

    $GEN_ROOT/<sample>/incl/gen/gen_<q>_incl_<jjjj>.{hepmc3,json,cards.tgz}
    $DATA_ROOT/<sample>/incl/sim/sim_<q>_incl_<iiiii>.{slcio,json}

The `.json` files hold the provenance: seeds, cross-section, cuts requested and used, image and repo
commits, and for sim files the HepMC3 file and events they came from.
