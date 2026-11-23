"""Make the curation exercise data for "Using agents to train AI".

Writes OUTDIR/curation-set/ with
  tiles/tile_XXXX.png   small synthetic fluorescence images, one nucleus each
                        (48 x 48 pixels, 8-bit grey)
  manifest.csv          one row per tile: file, sample_id, split, label,
                        pixel_size_um, annotator
  README.txt            what the data is (written for participants)
and prints the answer key (also written to OUTDIR/answer-key.json, which is
NOT part of the participant zip).

Task the tiles stand for: classify a nucleus as "intact" or "fragmented"
(for example dying cells). Everything is synthetic; no real images are used.

Planted problems (the exercise asks the agent to find them):
  - exact duplicates: byte-identical files under another name
  - near duplicates: the same nucleus mirrored, slightly brighter, re-noised
  - leakage: one sample has tiles in both train and test, and some
    duplicates cross the train/test boundary
  - wrong labels: some tiles carry the other class's label
  - hard but correct tiles: look unusual, label is right (a cleaner that
    removes everything unusual would delete them)
  - one corrupt (truncated) PNG file
  - metadata: one sample's pixel size entered in nanometres in the
    micrometre column; some labels written "Intact" instead of "intact"

Fixed seed: the output is identical on every run. Python 3 standard
library and numpy only.

Usage: python make-data.py [OUTDIR]     (default: the folder of this script)
"""
import csv
import json
import os
import struct
import sys
import zlib

import numpy as np

SEED = 20261123
N = 48


def write_png(path, arr):
    """Minimal 8-bit greyscale PNG writer (standard library only)."""
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    raw = b"".join(b"\x00" + arr[i].tobytes() for i in range(arr.shape[0]))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", arr.shape[1], arr.shape[0], 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return png


def blur(a, s):
    """Separable Gaussian blur with numpy only."""
    r = int(3 * s) + 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    k /= k.sum()
    a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="reflect"), k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="reflect"), k, "valid"), 1, a)


def ellipse(yy, xx, cy, cx, a, b, th):
    dy, dx = yy - cy, xx - cx
    u = dx * np.cos(th) + dy * np.sin(th)
    v = -dx * np.sin(th) + dy * np.cos(th)
    return (u / a) ** 2 + (v / b) ** 2 < 1


