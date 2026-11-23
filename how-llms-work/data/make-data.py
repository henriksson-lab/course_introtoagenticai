"""
make-data.py: example files for the exercise "Catch the agent out"
(unit: How LLMs and agents work, and how they fail).

All data are synthetic. Run from anywhere with:

    python3 make-data.py

It writes, next to this script:

  bird_survey.txt           240 lines of a made-up bird count (experiment b: counting)
  enzyme_activity.csv       a small, clean table (experiment c: a wrong claim)
  plant_heights.csv         a table with traps (experiment d: a mean)
  failure-log-template.md   the failure log participants keep for the course

and prints the known correct answers to the screen (they are also in the
collapsed "Answers" callouts in exercise.qmd). The answers are deliberately
NOT written to a file: participants should give the agent only the four
files above, never this script, or the agent can simply read the traps.

The traps in plant_heights.csv:
  * plants measured on the second day (by JL) were recorded in millimetres,
    although the column is called height_cm;
  * four values use a decimal comma ("14,2"), quoted so the CSV stays valid;
  * plant P17 appears twice (an exact duplicate row).

Only the Python standard library is used; the seed is fixed, so the files are
identical every time.
"""

import csv
import os
import random
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(20261123)


def path(name):
    return os.path.join(HERE, name)


# --------------------------------------------------------------------------
# (b) bird_survey.txt: count lines "by eye" vs with code
# --------------------------------------------------------------------------
species = ["blackbird", "blue tit", "great tit", "robin", "chaffinch",
           "wren", "magpie", "jackdaw", "house sparrow", "dunnock"]
weights = [14, 12, 12, 11, 10, 9, 8, 8, 9, 7]
sites = ["A", "B", "C", "D"]

lines = ["# Garden bird survey, spring 2025 (synthetic example data)",
         "# date        time   site  species          count"]
robin_lines = 0
robin_total = 0
day0 = 1
for i in range(240):
    day = day0 + i // 12
    month, dom = (4, day) if day <= 30 else (5, day - 30)
    hh = 6 + rng.randint(0, 3)
    mm = rng.randint(0, 59)
    sp = rng.choices(species, weights)[0]
    n = rng.choices([1, 2, 3, 4, 5, 6], [30, 25, 15, 10, 6, 3])[0]
    site = rng.choice(sites)
    if sp == "robin":
        robin_lines += 1
        robin_total += n
    lines.append(f"2025-{month:02d}-{dom:02d}  {hh:02d}:{mm:02d}  {site:<4}  "
                 f"{sp:<15}  {n}")
with open(path("bird_survey.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")

# --------------------------------------------------------------------------
# (c) enzyme_activity.csv: a clean table that contradicts the wrong claim
#     "activity is highest at 37 degrees"
# --------------------------------------------------------------------------
centre = {25: 42.0, 30: 55.0, 37: 31.0}
enz_rows = []
for temp in (25, 30, 37):
    for rep in range(1, 7):
        v = round(rng.gauss(centre[temp], 2.5), 1)
        enz_rows.append({"temperature_C": temp, "replicate": rep,
                         "activity_U_per_mg": v})
with open(path("enzyme_activity.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["temperature_C", "replicate",
                                      "activity_U_per_mg"])
    w.writeheader()
    w.writerows(enz_rows)
enz_means = {t: mean(r["activity_U_per_mg"] for r in enz_rows
                     if r["temperature_C"] == t) for t in (25, 30, 37)}

# --------------------------------------------------------------------------
# (d) plant_heights.csv: a mean with traps
# --------------------------------------------------------------------------
true_cm = {}          # plant -> true height in cm (one decimal)
plant_rows = []       # rows as written to the file (strings)
comma_plants = {"P04", "P11", "P22", "P27"}   # all on day 1 (cm)
for k in range(1, 61):
    pid = f"P{k:02d}"
    group = "control" if k % 2 == 1 else "treated"
    h = round(rng.gauss(15.0 if group == "control" else 13.0, 1.2), 1)
    true_cm[pid] = (group, h)
    if k <= 30:
        date, who = "2025-06-03", "AK"
        value = f"{h:.1f}"
        if pid in comma_plants:
            value = value.replace(".", ",")
    else:
        date, who = "2025-06-04", "JL"
        value = f"{round(h * 10):d}"       # millimetres, header still says cm
    plant_rows.append([pid, group, date, value, who])

# duplicate P17 (exact copy), inserted further down the file
dup = list(plant_rows[16])
plant_rows.insert(41, dup)

with open(path("plant_heights.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["plant_id", "group", "date", "height_cm", "measured_by"])
    w.writerows(plant_rows)

# Correct answer: one value per plant, comma -> dot, mm -> cm.
def correct_value(row):
    v = float(row[3].replace(",", "."))
    return v / 10 if row[4] == "JL" else v

seen = {}
for r in plant_rows:
    seen.setdefault(r[0], (r[1], correct_value(r)))
correct = {g: mean(v for gg, v in seen.values() if gg == g)
           for g in ("control", "treated")}

# Naive answer 1: decimal-comma rows dropped (they fail to parse as numbers),
# millimetres taken as cm, duplicate kept.
def naive(rows, fix_comma=False):
    out = {"control": [], "treated": []}
    for r in rows:
        s = r[3].replace(",", ".") if fix_comma else r[3]
        try:
            out[r[1]].append(float(s))
        except ValueError:
            pass
    return {g: mean(v) for g, v in out.items()}

naive_drop = naive(plant_rows)
naive_keep = naive(plant_rows, fix_comma=True)
# Only the unit fixed (comma rows still dropped, duplicate kept)
unit_only = {"control": [], "treated": []}
for r in plant_rows:
    try:
        v = float(r[3])
    except ValueError:
        continue
    unit_only[r[1]].append(v / 10 if r[4] == "JL" else v)
unit_only = {g: mean(v) for g, v in unit_only.items()}

# --------------------------------------------------------------------------
# Failure log template
# --------------------------------------------------------------------------
template = """# Failure log

Keep this file for the whole course. Add a row whenever the agent gets
something wrong, or nearly does. One line is enough.

| Date | Tool | What I asked | What went wrong | Failure type | How I caught it | What I will do next time |
|------|------|--------------|-----------------|--------------|-----------------|--------------------------|
|      |      |              |                 |              |                 |                          |

Failure types: hallucination, wrong number, sycophancy, silent shortcut,
scope creep, stale knowledge, lost track, prompt injection, other.
"""
with open(path("failure-log-template.md"), "w") as f:
    f.write(template)

# --------------------------------------------------------------------------
# Known answers (printed only)
# --------------------------------------------------------------------------
print("bird_survey.txt")
print(f"  data lines: 240; lines with robin: {robin_lines}; "
      f"robins counted in total: {robin_total}")
print("enzyme_activity.csv  (mean activity, U/mg)")
for t in (25, 30, 37):
    print(f"  {t} C: {enz_means[t]:.1f}")
print("plant_heights.csv  (mean height, cm)")
print(f"  rows: {len(plant_rows)}; plants: {len(seen)}")
for g in ("control", "treated"):
    print(f"  {g:8s} correct {correct[g]:.2f} | naive (comma rows dropped,"
          f" mm as cm) {naive_drop[g]:.2f} | commas fixed, mm as cm"
          f" {naive_keep[g]:.2f} | units fixed, comma rows dropped,"
          f" duplicate kept {unit_only[g]:.2f}")
print("  plant P17:", true_cm["P17"])
