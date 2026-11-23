#!/usr/bin/env python3
"""
make-data.py: example data for the unit "Organising a project for an agent".

Creates bird-project/ and bird-project.zip: a small, messy, synthetic
research project (volunteer bird counts at six sites, spring and autumn
2025) as it looks after a few months without a system. 16 files in one
folder: raw data, a cleaned file, two scripts, figures, notes, old copies,
and two files that must not be in a project folder at all
(volunteer_contacts.csv with made-up names and phone numbers, and
api_key.txt with a fake key).

The two scripts use only the Python standard library, so participants can
rerun them after restructuring without installing anything:
  clean.py       counts_raw_spring.csv + counts_raw_autumn.csv -> counts_clean.csv
  plot_sites.py  counts_clean.csv -> fig_sites.svg (total birds per site)

Everything is synthetic. The script is deterministic (fixed seed, fixed file
dates). At the end it prints the facts that exercise.qmd quotes. If you
change the data, update exercise.qmd to match.

Run from anywhere:

    python3 make-data.py
"""

import csv
import io
import os
import random
import shutil
import subprocess
import sys
import zipfile
import datetime as dt

random.seed(7)
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "bird-project")
if os.path.exists(PROJ):
    shutil.rmtree(PROJ)
os.makedirs(PROJ)


def write(name, text):
    with open(os.path.join(PROJ, name), "w", newline="") as f:
        f.write(text)


sites = ["A", "B", "C", "D", "E", "F"]
species = ["Great tit", "Blue tit", "Chaffinch", "Blackbird", "Robin",
           "Wood pigeon", "Magpie", "House sparrow"]
spelling = {"Great tit": ["Great tit", "great tit", "Great Tit"],
            "Blue tit": ["Blue tit", "blue tit"],
            "House sparrow": ["House sparrow", "house sparrow", "House Sparrow"]}
dates = {"spring": ["2025-04-12", "2025-05-10"],
         "autumn": ["2025-09-13", "2025-10-11"]}
observers = ["V01", "V02", "V03", "V04", "V05"]


def raw_rows(season):
    rows = []
    for d in dates[season]:
        for s in sites:
            obs = random.choice(observers)
            not_visited = (season == "spring" and s == "C" and d == "2025-05-10") or \
                          (season == "autumn" and s == "B" and d == "2025-09-13")
            for sp in species:
                name = random.choice(spelling.get(sp, [sp]))
                if not_visited:
                    count = ""
                else:
                    lam = {"A": 6, "B": 4, "C": 8, "D": 3, "E": 5, "F": 7}[s]
                    count = str(max(0, int(random.gauss(lam, 2.5))))
                rows.append([d, s, obs, name, count])
    return rows


spring = raw_rows("spring")
autumn = raw_rows("autumn")
hdr = "date,site,observer,species,count\n"
for fname, rows in [("counts_raw_spring.csv", spring), ("counts_raw_autumn.csv", autumn)]:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["date", "site", "observer", "species", "count"])
    w.writerows(rows)
    write(fname, buf.getvalue())

CLEAN_PY = '''# clean.py - combine and clean the raw bird counts
# reads counts_raw_spring.csv and counts_raw_autumn.csv, writes counts_clean.csv
import csv

rows = []
for season, fname in [("spring", "counts_raw_spring.csv"),
                      ("autumn", "counts_raw_autumn.csv")]:
    with open(fname) as f:
        for r in csv.DictReader(f):
            if r["count"] == "":          # blank = site not visited that day
                continue
            if season == "autumn" and r["site"] == "F":   # flooded, see notes
                continue
            rows.append({"date": r["date"], "site": r["site"], "season": season,
                         "species": r["species"].strip().lower(),
                         "count": int(r["count"])})

with open("counts_clean.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "site", "season", "species", "count"])
    w.writeheader()
    w.writerows(rows)
print("wrote counts_clean.csv:", len(rows), "rows,",
      sum(r["count"] for r in rows), "birds")
'''
write("clean.py", CLEAN_PY)

OLD_CLEAN = CLEAN_PY.replace(
    '''            if season == "autumn" and r["site"] == "F":   # flooded, see notes
                continue
''', "").replace('"species": r["species"].strip().lower()', '"species": r["species"]')
write("Copy of clean.py", OLD_CLEAN)

PLOT_PY = '''# plot_sites.py - total birds per site as a bar chart
# reads counts_clean.csv, writes fig_sites.svg (no extra packages needed)
import csv

totals = {}
with open("counts_clean.csv") as f:
    for r in csv.DictReader(f):
        totals[r["site"]] = totals.get(r["site"], 0) + int(r["count"])

sites = sorted(totals)
top = max(totals.values())
bars = []
for i, s in enumerate(sites):
    h = 300 * totals[s] / top
    x = 80 + i * 90
    bars.append(f'<rect x="{x}" y="{350 - h:.1f}" width="60" height="{h:.1f}" fill="#2a7f8f"/>'
                f'<text x="{x + 30}" y="375" text-anchor="middle">{s}</text>'
                f'<text x="{x + 30}" y="{340 - h:.1f}" text-anchor="middle">{totals[s]}</text>')
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 420" '
       'font-family="Helvetica, Arial, sans-serif" font-size="16">'
       '<rect width="640" height="420" fill="white"/>'
       '<text x="320" y="30" text-anchor="middle" font-size="20">Birds counted per site, 2025</text>'
       + "".join(bars) +
       '<line x1="70" y1="350" x2="620" y2="350" stroke="black"/>'
       '<text x="320" y="405" text-anchor="middle">site</text></svg>')
with open("fig_sites.svg", "w") as f:
    f.write(svg)
print("wrote fig_sites.svg:", totals)
'''
write("plot_sites.py", PLOT_PY)

