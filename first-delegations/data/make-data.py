#!/usr/bin/env python3
"""
make-data.py: example data for the unit "First delegations".

Creates three synthetic examples (one per job) and a zip file for each:

  messy-folder/   + messy-folder.zip   job 1: 40 badly named files to organise
  messy-sheet.xlsx + messy-sheet.zip   job 2: a messy lab spreadsheet to clean
  reports/        + reports.zip        job 3: six short PDF reports to summarise

Everything is synthetic: the people, the reports and the numbers are invented.
The script is deterministic (fixed random seed, fixed file dates), so rerunning
it gives the same files and the same expected answers.

Needs: Python 3 with matplotlib, and LibreOffice (soffice) on the PATH for the
.docx, .xlsx and .pdf files. Run from anywhere:

    python3 make-data.py

At the end it prints the facts that exercise.qmd quotes as expected outcomes
(file counts, duplicates, row counts, mean weight). If you change the data,
update exercise.qmd to match.
"""

import csv
import datetime as dt
import hashlib
import io
import os
import random
import shutil
import subprocess
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20240312
FOOTER = "Synthetic example for the course Introduction to agentic AI. Not a real report."

TMP = tempfile.mkdtemp(prefix="firstdeleg-")
LO_PROFILE = "file://" + os.path.join(TMP, "lo-profile")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def soffice(src, fmt, outdir, infilter=None):
    """Convert one file with LibreOffice and return the output path."""
    cmd = ["soffice", f"-env:UserInstallation={LO_PROFILE}", "--headless"]
    if infilter:
        cmd += [f"--infilter={infilter}"]
    cmd += ["--convert-to", fmt, "--outdir", outdir, src]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = os.path.splitext(os.path.basename(src))[0]
    ext = fmt.split(":")[0]
    out = os.path.join(outdir, base + "." + ext)
    assert os.path.exists(out), out
    return out


def html_doc(title, body_html):
    return f"""<html><head><meta charset="utf-8"><title>{title}</title>
<style>body {{ font-family: Liberation Sans, Arial, sans-serif; font-size: 11pt; }}
h1 {{ font-size: 18pt; }} h2 {{ font-size: 13pt; }}
p.foot {{ font-size: 8pt; color: #777777; }}
table {{ border-collapse: collapse; }} td, th {{ border: 1px solid #999999; padding: 3px 6px; }}
</style></head><body>{body_html}</body></html>"""


