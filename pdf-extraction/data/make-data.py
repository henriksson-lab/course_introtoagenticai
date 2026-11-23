#!/usr/bin/env python3
"""
make-data.py: example data for the unit "Extracting data from PDFs".

Creates seven small synthetic PDFs (six short "papers" and one supplementary
file) in papers/, a zip of that folder (papers.zip), and the answer key
answer-key.csv.

The task in the exercise: for each study, extract the number of participants
analysed and the mean serum 25-hydroxyvitamin D (25(OH)D) concentration, in
nmol/L, with the page and table it came from.

Each paper hides one typical difficulty:

  01_Aldersen-2021.pdf   clean text PDF, value in a table (the easy one)
  02_Moreau-2019.pdf     the table gives ng/mL, not nmol/L (units in the header;
                         1 ng/mL = 2.496 nmol/L)
  03_Nyberg-2022.pdf     a long table that runs over a page break, header not
                         repeated; decimal commas; the total row is on the last page
  04_Okonkwo-2018.pdf    a "scanned" paper: every page is an image, no text layer
  05_Petrova-2023.pdf    recruited (260) is not analysed (229); the abstract gives
                         the median, the table the mean; the introduction quotes
                         another survey's mean
  06_Quint-2020.pdf      the main text has no value; it is in the supplement
  06_Quint-2020_supplement.pdf

Everything is synthetic: the authors, towns, journals and numbers are invented.
The script is deterministic (fixed random seed), so rerunning it gives the same
files and the same answer key.

Needs: Python 3 with Pillow (PIL), LibreOffice (soffice) and poppler-utils
(pdftoppm, pdfinfo, pdftotext) on the PATH. Run from anywhere:

    python3 make-data.py

It prints the answer key and, per PDF, the page count and whether pdftotext
finds any text. If you change the data, update exercise.qmd to match.
"""

import csv
import os
import random
import shutil
import subprocess
import tempfile
import zipfile

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "papers")
SEED = 20261123
NGML_TO_NMOLL = 2.496
FOOTER = ("Synthetic example for the course Introduction to agentic AI. "
          "Not a real study; authors, places and numbers are invented.")

TMP = tempfile.mkdtemp(prefix="pdfextract-")
LO_PROFILE = "file://" + os.path.join(TMP, "lo-profile")
PB = '<p style="page-break-before: always"></p>'


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def soffice_pdf(src, outdir):
    cmd = ["soffice", f"-env:UserInstallation={LO_PROFILE}", "--headless",
           "--infilter=HTML (StarWriter)", "--convert-to", "pdf:writer_pdf_Export",
           "--outdir", outdir, src]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    assert os.path.exists(out), out
    return out


def html_doc(title, body):
    return f"""<html><head><meta charset="utf-8"><title>{title}</title>
<style>body {{ font-family: Liberation Serif, Times New Roman, serif; font-size: 11pt; }}
h1 {{ font-size: 16pt; font-family: Liberation Sans, Arial, sans-serif; }}
h2 {{ font-size: 12pt; font-family: Liberation Sans, Arial, sans-serif; }}
p.meta {{ font-size: 10pt; }} p.foot {{ font-size: 8pt; color: #777777; }}
p.cap {{ font-size: 10pt; }}
table {{ border-collapse: collapse; }} td {{ border: 1px solid #999999; padding: 2px 6px; font-size: 10pt; }}
</style></head><body>{body}</body></html>"""


def make_pdf(name, title, body):
    work = tempfile.mkdtemp(dir=TMP)
    src = os.path.join(work, "doc.html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html_doc(title, body))
    out = soffice_pdf(src, work)
    dest = os.path.join(OUT, name)
    shutil.copy(out, dest)
    return dest


def foot():
    return f'<p class="foot">{FOOTER}</p>'


def head(title, authors, where, journal):
    return (f"<h1>{title}</h1>"
            f'<p class="meta"><b>{authors}</b><br/>{where}<br/><i>{journal}</i></p>')


def table(header, rows, bold_last=False):
    """Plain table; the header row uses <td> so LibreOffice does not repeat it
    on the next page (the point of paper 03)."""
    h = "".join(f"<td><b>{c}</b></td>" for c in header)
    body = ""
    for i, r in enumerate(rows):
        cells = "".join((f"<td><b>{c}</b></td>" if bold_last and i == len(rows) - 1 else f"<td>{c}</td>")
                        for c in r)
        body += f"<tr>{cells}</tr>"
    return f"<table><tr>{h}</tr>{body}</table>"


def pages(path):
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    return int([l for l in info.splitlines() if l.startswith("Pages:")][0].split()[1])


def page_text(path, p):
    return subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", path, "-"],
                          capture_output=True, text=True).stdout


