"""
make-figures.py: redraws the benchmark graphs for the unit
"Choosing a model: families, sizes and benchmarks" (Part 6) as SVG,
from data downloaded from the original sources on 2026-11-23.

Run from anywhere with:   python3 make-figures.py
Writes, into the unit folder (one level up):
  fig10-saturation.svg     GPQA Diamond and SWE-bench Verified over time (Epoch AI)
  fig12-metr-horizon.svg   50% and 80% time horizons (METR, Time Horizon 1.1)
  fig13-eci-open-closed.svg Epoch Capabilities Index, open vs closed weights
  fig15-arena-ci.svg       LMArena text leaderboard, top 15, with 95% CIs
  fig16-arena-style.svg    LMArena rank with and without style control

Data files in this folder (subsets of the originals, unchanged values):
  metr_time_horizon_1.1.csv
      METR, "Task-Completion Time Horizons of Frontier AI Models",
      https://metr.org/time-horizons/ (page last updated 2026-09-08; it says
      it is no longer actively updated). Source file:
      https://metr.org/assets/benchmark_results_1_1.yaml. Licence: CC BY 4.0
      ("Please attribute to METR"). Values in minutes. The organisation and
      open_weights columns were added by us from the model names.
      Method: Kwa et al. 2025, arXiv:2503.14499.
  epoch_gpqa_diamond.csv, epoch_swe_bench_verified.csv, epoch_eci.csv
      Epoch AI, "Capabilities & benchmarking", https://epoch.ai/benchmarks,
      from https://epoch.ai/data/benchmark_data.zip (hub updated 2026-11-23).
      Licence: CC BY 4.0. Scores are Epoch's own runs (0-1). The open_weights
      flag comes from Epoch's model metadata ("accessibility").
  lmarena_text_overall_2026-11-22.csv
      LMArena (arena.ai) text leaderboard, category "overall", top 40, with and
      without style control, snapshot 2026-11-22, from the Hugging Face dataset
      lmarena-ai/leaderboard-dataset. Licence: CC BY 4.0.

Only the Python standard library is used.
"""
import csv
import datetime as dt
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
GREY, LIGHT = "#666666", "#e6e6e6"
FONT = 'font-family="Helvetica, Arial, sans-serif"'


def read(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def date(s):
    return dt.date.fromisoformat(s)


def year_frac(d):
    return d.year + (d.timetuple().tm_yday - 1) / 365.25


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" {FONT}>\n'
            f'  <rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}</svg>\n')


def text(x, y, s, size=16, fill="#333", anchor="start", weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w}{extra}>{esc(s)}</text>\n')


def best_so_far(points):
    """points: list of (x, y) sorted by x -> step line of the running maximum."""
    out, best = [], None
    for x, y in sorted(points):
        if best is None or y > best:
            if best is not None:
                out.append((x, best))
            best = y
            out.append((x, y))
    return out


# --------------------------------------------------------------------------
# fig10: saturation of two fixed tests (Epoch AI)
# --------------------------------------------------------------------------
def panel_scores(rows, x0, y0, w, h, title, xmin, xmax, refs):
    b = ""
    sx = lambda t: x0 + w * (t - xmin) / (xmax - xmin)
    sy = lambda v: y0 + h - h * v
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        b += f'  <line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{LIGHT}"/>\n'
        b += text(x0 - 8, sy(v) + 5, f"{int(v * 100)} %", 15, GREY, "end")
    for yr in range(math.ceil(xmin), int(xmax) + 1):
        b += text(sx(yr), y0 + h + 24, str(yr), 15, GREY, "middle")
        b += f'  <line x1="{sx(yr):.1f}" y1="{y0 + h}" x2="{sx(yr):.1f}" y2="{y0 + h + 6}" stroke="#333"/>\n'
    b += f'  <line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="#333" stroke-width="1.5"/>\n'
    for v, lab, col in refs:
        b += f'  <line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{col}" stroke-dasharray="6 4" stroke-width="1.5"/>\n'
    pts = [(year_frac(date(r["release_date"])), float(r["score"])) for r in rows]
    for x, y in pts:
        b += f'  <circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.2" fill="#b5b5b5"/>\n'
    line = best_so_far(pts)
    b += '  <polyline points="' + " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in line) + \
         f'" fill="none" stroke="{TEAL}" stroke-width="3"/>\n'
    b += text(x0, y0 - 14, title, 18, "#333", weight="bold")
    return b, line


