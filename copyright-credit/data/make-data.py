#!/usr/bin/env python3
"""
make-data.py: example folder for the unit "Copyright, memorisation and credit".

Creates pre-publication/ and pre-publication.zip: a small, made-up course page
project that someone is about to publish. It contains deliberate problems for
the pre-publication check in the exercise (the key is in exercise.qmd):

  page.md                    course page draft; one paragraph is copied word
                             for word from Wikipedia (see below) without credit;
                             a 1913 paper is cited without a reference
  fit_mm.py                  a script the agent wrote; it carries another
                             (invented) lab's GPL copyright header
  figures/fig1-rates.png     made by the script from synthetic data: fine
  figures/fig2-redrawn.png   "redrawn from a published figure": no credit yet
  figures/enzyme-cartoon.png source unknown ("found it online")
  README.md                  goal, planned licences, a Log of AI use with gaps
  NOTES.md                   the author's own notes on where things came from

Third-party text: the two sentences in page.md marked in the key are from the
English Wikipedia article "Michaelis-Menten kinetics"
(https://en.wikipedia.org/wiki/Michaelis%E2%80%93Menten_kinetics), licensed
CC BY-SA 4.0. They are included here, with this attribution, as an example of
material that needs credit. Everything else is invented for the course. The
"Example Enzyme Lab" and "Lindqvist et al. 2019" do not exist.

Needs Python 3 with matplotlib and numpy. Run from anywhere:
    python3 make-data.py
"""

import shutil
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "pre-publication"

PAGE = """\
# Week 3: Enzyme kinetics

*Course page draft for BIO-203, Biochemistry for engineers. Not yet published.*

## Why rates matter

Every enzyme assay in this course ends with a curve: reaction rate against
substrate concentration. This week you learn to read that curve and to fit
the two numbers that describe it, Vmax and Km.

## The model

In biochemistry, Michaelis–Menten kinetics, named after Leonor Michaelis and
Maud Menten, is the simplest case of enzyme kinetics, applied to
enzyme-catalysed reactions involving the transformation of one substrate into
one product. In 1913, Michaelis and Menten expanded on Victor Henri's
fundamental equation of enzyme kinetics, which was established in 1902.

The rate v depends on the substrate concentration S as
v = Vmax * S / (Km + S). At low S the rate rises almost in proportion to S; at
high S it levels off at Vmax. Km is the concentration at which the rate is half
of Vmax, as Michaelis and Menten (1913) showed for invertase.

## This week's data

Figure 1 shows rates measured by last year's lab groups (synthetic data for
this page). The script `fit_mm.py` fits the curve and prints Vmax and Km.

![Figure 1: rate against substrate concentration with the fitted curve](figures/fig1-rates.png)

Figure 2 shows the same kind of data as a double-reciprocal plot, which is
how the constants were estimated before computers.

![Figure 2](figures/fig2-redrawn.png)

![](figures/enzyme-cartoon.png)

## Exercises

1. Read Vmax and Km off Figure 1 by eye. Compare with the fitted values.
2. Why does the double-reciprocal plot exaggerate errors at low S?
"""

SCRIPT = '''\
# fit_mm.py - fit the Michaelis-Menten model to rate data
#
# Copyright (C) 2018 Example Enzyme Lab, University of Nowhere
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

import numpy as np
from scipy.optimize import curve_fit


def michaelis_menten(s, vmax, km):
    return vmax * s / (km + s)


def fit(s, v):
    """Return (vmax, km) fitted by non-linear least squares."""
    (vmax, km), _ = curve_fit(michaelis_menten, s, v, p0=[max(v), np.median(s)])
    return vmax, km


if __name__ == "__main__":
    data = np.loadtxt("rates.csv", delimiter=",", skiprows=1)
    vmax, km = fit(data[:, 0], data[:, 1])
    print(f"Vmax = {vmax:.2f} umol/min, Km = {km:.2f} mM")
'''

README = """\
# Enzyme kinetics course page (BIO-203, week 3)

## Goal
A public course page for week 3, with one figure, a fitting script and two
exercises. To be published on the course website next week.

## Licences I plan to use
- Text and figures: CC BY 4.0
- Code: MIT

## Log of AI use
- 2026-10-02, Claude Code (Pro): wrote fit_mm.py and made figures/fig1-rates.png
  from the synthetic data. I checked the fit against a hand calculation.
- 2026-10-03, Claude Code (Pro): redrew figure 2 from the PDF of the paper.
"""

NOTES = """\
# My notes (not for the page)

- Section "The model": the agent drafted it, I edited a bit. Check wording?
- Figure 2: asked the agent to redraw Fig. 3 of Lindqvist et al. 2019
  (journal article, not open access) with our own colours.
- Enzyme cartoon: found it online last year for my slides, can't remember
  where. Looks nice.
- Remember to cite Michaelis & Menten properly.
"""


def figures(dirpath):
    dirpath.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(3)
    s = np.array([0.5, 1, 2, 4, 8, 16, 32])
    v = 12 * s / (3 + s) * (1 + rng.normal(0, 0.05, s.size))
    np.savetxt(OUT / "rates.csv", np.column_stack([s, v]), delimiter=",",
               header="substrate_mM,rate_umol_per_min", comments="", fmt="%.3f")
    grid = np.linspace(0, 34, 200)

    fig, ax = plt.subplots(figsize=(5, 3.4), dpi=110)
    ax.plot(s, v, "o", color="#2a7f8f")
    ax.plot(grid, 12 * grid / (3 + grid), color="#6b4fa0")
    ax.set_xlabel("Substrate (mM)")
    ax.set_ylabel("Rate (µmol/min)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(dirpath / "fig1-rates.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.4), dpi=110)
    ax.plot(1 / s, 1 / v, "s", color="#a8324a")
    xs = np.linspace(-0.4, 2.1, 50)
    ax.plot(xs, (3 / 12) * xs + 1 / 12, color="#333333")
    ax.axhline(0, color="#999999", lw=0.8)
    ax.axvline(0, color="#999999", lw=0.8)
    ax.set_xlabel("1 / [S]")
    ax.set_ylabel("1 / v")
    ax.set_title("Double-reciprocal plot", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(dirpath / "fig2-redrawn.png")
    plt.close(fig)

    # a simple "clip-art" enzyme and substrate: stands in for an image of
    # unknown origin
    fig, ax = plt.subplots(figsize=(3, 2.2), dpi=110)
    ax.add_patch(plt.Circle((0.42, 0.5), 0.32, color="#8a6a12"))
    ax.add_patch(plt.Circle((0.70, 0.62), 0.10, color="white"))
    ax.add_patch(plt.Circle((0.86, 0.66), 0.08, color="#2a7f8f"))
    ax.text(0.42, 0.08, "enzyme + substrate", ha="center", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(dirpath / "enzyme-cartoon.png")
    plt.close(fig)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "page.md").write_text(PAGE, encoding="utf-8")
    (OUT / "fit_mm.py").write_text(SCRIPT, encoding="utf-8")
    (OUT / "README.md").write_text(README, encoding="utf-8")
    (OUT / "NOTES.md").write_text(NOTES, encoding="utf-8")
    figures(OUT / "figures")
    zpath = HERE / "pre-publication.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(HERE))
    print("wrote", OUT.name, "and", zpath.name)
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            print("  ", f.relative_to(HERE))


if __name__ == "__main__":
    main()
