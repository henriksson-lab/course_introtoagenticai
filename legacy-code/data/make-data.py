"""
make-data.py: example files for the exercise in the unit
"Reading other people's code" (Part 5: Scaling up).

All data are synthetic. Run from anywhere with:

    python3 make-data.py

It writes, into growth-legacy/ next to this script:

  plate_0312.csv   plate-reader growth curves, 24 wells, read every 15 min
  plate_0409.csv   a second plate, read every 10 min (new data for the port)

The MATLAB files in growth-legacy/ (gr_calc.m, blcorr.m, mvavg.m, fitwin.m,
README.txt) are written by hand to look like a former PhD student's code.
The reference output gr_out_0312.txt was produced by running the unchanged
gr_calc.m on plate_0312.csv in GNU Octave (see make-reference.sh); it stands
in for "the output the student saved".

Plate layout (4 rows x 6 columns, wells A1..D6, row by row):
  column 1 (A1, B1, C1, D1)  blanks (medium only)
  columns 2..6               strains WT, dA, dB, dC, dAB; rows = replicates

The traps, for the teacher (do NOT give this file to the agent):
  * BUG: gr_calc.m lists the blanks as wells [1 7 13], i.e. A1, B1, C1.
    D1 (well 19) is left out: it is not used for the blank and is "analysed"
    as a sample (row D1 with NaN in the output). D1 reads a little higher
    than the other blanks, so the blank is underestimated by about 0.004 OD
    and every growth rate shifts slightly.
  * ASSUMPTION: gr_calc.m ignores the time column and assumes one reading
    every 15 minutes. plate_0409.csv is read every 10 minutes, so the
    original script would silently give growth rates that are 1.5x too low
    on it.
  * Magic numbers: 0.02 / 0.2 OD thresholds for the exponential phase,
    0.001 floor, 3-point smoothing, 0.6931 = ln 2, fname(7:10) for the date.

Uses numpy; the seed is fixed, so the files are identical every time.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "growth-legacy")
os.makedirs(OUT, exist_ok=True)

WELLS = [f"{r}{c}" for r in "ABCD" for c in range(1, 7)]
STRAINS = {  # true growth rate (1/h), lag (h)
    "WT": (0.62, 1.6), "dA": (0.55, 1.8), "dB": (0.63, 2.4),
    "dC": (0.41, 1.7), "dAB": (0.34, 2.2)}
STRAIN_ORDER = ["WT", "dA", "dB", "dC", "dAB"]


def curve(t, mu, lag, n0, k):
    te = np.maximum(0.0, t - lag)
    e = np.exp(mu * te)
    return n0 * e / (1 + n0 / k * (e - 1))


def make_plate(path, step_min, hours, seed, blanks):
    rng = np.random.default_rng(seed)
    t_min = np.arange(0, hours * 60 + 1, step_min)
    t = t_min / 60.0
    cols = []
    for w in WELLS:
        row, col = "ABCD".index(w[0]), int(w[1:])
        if col == 1:
            base = blanks[row]
            y = base + rng.normal(0, 0.0015, t.size)
        else:
            mu, lag = STRAINS[STRAIN_ORDER[col - 2]]
            mu *= rng.normal(1, 0.04)
            lag *= rng.normal(1, 0.08)
            n0 = 0.010 * rng.normal(1, 0.1)
            k = 1.05 * rng.normal(1, 0.05)
            # slow drift of the background over the run (evaporation)
            base = 0.090 + 0.002 * t / hours
            y = base + curve(t, mu, lag, n0, k) + rng.normal(0, 0.002, t.size)
        cols.append(np.round(y, 4))
    with open(path, "w") as f:
        f.write("Time [min]," + ",".join(WELLS) + "\n")
        for i, tm in enumerate(t_min):
            f.write(f"{int(tm)}," + ",".join(f"{c[i]:.4f}" for c in cols) + "\n")


# D1 reads higher than the other blanks (a slightly scratched well)
make_plate(os.path.join(OUT, "plate_0312.csv"), 15, 14, 312,
           blanks=[0.089, 0.091, 0.090, 0.106])
make_plate(os.path.join(OUT, "plate_0409.csv"), 10, 14, 409,
           blanks=[0.090, 0.088, 0.091, 0.104])
print("wrote", os.listdir(OUT))