def fig10():
    g = read("epoch_gpqa_diamond.csv")
    s = read("epoch_swe_bench_verified.csv")
    body = ""
    b, lg = panel_scores(g, 80, 60, 390, 300, "GPQA Diamond (expert science questions)",
                         2023.0, 2027.0, [(0.25, "guessing: 25 %", GREY),
                                          (0.65, "PhD experts in the field: about 65 %", OCHRE)])
    body += b
    b, ls = panel_scores(s, 590, 60, 390, 300, "SWE-bench Verified (real code bugs)",
                         2023.0, 2027.0, [])
    body += b
    body += f'  <line x1="80" y1="420" x2="110" y2="420" stroke="{TEAL}" stroke-width="3"/>\n'
    body += text(118, 426, "best score so far", 16)
    body += '  <circle cx="300" cy="420" r="4" fill="#b5b5b5"/>\n'
    body += text(312, 426, "one model (and setting)", 16)
    body += text(590, 426, f"best: GPQA {lg[0][1]*100:.0f} → {lg[-1][1]*100:.0f} %, "
                           f"SWE-bench {ls[0][1]*100:.0f} → {ls[-1][1]*100:.0f} %", 16)
    body += text(975, 350, "Epoch's own runs end in June 2026", 13, GREY, "end")
    body += f'  <line x1="80" y1="452" x2="110" y2="452" stroke="{OCHRE}" stroke-dasharray="6 4" stroke-width="1.5"/>\n'
    body += text(118, 458, "PhD experts in the field: about 65 % (Rein et al. 2023)", 15)
    body += f'  <line x1="530" y1="452" x2="560" y2="452" stroke="{GREY}" stroke-dasharray="6 4" stroke-width="1.5"/>\n'
    body += text(568, 458, "guessing among 4 answers: 25 %", 15)
    body += text(980, 488, "Data: Epoch AI, Capabilities & benchmarking (epoch.ai/benchmarks), CC BY 4.0; "
                           "downloaded 2026-11-23. Epoch's own runs.", 13, "#999", "end")
    open(os.path.join(OUT, "fig10-saturation.svg"), "w").write(svg(1000, 495, body))