def rasterise(path, rng, dpi=110):
    """Replace a PDF by an image-only copy that looks like a photocopy:
    grey, slightly rotated, with specks. No text layer is left."""
    work = tempfile.mkdtemp(dir=TMP)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-png", path, os.path.join(work, "p")],
                   check=True)
    imgs = []
    for fn in sorted(os.listdir(work)):
        im = Image.open(os.path.join(work, fn)).convert("L")
        im = im.rotate(rng.choice([-0.7, 0.6, -0.5]), resample=Image.BICUBIC, fillcolor=245)
        d = ImageDraw.Draw(im)
        w, h = im.size
        for _ in range(350):
            x, y = rng.randrange(w), rng.randrange(h)
            g = rng.randrange(90, 200)
            d.point((x, y), fill=g)
        im = im.filter(ImageFilter.GaussianBlur(0.4))
        # a darker band at the left edge, as from a copier lid
        d = ImageDraw.Draw(im)
        for x in range(12):
            d.line([(x, 0), (x, h)], fill=200 + x * 3)
        imgs.append(im)
    imgs[0].save(path, "PDF", resolution=dpi, save_all=True, append_images=imgs[1:])


# ---------------------------------------------------------------------------
# the papers
# ---------------------------------------------------------------------------
def paper01():
    body = head("Vitamin D status of adults in a northern coastal town",
                "K. Aldersen, M. Brandt and S. Holm",
                "Department of Public Health, Harbourton (fictional)",
                "Course Example Reports in Nutrition 3 (2021) 14-16") + """
<p><b>Abstract.</b> We measured serum 25-hydroxyvitamin D (25(OH)D) in a random sample of adults
in Harbourton in late winter. Of 240 invited adults, 212 gave a blood sample. The mean
concentration was 58.4 nmol/L, and 31% were below 50 nmol/L.</p>
<h2>Introduction</h2>
<p>Vitamin D status is usually judged from the serum concentration of 25(OH)D. Concentrations below
50 nmol/L are often taken to indicate insufficiency. Northern populations are at risk in winter,
when the sun is too low for the skin to make vitamin D.</p>
<h2>Methods</h2>
<p>Adults aged 18 to 75 were drawn at random from the town register and invited by letter. Blood
was drawn in February and March 2020 and analysed by liquid chromatography-mass spectrometry.</p>
""" + foot() + PB + """
<h2>Results</h2>
<p>212 of the 240 invited adults took part (88%). Table 1 gives the serum concentrations.</p>
<p class="cap"><b>Table 1.</b> Serum 25(OH)D by sex.</p>
""" + table(["Group", "n", "Mean 25(OH)D (nmol/L)", "SD (nmol/L)", "Below 50 nmol/L (%)"],
            [["Women", "118", "60.1", "19.8", "28"],
             ["Men", "94", "56.3", "20.5", "35"],
             ["All", "212", "58.4", "20.2", "31"]]) + """
<h2>Discussion</h2>
<p>About a third of the adults in this town were below 50 nmol/L at the end of winter. This is
similar to other northern coastal populations.</p>
""" + foot()
    return make_pdf("01_Aldersen-2021.pdf", "Aldersen 2021", body)


