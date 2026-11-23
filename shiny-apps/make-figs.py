"""Write the SVG figures for shiny-apps/.
Run from the repo root: python3 shiny-apps/make-figs.py shiny-apps"""
import sys, os, math
from xml.sax.saxutils import escape as esc

OUT = sys.argv[1]
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
DARK, MID, LIGHT, PALE, BG = "#1b2a3a", "#5a6670", "#c9d3dd", "#f4f7fa", "#ffffff"
TEAL_L, PURPLE_L, CRIMSON_L, OCHRE_L = "#e3f1f3", "#eee9f6", "#f7e6ea", "#f5efdf"
TERM_BG, TERM_FG = "#1e2630", "#e8edf2"
FONT = "Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def svg(name, w, h, body):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'font-family="{FONT}">\n'
         '  <defs>\n'
         f'    <marker id="arw" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{DARK}"/></marker>\n'
         f'    <marker id="arwt" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{TEAL}"/></marker>\n'
         f'    <marker id="arwc" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{CRIMSON}"/></marker>\n'
         '  </defs>\n'
         f'  <rect x="0" y="0" width="{w}" height="{h}" fill="{BG}"/>\n'
         + body + '</svg>\n')
    with open(os.path.join(OUT, name), "w") as f:
        f.write(s)


def text(x, y, s, size=20, fill=DARK, anchor="start", weight="normal", family=None, style=""):
    fam = f' font-family="{family}"' if family else ""
    st = f' font-style="{style}"' if style else ""
    return (f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{fam}{st} xml:space="preserve">{esc(s)}</text>\n')


def lines(x, y, rows, size=20, fill=DARK, anchor="start", weight="normal", dy=None, family=None):
    dy = dy or size * 1.3
    return "".join(text(x, y + i * dy, r, size, fill, anchor, weight, family) for i, r in enumerate(rows))


def rect(x, y, w, h, fill=PALE, stroke=LIGHT, rx=8, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n'


def line(x1, y1, x2, y2, color=DARK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>\n'


def arrow(x1, y1, x2, y2, color=DARK, sw=2.5, marker="arw", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#{marker})"{d}/>\n'


def path(d, color=DARK, sw=2, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"{da}/>\n'


def circle(cx, cy, r, fill=TEAL, stroke="none", sw=0):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def illustrative(w, h, s="illustrative"):
    return text(w - 10, h - 10, s, 14, "#9aa4ad", "end", style="italic")


def box(x, y, w, h, label, color, fill, size=18, weight="bold"):
    rows = label.split("\n")
    b = rect(x, y, w, h, fill, color, rx=10, sw=2)
    y0 = y + h / 2 - (len(rows) - 1) * size * 0.65 + size * 0.35
    for i, r in enumerate(rows):
        b += text(x + w / 2, y0 + i * size * 1.3, r, size, DARK if i else color, "middle",
                  weight if i == 0 else "normal")
    return b


def terminal(x, y, w, h, title, rows, size=18, dy=None):
    """rows: list of (text, color) or str."""
    dy = dy or size * 1.45
    b = rect(x, y, w, h, TERM_BG, "#3a4654", rx=10, sw=1.5)
    b += f'  <rect x="{x}" y="{y}" width="{w}" height="34" rx="10" fill="#2d3743"/>\n'
    b += f'  <rect x="{x}" y="{y+24}" width="{w}" height="10" fill="#2d3743"/>\n'
    for i, c in enumerate(["#e0605a", "#e6b84f", "#5fbf6a"]):
        b += f'  <circle cx="{x+20+i*22}" cy="{y+17}" r="6.5" fill="{c}"/>\n'
    b += text(x + w / 2, y + 23, title, 15, "#b8c2cc", "middle")
    for i, r in enumerate(rows):
        if isinstance(r, str):
            r = (r, TERM_FG)
        b += text(x + 18, y + 34 + 28 + i * dy, r[0], size, r[1], family=MONO)
    return b


def browser(x, y, w, h, url, size=15):
    b = rect(x, y, w, h, "#ffffff", "#9aa4ad", rx=10, sw=1.5)
    b += f'  <rect x="{x}" y="{y}" width="{w}" height="40" rx="10" fill="#e9edf1"/>\n'
    b += f'  <rect x="{x}" y="{y+30}" width="{w}" height="10" fill="#e9edf1"/>\n'
    for i, c in enumerate(["#e0605a", "#e6b84f", "#5fbf6a"]):
        b += f'  <circle cx="{x+18+i*20}" cy="{y+20}" r="6" fill="{c}"/>\n'
    b += rect(x + 80, y + 8, w - 95, 24, "#ffffff", "#c9d3dd", rx=12, sw=1)
    b += text(x + 94, y + 25, url, size, MID)
    return b


def slider(x, y, w, frac, label, size=16, color=TEAL):
    b = text(x, y, label, size, DARK, weight="bold")
    b += line(x, y + 16, x + w, y + 16, "#c9d3dd", 6)
    b += line(x, y + 16, x + w * frac, y + 16, color, 6)
    b += circle(x + w * frac, y + 16, 9, "#ffffff", color, 3)
    return b


def button(x, y, w, label, size=15, h=30):
    b = rect(x, y, w, h, TEAL_L, TEAL, rx=6, sw=1.5)
    b += text(x + w / 2, y + h / 2 + size * 0.35, label, size, DARK, "middle")
    return b


def scurve(x0, y0, w, h, r=0.5, K=800, N0=10, tmax=40, nmax=1000, n=80):
    pts = []
    for i in range(n + 1):
        t = tmax * i / n
        N = K / (1 + (K - N0) / N0 * math.exp(-r * t))
        pts.append((x0 + w * t / tmax, y0 + h - h * N / nmax))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def axes(x0, y0, w, h, color="#9aa4ad"):
    return line(x0, y0 + h, x0 + w, y0 + h, color, 2) + line(x0, y0, x0, y0 + h, color, 2)


import csv

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(open(os.path.join(HERE, "data", "water-quality.csv"))))
SITE_COL = {"Alder Lake": TEAL, "Mill Creek": PURPLE, "North Pond": CRIMSON, "Stone River": OCHRE}


def series_path(site, var, x0, y0, w, h, vmin, vmax, d0="2022-01-01", d1="2024-12-31"):
    import datetime as dt
    a = dt.date.fromisoformat(d0); bdate = dt.date.fromisoformat(d1)
    span = (bdate - a).days
    pts = []
    for r in ROWS:
        if r["site"] != site or r[var] in ("", "NA"):
            continue
        d = dt.date.fromisoformat(r["date"])
        if d < a or d > bdate:
            continue
        v = float(r[var])
        pts.append((x0 + w * (d - a).days / span, y0 + h - h * (v - vmin) / (vmax - vmin)))
    return "M" + " L".join(f"{p:.1f},{q:.1f}" for p, q in pts), pts


def checkbox(x, y, label, on=True, size=15):
    b = rect(x, y - 13, 16, 16, TEAL if on else "#ffffff", TEAL if on else MID, rx=3, sw=1.5)
    if on:
        b += path(f"M{x+3},{y-5} l4,4 l7,-8", "#ffffff", 2.2)
    b += text(x + 24, y, label, size, DARK)
    return b


def app_mock(x, y, w, h, url="127.0.0.1:4321", sites=("Alder Lake", "Mill Creek"), small=False):
    b = browser(x, y, w, h, url, 14)
    b += text(x + 20, y + 72, "Water quality at four sites, 2022-2024 (synthetic data)", 17, DARK, weight="bold")
    sx, sy = x + 18, y + 88
    b += rect(sx, sy, 220, h - 105, PALE, LIGHT, rx=6)
    b += text(sx + 12, sy + 26, "Sites", 14, DARK, weight="bold")
    for i, s in enumerate(["Alder Lake", "Mill Creek", "North Pond", "Stone River"]):
        b += checkbox(sx + 14, sy + 52 + i * 24, s, s in sites, 14)
    b += text(sx + 12, sy + 160, "Dates", 14, DARK, weight="bold")
    b += rect(sx + 12, sy + 168, 90, 24, "#ffffff", LIGHT, rx=4)
    b += rect(sx + 116, sy + 168, 90, 24, "#ffffff", LIGHT, rx=4)
    b += text(sx + 18, sy + 185, "2022-01-05", 13, DARK)
    b += text(sx + 122, sy + 185, "2024-12-19", 13, DARK)
    b += text(sx + 12, sy + 218, "Measurement", 14, DARK, weight="bold")
    b += rect(sx + 12, sy + 226, 194, 26, "#ffffff", LIGHT, rx=4)
    b += text(sx + 20, sy + 244, "Nitrate (mg/L)   ▾", 13, DARK)
    b += checkbox(sx + 14, sy + 280, "Trend line per site", False, 13)
    b += rect(sx + 12, sy + 296, 194, 28, TEAL_L, TEAL, rx=5)
    b += text(sx + 109, sy + 315, "Download (CSV)", 13, DARK, "middle")
    # plot
    px, py, pw, ph = x + 270, y + 95, w - 300, 190 if not small else 150
    b += axes(px, py, pw, ph)
    for v in [0, 1, 2, 3, 4, 5]:
        yy = py + ph - ph * v / 5
        b += text(px - 6, yy + 4, str(v), 12, MID, "end")
    for i, yr in enumerate(["2022", "2023", "2024"]):
        b += text(px + pw * (i + 0.5) / 3, py + ph + 16, yr, 12, MID, "middle")
    for s in sites:
        d, pts = series_path(s, "nitrate_mg_l", px, py, pw, ph, 0, 5)
        b += path(d, SITE_COL[s], 1.5)
        for p, q in pts:
            b += circle(p, q, 2.2, SITE_COL[s])
    return b, (px, py, pw, ph)


# ---------------------------------------------------------------- fig01
def fig01():
    W, H = 1000, 460
    mails = [("From: a colleague", "Could you send me the nitrate plot", "for Mill Creek only?"),
             ("From: a student", "What was the mean temperature", "at North Pond in 2023?"),
             ("From: the project leader", "Can I have the numbers behind", "figure 2, but for 2024?")]
    b = ""
    for i, (a, l1, l2) in enumerate(mails):
        y = 30 + i * 125
        b += rect(30, y, 400, 105, "#ffffff", LIGHT, rx=8)
        b += text(50, y + 30, a, 15, MID, weight="bold")
        b += text(50, y + 60, l1, 18, DARK)
        b += text(50, y + 86, l2, 18, DARK)
        b += arrow(435, y + 52, 555, 200 + (i - 1) * 25)
    b += circle(615, 200, 55, PURPLE_L, PURPLE, 2.5)
    b += text(615, 207, "you", 22, PURPLE, "middle", "bold")
    b += lines(690, 170, ["open the data,", "filter, plot, export,", "reply ... every week"], 19, DARK, dy=27)
    b += text(500, 435, "Same data, different small questions. Each one costs you half an hour.", 19, CRIMSON, "middle", "bold")
    svg("fig01-requests.svg", W, H, b)


# ---------------------------------------------------------------- fig02
def fig02():
    W, H = 1000, 520
    b, (px, py, pw, ph) = app_mock(20, 20, 960, 440)
    # summary table
    tx, ty = px, py + ph + 40
    b += text(tx, ty, "Summary of the selected rows", 14, DARK, weight="bold")
    hdr = ["site", "samples", "missing", "mean", "min", "max"]
    rows = [["Alder Lake", "72", "0", "0.60", "0.32", "0.89"], ["Mill Creek", "72", "0", "2.72", "1.49", "4.65"]]
    for j, hname in enumerate(hdr):
        b += text(tx + j * 100, ty + 26, hname, 13, MID, weight="bold")
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            b += text(tx + j * 100, ty + 50 + i * 22, c, 13, DARK)
    b += rect(26, 104, 232, 350, "none", OCHRE, rx=8, sw=3)
    b += text(142, 495, "inputs: what the user chooses", 17, OCHRE, "middle", "bold")
    b += rect(266, 104, 706, 350, "none", TEAL, rx=8, sw=3)
    b += text(627, 495, "outputs: update by themselves", 17, TEAL, "middle", "bold")
    svg("fig02-app-mock.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig03
def fig03():
    W, H = 1000, 420
    b = text(140, 40, "Inputs", 22, OCHRE, "middle", "bold")
    for i, t in enumerate(["sites (tick boxes)", "dates (from, to)", "measurement (menu)"]):
        b += box(20, 60 + i * 90, 240, 70, t, OCHRE, OCHRE_L, 17, "normal")
    b += box(370, 140, 240, 110, "Selected rows\nthe data, filtered", PURPLE, PURPLE_L, 19)
    for i in range(3):
        b += arrow(262, 95 + i * 90, 365, 195)
    b += text(860, 40, "Outputs", 22, TEAL, "middle", "bold")
    for i, t in enumerate(["plot over time", "summary table", "download button"]):
        b += box(740, 60 + i * 90, 240, 70, t, TEAL, TEAL_L, 17, "normal")
        b += arrow(612, 195, 735, 95 + i * 90, TEAL, 2.5, "arwt")
    b += text(500, 360, "Change an input, and everything that depends on it is recomputed.", 19, DARK, "middle")
    b += text(500, 392, "The script describes these connections once; Shiny keeps them up to date.", 18, MID, "middle")
    svg("fig03-inputs-outputs.svg", W, H, b)


# ---------------------------------------------------------------- fig04
def fig04():
    W, H = 1000, 470
    cols = ["site", "date", "temperature_c", "ph", "nitrate_mg_l", "oxygen_mg_l"]
    widths = [150, 130, 160, 90, 160, 160]
    x0, y0 = 40, 40
    b = rect(x0 - 30, y0 - 30, 880, 360, "#ffffff", LIGHT, rx=6)
    xs = [x0]
    for wd in widths:
        xs.append(xs[-1] + wd)
    b += f'  <rect x="{x0}" y="{y0}" width="{xs[-1]-x0}" height="32" fill="{TEAL_L}"/>\n'
    for j, c in enumerate(cols):
        b += text(xs[j] + 8, y0 + 22, c, 16, DARK, weight="bold")
    show = ROWS[:4] + ROWS[4:8]
    # include one row with NA
    na = [r for r in ROWS if r["oxygen_mg_l"] in ("NA", "")][0]
    show = ROWS[:6] + [na]
    for i, r in enumerate(show):
        y = y0 + 32 + i * 34
        b += line(x0, y, xs[-1], y, "#e3e7eb", 1)
        for j, c in enumerate(cols):
            v = r[c]
            col = CRIMSON if v in ("NA", "") else DARK
            b += text(xs[j] + 8, y + 23, v if v else "NA", 16, col, family=MONO if j > 1 else None)
    b += text(x0 + 8, y0 + 32 + 7 * 34 + 24, "...", 18, MID)
    for xx in xs:
        b += line(xx, y0, xx, y0 + 32 + 7 * 34, "#e3e7eb", 1)
    b += lines(40, 390, ["288 rows: 4 sites, sampled twice a month from 2022 to 2024.",
                         "Invented numbers. Six values are missing on purpose: a broken oxygen probe, two lost pH readings."], 18, DARK, dy=26)
    svg("fig04-dataset.svg", W, H, b + illustrative(W, H, "water-quality.csv, first rows and one missing value"))


# ---------------------------------------------------------------- fig05
def fig05():
    W, H = 1000, 520
    rows = [
        ("> Make a Shiny app in app.R for water-quality.csv ...", "#9fe0ea"),
        ("● I'll write app.R with a sidebar of filters, a plot,", TERM_FG),
        ("  a summary table and a download button.", TERM_FG),
        ("  Write(app.R)   +96 lines", "#e6b84f"),
        ("● The app needs the R package shiny. Install it?", TERM_FG),
        ("  Rscript -e 'install.packages(\"shiny\")'", "#ffffff"),
        ("  Do you want to proceed?   > 1. Yes    2. No", "#e6b84f"),
        ("● Start the app with:  Rscript -e 'shiny::runApp()'", TERM_FG),
        ("  Then open the address it prints in your browser.", TERM_FG),
    ]
    b = terminal(20, 20, 960, 380, "water-app: agent session", rows, 18, 34)
    b += rect(28, 192, 700, 104, "none", "#e6b84f", rx=6, sw=2.5)
    b += lines(30, 440, ["Installing shiny (and ggplot2) is a normal, one-time step: read the command, then say yes.",
                         "The agent should not install anything you did not expect; ask what it is if unsure."], 17, DARK, dy=26)
    svg("fig05-session.svg", W, H, b + illustrative(W, H, "illustrative: your session will look different"))


# ---------------------------------------------------------------- fig06
def fig06():
    W, H = 1000, 500
    rows = [("$ Rscript -e 'shiny::runApp()'", "#9fe0ea"), "",
            ("Listening on http://127.0.0.1:4321", "#c8e6a0"), "", ("(runs until you press Ctrl+C)", "#9aa4ad")]
    b = terminal(20, 30, 420, 240, "terminal", rows, 16, 28)
    b += arrow(445, 150, 495, 150)
    m, _ = app_mock(500, 30, 480, 330, small=True)
    # crop app mock: draw just a simplified browser
    b += browser(500, 30, 480, 330, "127.0.0.1:4321", 14)
    b += text(520, 100, "Water quality at four sites", 17, DARK, weight="bold")
    b += rect(520, 120, 130, 210, PALE, LIGHT, rx=6)
    for i, s in enumerate(["Alder Lake", "Mill Creek", "North Pond", "Stone River"]):
        b += checkbox(532, 150 + i * 26, s, i < 2, 13)
    px, py, pw, ph = 680, 125, 280, 190
    b += axes(px, py, pw, ph)
    for s in ["Alder Lake", "Mill Creek"]:
        d, pts = series_path(s, "nitrate_mg_l", px, py, pw, ph, 0, 5)
        b += path(d, SITE_COL[s], 1.5)
    b += rect(584, 36, 112, 28, "none", CRIMSON, rx=6, sw=2.5)
    b += lines(20, 320, ["127.0.0.1 means \"this computer\".", "Nobody else can open this address."], 19, DARK, dy=27)
    b += lines(20, 400, ["Stop the app: Ctrl+C in the terminal.", "Change app.R, then start it again", "(or reload, if your tool restarts it for you)."], 17, MID, dy=24)
    svg("fig06-run-local.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig07
def fig07():
    W, H = 1000, 440
    b = text(230, 36, "In the app", 22, TEAL, "middle", "bold")
    b += rect(20, 55, 420, 270, "#ffffff", LIGHT, rx=8)
    b += lines(40, 90, ["Sites: Mill Creek", "Dates: 2023-01-01 to 2023-12-31", "Measurement: Nitrate (mg/L)"], 16, MID, dy=24)
    hdr = ["site", "samples", "missing", "mean"]
    for j, hname in enumerate(hdr):
        b += text(40 + j * 100, 190, hname, 16, MID, weight="bold")
    for j, c in enumerate(["Mill Creek", "24", "0", "2.66"]):
        b += text(40 + j * 100, 222, c, 17, DARK)
    b += rect(330, 200, 70, 32, "none", TEAL, rx=6, sw=3)
    b += text(770, 36, "In the spreadsheet", 22, OCHRE, "middle", "bold")
    b += rect(560, 55, 420, 270, "#ffffff", LIGHT, rx=8)
    b += lines(580, 90, ["Filter: site = Mill Creek", "Filter: date begins with 2023", "Select the nitrate column:"], 16, MID, dy=24)
    b += rect(580, 175, 380, 36, PALE, LIGHT, rx=4)
    b += text(592, 199, "Count: 24    Average: 2.66", 17, DARK, family=MONO)
    b += rect(700, 175, 120, 36, "none", OCHRE, rx=6, sw=3)
    b += text(500, 200, "=", 40, DARK, "middle", "bold")
    b += lines(500, 370, ["Pick one filter setting, compute the same number by hand,",
                          "and compare. Then change the filter and do it once more."], 19, DARK, "middle", dy=28)
    svg("fig07-check-number.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig08
def fig08():
    W, H = 1000, 470
    cases = [("No site ticked", "Choose at least one site.", "red error text,\nor an empty plot"),
             ("Dates with no samples", "No samples in this\ndate range.", "the app stops\nwith an error"),
             ("Oxygen, North Pond 2023", "24 samples, 4 missing,\nmean 11.78", "mean = NA,\nor rows silently lost")]
    b = ""
    for i, (t, good, bad) in enumerate(cases):
        x = 20 + i * 325
        b += text(x + 152, 36, t, 19, DARK, "middle", "bold")
        b += rect(x, 55, 305, 150, TEAL_L, TEAL, rx=10, sw=2)
        b += text(x + 18, 85, "good", 16, TEAL, weight="bold")
        b += lines(x + 18, 120, good.split("\n"), 18, DARK, dy=26)
        b += rect(x, 225, 305, 130, CRIMSON_L, CRIMSON, rx=10, sw=2)
        b += text(x + 18, 255, "bad", 16, CRIMSON, weight="bold")
        b += lines(x + 18, 290, bad.split("\n"), 18, DARK, dy=26)
    b += text(500, 410, "Try to break the app on purpose. A good app says what is wrong in plain words,", 18, DARK, "middle")
    b += text(500, 438, "and counts missing values instead of hiding them.", 18, DARK, "middle")
    svg("fig08-break-it.svg", W, H, b)


# ---------------------------------------------------------------- fig09
def fig09():
    W, H = 1000, 520
    cols = [
        ("Shinylive", "static files, e.g. on GitHub Pages", TEAL, TEAL_L,
         [("the app runs in the", "visitor's browser"), ("no server to run;", "free, next to your page"), ("all data is public", "")]),
        ("Hosted server", "shinyapps.io, Posit Connect Cloud", PURPLE, PURPLE_L,
         [("R or Python runs on", "the provider's server"), ("an account; free tiers", "have limits"), ("login only on", "some paid plans")]),
        ("University server", "Shiny Server or Posit Connect, run by IT", OCHRE, OCHRE_L,
         [("runs inside the", "university"), ("data stays in-house;", "login possible"), ("ask IT whether", "one exists")]),
    ]
    b = ""
    for i, (t, sub, c, cl, items) in enumerate(cols):
        x = 20 + i * 325
        b += rect(x, 20, 305, 420, cl, c, rx=12, sw=2)
        b += text(x + 152, 60, t, 24, c, "middle", "bold")
        b += lines(x + 152, 90, [sub] if len(sub) < 34 else [sub[:sub.index(",")+1], sub[sub.index(",")+2:]], 15, MID, "middle", dy=20)
        for j, (l1, l2) in enumerate(items):
            yy = 165 + j * 90
            red = (i == 0 and j == 2)
            b += circle(x + 30, yy - 6, 5, c)
            b += text(x + 45, yy, l1, 19, CRIMSON if red else DARK, weight="bold" if red else "normal")
            b += text(x + 45, yy + 26, l2, 19, DARK)
    b += text(500, 490, "Same app.R in all three. What changes is where the code runs and who can see the data.", 18, DARK, "middle")
    svg("fig09-three-ways.svg", W, H, b)


# ---------------------------------------------------------------- fig10
def fig10():
    W, H = 1000, 500
    b = text(170, 36, "GitHub Pages", 22, MID, "middle", "bold")
    b += rect(20, 55, 300, 300, PALE, LIGHT, rx=10)
    files = [("index.html", DARK), ("app.json", TEAL), ("   app.R + water-quality.csv", TEAL),
             ("shinylive/", DARK), ("   R for the browser (webR)", MID), ("   packages: shiny, ggplot2 ...", MID)]
    for i, (f, c) in enumerate(files):
        b += text(40, 95 + i * 38, f, 17, c, family=MONO if not f.startswith("   ") else None)
    b += text(170, 385, "only stores and sends files;", 16, MID, "middle")
    b += text(170, 407, "no R runs here", 16, MID, "middle")
    b += arrow(330, 200, 520, 200, DARK, 3)
    b += lines(425, 170, ["download, once", "(several MB)"], 16, DARK, "middle", dy=20)
    b += text(750, 36, "The visitor's browser", 22, TEAL, "middle", "bold")
    b += browser(530, 55, 450, 300, "you.github.io/my-project/water-app/", 13)
    b += rect(550, 110, 410, 225, TEAL_L, TEAL, rx=8, sw=2)
    b += text(755, 145, "R runs here, inside the browser", 18, TEAL, "middle", "bold")
    b += text(755, 175, "app.R reads water-quality.csv", 16, DARK, "middle")
    b += axes(600, 195, 310, 120)
    for s in ["Alder Lake", "Mill Creek"]:
        d, pts = series_path(s, "nitrate_mg_l", 600, 195, 310, 120, 0, 5)
        b += path(d, SITE_COL[s], 1.5)
    b += lines(500, 450, ["The first visit is slow while R loads; later visits use the browser's cache.",
                          "No server means nothing to maintain, and nothing kept secret."], 18, DARK, "middle", dy=26)
    svg("fig10-shinylive-how.svg", W, H, b + "")


# ---------------------------------------------------------------- fig11
def fig11():
    W, H = 1000, 500
    b = browser(20, 20, 960, 400, "you.github.io/my-project/water-app/", 14)
    b += rect(20, 60, 960, 34, "#e9edf1", "#c9d3dd", rx=0, sw=1)
    for i, t in enumerate(["Elements", "Console", "Network", "Sources"]):
        b += text(50 + i * 110, 83, t, 15, TEAL if t == "Network" else MID, weight="bold" if t == "Network" else "normal")
    b += line(270, 92, 350, 92, TEAL, 3)
    names = [("index.html", "3 kB"), ("app.json", "26 kB"), ("webR.wasm", "large"), ("shiny (package)", "large"), ("ggplot2 (package)", "large")]
    for i, (n, s) in enumerate(names):
        y = 125 + i * 34
        if n == "app.json":
            b += rect(30, y - 22, 380, 32, TEAL_L, TEAL, rx=4, sw=2)
        b += text(45, y, n, 16, DARK, family=MONO)
        b += text(395, y, s, 15, MID, "end")
    b += line(420, 100, 420, 410, LIGHT, 1.5)
    b += text(440, 125, "app.json  >  files  >  water-quality.csv", 15, MID, family=MONO)
    csvrows = ['"site","date","temperature_c","ph",...', '"Alder Lake","2022-01-05",3.5,7.18,...',
               '"Mill Creek","2022-01-05",3.7,6.88,...', '"North Pond","2022-01-05",3.4,7.86,...', '... all 288 rows']
    for i, r in enumerate(csvrows):
        b += text(440, 160 + i * 30, r, 15, DARK, family=MONO)
    b += rect(432, 136, 535, 160, "none", CRIMSON, rx=6, sw=3)
    b += text(700, 330, "every row, every column, even the ones", 17, CRIMSON, "middle", "bold")
    b += text(700, 354, "the app never shows on screen", 17, CRIMSON, "middle", "bold")
    b += text(500, 465, "Any visitor can open the browser's developer tools (F12) and save the data.", 19, DARK, "middle")
    svg("fig11-data-ships.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig12
def fig12():
    W, H = 1000, 500
    b = text(20, 32, "Project folder (private)", 19, PURPLE, weight="bold")
    b += rect(20, 45, 330, 220, PURPLE_L, PURPLE, rx=8, sw=1.5)
    tree = [("my-project/", DARK, "bold"), ("  README.md", DARK, "normal"), ("  apps/", DARK, "bold"),
            ("    water-app/", PURPLE, "bold"), ("      app.R", PURPLE, "normal"), ("      water-quality.csv", PURPLE, "normal")]
    for i, (t, c, wgt) in enumerate(tree):
        b += text(35, 78 + i * 32, t, 17, c, weight=wgt, family=MONO)
    b += text(35, 290, "source: you edit and check it here", 15, PURPLE, weight="bold")
    b += arrow(355, 190, 420, 190, TEAL, 3, "arwt")
    b += lines(388, 160, ["shinylive", "export"], 14, TEAL, "middle", "bold", dy=17)
    b += text(430, 32, "Page folder (public)", 19, TEAL, weight="bold")
    b += rect(430, 45, 330, 290, TEAL_L, TEAL, rx=8, sw=1.5)
    tree2 = [("my-project-page/", DARK, "bold"), ("  _quarto.yml", DARK, "normal"), ("  index.qmd", DARK, "normal"),
             ("  explorer.qmd", DARK, "normal"), ("  water-app-site/", TEAL, "bold"), ("  docs/", DARK, "bold"),
             ("    water-app-site/", TEAL, "normal"), ("    explorer.html ...", DARK, "normal")]
    for i, (t, c, wgt) in enumerate(tree2):
        b += text(445, 78 + i * 32, t, 17, c, weight=wgt, family=MONO)
    b += arrow(765, 270, 830, 270, DARK, 3)
    b += lines(797, 240, ["push"], 14, DARK, "middle", "bold")
    b += browser(835, 45, 150, 290, "github.io", 12)
    b += lines(910, 120, ["Data", "explorer"], 15, DARK, "middle", "bold", dy=20)
    b += rect(850, 170, 120, 120, "#ffffff", TEAL, rx=6, sw=2, dash="5 4")
    b += lines(910, 220, ["the app", "runs here"], 14, TEAL, "middle", dy=18)
    b += lines(500, 390, ["Only the export goes into the public page folder: it holds app.R and the data file.",
                          "_quarto.yml lists water-app-site under resources, so rendering copies it into docs/.",
                          "Re-export after every change to the app; never edit the export by hand."], 17, DARK, "middle", dy=26)
    svg("fig12-site-layout.svg", W, H, b + illustrative(W, H, "illustrative: folder names are examples"))


# ---------------------------------------------------------------- fig13
def fig13():
    W, H = 1000, 560
    b = box(270, 20, 460, 80, "May anyone in the world\ndownload all of this data?", DARK, PALE, 19)
    b += arrow(400, 102, 230, 160)
    b += text(290, 140, "yes", 17, TEAL, "end", "bold")
    b += arrow(600, 102, 770, 160)
    b += text(710, 140, "no", 17, CRIMSON, "start", "bold")
    b += box(40, 165, 380, 90, "Does it need secrets, a database,\nlarge data or unusual packages?", DARK, PALE, 17)
    b += arrow(130, 258, 130, 320)
    b += text(120, 295, "no", 17, TEAL, "end", "bold")
    b += arrow(330, 258, 330, 320)
    b += text(340, 295, "yes", 17, OCHRE, "start", "bold")
    b += box(20, 325, 220, 110, "Shinylive\non GitHub Pages", TEAL, TEAL_L, 20)
    b += box(255, 325, 200, 110, "A server\nhosted or university", PURPLE, PURPLE_L, 18)
    b += box(560, 165, 420, 90, "Personal, sensitive or\ngiven in confidence?", DARK, PALE, 18)
    b += arrow(650, 258, 650, 320)
    b += text(640, 295, "no (internal)", 17, OCHRE, "end", "bold")
    b += arrow(880, 258, 880, 320)
    b += text(890, 295, "yes", 17, CRIMSON, "start", "bold")
    b += box(530, 325, 230, 110, "Server with login\nin the university", OCHRE, OCHRE_L, 18)
    b += box(775, 325, 215, 110, "Do not publish\nuse aggregated or\nsynthetic data", CRIMSON, CRIMSON_L, 17)
    b += text(500, 490, "A login protects who can open the app. It does not change what the app shows", 18, DARK, "middle")
    b += text(500, 516, "to those who can. Ask the data owner before anything leaves your computer.", 18, DARK, "middle")
    svg("fig13-choose-host.svg", W, H, b)


for f in [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12, fig13]:
    f()
print("ok")
