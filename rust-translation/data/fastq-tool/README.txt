fastq_stats.py - quick QC numbers for a FASTQ file (read count, lengths,
GC, N, quality, most common k-mers). Python 3, no extra packages.

  python fastq_stats.py reads.fastq > stats.tsv

Works fine on the test file but takes ages on a whole sequencing run.
Students on Windows could not run it without installing Python first.

Files:
  fastq_stats.py   the tool
  make_fastq.py    makes synthetic test reads (python make_fastq.py --help)
  reads.fastq      2000 synthetic reads, made with make_fastq.py --reads 2000
  tiny.fastq       3 reads, small enough to check by hand
  edge-cases/      files that are empty, broken or unusual on purpose
