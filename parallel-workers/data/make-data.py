# make-data.py: generates the synthetic example data for the unit
# "Parallel workers: Claude and Codex" (Introduction to agentic AI).
#
# Output (written next to this script):
#   lakes.csv               raw monitoring data with deliberate traps
#   lake-summary-answer.csv answer key: one row per lake and year
#
# Everything is invented: four fictional lakes, monthly samples May-October
# in 2023 and 2024 (48 real samples). The traps, which the two agents may
# handle differently, are:
#   1. 3 exact duplicate rows                         -> 51 rows in the file
#   2. "Lilla Sjön" spelled four ways
#   3. temp_c = -999 (sensor failure) in 2 rows       -> missing, not a number
#   4. nitrate_unit "ug/L" in 3 rows (value x1000)    -> convert to mg/L
#   5. tot_p_ug_l "<5" (below detection limit) in 4 rows, all Tallträsk
# The answer key uses: duplicates removed, names merged, -999 as missing,
# ug/L converted. For "<5" it gives three columns, one per common convention
# (half the detection limit, treat as missing, use the limit itself).
#
# Run:  python3 make-data.py   (needs only the Python standard library)

import csv
import random
from pathlib import Path

random.seed(20261123)
here = Path(__file__).parent

lakes = {
    # name: (temp offset, nitrate mean mg/L, tot-P mean ug/L)
    "Björksjön": (0.8, 0.95, 28.0),
    "Lilla Sjön": (1.5, 1.60, 45.0),
    "Mörtsjön": (0.0, 0.55, 15.0),
    "Tallträsk": (-1.8, 0.22, 7.0),
}
months = [5, 6, 7, 8, 9, 10]
season_temp = {5: 9.5, 6: 15.0, 7: 19.0, 8: 18.0, 9: 13.0, 10: 7.5}
samplers = ["AK", "JL", "MS"]

rows = []
for year in (2023, 2024):
    for lake, (toff, nit, tp) in lakes.items():
        for m in months:
            day = random.randint(3, 25)
            temp = round(season_temp[m] + toff + random.gauss(0, 0.8), 1)
            # nitrate lower in summer (uptake), a little higher in 2024
            nfac = {5: 1.25, 6: 1.0, 7: 0.8, 8: 0.75, 9: 0.95, 10: 1.2}[m]
            nitrate = round(nit * nfac * (1.08 if year == 2024 else 1.0)
                            * random.uniform(0.9, 1.1), 2)
            totp = round(tp * random.uniform(0.75, 1.3), 0)
            rows.append({
                "lake": lake,
                "date": f"{year}-{m:02d}-{day:02d}",
                "depth_m": 0.5,
                "temp_c": temp,
                "nitrate": nitrate,
                "nitrate_unit": "mg/L",
                "tot_p_ug_l": int(totp),
                "sampler": random.choice(samplers),
            })

# Trap 5: four Tallträsk phosphorus values below the detection limit (5 ug/L).
for r in rows:
    if r["lake"] == "Tallträsk" and r["date"][:7] in ("2023-07", "2023-08", "2024-07", "2024-08"):
        r["tot_p_ug_l"] = "<5"

# Trap 3: two failed temperature readings.
for r in rows:
    if (r["lake"], r["date"][:7]) in (("Mörtsjön", "2023-09"), ("Björksjön", "2024-06")):
        r["temp_c"] = -999

# Trap 4: three nitrate values reported in ug/L by another lab.
for r in rows:
    if (r["lake"], r["date"][:7]) in (("Björksjön", "2023-10"), ("Lilla Sjön", "2024-05"),
                                      ("Mörtsjön", "2024-09")):
        r["nitrate"] = int(round(r["nitrate"] * 1000))
        r["nitrate_unit"] = "ug/L"

# ---- answer key, computed from the clean rows before names are messed up ----
def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")

key = []
for lake in lakes:
    for year in (2023, 2024):
        sel = [r for r in rows if r["lake"] == lake and r["date"].startswith(str(year))]
        temps = [r["temp_c"] for r in sel if r["temp_c"] != -999]
        nit = [r["nitrate"] / 1000 if r["nitrate_unit"] == "ug/L" else r["nitrate"] for r in sel]
        p_half = [2.5 if r["tot_p_ug_l"] == "<5" else r["tot_p_ug_l"] for r in sel]
        p_na = [r["tot_p_ug_l"] for r in sel if r["tot_p_ug_l"] != "<5"]
        p_lim = [5 if r["tot_p_ug_l"] == "<5" else r["tot_p_ug_l"] for r in sel]
        key.append({
            "lake": lake, "year": year, "n_samples": len(sel),
            "mean_temp_c": f"{mean(temps):.2f}",
            "mean_nitrate_mg_l": f"{mean(nit):.3f}",
            "mean_tot_p_half_dl": f"{mean(p_half):.2f}",
            "mean_tot_p_missing": f"{mean(p_na):.2f}",
            "mean_tot_p_at_dl": f"{mean(p_lim):.2f}",
        })

# Trap 2: Lilla Sjön spelled four ways (only in the raw file).
variants = ["Lilla sjön", "Lilla Sjon", "lilla sjön "]
k = 0
for r in rows:
    if r["lake"] == "Lilla Sjön" and r["date"][5:7] in ("06", "09"):
        r["lake"] = variants[k % 3]
        k += 1

# Trap 1: three exact duplicates (data pasted twice), placed right after the original.
dup_keys = [("Björksjön", "2023-06"), ("Mörtsjön", "2024-07"), ("Tallträsk", "2023-09")]
out = []
for r in rows:
    out.append(r)
    if (r["lake"], r["date"][:7]) in dup_keys:
        out.append(dict(r))

# Sort by date then lake, as a field team's spreadsheet export would be.
out.sort(key=lambda r: (r["date"], r["lake"].strip().lower()))

with open(here / "lakes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

with open(here / "lake-summary-answer.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(key[0].keys()))
    w.writeheader()
    w.writerows(key)

print(f"lakes.csv: {len(out)} rows; answer key: {len(key)} rows")