def paper02():
    body = head("Serum vitamin D in nursing students before and after a winter term",
                "L. Moreau and T. Achebe",
                "School of Nursing, Valcourt (fictional)",
                "Course Example Reports in Nutrition 1 (2019) 41-43") + """
<p><b>Abstract.</b> We report serum 25-hydroxyvitamin D (25(OH)D) in 140 nursing students at the
start of the spring term. Many students were below the commonly used threshold of 20 ng/mL
(50 nmol/L).</p>
<h2>Methods</h2>
<p>All 152 students in the second year were invited; 140 gave a sample in January 2018. Serum
25(OH)D was measured by immunoassay. Results are reported in ng/mL, as the laboratory delivers
them.</p>
""" + foot() + PB + """
<h2>Results</h2>
<p class="cap"><b>Table 1.</b> Serum 25(OH)D at the start of term (n = 140).</p>
""" + table(["Measure", "Value"],
            [["Participants (n)", "140"],
             ["Mean 25(OH)D (ng/mL)", "21.6"],
             ["SD (ng/mL)", "7.9"],
             ["Median 25(OH)D (ng/mL)", "20.8"],
             ["Below 20 ng/mL (%)", "46"]]) + """
<p>Students who reported a holiday in a sunny country during the winter had higher values.</p>
<h2>Discussion</h2>
<p>Almost half of the students were below 20 ng/mL. A supplement in winter may be worth
recommending to this group.</p>
""" + foot()
    return make_pdf("02_Moreau-2019.pdf", "Moreau 2019", body)


def paper03(rng):
    names = ["Ask", "Berga", "Dalby", "Ekeby", "Fors", "Gnesta", "Hallby", "Ingå", "Järna",
             "Kvarn", "Lid", "Mora", "Norrby", "Ockelbo", "Rasbo", "Sala", "Tierp", "Ulva",
             "Vreta", "Ytterby", "Åby", "Ödeby", "Alby", "Bro", "Edsbro", "Fjäll", "Gimo",
             "Husby", "Kil", "Ljusne", "Malma", "Nora", "Orsa", "Rimbo", "Sigtuna", "Torsby",
             "Vik", "Älvsbyn"]
    rows, tot_n, tot_sum = [], 0, 0.0
    for nm in names:
        n = rng.randrange(6, 16)
        m = round(rng.uniform(36, 60), 1)
        sd = round(rng.uniform(12, 22), 1)
        rows.append([nm, str(n), f"{m:.1f}".replace(".", ","), f"{sd:.1f}".replace(".", ",")])
        tot_n += n
        tot_sum += n * m
    overall = round(tot_sum / tot_n, 1)
    rows.append(["All districts", str(tot_n), f"{overall:.1f}".replace(".", ","), "17,9"])
    body = head("Vitamin D in older adults across rural districts: a register-based survey",
                "E. Nyberg, P. Lund and A. Sjöberg",
                "Regional Health Office, Norrvik (fictional)",
                "Course Example Reports in Nutrition 4 (2022) 77-80") + f"""
<p><b>Abstract.</b> We measured serum 25-hydroxyvitamin D (25(OH)D) in adults aged 65 and over in
{len(names)} rural districts. Mean concentrations varied between districts. Decimal commas are
used throughout, as in the original regional report.</p>
<h2>Methods</h2>
<p>Participants were drawn from the regional health register and sampled at their local health
centre between November 2021 and February 2022. Table 1 gives the number of participants, the mean
and the standard deviation of serum 25(OH)D for each district, and for all districts together in
the last row.</p>
<h2>Results</h2>
<p>District means ranged from about 36 to 60 nmol/L. There was no clear north-south gradient.</p>
<p class="cap"><b>Table 1.</b> Serum 25(OH)D (nmol/L) by district.</p>
""" + table(["District", "n", "Mean (nmol/L)", "SD (nmol/L)"], rows, bold_last=True) + """
<h2>Discussion</h2>
<p>Vitamin D status in older rural adults was lower than in the region's towns. The districts with
the lowest means had the oldest participants.</p>
""" + foot()
    path = make_pdf("03_Nyberg-2022.pdf", "Nyberg 2022", body)
    return path, tot_n, overall


