"""make-data.py : builds the SYNTHETIC practice project for the exercise of
"Git as undo button and lab notebook" (Introduction to agentic AI).

Run from this folder:  python3 make-data.py
Writes the folder plate-growth/ and the zip file plate-growth.zip.
Everything is invented: plates, readings and the "secret" key in .env
(which is a harmless dummy string, there to practise .gitignore).
Uses only the Python standard library; random.seed() makes it repeatable.
"""
import csv
import os
import random
import shutil
import zipfile

random.seed(42)
root = "plate-growth"
shutil.rmtree(root, ignore_errors=True)
os.makedirs(f"{root}/data/raw")
os.makedirs(f"{root}/results")
os.makedirs(f"{root}/notes")

# 12 plates, 3 conditions, 4 plates each;
# optical density read at 0, 2, 4, 6, 8 hours.
conditions = {"control": 0.12, "glucose": 0.18, "salt": 0.07}
rows = []
plate = 0
for cond, rate in conditions.items():
    for _ in range(4):
        plate += 1
        od = 0.05
        for hour in range(0, 10, 2):
            value = od * (1 + rate) ** (hour * 3) + random.gauss(0, 0.004)
            rows.append([f"P{plate:02d}", cond, hour, round(value, 3)])
# plate 7 is contaminated: much higher readings, flagged in the notes
for r in rows:
    if r[0] == "P07":
        r[3] = round(r[3] * 1.8, 3)
with open(f"{root}/data/raw/plates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["plate", "condition", "hour", "od600"])
    w.writerows(rows)

with open(f"{root}/notes/2026-11-20.md", "w") as f:
    f.write("# Lab notes 2026-11-20\n\n"
            "- Plate P07 (glucose) looked cloudy at 4 h: probably contaminated.\n"
            "  Exclude it from the analysis.\n")

with open(f"{root}/README.md", "w") as f:
    f.write("# Plate growth (practice project)\n\n"
            "Synthetic practice data for the git exercise.\n\n"
            "- `data/raw/plates.csv`: optical density (OD600) of 12 plates,\n"
            "  3 conditions (control, glucose, salt), read every 2 hours.\n"
            "  Raw data: never edit.\n"
            "- `clean.py`: removes excluded plates and writes\n"
            "  `results/summary.csv` with the mean OD600 at 8 h per condition.\n"
            "- `notes/`: lab notes.\n\n"
            "Run: `python3 clean.py` (or `python clean.py` on Windows).\n")

with open(f"{root}/clean.py", "w") as f:
    f.write('''"""Remove excluded plates and summarise OD600 at 8 h per condition."""
import csv
from statistics import mean

EXCLUDE = {"P07"}          # contaminated, see notes/2026-11-20.md
FINAL_HOUR = 8

with open("data/raw/plates.csv", newline="") as f:
    rows = [r for r in csv.DictReader(f) if r["plate"] not in EXCLUDE]

by_condition = {}
for r in rows:
    if int(r["hour"]) == FINAL_HOUR:
        by_condition.setdefault(r["condition"], []).append(float(r["od600"]))

with open("results/summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["condition", "n_plates", "mean_od600_8h"])
    for cond in sorted(by_condition):
        values = by_condition[cond]
        w.writerow([cond, len(values), round(mean(values), 3)])
print("Wrote results/summary.csv")
''')

with open(f"{root}/.env", "w") as f:
    f.write("# Pretend secret for practising .gitignore. Not a real key.\n"
            "PLATE_READER_API_KEY=dummy-0000-not-a-real-key\n")

# run the script once so results/summary.csv exists
cwd = os.getcwd()
os.chdir(root)
exec(open("clean.py").read())
os.chdir(cwd)

with zipfile.ZipFile("plate-growth.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for dirpath, _, files in os.walk(root):
        for name in sorted(files):
            z.write(os.path.join(dirpath, name))
print("Wrote plate-growth/ and plate-growth.zip")
