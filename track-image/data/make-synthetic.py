#!/usr/bin/env python3
"""
make-synthetic.py: OPTIONAL synthetic microscopy images for "Track C: Image
analysis in Python", for those who want a demo with an EXACT known answer.
The worked example uses real images (BBBC039); this script is an extra.
Nothing it makes is stored in the repository: it writes into a folder you
choose (default: ./nuclei-synthetic in the current folder).

Creates 12 fluorescence-like images (400 x 400 pixels) of stained nuclei:

  <out>/                               the images
      2026-04-02_ctrl_field01.tif ...  6 control fields
      2026-04-02_drug_field01.tif ...  6 drug-treated fields
      imaging-notes.txt                microscope notes (pixel size, settings)
  <out>-answer-key.csv                 ANSWER KEY, next to the folder (keep it
                                       away from the agent): number of
                                       nuclei per image, how many touch another
                                       nucleus or the image border, true mean
                                       area in square micrometres

What is planted (what a careful analysis has to deal with):
  - Images are 16-bit greyscale TIFF (camera values 0-4095, a 12-bit
    camera). They look dark in some image viewers. That is normal.
  - Pixel size is 0.65 micrometres (in imaging-notes.txt, not in the file
    names). Areas in pixels must be converted: 1 px = 0.4225 um^2.
  - The drug fields have FEWER nuclei and LARGER nuclei than the controls.
  - Every image has some pairs of TOUCHING nuclei (a plain threshold merges
    them into one object, so it undercounts).
  - Every image has a few small bright specks of DEBRIS (not nuclei).
  - Some nuclei are cut by the image border.
  - Illumination is uneven (brighter in the middle); one image,
    2026-04-02_ctrl_field04.tif, is much darker in one corner, so a single
    global threshold misses the dim nuclei there.

Needs Python 3 with numpy and Pillow. Deterministic (fixed seed). Run:
    python3 make-synthetic.py [output-folder]
It prints the true counts.
"""

import csv
import os
import shutil
import sys

import numpy as np
from PIL import Image

RNG = np.random.default_rng(20261123)
SIZE = 400
PIXEL_UM = 0.65
OUT = sys.argv[1] if len(sys.argv) > 1 else "nuclei-synthetic"


def gaussian_blur(img, sigma):
    """Gaussian blur by FFT (numpy only)."""
    n = img.shape[0]
    f = np.fft.fftfreq(n)
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (f[:, None] ** 2 + f[None, :] ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * g))


def ellipse_mask(cy, cx, ry, rx, angle, yy, xx):
    c, s = np.cos(angle), np.sin(angle)
    y, x = yy - cy, xx - cx
    u = (x * c + y * s) / rx
    v = (-x * s + y * c) / ry
    return u * u + v * v <= 1.0


def place_nuclei(n, r_mean, n_pairs):
    """Return a list of (cy, cx, ry, rx, angle). n_pairs of them touch a partner."""
    nuclei = []
    tries = 0
    while len(nuclei) < n - n_pairs and tries < 20000:
        tries += 1
        r = RNG.normal(r_mean, r_mean * 0.12)
        ry, rx = r * RNG.uniform(0.8, 1.0), r * RNG.uniform(1.0, 1.25)
        cy, cx = RNG.uniform(-5, SIZE + 5, 2)
        ok = all(np.hypot(cy - a, cx - b) > (max(ry, rx) + max(c, d)) * 1.35
                 for a, b, c, d, _ in nuclei)
        if ok:
            nuclei.append((cy, cx, ry, rx, RNG.uniform(0, np.pi)))
    # touching partners: placed just overlapping an existing interior nucleus
    k = 0
    tries = 0
    while k < n_pairs and tries < 20000:
        tries += 1
        cy0, cx0, ry0, rx0, _ = nuclei[RNG.integers(len(nuclei))]
        if not (40 < cy0 < SIZE - 40 and 40 < cx0 < SIZE - 40):
            continue
        r = RNG.normal(r_mean, r_mean * 0.12)
        ry, rx = r * RNG.uniform(0.85, 1.0), r * RNG.uniform(1.0, 1.15)
        d = (min(ry0, rx0) + min(ry, rx)) * 0.85
        ang = RNG.uniform(0, 2 * np.pi)
        cy, cx = cy0 + d * np.sin(ang), cx0 + d * np.cos(ang)
        # must not touch any third nucleus
        others = [q for q in nuclei if (q[0], q[1]) != (cy0, cx0)]
        ok = all(np.hypot(cy - a, cx - b) > (max(ry, rx) + max(c, e)) * 1.25
                 for a, b, c, e, _ in others)
        ok = ok and 15 < cy < SIZE - 15 and 15 < cx < SIZE - 15
        if ok:
            nuclei.append((cy, cx, ry, rx, RNG.uniform(0, np.pi)))
            k += 1
    return nuclei, k


