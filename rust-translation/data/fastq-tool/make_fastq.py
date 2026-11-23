#!/usr/bin/env python3
"""Write a synthetic FASTQ file (made-up reads, no real organism).

Usage:
    python make_fastq.py --reads 2000 --out reads.fastq
    python make_fastq.py --reads 1000000 --out big.fastq      # about 290 MB

The same --reads and --seed always give the same file, on any computer.
Reads are 50 to 150 bases long (most are 150), with about 45 % GC.
About 5 % of reads end in a piece of the Illumina adapter (AGATCGGAAGAGC),
about 3 % contain one to three N bases, and quality falls towards the end
of each read, as in real Illumina data. Python standard library only.
"""
import argparse
import random

ADAPTER = "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC"


def make_read(rng, i):
    length = 150 if rng.random() < 0.7 else rng.randint(50, 149)
    seq = rng.choices("ACGT", weights=[27.5, 22.5, 22.5, 27.5], k=length)
    if rng.random() < 0.05:
        start = rng.randint(max(0, length - 40), length - 13)
        for j, base in enumerate(ADAPTER[: length - start]):
            seq[start + j] = base
    if rng.random() < 0.03:
        for _ in range(rng.randint(1, 3)):
            seq[rng.randrange(length)] = "N"
    qual = []
    for j in range(length):
        mean = 37 - 12 * (j / 150) ** 2
        q = int(round(rng.gauss(mean, 3)))
        if seq[j] == "N":
            q = 2
        qual.append(chr(33 + min(41, max(2, q))))
    return f"@read{i + 1}\n{''.join(seq)}\n+\n{''.join(qual)}\n"


def main():
    parser = argparse.ArgumentParser(description="Write a synthetic FASTQ file")
    parser.add_argument("--reads", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="reads.fastq")
    args = parser.parse_args()
    rng = random.Random(args.seed)
    with open(args.out, "w", newline="\n") as f:
        for i in range(args.reads):
            f.write(make_read(rng, i))


if __name__ == "__main__":
    main()