def office_from_html(name, title, body_html, ext, outdir):
    """Write HTML to a temp file, convert to docx or pdf, copy to outdir/name."""
    work = tempfile.mkdtemp(dir=TMP)
    src = os.path.join(work, "doc.html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html_doc(title, body_html))
    fmt = {"docx": "docx:MS Word 2007 XML", "pdf": "pdf:writer_pdf_Export"}[ext]
    out = soffice(src, fmt, work, infilter="HTML (StarWriter)")
    shutil.copy(out, os.path.join(outdir, name))


def small_png(path, kind, rng, label=""):
    """Tiny PNG images: plots, 'photos', screenshots, a logo, microscopy."""
    fig = plt.figure(figsize=(2.4, 1.8), dpi=60)
    ax = fig.add_axes([0.12, 0.15, 0.83, 0.75])
    if kind == "plot":
        x = list(range(10))
        ax.plot(x, [v + rng.gauss(0, 1) for v in x], "o-", color="#2a7f8f")
        ax.set_title(label, fontsize=8)
    elif kind == "bar":
        ax.bar(["A", "B", "C"], [rng.uniform(2, 9) for _ in range(3)], color="#6b4fa0")
        ax.set_title(label, fontsize=8)
    elif kind == "photo":
        ax.set_position([0, 0, 1, 1])
        ax.imshow([[(rng.random(), rng.random() * 0.6, 0.3) for _ in range(8)] for _ in range(6)],
                  interpolation="bilinear")
        ax.axis("off")
    elif kind == "micro":
        ax.set_position([0, 0, 1, 1])
        ax.set_facecolor("black")
        for _ in range(25):
            ax.add_patch(plt.Circle((rng.random(), rng.random()), rng.uniform(0.02, 0.06),
                                    color=(0.2, rng.uniform(0.6, 1.0), 0.3)))
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        fig.patch.set_facecolor("black")
    elif kind == "screenshot":
        ax.set_position([0, 0, 1, 1])
        ax.add_patch(plt.Rectangle((0, 0.85), 1, 0.15, color="#cccccc"))
        ax.text(0.05, 0.7, label, fontsize=7)
        for i in range(4):
            ax.add_patch(plt.Rectangle((0.05, 0.5 - i * 0.12), rng.uniform(0.3, 0.9), 0.05, color="#999999"))
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    elif kind == "logo":
        ax.set_position([0, 0, 1, 1])
        ax.add_patch(plt.Circle((0.5, 0.5), 0.35, color="#a8324a"))
        ax.text(0.5, 0.45, "LAB", ha="center", fontsize=14, color="white", weight="bold")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.savefig(path, metadata={"Software": None})
    plt.close(fig)


def set_mtime(path, when):
    t = dt.datetime.strptime(when, "%Y-%m-%d %H:%M").timestamp()
    os.utime(path, (t, t))


def make_zip(zip_path, root, arc_prefix):
    """Zip a file or folder with sorted entries and the files' own dates."""
    paths = []
    if os.path.isdir(root):
        for dirpath, _, files in os.walk(root):
            for fn in files:
                paths.append(os.path.join(dirpath, fn))
    else:
        paths = [root]
    paths.sort()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if os.path.isdir(root):
            z.writestr(zipfile.ZipInfo(arc_prefix + "/", date_time=(2024, 4, 15, 9, 0, 0)), "")
        for p in paths:
            rel = os.path.relpath(p, os.path.dirname(root))
            mt = dt.datetime.fromtimestamp(os.path.getmtime(p))
            zi = zipfile.ZipInfo(rel, date_time=mt.timetuple()[:6])
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(p, "rb") as f:
                z.writestr(zi, f.read())


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Job 1: the messy folder
# ---------------------------------------------------------------------------
def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def plate_csv(rng, date):
    rows = [[date, f"{r}{c}", round(rng.uniform(0.05, 1.2), 3)] for r in "AB" for c in range(1, 7)]
    return csv_text(["date", "well", "od600"], rows)


def growth_csv(rng, date):
    rows = [[date, h, round(0.05 * 1.35 ** h * rng.uniform(0.9, 1.1), 3)] for h in range(0, 13, 2)]
    return csv_text(["date", "hour", "od600"], rows)


def temps_csv(rng):
    rows = [[f"2024-04-09 {h:02d}:00", round(rng.uniform(19, 23), 1)] for h in range(8, 18)]
    return csv_text(["time", "room_temp_c"], rows)


def survey_csv(rng, n):
    rows = [[i + 1, rng.choice([1, 2, 3, 4, 5]), rng.choice(["yes", "no"])] for i in range(n)]
    return csv_text(["respondent", "rating_1to5", "would_recommend"], rows)


def make_messy_folder(rng):
    out = os.path.join(HERE, "messy-folder")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    def text(name, content, when):
        p = os.path.join(out, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        set_mtime(p, when)

    def png(name, kind, when, label=""):
        p = os.path.join(out, name)
        small_png(p, kind, rng, label)
        set_mtime(p, when)

    def doc(name, title, body, when):
        ext = name.rsplit(".", 1)[1]
        office_from_html(name, title, body, ext, out)
        set_mtime(os.path.join(out, name), when)

    def xlsx(name, rows, when):
        work = tempfile.mkdtemp(dir=TMP)
        src = os.path.join(work, "budget.csv")
        with open(src, "w", encoding="utf-8") as f:
            f.write(csv_text(["item", "cost_sek"], rows))
        res = soffice(src, "xlsx:Calc MS Excel 2007 XML", work)
        shutil.copy(res, os.path.join(out, name))
        set_mtime(os.path.join(out, name), when)

    def dup(new, original):
        shutil.copy(os.path.join(out, original), os.path.join(out, new))
        shutil.copystat(os.path.join(out, original), os.path.join(out, new))

    # --- data (10 csv, 2 exact duplicates) ---
    text("data 2024-03-05.csv", plate_csv(rng, "2024-03-05"), "2024-03-05 16:20")
    dup("data_05-03-2024 (1).csv", "data 2024-03-05.csv")            # duplicate 1
    text("Plate_reader_12.3.2024.csv", plate_csv(rng, "2024-03-12"), "2024-03-12 15:02")
    text("plate reader 2024_03_19.csv", plate_csv(rng, "2024-03-19"), "2024-03-19 14:48")
    text("growth_curve_Mar26.csv", growth_csv(rng, "2024-03-26"), "2024-03-26 18:30")
    text("GrowthCurve-2024-04-02.csv", growth_csv(rng, "2024-04-02"), "2024-04-02 17:55")
    text("survey_results_FINAL.csv", survey_csv(rng, 12), "2024-03-28 09:10")
    text("survey_results_FINAL_v2.csv", survey_csv(rng, 14), "2024-04-03 11:45")
    text("temps_20240409.csv", temps_csv(rng), "2024-04-09 18:01")
    dup("Copy of temps_20240409.csv", "temps_20240409.csv")         # duplicate 2

    # --- images (12 png, 1 exact duplicate) ---
    png("IMG_0041.png", "photo", "2024-03-07 12:31")
    png("IMG_0042.png", "photo", "2024-03-07 12:32")
    dup("IMG_0042 (1).png", "IMG_0042.png")                           # duplicate 3
    png("Screenshot 2024-03-07 at 10.15.32.png", "screenshot", "2024-03-07 10:15", "Booking system")
    png("Screenshot 2024-04-11 at 14.02.10.png", "screenshot", "2024-04-11 14:02", "Course page")
    png("figure1.png", "plot", "2024-03-20 10:00", "Figure 1")
    png("Figure 1 NEW.png", "plot", "2024-04-04 15:40", "Figure 1 (new)")
    png("fig2_final.png", "bar", "2024-04-05 09:12", "Figure 2")
    png("fig2_final_REALLYfinal.png", "bar", "2024-04-08 22:47", "Figure 2")
    png("microscope 14-03-24.png", "micro", "2024-03-14 13:20")
    png("microscope_2024.03.21.png", "micro", "2024-03-21 13:05")
    png("logo.png", "logo", "2024-01-15 08:30")

    # --- documents (5 docx) ---
    doc("Lab protocol v1.docx", "Lab protocol",
        "<h1>Plate reader protocol</h1><p>Version 1. Measure OD600 every two hours.</p>",
        "2024-02-20 10:00")
    doc("lab_protocol_v2_final.docx", "Lab protocol",
        "<h1>Plate reader protocol</h1><p>Version 2. Measure OD600 every two hours. "
        "Shake for 10 s before each read.</p>", "2024-03-01 14:00")
    doc("lab_protocol_v2_final_REALLYfinal.docx", "Lab protocol",
        "<h1>Plate reader protocol</h1><p>Version 2 (corrected). Measure OD600 every two hours. "
        "Shake for 10 s before each read. Blank with medium only.</p>", "2024-03-04 09:30")
    doc("report draft.docx", "Report",
        "<h1>Growth of strain K7: progress report</h1><p>Draft. Results to be added.</p>",
        "2024-04-01 16:00")
    doc("Report_final_v2.docx", "Report",
        "<h1>Growth of strain K7: progress report</h1><p>Final version. Strain K7 doubled every "
        "2.3 hours at 30 degrees.</p>", "2024-04-12 11:20")

    # --- text notes (5 txt) and one markdown file ---
    text("Meeting notes 4 March.txt", "Group meeting 2024-03-04\n- order new plates\n- Sam on leave next week\n",
         "2024-03-04 15:00")
    text("meeting-notes-2024-03-18.txt", "Group meeting 2024-03-18\n- growth curves look noisy\n- check shaker\n",
         "2024-03-18 15:00")
    text("MeetingNotes_01APR2024.txt", "Group meeting 2024-04-01\n- draft report due 12 April\n",
         "2024-04-01 15:00")
    text("todo.txt", "- book microscope\n- send survey reminder\n- update figure 2\n", "2024-04-10 08:15")
    text("TODO (old).txt", "- order plates\n- fix shaker\n", "2024-03-02 08:15")
    text("reading list.md", "# Reading list\n\n- A paper on growth curves\n- A review of plate readers\n",
         "2024-02-25 19:40")

    # --- pdf (5) ---
    doc("Course schedule spring 2024.pdf", "Schedule",
        "<h1>Course schedule, spring 2024</h1><p>Week 10: introduction. Week 12: lab 1. Week 14: lab 2.</p>",
        "2024-01-10 10:00")
    doc("course_schedule_2024_v3.pdf", "Schedule",
        "<h1>Course schedule, spring 2024 (version 3)</h1><p>Week 10: introduction. Week 13: lab 1 "
        "(moved). Week 15: lab 2 (moved).</p>", "2024-02-28 10:00")
    doc("Ethics approval letter 2024.pdf", "Letter",
        "<h1>Approval letter (example)</h1><p>This placeholder stands in for an approval letter. "
        "It contains no real decision.</p>", "2024-01-30 09:00")
    doc("Lecture 1 slides.pdf", "Lecture 1",
        "<h1>Lecture 1: bacterial growth</h1><p>Lag, log and stationary phase.</p>", "2024-03-06 07:50")
    doc("lecture2_slides_FINAL.pdf", "Lecture 2",
        "<h1>Lecture 2: measuring growth</h1><p>Optical density and its limits.</p>", "2024-03-13 07:45")

    # --- spreadsheets (2 xlsx) ---
    xlsx("budget 2024.xlsx", [["plates", 4200], ["media", 1800], ["microscope hours", 3000]],
         "2024-01-12 11:00")
    xlsx("Budget_2024_revised.xlsx", [["plates", 4200], ["media", 2300], ["microscope hours", 3000],
                                     ["shaker repair", 1500]], "2024-03-22 11:00")

    # facts
    files = sorted(os.listdir(out))
    hashes = {}
    for fn in files:
        hashes.setdefault(sha(os.path.join(out, fn)), []).append(fn)
    dups = [v for v in hashes.values() if len(v) > 1]
    by_ext = {}
    for fn in files:
        by_ext[fn.rsplit(".", 1)[1]] = by_ext.get(fn.rsplit(".", 1)[1], 0) + 1
    return {"files": len(files), "distinct": len(hashes), "duplicate_groups": dups, "by_ext": by_ext}


# ---------------------------------------------------------------------------
# Job 2: the messy spreadsheet (written as flat ODS XML, converted to .xlsx)
# ---------------------------------------------------------------------------
def make_messy_sheet(rng):
    # 48 mice in two batches of 24; 8 control, 8 low dose, 8 high dose per batch.
    sexes = ["F"] * 26 + ["M"] * 22
    rng.shuffle(sexes)
    animals = []
    for b, date in ((1, "2024-03-12"), (2, "2024-04-09")):
        groups = ["control"] * 8 + ["low"] * 8 + ["high"] * 8
        rng.shuffle(groups)
        for i in range(24):
            sex = sexes[(b - 1) * 24 + i]
            mu = 21.0 if sex == "F" else 25.5
            animals.append({"id": f"B{b}-{i + 1:02d}", "sex": sex, "group": groups[i],
                            "date": date, "weight": round(rng.gauss(mu, 1.6), 1)})
    missing_id = "B2-11"          # 'not weighed (sick)': weight unknown
    for a in animals:
        if a["id"] == missing_id:
            a["weight"] = None

    dose = {"control": 0, "low": 5, "high": 20}
    sex_spell = {"F": ["Female", "female", "F", "f", "F "], "M": ["Male", "male", "M", "m"]}
    group_spell = {"control": ["Control", "control", "ctrl", "Ctrl"],
                   "low": ["Low dose", "low dose", "LD", "low"],
                   "high": ["High dose", "high-dose", "HD", "High"]}
    dose_spell = {0: ["0", "0 mg/kg", "-", "none"], 5: ["5 mg/kg", "5mg/kg", "5"],
                  20: ["20 mg/kg", "20mg/kg", "20"]}

    def date_cell(iso, k):
        d = dt.date.fromisoformat(iso)
        variants = [("date", iso), ("date", iso), ("date", iso),
                    ("string", d.strftime("%d/%m/%Y")),
                    ("string", f"{d.day}.{d.month}.{d.year}"),
                    ("string", f"{d.day} {d.strftime('%B')} {d.year}"),
                    ("string", iso)]
        return variants[k % len(variants)]

    def weight_cell(w, k):
        if k % 9 == 1:
            return ("string", f"{w} g")
        if k % 9 == 4:
            return ("string", f"{w}".replace(".", ","))
        if k % 9 == 7:
            return ("string", f"{w}g")
        return ("float", w)

    comments = {"B1-04": "bite wound on tail", "B1-19": "", "B2-02": "moved to cage 7",
                "B2-11": "", "B2-20": "scale recalibrated before this one"}

    rows = []  # each row: list of 7 cells (type, value) or None for empty
    for k, a in enumerate(animals):
        aid = a["id"]
        if aid == "B1-07":
            aid = "B1-07 "
        if aid == "B2-03":
            aid = "b2-3"
        sex = rng.choice(sex_spell[a["sex"]])
        grp = rng.choice(group_spell[a["group"]])
        dcell = ("string", rng.choice(dose_spell[dose[a["group"]]]))
        if dcell[1] in ("0", "5", "20"):
            dcell = ("float", int(dcell[1]))
        date = date_cell(a["date"], k)
        if a["id"] == "B2-17":
            date = ("string", "04/09/2024")      # written US-style: month/day
        if a["weight"] is None:
            wcell = ("string", "not weighed (sick)")
        elif a["id"] == "B1-19":
            wcell = ("string", f"{a['weight']} (re-weighed)")
        else:
            wcell = weight_cell(a["weight"], k)
        com = comments.get(a["id"], "")
        rows.append([("string", aid), ("string", sex), ("string", grp), dcell, date, wcell,
                     ("string", com) if com else None])
        if a["id"] == "B1-15":                    # copy-paste duplicate row
            rows.append(list(rows[-1]))
        if a["id"] in ("B1-08", "B2-08"):
            rows.append([None] * 7)                # blank rows
        if a["id"] == "B1-24":
            rows.append([None] * 7)
            rows.append([("string", "Batch 2 - arrived 2 April, weighed one week later")] + [None] * 6)

    weights = [a["weight"] for a in animals if a["weight"] is not None]
    mean_w = round(sum(weights) / len(weights), 2)
    rows.append([None] * 7)
    rows.append([("string", "Mean"), None, None, None, None, ("float", mean_w),
                 ("string", "Total animals: 48")])

    # ---- write flat ODS ----
    def cell(c):
        if c is None:
            return "<table:table-cell/>"
        t, v = c
        if t == "string":
            esc = str(v).replace("&", "&amp;").replace("<", "&lt;")
            return f'<table:table-cell office:value-type="string"><text:p>{esc}</text:p></table:table-cell>'
        if t == "float":
            return f'<table:table-cell office:value-type="float" office:value="{v}"><text:p>{v}</text:p></table:table-cell>'
        if t == "date":
            return (f'<table:table-cell table:style-name="cdate" office:value-type="date" '
                    f'office:date-value="{v}"><text:p>{v}</text:p></table:table-cell>')
        raise ValueError(t)

    def bold(text, span=1):
        cov = "<table:covered-table-cell/>" * (span - 1)
        sp = f' table:number-columns-spanned="{span}" table:number-rows-spanned="1"' if span > 1 else ""
        return (f'<table:table-cell table:style-name="cbold"{sp} office:value-type="string">'
                f"<text:p>{text}</text:p></table:table-cell>{cov}")

    head = [
        bold("Cohort B body weights, spring 2024. Compound X17 (synthetic example data)", 7),
        bold("Animal", 3) + bold("Treatment") + bold("Weighing", 2) + bold("Notes"),
        bold("ID") + bold("Sex") + bold("Group") + bold("Dose") + bold("Date") + bold("Weight (g)")
        + bold("Comment"),
    ]
    body = "".join("<table:table-row>" + "".join(cell(c) for c in r) + "</table:table-row>" for r in rows)
    fods = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
 xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
 office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
<office:automatic-styles>
 <number:date-style style:name="ndate"><number:year number:style="long"/><number:text>-</number:text>
  <number:month number:style="long"/><number:text>-</number:text><number:day number:style="long"/></number:date-style>
 <style:style style:name="cdate" style:family="table-cell" style:data-style-name="ndate"/>
 <style:style style:name="cbold" style:family="table-cell"><style:text-properties fo:font-weight="bold"/></style:style>
 <style:style style:name="colw" style:family="table-column"><style:table-column-properties style:column-width="1.1in"/></style:style>
</office:automatic-styles>
<office:body><office:spreadsheet>
<table:table table:name="weights">
<table:table-column table:style-name="colw" table:number-columns-repeated="7"/>
{''.join('<table:table-row>' + h + '</table:table-row>' for h in head)}
{body}
</table:table>
</office:spreadsheet></office:body></office:document>
"""
    work = tempfile.mkdtemp(dir=TMP)
    src = os.path.join(work, "messy-sheet.fods")
    with open(src, "w", encoding="utf-8") as f:
        f.write(fods)
    res = soffice(src, "xlsx:Calc MS Excel 2007 XML", work)
    target = os.path.join(HERE, "messy-sheet.xlsx")
    shutil.copy(res, target)
    set_mtime(target, "2024-04-10 17:30")

    sexes_n = {s: sum(1 for a in animals if a["sex"] == s) for s in "FM"}
    return {"animals": len(animals), "sheet_rows_below_header": len(rows), "mean_weight": mean_w,
            "n_weights": len(weights), "missing": missing_id, "sex": sexes_n,
            "answer": animals}


# ---------------------------------------------------------------------------
# Job 3: six short PDF reports
# ---------------------------------------------------------------------------
PB = '<p style="page-break-before: always"></p>'


def foot():
    return f'<p class="foot">{FOOTER}</p>'


REPORTS = [
    ("report-flipped-chemistry.pdf", "Flipped classroom pilot in first-year chemistry", f"""
<h1>Flipped classroom pilot in first-year chemistry</h1>
<p><b>Lena Bergqvist and Omar Haddad</b><br/>Teaching development project, final report<br/>14 March 2025</p>
<h2>Background</h2>
<p>The first-year course General Chemistry 1 has had a pass rate of about 60% for several years.
Students often reported that the lectures moved too fast and that they had no time to ask questions.
In spring 2025 we replaced half of the lectures with short videos that students watched before class,
and used the class time for problem solving in groups of four.</p>
<h2>Method</h2>
<p>We compared the 2025 cohort with the 2024 cohort, which took the same final exam format with
lectures only. We also counted attendance at the class sessions and ran a short questionnaire in
week 8.</p>{foot()}{PB}
<h2>Results</h2>
<p>The pass rate on the final exam rose from 61% in 2024 (142 students) to 72% in 2025 (138 students).
Attendance at the class sessions fell from about 80% in the first weeks to 55% by the end of the
course. In the questionnaire, 70% of the respondents said the videos helped them prepare.</p>
<h2>Conclusions</h2>
<p>The flipped format was followed by a higher pass rate, but attendance dropped over the term.
Because the two cohorts differ in more ways than the teaching format, we cannot say that the format
caused the change. We will keep the format and add short quizzes to keep attendance up.</p>{foot()}
"""),
    ("report-soil-sensors.pdf", "Soil moisture sensors in three urban allotments", f"""
<h1>Soil moisture sensors in three urban allotments</h1>
<p><b>Priya Natarajan</b><br/>Field station technical report 2025-07<br/>2025-06-30</p>
<h2>Background</h2>
<p>Allotment holders want to water less without harming their crops. Low-cost capacitive soil
moisture sensors are cheap, but their accuracy in mixed urban soils is not known. This report
compares such sensors with the standard gravimetric method, where a soil sample is weighed before
and after drying.</p>
<h2>Method</h2>
<p>We placed 12 sensors in three allotments (four per site) and took a soil core next to each sensor
once a week for ten weeks, giving 120 paired readings.</p>{foot()}{PB}
<h2>Results</h2>
<p>On average, the sensors read 4.1 percentage points higher than the gravimetric reference. The
error was small in dry soil and grew above about 35% volumetric water content. One sensor failed
after six weeks and was replaced.</p>
<h2>Conclusions</h2>
<p>The low-cost sensors are good enough to tell gardeners when the soil is dry, but they should not
be used to measure how wet a soil is after heavy rain without a site-specific calibration.</p>{foot()}
"""),
    ("report-peer-feedback.pdf", "Peer feedback on lab reports in a molecular biology course", f"""
<h1>Peer feedback on lab reports in a molecular biology course</h1>
<p><b>Henrik Sjöström, Maja Lindgren and Tomás Ruiz</b><br/>Course development report<br/>03/09/2025</p>
<h2>Background</h2>
<p>Lab reports take a long time to mark, and students get feedback only after the course is over.
A pilot at another department reported that peer feedback improved report grades by a full grade
step. We tried peer feedback in our own course in spring 2025 and write this report in the first
week of the autumn term, before the next run of the course.</p>
<h2>Method</h2>
<p>Students in two of the four lab groups (48 students) gave each other written feedback on a draft,
using a short checklist. The other two groups (46 students) handed in their reports without peer
feedback. All reports were marked by the same two teachers on a 5-point scale.</p>{foot()}{PB}
<h2>Results</h2>
<p>We found no clear difference in the final report grades: the mean grade was 3.9 with peer
feedback and 3.8 without. In the course evaluation, most students in the peer feedback groups said
that reading other students' reports helped them see what a good report looks like.</p>
<h2>Conclusions</h2>
<p>Peer feedback did not change grades in our course, but students valued it and it cost little
teacher time. We will keep it as an optional step.</p>{foot()}
"""),
    ("report-barley-drought.pdf", "Drought tolerance of six barley lines in a greenhouse trial", f"""
<h1>Drought tolerance of six barley lines in a greenhouse trial</h1>
<p><b>Aino Virtanen</b><br/>Plant breeding group, internal report<br/>November 2024</p>
<h2>Background</h2>
<p>Dry springs are becoming more common in the region. We tested six barley lines from the
breeding programme for how well they keep growing when water is withheld for three weeks at the
tillering stage.</p>{foot()}{PB}
<h2>Method</h2>
<p>Each line was grown in 20 pots: 10 watered normally (control) and 10 with no water for three
weeks. After the drought period all pots were watered normally again. Above-ground biomass was
harvested and dried at the end of the trial. For each line we report the biomass under drought as a
percentage of the biomass of its own control pots.</p>
<p>The greenhouse kept a day temperature of 20 degrees and 16 hours of light. One pot of line
HB-09 was lost to a fungal infection and was left out.</p>{foot()}{PB}
<h2>Results</h2>
<table>
<tr><th>Line</th><th>Biomass under drought (% of control)</th></tr>
<tr><td>HB-03</td><td>61</td></tr>
<tr><td>HB-09</td><td>55</td></tr>
<tr><td>HB-12</td><td>68</td></tr>
<tr><td>HB-17</td><td>82</td></tr>
<tr><td>HB-21</td><td>64</td></tr>
<tr><td>HB-30</td><td>59</td></tr>
</table>
<p>Line HB-17 kept clearly more of its biomass than the other five lines, which ranged from 55% to
68%. We will test HB-17 in the field next season.</p>{foot()}
"""),
    ("report-hand-hygiene.pdf", "Hand-hygiene reminders on a surgical ward", f"""
<h1>Hand-hygiene reminders on a surgical ward: a before-and-after audit</h1>
<p><b>Grace Okafor and Daniel Weiss</b><br/>Quality improvement report<br/>22 Jan 2025</p>
<table><tr><td><b>Key finding.</b> Observed hand-hygiene compliance rose from 64% (410 observed
opportunities) before the reminders to 79% (395 opportunities) after them.</td></tr></table>
<h2>Background</h2>
<p>Hand hygiene at the right moments is one of the simplest ways to prevent infections in hospital.
Audits on the ward in 2024 showed that staff often missed the moment before touching a patient.</p>
<h2>Method</h2>
<p>Two trained observers recorded hand-hygiene opportunities for four weeks before and four weeks
after we put up reminder signs and placed hand-rub dispensers at every bed. All data were
anonymous; no staff member was identified.</p>{foot()}{PB}
<h2>Results</h2>
<p>Compliance improved for every type of staff. The largest change was before touching a patient.
Compliance after touching the patient's surroundings changed least.</p>
<h2>Conclusions</h2>
<p>Simple reminders and better placed dispensers were followed by higher compliance. Observers may
change behaviour by being present, so the true level is likely lower than measured. We will repeat
the audit in six months.</p>{foot()}
"""),
    ("report-printed-steel.pdf", "Corrosion of 3D-printed stainless steel coupons in seawater", f"""
<h1>Corrosion of 3D-printed stainless steel coupons in seawater</h1>
<p><b>Mateo Fernández</b><br/>Materials laboratory, project report</p>
<h2>Background</h2>
<p>Parts made by 3D printing in stainless steel are being considered for small marine fittings.
Printed metal can contain small pores that may make it corrode faster than machined metal of the
same grade.</p>
<h2>Method</h2>
<p>We printed 10 coupons and machined 10 coupons from the same steel grade. Half of the printed
coupons were heat-treated after printing. All coupons were kept in natural seawater for 12 weeks
and weighed before and after cleaning.</p>{foot()}{PB}
<h2>Results</h2>
<p>The printed coupons that were not heat-treated lost about twice as much mass as the machined
coupons (0.42 against 0.20 mg per square centimetre). Heat treatment reduced the loss of the printed
coupons to 0.27 mg per square centimetre.</p>
<h2>Conclusions</h2>
<p>As printed, the parts corrode faster than machined parts. Heat treatment closes much of the gap,
so we recommend it for any printed part meant for seawater.</p>
<p>Submitted 3 February 2025.</p>{foot()}
"""),
]


def make_reports():
    out = os.path.join(HERE, "reports")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    pages = {}
    for i, (name, title, body) in enumerate(REPORTS):
        office_from_html(name, title, body, "pdf", out)
        set_mtime(os.path.join(out, name), f"2025-0{i + 2}-10 12:00")
        info = subprocess.run(["pdfinfo", os.path.join(out, name)], capture_output=True, text=True).stdout
        pages[name] = int([l for l in info.splitlines() if l.startswith("Pages:")][0].split()[1])
    return pages


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    rng = random.Random(SEED)
    f1 = make_messy_folder(rng)
    f2 = make_messy_sheet(rng)
    f3 = make_reports()

    make_zip(os.path.join(HERE, "messy-folder.zip"), os.path.join(HERE, "messy-folder"), "messy-folder")
    make_zip(os.path.join(HERE, "messy-sheet.zip"), os.path.join(HERE, "messy-sheet.xlsx"), "")
    make_zip(os.path.join(HERE, "reports.zip"), os.path.join(HERE, "reports"), "reports")

    # answer key for the spreadsheet (for teachers; not given to participants)
    with open(os.path.join(HERE, "messy-sheet-answer.csv"), "w", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["animal_id", "sex", "group", "dose_mg_per_kg", "date_weighed", "weight_g"])
        dose = {"control": 0, "low": 5, "high": 20}
        for a in f2["answer"]:
            w.writerow([a["id"], a["sex"], a["group"], dose[a["group"]], a["date"],
                        "" if a["weight"] is None else a["weight"]])

    shutil.rmtree(TMP, ignore_errors=True)
    print("Job 1 messy folder:", {k: v for k, v in f1.items()})
    print("Job 2 messy sheet:", {k: v for k, v in f2.items() if k != "answer"})
    print("Job 3 report pages:", f3)