def make_image(n, r_mean, n_pairs, dark_corner=False):
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(float)
    nuclei, pairs = place_nuclei(n, r_mean, n_pairs)
    signal = np.zeros((SIZE, SIZE))
    areas, border = [], 0
    for cy, cx, ry, rx, a in nuclei:
        m = ellipse_mask(cy, cx, ry, rx, a, yy, xx)
        if not m.any():
            continue
        brightness = RNG.uniform(0.65, 1.0)
        texture = 1 + 0.15 * gaussian_blur(RNG.normal(0, 1, (SIZE, SIZE)), 2)
        signal += m * brightness * texture
        areas.append(m.sum())
        if m[0, :].any() or m[-1, :].any() or m[:, 0].any() or m[:, -1].any():
            border += 1
    # debris: small bright specks
    for _ in range(RNG.integers(3, 7)):
        cy, cx = RNG.uniform(10, SIZE - 10, 2)
        signal += ellipse_mask(cy, cx, 1.8, 1.8, 0, yy, xx) * 1.4
    signal = gaussian_blur(signal, 1.5)
    # uneven illumination: brighter in the middle
    r2 = ((yy - SIZE / 2) ** 2 + (xx - SIZE / 2) ** 2) / (SIZE / 2) ** 2
    illum = 1 - 0.25 * r2
    if dark_corner:
        illum *= 1 - 0.85 * np.clip(1 - np.hypot(yy - SIZE, xx - SIZE) / (SIZE * 0.9), 0, 1)
    expected = 180 + 220 * illum + 2200 * signal * illum
    img = RNG.poisson(np.clip(expected, 0, None)) + RNG.normal(0, 12, expected.shape)
    img = np.clip(np.round(img), 0, 4095).astype(np.uint16)
    return img, len(areas), pairs, border, float(np.mean(areas)) * PIXEL_UM ** 2


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    rows = []
    plan = [("ctrl", i, RNG.integers(28, 37), 9.0) for i in range(1, 7)] + \
           [("drug", i, RNG.integers(17, 24), 12.0) for i in range(1, 7)]
    for cond, i, n, r in plan:
        name = f"2026-04-02_{cond}_field{i:02d}.tif"
        img, count, pairs, border, area = make_image(
            int(n), r, n_pairs=int(RNG.integers(2, 5)),
            dark_corner=(cond == "ctrl" and i == 4))
        Image.fromarray(img).save(os.path.join(OUT, name), compression="tiff_deflate")
        rows.append({"file": name, "condition": "control" if cond == "ctrl" else "drug",
                     "true_nuclei": count, "touching_pairs": pairs,
                     "nuclei_on_border": border, "true_mean_area_um2": round(area, 1)})
    with open(os.path.join(OUT, "imaging-notes.txt"), "w") as f:
        f.write(
            "Imaging notes (synthetic example data)\n\n"
            "Experiment: cultured cells, control or drug for 48 h, nuclei stained\n"
            "with a DNA dye. One plate, 6 random fields per condition.\n"
            "Microscope: widefield, 20x objective, camera binning 2x2.\n"
            "Pixel size: 0.65 micrometres (um) per pixel, in x and y.\n"
            "Camera: 12-bit (values 0-4095), saved as 16-bit TIFF.\n"
            "Exposure: 80 ms, same for all fields.\n"
            "Note: field ctrl_04 was taken near the well edge.\n")
    with open(OUT.rstrip("/\\") + "-answer-key.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    for c in ("control", "drug"):
        sel = [r for r in rows if r["condition"] == c]
        print(c, "total nuclei", sum(r["true_nuclei"] for r in sel),
              "mean per image", round(np.mean([r["true_nuclei"] for r in sel]), 1),
              "mean area", round(np.mean([r["true_mean_area_um2"] for r in sel]), 1))


if __name__ == "__main__":
    main()
