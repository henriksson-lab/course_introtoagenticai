"""plot_lake.py : one possible reference solution for the Python variant in
"Reproducible figures". Your agent's script will look different; compare the
FIGURE and the numbers, not the code.

Usage:  python plot_lake.py [input.csv] [output-name]
  defaults: ../lake-temperature.csv  lake_figure
Writes <output-name>.pdf, .svg and .png (300 dpi), 180 mm wide (a typical
double journal column). Uses only the standard library and matplotlib.
"""
import csv
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

infile = sys.argv[1] if len(sys.argv) > 1 else "../lake-temperature.csv"
out = sys.argv[2] if len(sys.argv) > 2 else "lake_figure"

series = {}
with open(infile, newline="") as f:
    for row in csv.DictReader(f):
        d = date.fromisoformat(row["date"])
        t = float(row["temp_c"]) if row["temp_c"] else float("nan")  # gaps stay gaps
        series.setdefault(float(row["depth_m"]), []).append((d, t))

colours = {1.0: "#E69F00", 5.0: "#009E73", 15.0: "#0072B2"}   # Okabe-Ito
plt.rcParams.update({"font.size": 8, "font.family": "sans-serif"})
mm = 1 / 25.4
fig, ax = plt.subplots(figsize=(180 * mm, 70 * mm))
for depth in sorted(series):
    days, temps = zip(*sorted(series[depth]))
    ax.plot(days, temps, lw=1, color=colours.get(depth), label=f"{depth:g} m")
    print(f"{depth:g} m: {len(temps)} days, max {max(t for t in temps if t == t):.2f} °C")
ax.set_ylabel("Water temperature (°C)")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.spines[["top", "right"]].set_visible(False)
ax.legend(title="Depth", frameon=False, loc="upper left")
fig.tight_layout()
for ext in ("pdf", "svg", "png"):
    fig.savefig(f"{out}.{ext}", dpi=300)