# run old clean first -> counts_clean_OLD.csv and fig_sites_v2.svg; then current
def run(script, cwd):
    subprocess.run([sys.executable, "-I", script], cwd=cwd, check=True,
                   stdout=subprocess.PIPE)

run("Copy of clean.py", PROJ)
os.rename(os.path.join(PROJ, "counts_clean.csv"), os.path.join(PROJ, "counts_clean_OLD.csv"))
shutil.copy(os.path.join(PROJ, "counts_clean_OLD.csv"), os.path.join(PROJ, "counts_clean.csv"))
run("plot_sites.py", PROJ)
os.rename(os.path.join(PROJ, "fig_sites.svg"), os.path.join(PROJ, "fig_sites_v2.svg"))
os.remove(os.path.join(PROJ, "counts_clean.csv"))
run("clean.py", PROJ)
run("plot_sites.py", PROJ)

write("site_coordinates.csv",
      "site,name,lat,lon,habitat\n"
      "A,Old orchard,59.8571,17.6302,orchard\n"
      "B,Riverside path,59.8492,17.6511,riverbank\n"
      "C,Botanical garden,59.8530,17.6260,park\n"
      "D,Industrial estate,59.8705,17.6640,urban\n"
      "E,Beech wood,59.8402,17.6105,woodland\n"
      "F,Flood meadow,59.8350,17.6720,wet meadow\n")

write("notes.txt",
      "Notes on the bird counts (started March 2025)\n\n"
      "- Blank count = the site was not visited that day. 0 = visited, none seen.\n"
      "  Do NOT treat blanks as zeros.\n"
      "- Site C not visited 10 May (gate locked). Site B not visited 13 Sep (rain).\n"
      "- 2 Oct: decided to drop site F for autumn completely. The meadow was\n"
      "  flooded in September and October and the counts are not comparable.\n"
      "  (Discussed with the group, everyone agreed.)\n"
      "- Species names were typed by hand: Great tit / great tit / Great Tit are\n"
      "  the same. clean.py lower-cases them.\n"
      "- counts_clean_OLD.csv is from before the site F decision. Do not use.\n")

write("TODO.txt",
      "TODO\n"
      "- [x] clean the spring and autumn data\n"
      "- [x] bar chart per site\n"
      "- [ ] species per habitat (use site_coordinates.csv)\n"
      "- [ ] compare spring and autumn per species\n"
      "- [ ] methods paragraph for the report to the municipality (due 15 Dec)\n")

write("methods draft.md",
      "# Methods (draft)\n\n"
      "Volunteers counted birds at six sites in and around the city on two\n"
      "mornings in spring and two in autumn 2025, using a 10-minute point count.\n"
      "Site F was excluded in autumn because of flooding.\n\n"
      "TODO: say how many volunteers, cite the point-count protocol.\n")

write("README.txt", "bird counts 2025. ask Kim\n")

write("volunteer_contacts.csv",
      "code,name,phone,email\n"
      "V01,Alex Example,070-000 00 01,alex@example.org\n"
      "V02,Sam Placeholder,070-000 00 02,sam@example.org\n"
      "V03,Robin Madeup,070-000 00 03,robin@example.org\n"
      "V04,Kim Fictional,070-000 00 04,kim@example.org\n"
      "V05,Charlie Invented,070-000 00 05,charlie@example.org\n")

write("api_key.txt",
      "# key for the bird observation database API\n"
      "API_KEY=FAKE-0000-this-is-not-a-real-key-course-exercise\n")

# fixed file dates, oldest first, so the folder looks lived-in
stamp = {
    "site_coordinates.csv": "2025-03-03", "volunteer_contacts.csv": "2025-03-10",
    "api_key.txt": "2025-03-21", "counts_raw_spring.csv": "2025-05-12",
    "Copy of clean.py": "2025-05-20", "counts_clean_OLD.csv": "2025-05-20",
    "fig_sites_v2.svg": "2025-05-21", "notes.txt": "2025-10-02",
    "counts_raw_autumn.csv": "2025-10-13", "clean.py": "2025-10-14",
    "counts_clean.csv": "2025-10-14", "plot_sites.py": "2025-10-15",
    "fig_sites.svg": "2025-10-15", "TODO.txt": "2025-10-20",
    "methods draft.md": "2025-11-04", "README.txt": "2025-11-05"}
assert sorted(stamp) == sorted(os.listdir(PROJ)), sorted(os.listdir(PROJ))
for name, day in stamp.items():
    ts = dt.datetime.fromisoformat(day + "T10:00").timestamp()
    os.utime(os.path.join(PROJ, name), (ts, ts))

zpath = os.path.join(HERE, "bird-project.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for name in sorted(os.listdir(PROJ)):
        p = os.path.join(PROJ, name)
        info = zipfile.ZipInfo.from_file(p, arcname=f"bird-project/{name}")
        with open(p, "rb") as f:
            z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)

# ---- facts for exercise.qmd -------------------------------------------------
with open(os.path.join(PROJ, "counts_clean.csv")) as f:
    clean = list(csv.DictReader(f))
with open(os.path.join(PROJ, "counts_clean_OLD.csv")) as f:
    old = list(csv.DictReader(f))
tot = {}
for r in clean:
    tot[r["site"]] = tot.get(r["site"], 0) + int(r["count"])
print("files:", len(os.listdir(PROJ)))
print("raw rows spring/autumn:", len(spring), len(autumn))
print("counts_clean.csv rows:", len(clean), "birds:", sum(int(r["count"]) for r in clean))
print("counts_clean_OLD.csv rows:", len(old))
print("totals per site:", dict(sorted(tot.items())))
print("species in clean:", sorted({r["species"] for r in clean}))
print("zip:", zpath, os.path.getsize(zpath), "bytes")