def paper04(rng):
    body = head("Vitamin D status in outpatients with chronic kidney disease",
                "C. Okonkwo, R. Haddad and J. Vinter",
                "Renal Outpatient Clinic, Eastholm (fictional)",
                "Course Example Reports in Nutrition 0 (2018) 5-7") + """
<p><b>Abstract.</b> We report serum 25-hydroxyvitamin D (25(OH)D) in outpatients with chronic
kidney disease stages 3 and 4 seen at one clinic during one year.</p>
<h2>Methods</h2>
<p>All adult outpatients with stage 3 or 4 disease seen between January and December 2017 were
eligible. 25(OH)D was measured as part of routine care. Patients taking vitamin D supplements were
included and analysed as a separate group.</p>
""" + foot() + PB + """
<h2>Results</h2>
<p>Ninety-six patients were included. Table 1 gives the results.</p>
<p class="cap"><b>Table 1.</b> Serum 25(OH)D by supplement use.</p>
""" + table(["Group", "n", "Mean 25(OH)D (nmol/L)", "SD (nmol/L)"],
            [["No supplement", "61", "57.2", "21.0"],
             ["Supplement", "35", "81.3", "24.4"],
             ["All patients", "96", "66.0", "25.1"]]) + """
<h2>Discussion</h2>
<p>Patients who took a supplement had clearly higher concentrations.</p>
""" + foot()
    path = make_pdf("04_Okonkwo-2018.pdf", "Okonkwo 2018", body)
    rasterise(path, rng)
    return path


def paper05():
    body = head("Vitamin D and physical activity in office workers: baseline data",
                "D. Petrova, F. Ruiz and H. Tanaka",
                "Occupational Health Unit, Lakemouth (fictional)",
                "Course Example Reports in Nutrition 5 (2023) 102-105") + """
<p><b>Abstract.</b> We recruited 260 office workers to a study of physical activity. At baseline,
the median serum 25-hydroxyvitamin D (25(OH)D) concentration was 42.5 nmol/L.</p>
<h2>Introduction</h2>
<p>A national survey reported a mean 25(OH)D concentration of 71 nmol/L in working-age adults.
Office workers spend most daylight hours indoors and may have lower values.</p>
<h2>Methods</h2>
<p>We recruited 260 office workers from four companies in autumn 2022. Of these, 18 did not attend
the baseline visit, 9 had a haemolysed sample and 4 withdrew consent, leaving 229 participants for
the analysis. 25(OH)D was measured by LC-MS/MS.</p>
""" + foot() + PB + """
<h2>Results</h2>
<p class="cap"><b>Table 1.</b> Characteristics of the 229 analysed participants.</p>
""" + table(["Characteristic", "Value"],
            [["Age, years (mean)", "44.1"],
             ["Women (%)", "57"],
             ["Steps per day (median)", "6 120"]]) + """
<p class="cap"><b>Table 2.</b> Serum 25(OH)D at baseline (n = 229).</p>
""" + table(["Measure", "nmol/L"],
            [["Mean", "44.8"], ["SD", "18.3"], ["Median", "42.5"], ["Interquartile range", "31.0-56.4"]]) + """
<h2>Discussion</h2>
<p>Values were well below the national survey. Workers with more steps per day had slightly higher
concentrations.</p>
""" + foot()
    return make_pdf("05_Petrova-2023.pdf", "Petrova 2023", body)


