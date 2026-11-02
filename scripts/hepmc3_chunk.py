#!/usr/bin/env python3
"""Copy events skip .. skip+n-1 of a HepMC3 ASCII file into a file of their own.

  hepmc3_chunk.py <in.hepmc3> <out.hepmc3> <skip> <n>

ddsim's --skipNEvents is not used: with HepMC3 input, DD4hep 1.29 (MuSIC v2.5)
starts at event skip+1, not skip (seen in the run_sim.sh smoke test; mucoll-production
found the same in DD4hep 1.37). The header lines before the first event and the
end-of-listing line are kept, so the chunk is a complete HepMC3 file that ddsim
reads from its first event. Prints the number of events written.
"""
import sys

END = "HepMC::Asciiv3-END_EVENT_LISTING"


def main():
    src, dst, skip, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    index, written, keep = -1, 0, False
    with open(src, errors="replace") as fin, open(dst, "w") as fout:
        for line in fin:
            if line.startswith("E "):
                index += 1
                if index >= skip + n:
                    break
                keep = index >= skip
                written += keep
            elif line.startswith(END):
                break
            if index < 0 or keep:          # header, or a line of a kept event
                fout.write(line)
        fout.write(END + "\n")
    print(written)


if __name__ == "__main__":
    main()
