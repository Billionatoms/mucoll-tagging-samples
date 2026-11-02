#!/usr/bin/env python3
"""Generate ONE HepMC3 file for one process. Runs INSIDE the eventgen image.

  gen_job.py --process-dir DIR --events N --seed S --cores C --work DIR [--ufo DIR]

MadGraph (process from proc.mg5, cuts from run_card.set) -> LHE ->
pythia8-lhe-hepmc3 (Pythia settings below) -> events.hepmc3, all in --work.
Follows mucoll-production workflows/production/run_job.py: every requested
run-card value is checked against the run banner (what MadGraph actually used),
every active cut is recorded, including MadGraph defaults nobody asked for, and
the events are counted at each stage. metadata.json is written in every case;
it has "failed" when the job failed, and the exit status is then non-zero.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

# Every process here is 10 TeV mu+ mu- with fixed-energy beams (no lepton PDF,
# no beam spectrum), like the official VBF samples and mucoll-production.
BEAM_SETTINGS = {"lpp1": 0, "lpp2": 0, "ebeam1": 5000.0, "ebeam2": 5000.0,
                 "use_syst": "False"}

# Cuts as MadGraph names them. A cut counts as active when its value differs
# from the "no cut" value: 0 for minima, -1 for maxima and for |eta| limits.
MIN_CUTS = ("ptj", "ptb", "pta", "ptl", "drjj", "drbb", "drbj", "drjl", "drbl",
            "mmjj", "mmbb", "mmll", "ihtmin", "ptheavy", "xptj", "xptb", "xpta", "xptl")
MAX_CUTS = ("ptjmax", "ptbmax", "drjjmax", "drbbmax", "mmjjmax", "mmbbmax", "ihtmax",
            "etaj", "etab", "etaa", "etal")

# Pythia: the same command file as mucoll-production (docs/04-pythia.md).
PYTHIA_TEMPLATE = """\
! Pythia 8 configuration for one LHE input, one subrun.
! Decays are INCLUSIVE: nothing is forced.
Beams:frameType = 4
Beams:LHEF = {lhe}
Main:numberOfSubruns = 1
Main:numberOfEvents = {nevents}
Main:timesAllowErrors = 10
Random:setSeed = on
Random:seed = {seed}
PartonLevel:ISR = on
PartonLevel:FSR = on
PartonLevel:MPI = off
SpaceShower:QEDshowerByL = on
TimeShower:QEDshowerByL = on
HadronLevel:Hadronize = on
HadronLevel:Decay = on
Init:showChangedSettings = on
Init:showChangedParticleData = off
Next:numberCount = 1000
Next:numberShowInfo = 0
Next:numberShowProcess = 0
Next:numberShowEvent = 0
Stat:showProcessLevel = on
"""

SEED_MAX = 900_000_000      # MadGraph maps iseed into RANMAR up to this value


class JobError(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd, log, cwd=None):
    with open(log, "w") as out:
        rc = subprocess.call(cmd, stdout=out, stderr=subprocess.STDOUT, cwd=cwd)
    return rc, open(log, errors="replace").read()


def read_settings(path):
    """key = value lines; # starts a comment."""
    out = {}
    for line in open(path):
        line = line.split("#", 1)[0].strip()
        if line:
            key, value = (s.strip() for s in line.split("=", 1))
            out[key] = value
    return out


