"""Result plots for the Survey track deck, made from the synthetic data in
data/ (run data/make-data.py first). The concept figures in this folder are
hand-written SVG. Needs numpy, pandas and matplotlib.

Run from anywhere:  python make-figs.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
DIV = ["#a8324a", "#d9a0ab", "#cfcfcf", "#8fc1c9", "#2a7f8f"]
LAB = ["Strongly disagree", "Disagree", "Neither", "Agree", "Strongly agree"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path", "svg.hashsalt": "track-survey"})

df = pd.read_csv(HERE / "data" / "truth-clean.csv", na_values=[""], keep_default_na=False)
items = [f"q{k:02d}" for k in range(1, 13)]
X = df[items].replace("NA", np.nan).apply(pd.to_numeric)
SHORT = ["Outcomes clear", "Lectures helped", "Recordings helped", "Labs helped",
         "Workload too high (R)", "Literature useful", "Useful feedback",
         "Feedback in time", "Unsure what expected (R)", "Exam matched practice",
         "Teachers approachable", "Overall satisfied"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / name, format="svg", metadata={"Date": None})
    plt.close(fig)


def diverging(ax, rows, labels):
    """rows: list of 1-D arrays of answers 1-5 (NaN dropped)."""
    for y, v in enumerate(rows):
        v = v[~np.isnan(v)]
        p = np.array([np.mean(v == k) for k in range(1, 6)]) * 100
        left = -(p[0] + p[1] + p[2] / 2)
        for k in range(5):
            ax.barh(y, p[k], left=left, color=DIV[k], height=0.7,
                    edgecolor="white", linewidth=0.5)
            left += p[k]
        ax.text(102, y, f"n={len(v)}", va="center", fontsize=13, color="#555")
    ax.axvline(0, color="#333", lw=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(-100, 115)
    ax.set_xticks([-100, -50, 0, 50, 100])
    ax.set_xticklabels(["100 %", "50 %", "0", "50 %", "100 %"])
    ax.spines[["left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)


# ---- reverse-coding check: each item's correlation with the rest -----------
def item_rest(M):
    out = []
    for k in range(12):
        rest = M.drop(columns=M.columns[k]).mean(axis=1)
        out.append(M.iloc[:, k].corr(rest))
    return np.array(out)


Xr = X.copy()
for c in ("q05", "q09"):
    Xr[c] = 6 - Xr[c]
r_raw, r_rev = item_rest(X), item_rest(Xr)
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, r, title in [(axes[0], r_raw, "As worded"), (axes[1], r_rev, "After reversing items 5 and 9")]:
    cols = [CRIMSON if v < 0 else TEAL for v in r]
    ax.barh(range(12), r, color=cols)
    ax.axvline(0, color="#333", lw=1)
    ax.set_xlim(-0.8, 0.8)
    ax.set_title(title)
    ax.set_xlabel("agreement with the other items")
axes[0].set_yticks(range(12))
axes[0].set_yticklabels(SHORT)
axes[0].invert_yaxis()
save(fig, "fig08-reverse-check.svg")

# ---- means hide the shape ---------------------------------------------------------
a = np.array([3] * 40 + [2] * 5 + [4] * 5, dtype=float)
b = np.array([1] * 22 + [5] * 22 + [3] * 6, dtype=float)
fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw={"width_ratios": [1, 2.2]})
ax = axes[0]
ax.bar([0, 1], [a.mean(), b.mean()], color=[PURPLE, OCHRE], width=0.6)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Course A", "Course B"])
ax.set_ylim(1, 5)
ax.set_ylabel("mean (1-5)")
ax.set_title("Means: identical")
for x_, m in zip([0, 1], [a.mean(), b.mean()]):
    ax.text(x_, m + 0.1, f"{m:.1f}", ha="center")
ax = axes[1]
diverging(ax, [a, b], ["Course A", "Course B"])
ax.set_title("Distributions: opposite stories")
save(fig, "fig10-means-hide.svg")

# ---- diverging stacked bars, all 12 items ---------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.2))
diverging(ax, [X[c].to_numpy(dtype=float) for c in items], SHORT)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in DIV]
ax.legend(handles, LAB, ncol=5, frameon=False, loc="upper center",
          bbox_to_anchor=(0.45, -0.07), fontsize=13, handlelength=1)
save(fig, "fig11-diverging-bars.svg")

# ---- campus vs distance, items 3, 4 and 12 -----------------------------------------------
camp = df["mode"] == "Campus"
rows, labels = [], []
for c, name in [("q03", "Recordings helped"), ("q04", "Labs helped"), ("q12", "Overall satisfied")]:
    for grp, mask in [("campus", camp), ("distance", ~camp)]:
        rows.append(X.loc[mask, c].to_numpy(dtype=float))
        labels.append(f"{name}: {grp}")
fig, ax = plt.subplots(figsize=(12, 4.6))
diverging(ax, rows, labels)
for y in (1.5, 3.5):
    ax.axhline(y, color="#ddd", lw=1)
ax.legend(handles, LAB, ncol=5, frameon=False, loc="upper center",
          bbox_to_anchor=(0.4, -0.12), fontsize=13, handlelength=1)
save(fig, "fig12-campus-distance.svg")

# ---- free-text themes (truth) ------------------------------------------------------------
cm = pd.read_csv(HERE / "data" / "truth-comments.csv")
imp = cm[cm.question == "improve"].theme.value_counts()
fig, ax = plt.subplots(figsize=(11, 4.6))
cols = [CRIMSON if t in ("lab accessibility", "complaint about a named lecturer") else TEAL
        for t in imp.index]
ax.barh(range(len(imp)), imp.values, color=cols)
ax.set_yticks(range(len(imp)))
ax.set_yticklabels(imp.index)
ax.invert_yaxis()
for y, v in enumerate(imp.values):
    ax.text(v + 0.2, y, str(v), va="center")
ax.set_xlabel("number of comments")
ax.set_title(f'"What should be improved?" ({imp.sum()} comments)')
save(fig, "fig16-themes.svg")
print("done")
