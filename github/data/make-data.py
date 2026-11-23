# make-data.py: builds plant-growth.zip for the exercise of the unit "GitHub".
#
# The zip holds a small, entirely SYNTHETIC project folder "plant-growth":
# a greenhouse trial with three fertiliser treatments, 8 plants each,
# heights measured weekly for 6 weeks. The project is deliberately imperfect.
# Six problems are planted for the agent review in the exercise:
#   1. README says to run scripts/make_figure.py; the script is scripts/plot_growth.py
#   2. the script reads an absolute path on someone else's laptop
#   3. the data column is called "ht", the README's data dictionary says "height_cm"
#   4. AGENTS.md says results go in output/; the folder is results/
#   5. there is no licence
#   6. notes/contacts.txt holds names, e-mails and phone numbers of field
#      assistants (invented), which should not be in a shared repository
# All names, e-mail addresses and phone numbers are invented.
#
# Run:  python3 make-data.py   (needs numpy and matplotlib)
# Output: plant-growth.zip next to this script (no git history inside).

import csv
import io
import os
import zipfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261123)

# ---- data -----------------------------------------------------------------
treatments = {"control": 1.6, "low_N": 2.1, "high_N": 2.6}   # cm per week
rows = []
for t, (name, rate) in enumerate(treatments.items()):
    for p in range(1, 9):
        pid = f"{name[0].upper()}{p:02d}" if name == "control" else f"{'L' if name == 'low_N' else 'H'}{p:02d}"
        h = 4.0 + rng.normal(0, 0.4)
        prate = rate + rng.normal(0, 0.25)
        for week in range(0, 7):
            if week > 0:
                h += max(0.1, prate + rng.normal(0, 0.3))
            rows.append((pid, name, week, round(h, 1)))

csv_buf = io.StringIO()
w = csv.writer(csv_buf, lineterminator="\n")
w.writerow(["plant_id", "treatment", "week", "ht"])
w.writerows(rows)

# ---- figure (what the script would make) ------------------------------------
fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
colours = {"control": "#888888", "low_N": "#2a7f8f", "high_N": "#6b4fa0"}
for name in treatments:
    weeks = range(0, 7)
    means = [np.mean([r[3] for r in rows if r[1] == name and r[2] == wk]) for wk in weeks]
    ax.plot(list(weeks), means, marker="o", color=colours[name], label=name)
ax.set_xlabel("Week")
ax.set_ylabel("Mean height (cm)")
ax.set_title("Plant height by treatment (n = 8 per group)")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
png_buf = io.BytesIO()
fig.savefig(png_buf, format="png")
plt.close(fig)

# ---- text files ----------------------------------------------------------------
readme = """# Plant growth under three fertiliser levels

A small greenhouse trial (spring 2026). Does nitrogen fertiliser change how
fast young bean plants grow?

## Data

`data/raw/growth.csv`: one row per plant per week.

| Column | Meaning |
|---|---|
| plant_id | C01-C08 control, L01-L08 low N, H01-H08 high N |
| treatment | control, low_N or high_N |
| week | 0 to 6 |
| height_cm | plant height in cm, soil surface to top leaf |

## How to make the figure

Run `python scripts/make_figure.py`. The figure is saved in `results/`.

## Results

Mean height per treatment and week: `results/growth_plot.png`.
"""

agents = """# Notes for the coding agent

- Raw data is in data/raw/. Never change it.
- Scripts go in scripts/.
- Figures and tables go in output/.
- Use Python with matplotlib only.
"""

script = '''# plot_growth.py: mean plant height per treatment and week
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = "C:/Users/anna.k/Desktop/greenhouse/growth.csv"

heights = defaultdict(list)
with open(DATA) as f:
    for row in csv.DictReader(f):
        heights[(row["treatment"], int(row["week"]))].append(float(row["ht"]))

fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
for name, colour in [("control", "#888888"), ("low_N", "#2a7f8f"), ("high_N", "#6b4fa0")]:
    weeks = sorted(w for (t, w) in heights if t == name)
    means = [sum(heights[(name, w)]) / len(heights[(name, w)]) for w in weeks]
    ax.plot(weeks, means, marker="o", color=colour, label=name)
ax.set_xlabel("Week")
ax.set_ylabel("Mean height (cm)")
ax.set_title("Plant height by treatment (n = 8 per group)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("results/growth_plot.png")
'''

contacts = """Field assistants, spring 2026 (for the watering rota)

Lina Westerberg   lina.westerberg@example.org   070-000 12 34
Jonas Akhtar      jonas.akhtar@example.org      070-000 56 78
Emma Lindqvist    emma.lindqvist@example.org    070-000 90 12
"""

notes = """2026-03-02  Sowed 24 bean plants, 8 per treatment.
2026-03-09  Week 1 measured. H05 leaning, staked.
2026-03-30  Week 4: L03 lost top leaf to a snail; height still measured to top.
2026-04-13  Week 6, last measurement. Trial ended.
"""

files = {
    "plant-growth/README.md": readme,
    "plant-growth/AGENTS.md": agents,
    "plant-growth/data/raw/growth.csv": csv_buf.getvalue(),
    "plant-growth/scripts/plot_growth.py": script,
    "plant-growth/notes/lab-notes.txt": notes,
    "plant-growth/notes/contacts.txt": contacts,
}

out = os.path.join(HERE, "plant-growth.zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name, text in files.items():
        z.writestr(name, text)
    z.writestr("plant-growth/results/growth_plot.png", png_buf.getvalue())
print("wrote", out, os.path.getsize(out), "bytes;", len(rows), "data rows")