# --------------------------------------------------------------------------
# fig12: METR time horizons (log scale)
# --------------------------------------------------------------------------
def fig12():
    rows = read("metr_time_horizon_1.1.csv")
    x0, y0, w, h = 120, 40, 820, 350
    xmin, xmax = 2019.0, 2026.75
    lmin, lmax = math.log10(1 / 60), math.log10(3 * 24 * 60)
    sx = lambda t: x0 + w * (t - xmin) / (xmax - xmin)
    sy = lambda m: y0 + h - h * (math.log10(max(m, 10 ** lmin)) - lmin) / (lmax - lmin)
    b = ""
    # unreliable zone above 16 h
    b += f'  <rect x="{x0}" y="{y0}" width="{w}" height="{sy(16 * 60) - y0:.1f}" fill="#f3f3f3"/>\n'
    b += text(x0 + 8, y0 + 20, "above 16 hours: METR says its measurements are unreliable", 14, GREY)
    for m, lab in [(1 / 60, "1 sec"), (1, "1 min"), (10, "10 min"), (60, "1 hour"),
                   (4 * 60, "4 hours"), (16 * 60, "16 hours"), (3 * 24 * 60, "3 days")]:
        b += f'  <line x1="{x0}" y1="{sy(m):.1f}" x2="{x0 + w}" y2="{sy(m):.1f}" stroke="{LIGHT}"/>\n'
        b += text(x0 - 8, sy(m) + 5, lab, 15, GREY, "end")
    for yr in range(2019, 2027):
        b += text(sx(yr), y0 + h + 24, str(yr), 15, GREY, "middle")
        b += f'  <line x1="{sx(yr):.1f}" y1="{y0 + h}" x2="{sx(yr):.1f}" y2="{y0 + h + 6}" stroke="#333"/>\n'
    b += f'  <line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="#333" stroke-width="1.5"/>\n'
    b += text(30, y0 + h / 2, "length of task (human expert time)", 16, "#333", "middle",
              extra=f' transform="rotate(-90 30 {y0 + h / 2})"')
    label = {"GPT-2": (10, -10), "GPT-4": (-8, -14), "Claude 3.7 Sonnet": (-10, -14),
             "Claude Opus 4.6": (-14, -2), "Claude Mythos Preview (early)": (-14, -10)}
    for r in rows:
        x = sx(year_frac(date(r["release_date"])))
        lo, hi, p50, p80 = (float(r[k]) for k in ("p50_ci_low", "p50_ci_high", "p50_minutes", "p80_minutes"))
        b += f'  <line x1="{x:.1f}" y1="{sy(lo):.1f}" x2="{x:.1f}" y2="{sy(min(hi, 3 * 24 * 60)):.1f}" stroke="{TEAL}" stroke-opacity="0.35" stroke-width="2"/>\n'
        b += f'  <rect x="{x - 4:.1f}" y="{sy(p80) - 4:.1f}" width="8" height="8" fill="#fff" stroke="{PURPLE}" stroke-width="2" transform="rotate(45 {x:.1f} {sy(p80):.1f})"/>\n'
        b += f'  <circle cx="{x:.1f}" cy="{sy(p50):.1f}" r="5" fill="{TEAL}" stroke="#fff" stroke-width="1.5"/>\n'
        if r["model"] in label:
            dx, dy = label[r["model"]]
            name = r["model"].replace(" (early)", "")
            b += text(x + dx, sy(p50) + dy, name, 14, "#333", "end" if dx < 0 else "start")
    # legend
    lx, ly = sx(2024.4), sy(0.12)
    b += f'  <circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="{TEAL}"/>\n'
    b += text(lx + 12, ly + 5, "50 % success (line: 95 % CI)", 15)
    b += f'  <rect x="{lx - 4:.1f}" y="{ly + 21:.1f}" width="8" height="8" fill="#fff" stroke="{PURPLE}" stroke-width="2" transform="rotate(45 {lx:.1f} {ly + 25:.1f})"/>\n'
    b += text(lx + 12, ly + 30, "80 % success", 15)
    b += text(980, 462, "Data: METR, Task-Completion Time Horizons of Frontier AI Models, Time Horizon 1.1 "
                        "(metr.org/time-horizons), CC BY 4.0;", 13, "#999", "end")
    b += text(980, 478, "page last updated 2026-09-08, downloaded 2026-11-23. Method: Kwa et al. 2025.",
              13, "#999", "end")
    open(os.path.join(OUT, "fig12-metr-horizon.svg"), "w").write(svg(1000, 486, b))


