"""Write the SVG figures for interactive-demos/.
Run from the repo root: python3 interactive-demos/make-figs.py interactive-demos"""
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


# ---------------------------------------------------------------- fig01
def fig01():
    W, H = 1000, 500
    b = text(255, 40, "A figure in the textbook", 22, MID, "middle", "bold")
    b += rect(40, 60, 430, 330, PALE, LIGHT)
    b += axes(90, 90, 340, 230)
    b += path(scurve(90, 90, 340, 230), TEAL, 4)
    b += line(90, 90 + 230 - 230 * 0.8, 430, 90 + 230 - 230 * 0.8, CRIMSON, 2, "8 6")
    b += text(425, 90 + 230 - 230 * 0.8 - 8, "K", 18, CRIMSON, "end", "bold")
    b += text(260, 350, "time", 16, MID, "middle")
    b += text(65, 205, "N", 16, MID, "middle")
    b += text(60, 378, "Fig. 3. Logistic growth, r = 0.5, K = 800.", 16, MID, style="italic")
    b += lines(255, 430, ["One set of numbers. Students read it once", "and may not see why it bends."], 18, MID, "middle")

    b += text(745, 40, "A demo", 22, TEAL, "middle", "bold")
    b += browser(530, 60, 430, 330, "logistic-growth.html", 14)
    b += slider(555, 125, 150, 0.35, "r", 16)
    b += slider(555, 185, 150, 0.75, "K", 16)
    b += button(555, 235, 80, "Reset", 14)
    b += axes(735, 115, 200, 200)
    b += path(scurve(735, 115, 200, 200, 0.5, 750, 10, 40, 1000), TEAL, 3.5)
    b += path(scurve(735, 115, 200, 200, 0.5, 450, 10, 40, 1000), TEAL, 2, dash="5 5")
    b += line(735, 115 + 200 - 200 * 0.75, 935, 115 + 200 - 200 * 0.75, CRIMSON, 2, "8 6")
    b += circle(925, 115 + 200 - 200 * 0.75, 8, CRIMSON)
    b += arrow(925, 135, 925, 155, CRIMSON, 2.5, "arwc")
    b += text(912, 133, "drag", 15, CRIMSON, "end", "bold")
    b += text(560, 350, "Students change r and K and", 16, MID)
    b += text(560, 372, "watch where the curve bends.", 16, MID)
    b += lines(745, 430, ["Same model. Now the student asks", "the questions and sees the answers."], 18, TEAL, "middle", "bold")
    svg("fig01-static-vs-demo.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig02
def fig02():
    W, H = 1000, 500
    # file icon
    fx, fy = 400, 150
    b = f'  <path d="M{fx},{fy} h150 l50,50 v170 h-200 z" fill="{TEAL_L}" stroke="{TEAL}" stroke-width="3"/>\n'
    b += f'  <path d="M{fx+150},{fy} v50 h50" fill="none" stroke="{TEAL}" stroke-width="3"/>\n'
    b += text(fx + 100, fy + 95, "my-demo.html", 20, TEAL, "middle", "bold")
    b += lines(fx + 100, fy + 135, ["page + style", "+ JavaScript", "in one file"], 17, DARK, "middle")
    b += text(fx + 100, fy + 245, "typically 10-50 kB", 16, MID, "middle", style="italic")
    targets = [
        (40, 40, "Any browser", "double-click to open", TEAL, TEAL_L),
        (720, 40, "A phone", "same file, touch works", PURPLE, PURPLE_L),
        (40, 360, "Your course page", "embedded with one line", OCHRE, OCHRE_L),
        (720, 360, "Offline", "no internet, no install", CRIMSON, CRIMSON_L),
    ]
    for x, y, t1, t2, c, cl in targets:
        b += box(x, y, 240, 90, f"{t1}\n{t2}", c, cl, 19)
    b += arrow(395, 190, 285, 120)
    b += arrow(605, 190, 715, 120)
    b += arrow(395, 330, 285, 385)
    b += arrow(605, 330, 715, 385)
    svg("fig02-one-file.svg", W, H, b)


# ---------------------------------------------------------------- fig03
def fig03():
    W, H = 1000, 580
    tiles = [(20, 20), (510, 20), (20, 290), (510, 290)]
    tw, th = 470, 250
    b = ""
    for (x, y) in tiles:
        b += rect(x, y, tw, th, "#ffffff", LIGHT, rx=10, sw=1.5)
    # 1 dot product
    x, y = tiles[0]
    b += text(x + 15, y + 30, "Dot product: drag the arrows", 18, TEAL, weight="bold")
    ox, oy = x + 60, y + 190
    b += axes(ox, y + 50, 180, 140)
    b += arrow(ox, oy, ox + 150, oy - 60, TEAL, 4, "arwt")
    b += arrow(ox, oy, ox + 70, oy - 120, PURPLE, 4)
    b += path(f"M{ox+50},{oy-20} A54,54 0 0,0 {ox+28},{oy-48}", OCHRE, 2.5)
    b += circle(ox + 150, oy - 60, 8, TEAL)
    b += circle(ox + 70, oy - 120, 8, PURPLE)
    b += lines(x + 270, y + 80, ["cos θ = 0.71", "distance = 2.3", "depth × 2:", "cos θ = 0.71"], 16, DARK, dy=24, family=MONO)
    b += text(x + 15, y + 232, "Discover: scaling changes the distance, not the angle.", 16, MID, style="italic")
    # 2 walkers
    x, y = tiles[1]
    b += text(x + 15, y + 30, "Random walkers on a state diagram", 18, TEAL, weight="bold")
    centres = [(x + 90, y + 115), (x + 230, y + 80), (x + 195, y + 175)]
    for (cx, cy), lab in zip(centres, "ABC"):
        b += circle(cx, cy, 34, PURPLE_L, PURPLE, 2.5)
        b += text(cx, cy - 10, lab, 18, PURPLE, "middle", "bold")
    b += arrow(122, 0, 0, 0) if False else ""
    b += arrow(centres[0][0] + 34, centres[0][1] - 12, centres[1][0] - 36, centres[1][1] + 4)
    b += arrow(centres[1][0] - 4, centres[1][1] + 36, centres[2][0] + 6, centres[2][1] - 36)
    b += arrow(centres[2][0] - 34, centres[2][1] - 8, centres[0][0] + 26, centres[0][1] + 26)
    import random
    rnd = random.Random(3)
    for (cx, cy), n in zip(centres, [7, 4, 9]):
        for _ in range(n):
            a = rnd.uniform(0.3, 2.84); rr = rnd.uniform(6, 22)
            b += circle(cx + rr * math.cos(a), cy + rr * math.sin(a), 3.5, OCHRE)
    for i, (lab, v) in enumerate([("A", 0.35), ("B", 0.20), ("C", 0.45)]):
        b += text(x + 320, y + 90 + i * 40, lab, 16, DARK, weight="bold")
        b += rect(x + 340, y + 75 + i * 40, 110 * v / 0.45, 20, PURPLE_L, PURPLE, rx=3, sw=1.5)
    b += text(x + 15, y + 232, "Discover: the fractions settle, the walkers never do.", 16, MID, style="italic")
    # 3 poisson
    x, y = tiles[2]
    b += text(x + 15, y + 30, "Random events along a line", 18, TEAL, weight="bold")
    rnd = random.Random(11)
    pos = sorted(rnd.uniform(0, 430) for _ in range(28))
    b += line(x + 20, y + 80, x + 450, y + 80, "#9aa4ad", 2)
    for p in pos:
        b += line(x + 20 + p, y + 66, x + 20 + p, y + 94, CRIMSON, 2.5)
    counts = [1, 4, 7, 6, 4, 2, 1]
    for i, c in enumerate(counts):
        b += rect(x + 60 + i * 50, y + 205 - c * 13, 40, c * 13, TEAL_L, TEAL, rx=2, sw=1.5)
    b += text(x + 15, y + 232, "Discover: random events cluster more than you expect.", 16, MID, style="italic")
    # 4 leakage
    x, y = tiles[3]
    b += text(x + 15, y + 30, "Cross-validation on pure noise", 18, TEAL, weight="bold")
    b += text(x + 115, y + 62, "leaky", 16, CRIMSON, "middle", "bold")
    b += text(x + 345, y + 62, "honest", 16, TEAL, "middle", "bold")
    for k, (cx, col, cl) in enumerate([(x + 115, CRIMSON, CRIMSON_L), (x + 345, TEAL, TEAL_L)]):
        hs = [1, 3, 6, 8, 5, 2] if k == 0 else [2, 5, 8, 6, 3, 1]
        off = 30 if k == 0 else -10
        for i, hh in enumerate(hs):
            b += rect(cx - 75 + off + i * 22, y + 195 - hh * 13, 20, hh * 13, cl, col, rx=2, sw=1.5)
        b += line(cx - 20, y + 75, cx - 20, y + 200, "#9aa4ad", 2, "5 4")
    b += text(x + 115, y + 216, "~90% accuracy", 15, CRIMSON, "middle")
    b += text(x + 345, y + 216, "~50% (chance)", 15, TEAL, "middle")
    b += text(x + 15, y + 240, "Discover: selecting on all samples fakes accuracy.", 16, MID, style="italic")
    svg("fig03-demo-gallery.svg", W, H, b + illustrative(W, H, "illustrative sketches of demos from a sister course"))


# ---------------------------------------------------------------- fig04
def fig04():
    W, H = 1000, 400
    steps = [
        ("1. Goal", "students understand\ncarrying capacity", TEAL, TEAL_L),
        ("2. Discovery", "growth is fastest\nat half of K", TEAL, TEAL_L),
        ("3. One control", "a slider for K\n(drag the line)", PURPLE, PURPLE_L),
        ("4. What to watch", "the steepest point\nfollows K / 2", PURPLE, PURPLE_L),
        ("5. Known case", "at N = K/2 the slope\nis r·K/4", OCHRE, OCHRE_L),
    ]
    b = ""
    bw, gap = 176, 20
    for i, (t, d, c, cl) in enumerate(steps):
        x = 10 + i * (bw + gap)
        b += rect(x, 110, bw, 150, cl, c, rx=10, sw=2)
        b += text(x + bw / 2, 145, t, 18, c, "middle", "bold")
        b += lines(x + bw / 2, 190, d.split("\n"), 17, DARK, "middle")
        if i < 4:
            b += arrow(x + bw + 2, 185, x + bw + gap - 2, 185)
    b += text(10 + bw / 2, 70, "start here", 20, CRIMSON, "middle", "bold")
    b += arrow(10 + bw / 2, 78, 10 + bw / 2, 104, CRIMSON, 2.5, "arwc")
    b += text(500, 320, "Steps 1 and 2 are yours. The agent is good at 3 and 4.", 20, DARK, "middle")
    b += text(500, 352, "Step 5 is how you find out whether it got the model right.", 20, DARK, "middle")
    svg("fig04-goal-first.svg", W, H, b)


# ---------------------------------------------------------------- fig05
def fig05():
    W, H = 1000, 500
    b = text(245, 36, "Everything adjustable", 22, CRIMSON, "middle", "bold")
    b += rect(20, 55, 450, 360, "#ffffff", LIGHT)
    labels = ["r", "K", "N0", "t max", "step dt", "noise", "seed", "line width", "colour", "log axis"]
    for i, lab in enumerate(labels):
        col, row = i % 2, i // 2
        b += slider(40 + col * 120, 85 + row * 42, 90, [0.3, 0.7, 0.1, 0.5, 0.2, 0.6, 0.4, 0.3, 0.8, 0.0][i], lab, 13)
    b += axes(290, 80, 160, 170)
    b += path(scurve(290, 80, 160, 170, 0.6, 800, 10, 40, 1000), TEAL, 2)
    b += lines(40, 330, ["Students fiddle with ten things", "and learn none of them."], 18, CRIMSON)

    b += text(755, 36, "One question", 22, TEAL, "middle", "bold")
    b += rect(530, 55, 450, 360, "#ffffff", LIGHT)
    b += slider(555, 95, 170, 0.35, "growth rate r", 17)
    b += slider(555, 165, 170, 0.75, "capacity K", 17)
    b += button(555, 215, 80, "Reset", 15)
    b += button(645, 215, 80, "Deer", 15)
    b += axes(760, 80, 200, 200)
    b += path(scurve(760, 80, 200, 200, 0.5, 750, 10, 40, 1000), TEAL, 4)
    b += line(760, 80 + 200 - 150, 960, 80 + 200 - 150, CRIMSON, 2, "8 6")
    b += lines(555, 330, ["Two sliders, a reset and a preset:", "students see what K does."], 18, TEAL)
    b += text(500, 465, "Fix everything the learning goal does not need. Add presets for interesting cases.", 18, MID, "middle")
    svg("fig05-few-controls.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig06
def fig06():
    W, H = 1000, 500
    rows = [
        ("> Make one self-contained HTML file logistic-growth.html ...", "#9fe0ea"),
        "",
        ("● I'll write a single file: HTML, CSS and plain JavaScript,", TERM_FG),
        ("  no libraries and nothing loaded from the internet.", TERM_FG),
        ("  Write(logistic-growth.html)   +281 lines", "#e6b84f"),
        "",
        ("● Done. Open logistic-growth.html in your browser.", TERM_FG),
        ("  Model: N(t) = K / (1 + ((K - N0)/N0) e^(-r t))", "#c8e6a0"),
        ("  Check: at t = ln((K - N0)/N0) / r, N should be K/2.", "#c8e6a0"),
        ("  Try: drag K, press 'Check the model'.", TERM_FG),
    ]
    b = terminal(20, 20, 960, 400, "interactive-demos: agent session", rows, 18, 30)
    b += rect(28, 120, 620, 92, "none", "#e6b84f", rx=6, sw=2.5)
    b += rect(28, 270, 690, 62, "none", "#c8e6a0", rx=6, sw=2.5)
    b += text(30, 452, "One file, no libraries.", 19, OCHRE, weight="bold")
    b += text(330, 452, "The agent states the formula and a known case: check both.", 19, TEAL, weight="bold")
    svg("fig06-agent-session.svg", W, H, b + illustrative(W, H, "illustrative: your session will look different"))


# ---------------------------------------------------------------- fig07
def fig07():
    W, H = 1000, 460
    b = rect(20, 40, 340, 330, "#ffffff", "#9aa4ad", rx=10)
    b += f'  <rect x="20" y="40" width="340" height="40" rx="10" fill="#e9edf1"/>\n'
    b += f'  <rect x="20" y="70" width="340" height="10" fill="#e9edf1"/>\n'
    b += text(190, 66, "interactive-demos", 16, MID, "middle", "bold")
    files = ["logistic-growth.html", "prompt-notes.md", "screenshot-phone.png"]
    for i, f in enumerate(files):
        y = 110 + i * 50
        if i == 0:
            b += rect(30, y - 26, 320, 40, TEAL_L, TEAL, rx=6, sw=2)
        b += rect(45, y - 18, 18, 24, "#ffffff", MID, rx=2, sw=1.5)
        b += text(75, y, f, 17, DARK)
    b += text(190, 330, "double-click the .html file", 17, TEAL, "middle", "bold")
    b += arrow(365, 160, 425, 160)
    b += browser(430, 40, 550, 330, "file:///Users/you/agentic-course/interactive-demos/...", 13)
    b += text(450, 80, "", 14)
    b += slider(455, 110, 150, 0.35, "r", 15)
    b += slider(455, 170, 150, 0.75, "K", 15)
    b += axes(650, 95, 300, 220)
    b += path(scurve(650, 95, 300, 220, 0.5, 800, 10, 40, 1000), TEAL, 3.5)
    b += rect(505, 46, 120, 28, "none", CRIMSON, rx=6, sw=2.5)
    b += text(500, 410, "The address starts with file://: the demo runs from your disk.", 18, DARK, "middle")
    b += text(500, 438, "No server, no install, no internet.", 18, MID, "middle")
    svg("fig07-open-file.svg", W, H, b + illustrative(W, H))


# ---------------------------------------------------------------- fig08
def fig08():
    W, H = 1000, 500
    x0, y0, w, h = 80, 40, 480, 360
    r, K, N0 = 0.5, 800, 10
    th = math.log((K - N0) / N0) / r
    b = axes(x0, y0, w, h)
    for t in range(0, 41, 10):
        b += text(x0 + w * t / 40, y0 + h + 24, str(t), 15, MID, "middle")
    for n in range(0, 1001, 200):
        b += text(x0 - 8, y0 + h - h * n / 1000 + 5, str(n), 15, MID, "end")
    b += text(x0 + w / 2, y0 + h + 50, "time (days)", 16, MID, "middle")
    b += path(scurve(x0, y0, w, h, r, K, N0, 40, 1000), TEAL, 4)
    yk = y0 + h - h * K / 1000
    b += line(x0, yk, x0 + w, yk, CRIMSON, 2, "8 6")
    b += text(x0 + w - 5, yk - 8, "K = 800", 16, CRIMSON, "end", "bold")
    xt, yh = x0 + w * th / 40, y0 + h - h * (K / 2) / 1000
    b += line(xt, y0 + h, xt, yh, OCHRE, 2, "4 4") + line(x0, yh, xt, yh, OCHRE, 2, "4 4")
    # tangent with slope rK/4 = 100 per day
    dx = 3.0
    x1, x2 = xt - w * dx / 40, xt + w * dx / 40
    y1, y2 = yh + h * 100 * dx / 1000, yh - h * 100 * dx / 1000
    b += line(x1, y1, x2, y2, PURPLE, 3)
    b += circle(xt, yh, 8, OCHRE)
    b += text(xt + 12, yh + 28, "t = 8.74, N = 400", 16, OCHRE, weight="bold")
    b += text(xt + 12, yh + 52, "slope = 100 per day", 16, PURPLE, weight="bold")
    # check card
    cx = 610
    b += rect(cx, 30, 370, 420, PALE, LIGHT, rx=10)
    b += text(cx + 20, 75, "Known cases (r = 0.5, K = 800, N0 = 10)", 16, DARK, weight="bold")
    items = [
        ("Half of K at t = ln(79)/0.5", "= 8.74 days: N = 400", TEAL),
        ("Steepest slope r·K/4", "= 100 per day", PURPLE),
        ("Early doubling time ln 2 / r", "= 1.39 days", OCHRE),
        ("Step-by-step solution of", "dN/dt = rN(1 - N/K) matches", TEAL),
    ]
    for i, (a, c, col) in enumerate(items):
        y = 110 + i * 70
        b += circle(cx + 30, y + 4, 11, col)
        b += text(cx + 30, y + 10, "✓", 16, "#ffffff", "middle", "bold")
        b += text(cx + 52, y + 10, a, 17, DARK)
        b += text(cx + 52, y + 34, c, 17, DARK)
    b += text(cx + 20, 410, "Compute these by hand or in Excel,", 15, MID)
    b += text(cx + 20, 430, "then compare with the demo's readout.", 15, MID)
    svg("fig08-known-case.svg", W, H, b)


# ---------------------------------------------------------------- fig09
def fig09():
    W, H = 1000, 500
    ns = [2, 3, 5, 10, 30, 100]
    tcov = [94.9, 95.1, 94.8, 94.7, 95.0, 94.9]
    zcov = [70.3, 81.1, 87.7, 91.8, 93.7, 94.5]
    x0, y0, w, h = 110, 70, 600, 330
    lo, hi = 60, 100
    yv = lambda v: y0 + h - h * (v - lo) / (hi - lo)
    b = text(x0, 40, "Share of '95%' intervals that contain the true mean", 19, DARK, weight="bold")
    b += axes(x0, y0, w, h)
    for v in range(60, 101, 10):
        b += line(x0, yv(v), x0 + w, yv(v), "#eceff2", 1)
        b += text(x0 - 10, yv(v) + 5, f"{v}%", 15, MID, "end")
    b += line(x0, yv(95), x0 + w, yv(95), OCHRE, 2.5, "8 6")
    b += text(x0 + w + 8, yv(95) + 5, "95%", 16, OCHRE, weight="bold")
    gw = w / len(ns)
    for i, n in enumerate(ns):
        gx = x0 + i * gw + 18
        bw = (gw - 36) / 2
        b += rect(gx, yv(tcov[i]), bw, y0 + h - yv(tcov[i]), TEAL, TEAL, rx=2, sw=1)
        b += rect(gx + bw, yv(zcov[i]), bw, y0 + h - yv(zcov[i]), CRIMSON_L, CRIMSON, rx=2, sw=2)
        b += text(gx + bw, y0 + h + 24, f"n = {n}", 16, DARK, "middle")
    b += text(x0 + w / 2, y0 + h + 52, "sample size (20 000 samples each)", 15, MID, "middle")
    b += text(gx := x0 + 18 + 0 * gw + (gw - 36) * 0.75, yv(70.3) - 8, "70%", 15, CRIMSON, "middle", "bold")
    # legend + message
    lx = 760
    b += rect(lx, 90, 22, 22, TEAL, TEAL, rx=2)
    b += lines(lx + 32, 107, ["mean ± t · SD/√n", "(correct)"], 16, DARK, dy=20)
    b += rect(lx, 160, 22, 22, CRIMSON_L, CRIMSON, rx=2, sw=2)
    b += lines(lx + 32, 177, ["mean ± 1.96 · SD/√n", "(a common shortcut)"], 16, DARK, dy=20)
    b += lines(lx, 260, ["Both demos look the same", "on screen. Only the", "check against the", "known 95% shows that", "one is wrong for", "small samples."], 17, CRIMSON, dy=23)
    svg("fig09-coverage-check.svg", W, H, b)


# ---------------------------------------------------------------- fig10
def fig10():
    W, H = 1000, 470
    cards = [
        ("Visible labels", "every slider says what it is\nand shows its value", TEAL, TEAL_L),
        ("Keyboard works", "Tab to reach a control,\narrow keys to change it", TEAL, TEAL_L),
        ("Not colour alone", "a miss is red and dashed,\nnot only red", PURPLE, PURPLE_L),
        ("Big enough", "text 16 px or more; it must\nwork on a projector", PURPLE, PURPLE_L),
        ("Numbers as text", "key values in words too,\nfor screen readers", OCHRE, OCHRE_L),
        ("Calm", "no flashing, no autoplay,\nnothing only on hover", OCHRE, OCHRE_L),
    ]
    b = ""
    for i, (t, d, c, cl) in enumerate(cards):
        x = 20 + (i % 3) * 325
        y = 30 + (i // 3) * 200
        b += rect(x, y, 305, 170, cl, c, rx=10, sw=2)
        b += text(x + 20, y + 42, t, 22, c, weight="bold")
        b += lines(x + 20, y + 85, d.split("\n"), 18, DARK, dy=26)
    b += text(500, 450, "Ask the agent for these in the first prompt; then check them yourself with the keyboard.", 18, MID, "middle")
    svg("fig10-accessibility.svg", W, H, b)


# ---------------------------------------------------------------- fig11
def fig11():
    W, H = 1000, 560
    def phone(x, y):
        s = rect(x, y, 250, 470, "#1b2a3a", "#1b2a3a", rx=30)
        s += rect(x + 12, y + 40, 226, 390, "#ffffff", "#ffffff", rx=4)
        s += circle(x + 125, y + 450, 10, "#3a4654")
        return s
    b = text(165, 30, "Not tested", 22, CRIMSON, "middle", "bold")
    b += phone(40, 45)
    b += '  <clipPath id="scr"><rect x="52" y="85" width="226" height="390"/></clipPath>\n'
    b += '  <g clip-path="url(#scr)">\n'
    b += text(58, 100, "Why does a growing population level off? Move the sliders, or drag the red line", 9, DARK, weight="bold")
    for i, lab in enumerate(["r", "K", "N0"]):
        b += text(58, 118 + i * 30, lab, 8, DARK)
        b += line(58, 124 + i * 30, 118, 124 + i * 30, "#c9d3dd", 3)
        b += circle(80, 124 + i * 30, 4, "#ffffff", TEAL, 1.5)
    b += lines(58, 220, ["Early doubling time: 1.4 days", "Half of K at day 8.7"], 8, DARK, dy=11)
    b += axes(135, 110, 200, 130)
    b += path(scurve(135, 110, 200, 130), TEAL, 2.5)
    b += '  </g>\n'
    b += lines(320, 120, ["plot cut off", "at the edge"], 17, CRIMSON, dy=22)
    b += arrow(318, 140, 282, 175, CRIMSON, 2, "arwc")
    b += lines(320, 300, ["sliders a few mm wide,", "text too small to read"], 17, CRIMSON, dy=22)
    b += arrow(318, 296, 125, 160, CRIMSON, 2, "arwc")

    b += text(770, 30, "Tested", 22, TEAL, "middle", "bold")
    b += phone(645, 45)
    b += text(667, 108, "Why does growth level off?", 13, DARK, weight="bold")
    b += axes(675, 120, 190, 130)
    b += path(scurve(675, 120, 190, 130, 0.5, 800, 10, 40, 1000), TEAL, 3)
    b += slider(672, 290, 195, 0.35, "growth rate r", 14)
    b += slider(672, 345, 195, 0.75, "capacity K", 14)
    b += button(672, 385, 80, "Reset", 13, 28)
    b += lines(905, 250, ["stacked:", "plot, then", "big sliders"], 17, TEAL, dy=22)
    b += text(500, 545, "Also try: dragging with a finger, portrait and landscape, and the page inside your course site.", 17, MID, "middle")
    svg("fig11-phone.svg", W, H, b + "")


# ---------------------------------------------------------------- fig12
def fig12():
    W, H = 1000, 520
    b = text(20, 30, "Your page's folder", 19, MID, weight="bold")
    b += rect(20, 45, 290, 270, PALE, LIGHT)
    tree = [("my-course-page/", DARK, "bold"), ("  _quarto.yml", DARK, "normal"), ("  index.qmd", DARK, "normal"),
            ("  schedule.qmd", DARK, "normal"), ("  demos/", DARK, "bold"), ("    logistic-growth.html", TEAL, "bold")]
    for i, (t, c, wgt) in enumerate(tree):
        b += text(35, 80 + i * 36, t, 17, c, weight=wgt, family=MONO)
    b += rect(28, 235, 278, 32, "none", TEAL, rx=6, sw=2.5)
    b += text(20, 350, "In index.qmd (one line):", 19, MID, weight="bold")
    b += rect(20, 362, 600, 96, TERM_BG, TERM_BG, rx=8)
    b += lines(36, 392, ['<iframe src="demos/logistic-growth.html"', '        width="100%" height="600"', '        title="Logistic growth demo"></iframe>'], 16, TERM_FG, dy=24, family=MONO)
    b += browser(560, 30, 420, 310, "you.github.io/my-course-page", 14)
    b += text(580, 100, "Week 3: population growth", 18, DARK, weight="bold")
    b += lines(580, 130, ["Read chapter 4, then try the", "demo below before Thursday."], 15, MID, dy=20)
    b += rect(580, 175, 380, 150, "#ffffff", TEAL, rx=6, sw=2, dash="6 4")
    b += slider(595, 205, 110, 0.4, "r", 14)
    b += slider(595, 255, 110, 0.7, "K", 14)
    b += axes(740, 190, 200, 120)
    b += path(scurve(740, 190, 200, 120, 0.5, 800, 10, 40, 1000), TEAL, 3)
    b += arrow(315, 251, 570, 251, TEAL, 2.5, "arwt")
    b += text(640, 490, "The page builder must also copy the .html file:", 17, DARK, "middle")
    b += text(640, 512, "for a Quarto site, list it under resources in _quarto.yml.", 17, DARK, "middle")
    svg("fig12-embed.svg", W, H, b + "")


# ---------------------------------------------------------------- fig13
def fig13():
    W, H = 1000, 350
    steps = [("Agent edits", "the demo", PURPLE, PURPLE_L), ("Render", "site into docs/", TEAL, TEAL_L),
             ("Look", "try it locally", TEAL, TEAL_L), ("Commit", "incl. docs/", OCHRE, OCHRE_L),
             ("Push", "to GitHub", OCHRE, OCHRE_L), ("Check live", "laptop + phone", CRIMSON, CRIMSON_L)]
    b = ""
    bw, gap = 145, 18
    for i, (t, d, c, cl) in enumerate(steps):
        x = 12 + i * (bw + gap)
        b += box(x, 60, bw, 100, f"{t}\n{d}", c, cl, 18)
        if i < 5:
            b += arrow(x + bw + 1, 110, x + bw + gap - 1, 110)
    b += path(f"M{12 + 5 * (bw + gap) + bw / 2},162 C {800},260 {200},260 {12 + bw / 2},162", MID, 2.5, dash="7 5")
    b += f'  <path d="M{12 + bw / 2 - 7},176 L{12 + bw / 2},162 L{12 + bw / 2 + 9},174" fill="none" stroke="{MID}" stroke-width="2.5"/>\n'
    b += text(500, 275, "something to fix? round again", 18, MID, "middle", style="italic")
    b += text(500, 330, "The same loop as for your page: edit, render, look, commit, push, check live.", 18, DARK, "middle")
    svg("fig13-publish-loop.svg", W, H, b)


for f in [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12, fig13]:
    f()
print("ok")
