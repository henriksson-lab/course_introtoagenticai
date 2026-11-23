#!/usr/bin/env python3
"""make-data.py: example files for the exercise in the unit
"Translating code to Rust" (Part 5: Scaling up).

All data are synthetic. Run from anywhere with:

    python3 make-data.py

It builds fastq-tool.zip next to this script. The zip holds a folder
fastq-tool/ with:

  fastq_stats.py   the "inherited" Python tool to be ported (from fastq-tool/)
  make_fastq.py    the read generator (from fastq-tool/); participants use it
                   to make a large file for the benchmark on their own machine
  README.txt       the colleague's note (from fastq-tool/)
  reads.fastq      2000 synthetic reads: make_fastq.py --reads 2000 --seed 42
  tiny.fastq       3 hand-written reads (one lower case, one with N)
  edge-cases/
    empty.fastq                 0 bytes
    truncated.fastq             tiny.fastq with the last line missing
    all_n.fastq                 2 reads of only N (GC% and k-mers undefined)
    windows_line_endings.fastq  tiny.fastq with CRLF line endings
    no_final_newline.fastq      tiny.fastq without the last newline

The traps, for the teacher:
  * windows_line_endings.fastq: Python's open() in text mode turns "\r\n"
    into "\n", so the Python tool gives the same numbers as for tiny.fastq.
    A naive Rust port keeps the "\r", so read lengths, base counts and
    quality sums change (often a "different lengths" error is avoided only
    by accident). The port must strip "\r" too.
  * truncated.fastq must give the same error message and exit code 1.
  * all_n.fastq: GC% has no denominator (NA), and there are no k-mers.
  * empty.fastq: 0 reads, NA everywhere, header lines still printed.
  * Ties among k-mers: Python sorts by (-count, k-mer); a port that sorts
    only by count gives a different order for equal counts.
  * Rounding: Python's f"{x:.2f}" and Rust's format!("{:.2}", x) both round
    the exact binary value, so they agree; a port that rounds by hand
    (e.g. (x*100).round()/100) can differ in the last digit.

reference-rust/ (Cargo.toml + src/main.rs) is a reference port, checked to give
byte-identical output on every file above and on 20 generated files (k=5, 7).

Standard library only; the seed is fixed, so the files are identical every
time.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fastq-tool")

TINY = (
    "@r1\nACGTACGTNN\n+\nIIIIIIII##\n"
    "@r2\nacgtgggccc\n+\n5555555555\n"
    "@r3\nGATTACA\n+\n?????+(\n"
)
ALL_N = "@n1\nNNNNNN\n+\n######\n@n2\nNNNN\n+\n####\n"


def write(path, text):
    with open(path, "w", newline="") as f:
        f.write(text)


def main():
    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, "fastq-tool")
    edge = os.path.join(out, "edge-cases")
    os.makedirs(edge)
    for name in ("fastq_stats.py", "make_fastq.py", "README.txt"):
        shutil.copy(os.path.join(SRC, name), out)
    subprocess.run(
        [sys.executable, os.path.join(SRC, "make_fastq.py"),
         "--reads", "2000", "--seed", "42", "--out", os.path.join(out, "reads.fastq")],
        check=True,
    )
    write(os.path.join(out, "tiny.fastq"), TINY)
    write(os.path.join(edge, "empty.fastq"), "")
    write(os.path.join(edge, "truncated.fastq"), TINY[: TINY.rstrip("\n").rfind("\n") + 1])
    write(os.path.join(edge, "all_n.fastq"), ALL_N)
    write(os.path.join(edge, "windows_line_endings.fastq"), TINY.replace("\n", "\r\n"))
    write(os.path.join(edge, "no_final_newline.fastq"), TINY.rstrip("\n"))

    zpath = os.path.join(HERE, "fastq-tool.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in sorted(os.walk(out)):
            for name in sorted(files):
                full = os.path.join(root, name)
                z.write(full, os.path.relpath(full, tmp))
    shutil.rmtree(tmp)
    print("wrote", zpath)


if __name__ == "__main__":
    main()
