# make-data.py: generates the synthetic example data for the unit
# "Making the agent yours" (Introduction to agentic AI).
#
# Output (written next to this script):
#   growth.csv  plant height in a greenhouse trial: 3 treatments x 6 plants,
#               measured on days 0, 7, 14, 21 and 28 (90 rows, long format)
#   course-eval.csv  aggregated course-evaluation scores: 4 questions,
#               2021-2025, mean score (1-5) and number of responses (20 rows).
#               Aggregated numbers only, no individual answers.
#
# Both files are invented. They are deliberately different in shape (a time
# course and a yearly summary) so that a "house style" skill can be tested
# on two unlike figures: the two results should still look like one family.
#
# Run:  python3 make-data.py   (needs only the Python standard library)

import csv
import random
from pathlib import Path

random.seed(42)
here = Path(__file__).parent

# ---- growth.csv ----
growth_rate = {"control": 0.95, "low_N": 0.70, "high_N": 1.25}  # cm per day
rows = []
for treat, rate in growth_rate.items():
    for plant in range(1, 7):
        h0 = random.uniform(2.0, 3.0)
        r = rate * random.uniform(0.85, 1.15)
        for day in (0, 7, 14, 21, 28):
            # slight saturation towards the end of the trial
            h = h0 + r * day * (1 - day / 120) + (random.gauss(0, 0.4) if day else 0)
            rows.append({
                "treatment": treat,
                "plant_id": f"{treat[0].upper()}{plant:02d}",
                "day": day,
                "height_cm": round(h, 1),
            })
with open(here / "growth.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---- course-eval.csv ----
questions = {
    "Q1 clear goals": (3.6, 0.10),
    "Q2 useful exercises": (3.9, 0.08),
    "Q3 reasonable workload": (2.9, 0.15),
    "Q4 overall": (3.7, 0.09),
}
ev = []
for q, (start, trend) in questions.items():
    for i, year in enumerate(range(2021, 2026)):
        score = min(4.8, start + trend * i + random.gauss(0, 0.08))
        ev.append({
            "year": year,
            "question": q,
            "mean_score": round(score, 2),
            "n_responses": random.randint(38, 64),
        })
with open(here / "course-eval.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(ev[0].keys()))
    w.writeheader()
    w.writerows(ev)

print(f"growth.csv: {len(rows)} rows; course-eval.csv: {len(ev)} rows")