def render(rng, kind):
    """kind: intact, fragmented, hard_intact (debris speck), hard_fragmented (2 large pieces)."""
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    sig = np.zeros((N, N))
    c = N / 2 + rng.normal(0, 2, 2)
    if kind in ("intact", "hard_intact"):
        a, b = rng.uniform(10, 15), rng.uniform(7, 11)
        sig[ellipse(yy, xx, c[0], c[1], a, b, rng.uniform(0, np.pi))] = 1.0
        if kind == "hard_intact":       # a bright debris speck next to an intact nucleus
            ang = rng.uniform(0, 2 * np.pi)
            sy, sx = c[0] + 17 * np.sin(ang), c[1] + 17 * np.cos(ang)
            sig[ellipse(yy, xx, sy, sx, 2.5, 2.5, 0)] = 1.6
    elif kind == "fragmented":
        placed = []                      # 4-7 separate pieces, none hidden behind another
        want = rng.integers(4, 8)
        while len(placed) < want:
            fy, fx = c + rng.normal(0, 6.5, 2)
            r = rng.uniform(2.5, 4.5)
            if all((fy - py) ** 2 + (fx - px) ** 2 > (r + pr + 1) ** 2 for py, px, pr in placed):
                placed.append((fy, fx, r))
                sig[ellipse(yy, xx, fy, fx, r, r, 0)] = rng.uniform(1.2, 1.8)
    else:                                # hard_fragmented: two large pieces only
        for s in (-1, 1):
            r = rng.uniform(5, 6.5)
            sig[ellipse(yy, xx, c[0] + s * 6, c[1] + s * 4, r, r * 0.8, rng.uniform(0, 3))] = 1.4
    tex = blur(rng.normal(0, 1, (N, N)), 1.2)
    sig = sig * (1 + 0.25 * tex / tex.std())
    img = blur(sig, rng.uniform(0.8, 1.4)) * rng.uniform(150, 200) + 20
    img = rng.poisson(np.clip(img, 0, None)) + rng.normal(0, 3, (N, N))
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(out, "curation-set")
    tdir = os.path.join(root, "tiles")
    os.makedirs(tdir, exist_ok=True)
    for f in os.listdir(tdir):
        os.remove(os.path.join(tdir, f))
    rng = np.random.default_rng(SEED)

    # 15 samples (slides), 10 nuclei each. S01-S11 train, S12-S15 test.
    base = []
    for s in range(1, 16):
        sid = f"S{s:02d}"
        for j in range(10):
            frag = rng.random() < 0.28
            base.append(dict(sample_id=sid, true="fragmented" if frag else "intact",
                             kind="fragmented" if frag else "intact",
                             split="train" if s <= 11 else "test",
                             annotator="A" if rng.random() < 0.6 else "B"))
    # leakage: 4 of S09's tiles are listed as test
    s09 = [i for i, b in enumerate(base) if b["sample_id"] == "S09"]
    for i in s09[6:]:
        base[i]["split"] = "test"
    # hard but correct cases
    idx_int = [i for i, b in enumerate(base) if b["true"] == "intact" and b["sample_id"] not in ("S09",)]
    idx_frag = [i for i, b in enumerate(base) if b["true"] == "fragmented" and b["sample_id"] not in ("S09",)]
    hard = [int(rng.choice(idx_int)), int(rng.choice(idx_frag))]
    base[hard[0]]["kind"] = "hard_intact"
    base[hard[1]]["kind"] = "hard_fragmented"
    # wrong labels: 4 fragmented labelled intact, 2 intact labelled fragmented
    cand_f = [i for i in idx_frag if i not in hard]
    cand_i = [i for i in idx_int if i not in hard]
    wrong = sorted([int(i) for i in rng.choice(cand_f, 4, replace=False)] +
                   [int(i) for i in rng.choice(cand_i, 2, replace=False)])
    for b in base:
        b["label"] = b["true"]
    for i in wrong:
        base[i]["label"] = "intact" if base[i]["true"] == "fragmented" else "fragmented"

    imgs = [render(rng, b["kind"]) for b in base]

    # extra rows: 4 exact duplicates, 3 near duplicates
    pool = [i for i in range(len(base)) if i not in wrong and i not in hard and base[i]["split"] == "train"
            and base[i]["sample_id"] != "S09"]
    picks = [int(i) for i in rng.choice(pool, 7, replace=False)]
    exact_src, near_src = picks[:4], picks[4:]
    rows = []
    for i, b in enumerate(base):
        rows.append(dict(src=i, rowtype="original", **b))
    for n, i in enumerate(exact_src):     # 2 of 4 copies cross into test
        r = dict(base[i])
        r.update(src=i, rowtype="exact_duplicate", split="test" if n < 2 else "train")
        rows.append(r)
    near_imgs = {}
    for n, i in enumerate(near_src):      # 1 of 3 crosses into test
        r = dict(base[i])
        r.update(src=i, rowtype="near_duplicate", split="test" if n == 0 else "train")
        rows.append(r)
        near_imgs[len(rows) - 1] = np.fliplr(imgs[i]) * 1.08 + rng.normal(0, 2, (N, N))

    order = rng.permutation(len(rows))
    names = {}
    for k, ri in enumerate(order):
        names[int(ri)] = f"tile_{k + 1:04d}.png"
    corrupt_row = int(rng.choice([i for i in range(150) if i not in wrong and i not in hard
                                  and i not in picks and i not in s09]))

    s14 = "S14"
    cap_rows = [int(i) for i in rng.choice([i for i in range(150) if base[i]["label"] == "intact"
                                            and base[i]["sample_id"] != s14 and i not in wrong and i not in hard and i != corrupt_row], 3, replace=False)]
    manifest = []
    for ri in range(len(rows)):
        r = rows[ri]
        path = os.path.join(tdir, names[ri])
        if r["rowtype"] == "near_duplicate":
            write_png(path, near_imgs[ri])
        else:
            write_png(path, imgs[r["src"]])
        label = r["label"]
        if r["rowtype"] == "original" and ri in cap_rows:
            label = "Intact"
        manifest.append(dict(file="tiles/" + names[ri], sample_id=r["sample_id"], split=r["split"],
                             label=label, pixel_size_um="650" if r["sample_id"] == s14 else "0.65",
                             annotator=r["annotator"]))
    # corrupt one file: keep only the first 300 bytes
    cp = os.path.join(tdir, names[corrupt_row])
    data = open(cp, "rb").read()
    open(cp, "wb").write(data[:300])

    manifest.sort(key=lambda m: m["file"])
    with open(os.path.join(root, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)

    with open(os.path.join(root, "README.txt"), "w") as f:
        f.write("""Curation exercise data (synthetic)

A small labelled dataset for training a classifier of cell nuclei:
"intact" or "fragmented". Each tile is a 48 x 48 pixel, 8-bit greyscale
fluorescence image centred on one nucleus.

manifest.csv has one row per tile:
  file           path of the image
  sample_id      the slide (sample) the nucleus comes from
  split          train or test
  label          intact or fragmented
  pixel_size_um  pixel size in micrometres
  annotator      who labelled it (A or B)

All images were generated by a script for the course "Introduction to
agentic AI". They show no real cells and no real patients. Free to use.

The dataset is not clean. Before anyone trains on it, it needs an audit.
""")

    name = lambda i: names[i]  # noqa: E731
    key = dict(
        rows=len(rows), unique_nuclei=150, samples=15,
        exact_duplicate_pairs=[[name(r["src"]), name(i)] for i, r in enumerate(rows) if r["rowtype"] == "exact_duplicate"],
        near_duplicate_pairs=[[name(r["src"]), name(i)] for i, r in enumerate(rows) if r["rowtype"] == "near_duplicate"],
        duplicates_crossing_train_test=sum(1 for r in rows if r["rowtype"] != "original" and r["split"] == "test"),
        leaked_sample="S09", leaked_sample_train=6, leaked_sample_test=4,
        wrong_labels=[[name(i), base[i]["label"], base[i]["true"]] for i in wrong],
        hard_but_correct=[[name(i), base[i]["label"], base[i]["kind"]] for i in hard],
        corrupt_file=name(corrupt_row),
        pixel_size_problem=dict(sample="S14", rows=10, value="650 (nm) instead of 0.65 (um)"),
        label_spelling_rows=[name(i) for i in cap_rows],
        label_counts_as_given={k: sum(1 for m in manifest if m["label"] == k) for k in sorted({m["label"] for m in manifest})},
        true_counts_unique={"intact": sum(1 for b in base if b["true"] == "intact"),
                            "fragmented": sum(1 for b in base if b["true"] == "fragmented")},
        split_rows_as_given={k: sum(1 for m in manifest if m["split"] == k) for k in ("train", "test")},
    )
    json.dump(key, open(os.path.join(out, "answer-key.json"), "w"), indent=1)
    print(json.dumps(key, indent=1))


if __name__ == "__main__":
    main()
