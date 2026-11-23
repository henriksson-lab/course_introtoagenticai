#!/usr/bin/env python3
"""Quick quality statistics for a FASTQ file.

Usage:
    python fastq_stats.py reads.fastq            # k-mer length 5
    python fastq_stats.py reads.fastq --k 7

Writes a tab-separated report to the screen (redirect it with > to save it):
first a table of summary statistics, then a blank line, then the ten most
common k-mers. Quality scores are read as Phred+33 (Illumina 1.8 and later).

Rules (so that the numbers can be checked):
- bases are made upper case before counting
- GC% is G+C out of A+C+G+T (N and other letters are left out)
- N% is out of all bases
- mean_quality and q30_percent are over all bases of all reads
- k-mers containing anything other than A, C, G, T are skipped
- ties among k-mers are broken alphabetically
- an empty file gives 0 reads and NA for the other statistics
- a broken record stops the program with an error message and exit code 1
"""
import argparse
import sys
from collections import Counter


class FastqError(Exception):
    pass


def read_records(path):
    """Yield (sequence, quality) for each 4-line record."""
    with open(path) as f:
        line_no = 0
        while True:
            header = f.readline()
            if header == "":
                return
            seq = f.readline()
            plus = f.readline()
            qual = f.readline()
            start = line_no + 1
            line_no += 4
            if qual == "":
                raise FastqError(f"record starting at line {start} is incomplete")
            header = header.rstrip("\n")
            seq = seq.rstrip("\n").upper()
            plus = plus.rstrip("\n")
            qual = qual.rstrip("\n")
            if not header.startswith("@"):
                raise FastqError(f"line {start}: header does not start with '@'")
            if not plus.startswith("+"):
                raise FastqError(f"line {start + 2}: separator does not start with '+'")
            if len(seq) != len(qual):
                raise FastqError(f"line {start}: sequence and quality have different lengths")
            yield seq, qual


def count_kmers(seq, k, counts):
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        if all(c in "ACGT" for c in kmer):
            counts[kmer] += 1


def fmt(x):
    return "NA" if x is None else f"{x:.2f}"


def main():
    parser = argparse.ArgumentParser(description="Quality statistics for a FASTQ file")
    parser.add_argument("fastq")
    parser.add_argument("--k", type=int, default=5, help="k-mer length (default 5)")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be at least 1")

    reads = bases = 0
    min_len = max_len = None
    gc = acgt = n_bases = reads_with_n = 0
    qual_sum = q30 = 0
    kmers = Counter()

    try:
        for seq, qual in read_records(args.fastq):
            reads += 1
            length = len(seq)
            bases += length
            min_len = length if min_len is None else min(min_len, length)
            max_len = length if max_len is None else max(max_len, length)
            g_c = seq.count("G") + seq.count("C")
            gc += g_c
            acgt += g_c + seq.count("A") + seq.count("T")
            n = seq.count("N")
            n_bases += n
            if n > 0:
                reads_with_n += 1
            for c in qual:
                q = ord(c) - 33
                qual_sum += q
                if q >= 30:
                    q30 += 1
            count_kmers(seq, args.k, kmers)
    except FastqError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    out = sys.stdout
    out.write("metric\tvalue\n")
    out.write(f"reads\t{reads}\n")
    out.write(f"bases\t{bases}\n")
    out.write(f"min_length\t{'NA' if min_len is None else min_len}\n")
    out.write(f"max_length\t{'NA' if max_len is None else max_len}\n")
    out.write(f"mean_length\t{fmt(bases / reads if reads else None)}\n")
    out.write(f"gc_percent\t{fmt(100 * gc / acgt if acgt else None)}\n")
    out.write(f"n_bases\t{n_bases}\n")
    out.write(f"n_percent\t{fmt(100 * n_bases / bases if bases else None)}\n")
    out.write(f"reads_with_n\t{reads_with_n}\n")
    out.write(f"mean_quality\t{fmt(qual_sum / bases if bases else None)}\n")
    out.write(f"q30_percent\t{fmt(100 * q30 / bases if bases else None)}\n")
    out.write("\n")
    out.write(f"kmer_{args.k}\tcount\n")
    top = sorted(kmers.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    for kmer, count in top:
        out.write(f"{kmer}\t{count}\n")


if __name__ == "__main__":
    main()