# --------------------------------------------------------------------------
# fig13: Epoch Capabilities Index, open vs closed weights
# --------------------------------------------------------------------------
def fig13():
    rows = [r for r in read("epoch_eci.csv") if r["open_weights"] in ("True", "False")]
    x0, y0, w, h = 90, 40, 850, 330
    xmin, xmax, vmin, vmax = 2023.0, 2027.0, 40, 180
    sx = lambda t: x0 + w * (t - xmin) / (xmax - xmin)
    sy = lambda v: y0 + h - h * (v - vmin) / (vmax - vmin)
    b = ""
    for v in range(40, 181, 20):
        b += f'  <line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{LIGHT}"/>\n'
        b += text(x0 - 8, sy(v) + 5, str(v), 15, GREY, "end")
    for yr in range(2023, 2028):
        b += text(sx(yr), y0 + h + 24, str(yr), 15, GREY, "middle")
    b += f'  <line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="#333" stroke-width="1.5"/>\n'
    b += text(28, y0 + h / 2, "Epoch Capabilities Index", 16, "#333", "middle",
              extra=f' transform="rotate(-90 28 {y0 + h / 2})"')
    lines = {}
    for flag, col in (("False", TEAL), ("True", PURPLE)):
        pts = [(year_frac(date(r["release_date"])), float(r["score"])) for r in rows if r["open_weights"] == flag]
        for x, y in pts:
            if flag == "False":
                b += f'  <circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.5" fill="{col}" fill-opacity="0.35"/>\n'
            else:
                b += f'  <rect x="{sx(x) - 3.2:.1f}" y="{sy(y) - 3.2:.1f}" width="6.4" height="6.4" fill="{col}" fill-opacity="0.35"/>\n'
        line = best_so_far(pts)
        lines[flag] = line
        b += '  <polyline points="' + " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in line) + \
             f'" fill="none" stroke="{col}" stroke-width="3"/>\n'
    b += f'  <line x1="{x0 + 20}" y1="{y0 + 20}" x2="{x0 + 50}" y2="{y0 + 20}" stroke="{TEAL}" stroke-width="3"/>\n'
    b += text(x0 + 58, y0 + 26, "best closed model so far (circles: closed models)", 16)
    b += f'  <line x1="{x0 + 20}" y1="{y0 + 48}" x2="{x0 + 50}" y2="{y0 + 48}" stroke="{PURPLE}" stroke-width="3"/>\n'
    b += text(x0 + 58, y0 + 54, "best open-weights model so far (squares: open models)", 16)
    # lag: when did closed first reach today's best open score?
    best_open = lines["True"][-1][1]
    first_closed = next(x for x, y in lines["False"] if y >= best_open)
    t_open = lines["True"][-1][0]
    lag_months = (t_open - first_closed) * 12
    b += text(x0 + w, sy(70), f"best open model now: {best_open:.0f}; closed models first "
              f"reached that about {lag_months:.0f} months earlier", 15, PURPLE, "end")
    b += text(980, 432, "Data: Epoch AI, Capabilities & benchmarking (epoch.ai/benchmarks), Epoch Capabilities Index; "
                        "CC BY 4.0; downloaded 2026-11-23.", 13, "#999", "end")
    open(os.path.join(OUT, "fig13-eci-open-closed.svg"), "w").write(svg(1000, 440, b))
    print(f"ECI: best open {best_open}, lag {lag_months:.1f} months")


