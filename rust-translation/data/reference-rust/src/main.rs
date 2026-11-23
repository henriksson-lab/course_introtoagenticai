//! Rust port of fastq_stats.py: quick quality statistics for a FASTQ file.
//! Reference solution for the exercise in "Translating code to Rust".
//! It gives byte-identical output, error messages and exit codes to the
//! Python original (checked on all reference inputs and 40 generated runs).
//! Note: it is output-faithful, not structure-faithful: read_records() is
//! inlined into main() and there are small formatting helpers.
//! Build: cargo build --release (do not commit target/).
//!
//! Usage: fastq_stats reads.fastq [--k 5]

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Write};
use std::process;

/// Read one line; None at end of file. Strips "\n" and, like Python's
/// text mode, a "\r" before it (Windows line endings).
fn read_line(reader: &mut impl BufRead, buf: &mut Vec<u8>) -> io::Result<bool> {
    buf.clear();
    if reader.read_until(b'\n', buf)? == 0 {
        return Ok(false);
    }
    if buf.last() == Some(&b'\n') {
        buf.pop();
        if buf.last() == Some(&b'\r') {
            buf.pop();
        }
    }
    Ok(true)
}

fn fmt(x: Option<f64>) -> String {
    match x {
        None => "NA".to_string(),
        Some(v) => format!("{:.2}", v),
    }
}

fn fmt_int(x: Option<usize>) -> String {
    match x {
        None => "NA".to_string(),
        Some(v) => v.to_string(),
    }
}

fn count_kmers(seq: &[u8], k: usize, counts: &mut HashMap<Vec<u8>, u64>) {
    if seq.len() < k {
        return;
    }
    for i in 0..=(seq.len() - k) {
        let kmer = &seq[i..i + k];
        if kmer.iter().all(|c| matches!(c, b'A' | b'C' | b'G' | b'T')) {
            if let Some(n) = counts.get_mut(kmer) {
                *n += 1;
            } else {
                counts.insert(kmer.to_vec(), 1);
            }
        }
    }
}

fn usage_error(msg: &str) -> ! {
    eprintln!("usage: fastq_stats [--k K] fastq");
    eprintln!("fastq_stats: error: {}", msg);
    process::exit(2);
}

fn main() {
    // Arguments: one FASTQ path and an optional --k (default 5).
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut path: Option<String> = None;
    let mut k: i64 = 5;
    let mut i = 0;
    while i < args.len() {
        if args[i] == "--k" {
            i += 1;
            k = match args.get(i).and_then(|s| s.parse().ok()) {
                Some(v) => v,
                None => usage_error("argument --k: expected an integer"),
            };
        } else if let Some(v) = args[i].strip_prefix("--k=") {
            k = v.parse().unwrap_or_else(|_| usage_error("argument --k: expected an integer"));
        } else if path.is_none() {
            path = Some(args[i].clone());
        } else {
            usage_error("too many arguments");
        }
        i += 1;
    }
    let path = path.unwrap_or_else(|| usage_error("the following arguments are required: fastq"));
    if k < 1 {
        usage_error("--k must be at least 1");
    }
    let k = k as usize;

    let file = File::open(&path).unwrap_or_else(|e| {
        eprintln!("error: cannot open {}: {}", path, e);
        process::exit(1);
    });
    let mut reader = BufReader::with_capacity(1 << 20, file);

    let (mut reads, mut bases) = (0usize, 0usize);
    let (mut min_len, mut max_len): (Option<usize>, Option<usize>) = (None, None);
    let (mut gc, mut acgt, mut n_bases, mut reads_with_n) = (0usize, 0usize, 0usize, 0usize);
    let (mut qual_sum, mut q30) = (0i64, 0usize);
    let mut kmers: HashMap<Vec<u8>, u64> = HashMap::new();

    let (mut header, mut seq, mut plus, mut qual) = (Vec::new(), Vec::new(), Vec::new(), Vec::new());
    let mut line_no = 0usize;
    let fail = |msg: String| -> ! {
        eprintln!("error: {}", msg);
        process::exit(1);
    };
    loop {
        if !read_line(&mut reader, &mut header).expect("read error") {
            break;
        }
        let got_seq = read_line(&mut reader, &mut seq).expect("read error");
        let got_plus = got_seq && read_line(&mut reader, &mut plus).expect("read error");
        let got_qual = got_plus && read_line(&mut reader, &mut qual).expect("read error");
        let start = line_no + 1;
        line_no += 4;
        if !got_qual {
            fail(format!("record starting at line {} is incomplete", start));
        }
        seq.make_ascii_uppercase();
        if header.first() != Some(&b'@') {
            fail(format!("line {}: header does not start with '@'", start));
        }
        if plus.first() != Some(&b'+') {
            fail(format!("line {}: separator does not start with '+'", start + 2));
        }
        if seq.len() != qual.len() {
            fail(format!("line {}: sequence and quality have different lengths", start));
        }

        reads += 1;
        let length = seq.len();
        bases += length;
        min_len = Some(min_len.map_or(length, |m| m.min(length)));
        max_len = Some(max_len.map_or(length, |m| m.max(length)));
        let (mut a, mut c, mut g, mut t, mut n) = (0usize, 0usize, 0usize, 0usize, 0usize);
        for &b in seq.iter() {
            match b {
                b'A' => a += 1,
                b'C' => c += 1,
                b'G' => g += 1,
                b'T' => t += 1,
                b'N' => n += 1,
                _ => {}
            }
        }
        gc += g + c;
        acgt += g + c + a + t;
        n_bases += n;
        if n > 0 {
            reads_with_n += 1;
        }
        for &b in qual.iter() {
            let q = b as i64 - 33;
            qual_sum += q;
            if q >= 30 {
                q30 += 1;
            }
        }
        count_kmers(&seq, k, &mut kmers);
    }

    let ratio = |num: f64, den: usize| if den > 0 { Some(num / den as f64) } else { None };
    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());
    writeln!(out, "metric\tvalue").unwrap();
    writeln!(out, "reads\t{}", reads).unwrap();
    writeln!(out, "bases\t{}", bases).unwrap();
    writeln!(out, "min_length\t{}", fmt_int(min_len)).unwrap();
    writeln!(out, "max_length\t{}", fmt_int(max_len)).unwrap();
    writeln!(out, "mean_length\t{}", fmt(ratio(bases as f64, reads))).unwrap();
    writeln!(out, "gc_percent\t{}", fmt(ratio(100.0 * gc as f64, acgt))).unwrap();
    writeln!(out, "n_bases\t{}", n_bases).unwrap();
    writeln!(out, "n_percent\t{}", fmt(ratio(100.0 * n_bases as f64, bases))).unwrap();
    writeln!(out, "reads_with_n\t{}", reads_with_n).unwrap();
    writeln!(out, "mean_quality\t{}", fmt(ratio(qual_sum as f64, bases))).unwrap();
    writeln!(out, "q30_percent\t{}", fmt(ratio(100.0 * q30 as f64, bases))).unwrap();
    writeln!(out).unwrap();
    writeln!(out, "kmer_{}\tcount", k).unwrap();
    let mut top: Vec<(&Vec<u8>, &u64)> = kmers.iter().collect();
    top.sort_by(|x, y| y.1.cmp(x.1).then_with(|| x.0.cmp(y.0)));
    for (kmer, count) in top.into_iter().take(10) {
        writeln!(out, "{}\t{}", String::from_utf8_lossy(kmer), count).unwrap();
    }
}