def parse_run_card(text):
    """{name: value} from 'value = name ! comment' lines of a run card."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\s*(\S+)\s*=\s*(\w+)\b", line.split("!", 1)[0])
        if m:
            out[m.group(2)] = m.group(1)
    return out


def active_cuts(card):
    active = {}
    for key in MIN_CUTS + MAX_CUTS:
        if key not in card:
            continue
        try:
            value = float(card[key].replace("d", "e"))
        except ValueError:
            continue
        none = 0.0 if key in MIN_CUTS else -1.0
        if value != none and not (key in MAX_CUTS and value < 0):
            active[key] = value
    return active


def check_ufo(ufo, checksums):
    """Every file listed in ufo.sha256 must be present and unchanged."""
    bad = []
    for line in open(checksums):
        digest, rel = line.split()
        path = os.path.join(ufo, rel)
        if not os.path.isfile(path) or sha256(path) != digest:
            bad.append(rel)
    if bad:
        raise JobError(f"UFO {ufo} differs from {checksums}: {bad[:5]}")


def derive_restriction(model_dir, base, coeff_id):
    """Copy of the upstream restriction with the coefficient kept free.
    Upstream cards treat a value of exactly 1 as fixed, so it is set just below."""
    lines, changed = [], 0
    for line in open(os.path.join(model_dir, base)):
        parts = line.split()
        if len(parts) >= 2 and parts[0] == str(coeff_id):
            lines.append(f"    {coeff_id} 9.999999e-01 # coefficient {coeff_id}, kept free\n")
            changed += 1
        else:
            lines.append(line)
    if changed != 1:
        raise JobError(f"expected one line for coefficient {coeff_id} in {base}, found {changed}")
    path = os.path.join(model_dir, "restrict_mts.dat")
    open(path, "w").write("".join(lines))
    return path


def count_lhe(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as f:
        return sum(1 for line in f if line.lstrip().startswith("<event"))


def count_hepmc3(path):
    with open(path, errors="replace") as f:
        return sum(1 for line in f if line.startswith("E "))


def madgraph(args, meta):
    work, pdir = args.work, args.process_dir
    commands = open(os.path.join(pdir, "proc.mg5")).read()
    env = read_settings(os.path.join(pdir, "process.env")) if args.ufo else {}
    if args.ufo:
        check_ufo(args.ufo, os.path.join(pdir, "ufo.sha256"))
        model = os.path.join(work, "model")
        shutil.copytree(args.ufo, model)            # never write into the shared copy
        restrict = derive_restriction(model, env["UFO_RESTRICT_BASE"], env["UFO_COEFF_ID"])
        meta["ufo"] = {"source": args.ufo, "restriction_base": env["UFO_RESTRICT_BASE"],
                       "coefficient_id": env["UFO_COEFF_ID"],
                       "restriction_sha256": sha256(restrict)}
        commands = commands.replace("{MODEL}", f"{model}-mts")
    if "{MODEL}" in commands:
        raise JobError("proc.mg5 uses {MODEL} but no --ufo was given")

    proc = os.path.join(work, "mg5_proc")
    script = os.path.join(work, "mg5_commands.txt")
    open(script, "w").write("set automatic_html_opening False\n" + commands
                            + f"\noutput {proc}\n")
    rc, _ = run(["mg5_aMC", "-f", script], os.path.join(work, "logs", "mg5_output.log"), cwd=work)
    if rc != 0 or not os.path.isdir(proc):
        raise JobError(f"MadGraph output step failed (rc={rc}); see logs/mg5_output.log")

    # --- run card: beams, statistics, seed, cuts --------------------------------
    cuts = read_settings(os.path.join(pdir, "run_card.set"))
    wanted = {**BEAM_SETTINGS, "nevents": args.events, "iseed": args.seed, **cuts}
    run_card = os.path.join(proc, "Cards", "run_card.dat")
    card = open(run_card).read()
    applied, inapplicable = {}, {}
    for key, value in wanted.items():
        pat = re.compile(rf"^(\s*)\S+(\s*=\s*{key}\b.*)$", re.M)
        if pat.search(card):
            card = pat.sub(rf"\g<1>{value}\g<2>", card, count=1)
            applied[key] = value
        elif key in cuts and not re.search(rf"\b{key}\b", card):
            # The card has no such cut for this final state (e.g. mmjj for the
            # one-jet signal): MadGraph cannot apply it. Recorded, not fatal.
            inapplicable[key] = value
        else:
            raise JobError(f"run-card entry {key} could not be set")
    open(run_card, "w").write(card)

    conf = os.path.join(proc, "Cards", "me5_configuration.txt")
    text = open(conf).read()
    for key, value in (("run_mode", 2), ("nb_core", args.cores),
                       ("automatic_html_opening", "False")):
        text = re.sub(rf"^#?\s*{key}\s*=.*$", f"{key} = {value}", text, count=1, flags=re.M)
    open(conf, "w").write(text)

    rc, log = run([os.path.join(proc, "bin", "generate_events"), "-f"],
                  os.path.join(work, "logs", "mg5_generate.log"), cwd=proc)
    if rc != 0:
        raise JobError(f"MadGraph generate_events failed (rc={rc}); see logs/mg5_generate.log")

    # --- what MadGraph actually used: the run banner ------------------------------
    banners = sorted(glob.glob(os.path.join(proc, "Events", "*", "*_banner.txt")))
    if not banners:
        raise JobError("no run banner")
    banner = open(banners[-1], errors="replace").read()
    block = re.search(r"<MGRunCard>(.*?)</MGRunCard>", banner, re.S)
    used = parse_run_card(block.group(1) if block else banner)
    for key, value in applied.items():
        got = used.get(key)
        try:
            same = got is not None and float(got.replace("d", "e")) == float(value)
        except ValueError:
            same = got is not None and got.lower().strip(".") == str(value).lower().strip(".")
        if not same:
            raise JobError(f"MadGraph used {key}={got}, requested {value}")
    xs = re.search(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+-]+)", banner)
    err = re.search(r"Cross-section :\s*[0-9.eE+-]+\s*\+-\s*([0-9.eE+-]+)\s*pb", log)
    effective = active_cuts(used)
    meta.update(
        mg5_commands=open(script).read().splitlines(),
        run_card_requested=applied,
        cuts_requested={k: float(v) for k, v in cuts.items()},
        cuts_inapplicable=inapplicable,
        cuts_effective=effective,
        cuts_not_requested={k: v for k, v in effective.items() if k not in cuts},
        cross_section_pb=float(xs.group(1)) if xs else None,
        cross_section_uncertainty_pb=float(err.group(1)) if err else None,
        run_banner_sha256=hashlib.sha256(banner.encode()).hexdigest(),
    )
    if meta["cross_section_pb"] is None:
        raise JobError("no cross-section in the run banner")
    shutil.copy(banners[-1], os.path.join(work, "run_banner.txt"))

    found = sorted(glob.glob(os.path.join(proc, "Events", "*", "unweighted_events.lhe*")))
    if not found:
        raise JobError("MadGraph produced no LHE file")
    lhe = os.path.join(work, "events.lhe.gz" if found[0].endswith(".gz") else "events.lhe")
    shutil.move(found[0], lhe)
    return lhe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process-dir", required=True)
    ap.add_argument("--events", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--work", required=True)
    ap.add_argument("--ufo")
    args = ap.parse_args()
    os.makedirs(os.path.join(args.work, "logs"), exist_ok=True)
    meta = {"process": os.path.basename(args.process_dir.rstrip("/")),
            "events_requested": args.events, "seed": args.seed}
    try:
        if not 1 <= args.seed <= SEED_MAX:
            raise JobError(f"seed must be in [1, {SEED_MAX}]")
        lhe = madgraph(args, meta)
        meta["events_lhe"] = count_lhe(lhe)
        if meta["events_lhe"] != args.events:
            raise JobError(f"LHE holds {meta['events_lhe']} events, {args.events} requested")

        cmnd = os.path.join(args.work, "pythia.cmnd")
        open(cmnd, "w").write(PYTHIA_TEMPLATE.format(lhe=lhe, nevents=args.events, seed=args.seed))
        hepmc = os.path.join(args.work, "events.hepmc3")
        rc, log = run(["pythia8-lhe-hepmc3", "-c", cmnd, "-o", hepmc],
                      os.path.join(args.work, "logs", "pythia.log"))
        if rc != 0:
            raise JobError(f"pythia8-lhe-hepmc3 failed (rc={rc}); see logs/pythia.log")
        meta["events_hepmc3"] = count_hepmc3(hepmc)
        meta["pythia_event_loss"] = args.events - meta["events_hepmc3"]
        if meta["events_hepmc3"] < 1:
            raise JobError("the HepMC3 file holds no events")
        # Pythia may drop a few events it cannot shower; more than 1% is not that.
        if meta["pythia_event_loss"] > 0.01 * args.events:
            raise JobError(f"Pythia lost {meta['pythia_event_loss']} of {args.events} events")
        meta["pythia_cmnd"] = open(cmnd).read().splitlines()
        meta["hepmc3_sha256"] = sha256(hepmc)
    except JobError as exc:
        meta["failed"] = str(exc)
        print(f"JOB FAILED: {exc}", file=sys.stderr)
    json.dump(meta, open(os.path.join(args.work, "metadata.json"), "w"), indent=2)
    if "failed" in meta:
        return 1
    print(f"OK events={meta['events_hepmc3']} sigma={meta['cross_section_pb']} pb "
          f"cuts={meta['cuts_effective']} not_requested={meta['cuts_not_requested']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