def paper06():
    main = head("Winter and summer vitamin D in students at a northern university",
                "B. Quint and O. Larsen",
                "Student Health Service, Fjordby (fictional)",
                "Course Example Reports in Nutrition 2 (2020) 60-61") + """
<p><b>Abstract.</b> We measured serum 25-hydroxyvitamin D (25(OH)D) in university students in
February. Most students were below 50 nmol/L. Detailed results are given in the supplementary
material.</p>
<h2>Methods</h2>
<p>Students who visited the student health service for any reason in February 2019 were invited.
Serum 25(OH)D was measured by LC-MS/MS. The number of participants, means and standard deviations
are given in Supplementary Table S1.</p>
<h2>Results and discussion</h2>
<p>Most students were below 50 nmol/L, and students born outside the Nordic countries had lower
values than other students (Supplementary Table S1). A winter supplement should be recommended.</p>
""" + foot()
    p1 = make_pdf("06_Quint-2020.pdf", "Quint 2020", main)
    supp = """<h1>Supplementary material</h1>
<p class="meta">Quint and Larsen (2020), Winter and summer vitamin D in students at a northern
university. <i>Course Example Reports in Nutrition</i> 2: 60-61.</p>
<p class="cap"><b>Table S1.</b> Serum 25(OH)D (nmol/L) in February 2019.</p>
""" + table(["Group", "n", "Mean (nmol/L)", "SD (nmol/L)"],
            [["Born in a Nordic country", "121", "42.0", "15.2"],
             ["Born elsewhere", "37", "31.3", "13.6"],
             ["All students", "158", "39.5", "15.4"]]) + """
<p class="cap"><b>Table S2.</b> Questionnaire items (not shown in the main paper).</p>
<p>1. How many hours per week do you spend outdoors in daylight? 2. Do you take a vitamin D
supplement? 3. Did you travel to a sunny country in the last three months?</p>
""" + foot()
    p2 = make_pdf("06_Quint-2020_supplement.pdf", "Quint 2020 supplement", supp)
    return p1, p2


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    rng = random.Random(SEED)
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    p1 = paper01()
    p2 = paper02()
    p3, n3, m3 = paper03(rng)
    p4 = paper04(rng)
    p5 = paper05()
    p6, p6s = paper06()

    # where is the total row of paper 03?
    last3 = pages(p3)
    tot_page = [p for p in range(1, last3 + 1) if "All districts" in page_text(p3, p)][0]
    start_page = [p for p in range(1, last3 + 1) if "Table 1." in page_text(p3, p)][0]

    key = [
        ["01_Aldersen-2021.pdf", 212, "58.4", "58.4", "nmol/L", "2", "Table 1",
         "easy case; abstract and table agree"],
        ["02_Moreau-2019.pdf", 140, f"{21.6 * NGML_TO_NMOLL:.1f}", "21.6", "ng/mL", "2", "Table 1",
         "table is in ng/mL; 21.6 x 2.496 = 53.9 nmol/L; 152 invited, 140 analysed"],
        ["03_Nyberg-2022.pdf", n3, f"{m3:.1f}", f"{m3:.1f}".replace(".", ","), "nmol/L", str(tot_page),
         "Table 1 (last row)",
         f"table starts on p. {start_page} and runs over the page break without a repeated header; "
         "decimal commas; the total row 'All districts' is on the last page"],
        ["04_Okonkwo-2018.pdf", 96, "66.0", "66.0", "nmol/L", "2", "Table 1",
         "image-only PDF (looks scanned): no text layer, needs OCR or reading the page image"],
        ["05_Petrova-2023.pdf", 229, "44.8", "44.8", "nmol/L", "2", "Table 2",
         "260 recruited but 229 analysed; abstract gives the median (42.5), not the mean; "
         "71 nmol/L in the introduction is another survey"],
        ["06_Quint-2020.pdf", 158, "39.5", "39.5", "nmol/L", "1 (supplement)",
         "Table S1 in 06_Quint-2020_supplement.pdf",
         "the main paper has no numbers; they are in the supplement"],
    ]
    with open(os.path.join(HERE, "answer-key.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["file", "n_analysed", "mean_25ohd_nmol_per_L", "value_as_printed",
                    "unit_as_printed", "page", "table", "difficulty"])
        w.writerows(key)

    zpath = os.path.join(HERE, "papers.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(OUT)):
            z.write(os.path.join(OUT, fn), os.path.join("papers", fn))

    for fn in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, fn)
        txt = subprocess.run(["pdftotext", p, "-"], capture_output=True, text=True).stdout
        print(f"{fn:34s} pages={pages(p)}  text_chars={len(txt.strip()):5d}  "
              f"size={os.path.getsize(p) // 1024} kB")
    print(f"paper 03: table starts p. {start_page}, total row p. {tot_page}, n={n3}, mean={m3}")
    for row in key:
        print(row)
    shutil.rmtree(TMP, ignore_errors=True)
