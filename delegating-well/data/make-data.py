#!/usr/bin/env python3
"""
make-data.py: example data for the unit "Delegating well".

Creates reaction-times.csv: a synthetic teaching-lab experiment in which
12 students (codes P01-P12, no real people) measured their own reaction time
to a signal on screen under three conditions (quiet, music, notification),
five trials per condition. 180 rows.

Three deliberate traps, so that a weak prompt and a strong brief give visibly
different results:
  1. P07 typed all 15 values in seconds (0.312) instead of milliseconds.
  2. P03, notification, trial 2: 92 ms with the note "pressed before signal"
     (an anticipation, which should be excluded).
  3. P10, music, trial 4: no value, note "equipment glitch".

The script is deterministic (fixed seed). At the end it prints the expected
answers that exercise.qmd quotes. If you change the data, update
exercise.qmd to match.

Needs only the Python 3 standard library. Run from anywhere:

    python3 make-data.py
"""

import csv
import os
import random
import statistics

random.seed(20261123)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "reaction-times.csv")

conditions = ["quiet", "music", "notification"]
shift = {"quiet": 0, "music": 18, "notification": 62}

rows = []
for p in range(1, 13):
    pid = f"P{p:02d}"
    base = random.gauss(305, 28)
    for cond in conditions:
        for trial in range(1, 6):
            rt = round(base + shift[cond] + random.gauss(0, 24))
            note = ""
            value = str(rt)
            if pid == "P07":
                value = f"{rt / 1000:.3f}"
            if pid == "P03" and cond == "notification" and trial == 2:
                value, note = "92", "pressed before signal"
            if pid == "P10" and cond == "music" and trial == 4:
                value, note = "", "equipment glitch"
            rows.append([pid, cond, trial, value, note])

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["participant", "condition", "trial", "rt_ms", "note"])
    w.writerows(rows)

# ---- expected answers ------------------------------------------------------
clean = []
for pid, cond, trial, value, note in rows:
    if value == "" or note == "pressed before signal":
        continue
    v = float(value)
    if pid == "P07":
        v *= 1000
    clean.append((pid, cond, v))

print(f"wrote {OUT}: {len(rows)} rows")
print(f"kept after cleaning: {len(clean)} rows")
pmeans = {}
for pid in sorted({r[0] for r in clean}):
    for cond in conditions:
        vals = [v for p, c, v in clean if p == pid and c == cond]
        pmeans[(pid, cond)] = statistics.mean(vals)
for cond in conditions:
    m = statistics.mean(pmeans[(p, cond)] for p, c in pmeans if c == cond)
    print(f"group mean of participant means, {cond}: {m:.1f} ms")
slower = sum(
    1 for p in {k[0] for k in pmeans}
    if pmeans[(p, "notification")] > pmeans[(p, "quiet")]
)
print(f"participants slower with notification than quiet: {slower} of 12")
print("P07 means (ms):", {c: round(pmeans[("P07", c)]) for c in conditions})
# what a careless analysis gets: P07 left in seconds, anticipation kept
naive = []
for pid, cond, trial, value, note in rows:
    if value == "":
        continue
    naive.append((cond, float(value)))
for cond in conditions:
    vals = [v for c, v in naive if c == cond]
    print(f"naive mean of all rows, {cond}: {statistics.mean(vals):.1f}")
print("min/max raw value:", min(v for c, v in naive), max(v for c, v in naive))