# --------------------------------------------------------------------------
# fig15/16: LMArena
# --------------------------------------------------------------------------
def fig15():
    rows = [r for r in read("lmarena_text_overall_2026-11-22.csv") if r["variant"] == "style_control"][:15]
    x0, y0, w, rowh = 360, 40, 560, 24
    vmin, vmax = 1470, 1540
    sx = lambda v: x0 + w * (v - vmin) / (vmax - vmin)
    b = ""
    for v in range(1470, 1541, 10):
        b += f'  <line x1="{sx(v):.1f}" y1="{y0 - 6}" x2="{sx(v):.1f}" y2="{y0 + 15 * rowh}" stroke="{LIGHT}"/>\n'
        b += text(sx(v), y0 + 15 * rowh + 22, str(v), 15, GREY, "middle")
    top_lo = float(rows[0]["rating_lower"])
    b += f'  <rect x="{sx(top_lo):.1f}" y="{y0 - 6}" width="{sx(vmax) - sx(top_lo):.1f}" height="{15 * rowh + 6}" fill="{TEAL}" fill-opacity="0.07"/>\n'
    for i, r in enumerate(rows):
        y = y0 + i * rowh + rowh / 2
        lo, hi, v = float(r["rating_lower"]), float(r["rating_upper"]), float(r["rating"])
        col = TEAL if r["license"] == "Proprietary" else PURPLE
        b += text(x0 - 12, y + 5, f'{i + 1}. {r["model_name"]}', 15, "#333", "end")
        b += f'  <line x1="{sx(lo):.1f}" y1="{y:.1f}" x2="{sx(hi):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.5"/>\n'
        b += f'  <circle cx="{sx(v):.1f}" cy="{y:.1f}" r="5" fill="{col}" stroke="#fff" stroke-width="1.5"/>\n'
    b += text(x0 + w / 2, y0 + 15 * rowh + 46, "rating from blind side-by-side votes (style control), with 95 % interval",
              16, "#333", "middle")
    b += text(x0 + w, y0 - 14, "shaded: overlaps the top model's interval", 14, TEAL, "end")
    b += text(980, 474, f'Data: LMArena (arena.ai) text leaderboard, overall, snapshot {rows[0]["leaderboard_publish_date"]}, '
                        "Hugging Face lmarena-ai/leaderboard-dataset, CC BY 4.0; downloaded 2026-11-23.", 13, "#999", "end")
    open(os.path.join(OUT, "fig15-arena-ci.svg"), "w").write(svg(1000, 482, b))


def fig16():
    rows = read("lmarena_text_overall_2026-11-22.csv")
    d = [r for r in rows if r["variant"] == "default"]
    s = [r for r in rows if r["variant"] == "style_control"]
    rank_d = {r["model_name"]: i + 1 for i, r in enumerate(d)}
    rank_s = {r["model_name"]: i + 1 for i, r in enumerate(s)}
    top = [r["model_name"] for r in d[:12]]
    xl, xr, y0, rowh = 380, 620, 70, 22
    b = text(xl, 40, "default", 17, "#333", "middle", "bold")
    b += text(xr, 40, "style control", 17, "#333", "middle", "bold")
    for m in top:
        a, c = rank_d[m], rank_s[m]
        ya, yc = y0 + (a - 1) * rowh, y0 + (c - 1) * rowh
        moved = abs(a - c) >= 5
        col = CRIMSON if moved else "#9a9a9a"
        wdt = 3 if moved else 1.8
        b += f'  <line x1="{xl + 14}" y1="{ya:.1f}" x2="{xr - 14}" y2="{yc:.1f}" stroke="{col}" stroke-width="{wdt}"/>\n'
        b += f'  <circle cx="{xl + 14}" cy="{ya:.1f}" r="5" fill="{col}"/>\n'
        b += f'  <circle cx="{xr - 14}" cy="{yc:.1f}" r="5" fill="{col}"/>\n'
        b += text(xl, ya + 5, f"{a}. {m}", 15, "#333", "end")
        b += text(xr, yc + 5, str(c), 15, "#333")
    b += text(700, 120, "Style control asks: which answer would", 16, "#333")
    b += text(700, 144, "win if length and formatting (headings,", 16, "#333")
    b += text(700, 168, "bold, lists) were the same?", 16, "#333")
    b += text(700, 210, "Red: moved 5 or more places.", 16, CRIMSON)
    b += text(980, 548, "Data: LMArena (arena.ai) text leaderboard, overall, snapshot 2026-11-22, "
                        "Hugging Face lmarena-ai/leaderboard-dataset, CC BY 4.0.", 13, "#999", "end")
    open(os.path.join(OUT, "fig16-arena-style.svg"), "w").write(svg(1000, 556, b))
    for m in top:
        print(m, rank_d[m], rank_s.get(m))


fig10()
fig12()
fig13()
fig15()
fig16()
