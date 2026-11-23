#!/usr/bin/env python3
"""
make-figs.py: result plots for the lecture of "Track A: Bulk RNA-seq".

Reads the CSV files written by make-figs.R and writes SVG figures into the
unit folder (one level up):

    Rscript make-figs.R <tmpdir>
    python3 make-figs.py <tmpdir> ..

Figures: fig07-library-sizes, fig08-pca, fig09-correlation,
fig13-multiple-testing, fig14-swap-effect, fig15-volcano, fig16-ma-plot.
Needs numpy, pandas and matplotlib.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

D, OUT = sys.argv[1], sys.argv[2]
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
GREY, DARK = "#b8b8b8", "#333333"
plt.rcParams.update({
    "svg.fonttype": "none", "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 15,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#666",
    "axes.labelcolor": DARK, "xtick.color": "#555", "ytick.color": "#555",
    "figure.facecolor": "white", "axes.facecolor": "white", "svg.hashsalt": "fig",
})


def fix_fonts(path):
    """matplotlib writes the font it found (DejaVu Sans); use a portable stack."""
    t = open(path).read()
    t = t.replace("font-family: 'DejaVu Sans'", "font-family: Helvetica, Arial, sans-serif")
    open(path, "w").write(t)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), format="svg", bbox_inches="tight", dpi=150, metadata={"Date": None})
    plt.close(fig)
    fix_fonts(os.path.join(OUT, name))


# fig07 library sizes ---------------------------------------------------------
lib = pd.read_csv(os.path.join(D, "libsizes.csv"))
fig, ax = plt.subplots(figsize=(10, 4.2))
cols = [TEAL if t == "control" else CRIMSON for t in lib.treatment]
ax.bar(lib["sample"], lib.reads / 1e6, color=cols, width=0.7)
ax.set_ylabel("reads counted (millions)")
ax.set_ylim(0, 7.5)
i3 = list(lib["sample"]).index("S03")
ax.annotate("S03: about 5 times\nfewer reads", (i3, lib.reads[i3] / 1e6), (i3 + 0.9, 6.6),
            fontsize=14, color=DARK, arrowprops=dict(arrowstyle="->", color=DARK))
ax.bar([0], [0], color=TEAL, label="control (sample sheet)")
ax.bar([0], [0], color=CRIMSON, label="treated (sample sheet)")
ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(1, 1.12), ncol=2, fontsize=13)
save(fig, "fig07-library-sizes.svg")

# fig08 PCA -------------------------------------------------------------------
p = pd.read_csv(os.path.join(D, "pca.csv"))
fig, ax = plt.subplots(figsize=(8.5, 5.6))
for (t, b), g in p.groupby(["treatment", "batch"]):
    ax.scatter(g.PC1, g.PC2, s=140, color=TEAL if t == "control" else CRIMSON,
               marker="o" if b == "day1" else "^", edgecolor="white", linewidth=1.5,
               label=f"{t}, {b}", zorder=3)
for _, r in p.iterrows():
    if r["sample"] in ("S08", "S11"):
        ax.annotate(f"{r['sample']}: labelled {r.treatment},\nsits with the other group", (r.PC1, r.PC2 - 1),
                    (r.PC1 + (-17 if r.PC1 > 0 else 4), r.PC2 + (-7.5 if r.PC1 > 0 else 3.5)), fontsize=13, color=DARK,
                    arrowprops=dict(arrowstyle="->", color=DARK))
        ax.scatter([r.PC1], [r.PC2], s=420, facecolor="none", edgecolor=OCHRE, linewidth=2.2, zorder=4)
ax.set_xlabel(f"PC1 ({p.pv1[0]*100:.0f}% of variance)")
ax.set_ylabel(f"PC2 ({p.pv2[0]*100:.0f}%)")
ax.axhline(0, color="#eee", zorder=0); ax.axvline(0, color="#eee", zorder=0)
ax.set_ylim(-16, 16); ax.set_xlim(-25, 25)
ax.legend(frameon=False, fontsize=12, loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=4,
          handletextpad=0.2, columnspacing=1)
save(fig, "fig08-pca.svg")

# fig09 correlation heatmap ---------------------------------------------------
c = pd.read_csv(os.path.join(D, "cor.csv"), index_col=0)
order = ["S01", "S02", "S03", "S07", "S08", "S09", "S04", "S05", "S06", "S10", "S11", "S12"]
c = c.loc[order, order]
fig, ax = plt.subplots(figsize=(7.4, 6.2))
im = ax.imshow(c.values, cmap="Blues", vmin=0.93, vmax=1.0)
ax.set_xticks(range(12)); ax.set_xticklabels(order, rotation=90, fontsize=12)
ax.set_yticks(range(12)); ax.set_yticklabels(order, fontsize=12)
for k in (5.5,):
    ax.axhline(k, color=DARK, lw=1.5); ax.axvline(k, color=DARK, lw=1.5)
ax.text(2.5, -1.0, "labelled control", ha="center", fontsize=13, color=TEAL)
ax.text(8.5, -1.0, "labelled treated", ha="center", fontsize=13, color=CRIMSON)
for s in ("S08", "S11"):
    j = order.index(s)
    ax.add_patch(plt.Rectangle((-0.5, j - 0.5), 12, 1, fill=False, edgecolor=OCHRE, lw=2.2))
for sp in ax.spines.values():
    sp.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
cb.set_label("correlation", fontsize=13); cb.ax.tick_params(labelsize=11)
save(fig, "fig09-correlation.svg")

# fig13 multiple testing and fig14 swap effect --------------------------------
s = pd.read_csv(os.path.join(D, "synthetic_summary.csv")).set_index("analysis")
sc = s.loc["swap corrected"]
fig, ax = plt.subplots(figsize=(9.5, 4.0))
labels = ["p < 0.05\n(no correction)", "padj < 0.05\n(corrected)"]
tot = [sc.raw_p05, sc.called]
falsep = [sc.raw_p05_not_planted, sc.called - sc.planted]
truep = [t - f for t, f in zip(tot, falsep)]
y = [1, 0]
ax.barh(y, truep, color=TEAL, height=0.55, label="planted (really changed)")
ax.barh(y, falsep, left=truep, color=CRIMSON, height=0.55, label="not planted (false)")
for yy, t, f, tr in zip(y, tot, falsep, truep):
    ax.text(t + 12, yy, f"{int(t)} genes: {int(f)} false", va="center", fontsize=15, color=DARK)
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlim(0, 1300); ax.set_xlabel("genes called changed (of 10 000)")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=2, fontsize=13)
save(fig, "fig13-multiple-testing.svg")

fig, ax = plt.subplots(figsize=(9.5, 4.0))
rows = ["sheet as given", "S08 and S11 left out", "swap corrected"]
nice = ["sample sheet as given\n(S08, S11 swapped)", "S08 and S11\nleft out", "swap corrected"]
y = [2, 1, 0]
for yy, r in zip(y, rows):
    tp, n = s.loc[r, "planted"], s.loc[r, "called"]
    ax.barh(yy, tp, color=TEAL, height=0.55)
    ax.barh(yy, n - tp, left=tp, color=CRIMSON, height=0.55)
    ax.text(n + 8, yy, f"{int(n)} called, {int(tp)} planted", va="center", fontsize=15, color=DARK)
ax.set_yticks(y); ax.set_yticklabels(nice)
ax.axvline(400, color="#777", ls="--", lw=1.2)
ax.text(400, 2.55, "400 planted", ha="center", fontsize=13, color="#555")
ax.set_xlim(0, 650); ax.set_xlabel("genes at padj < 0.05, design ~ batch + treatment")
save(fig, "fig14-swap-effect.svg")

# fig15 volcano and fig16 MA (airway) -----------------------------------------
a = pd.read_csv(os.path.join(D, "airway_res.csv"))
a["y"] = -np.log10(a.padj.clip(lower=1e-150))
sig = a.padj < 0.05
big = sig & (a.lfc.abs() > 1)
known = ["FKBP5", "TSC22D3", "PER1", "ZBTB16", "DUSP1", "KLF15", "GAPDH"]
fig, ax = plt.subplots(figsize=(9, 5.6))
ax.scatter(a.lfc[~sig], a.y[~sig], s=5, color=GREY, linewidth=0, rasterized=True)
ax.scatter(a.lfc[sig & ~big], a.y[sig & ~big], s=5, color=OCHRE, linewidth=0, rasterized=True)
ax.scatter(a.lfc[big], a.y[big], s=5, color=CRIMSON, linewidth=0, rasterized=True)
for g in known:
    r = a[a.gene == g].iloc[0]
    ax.scatter([r.lfc], [r.y], s=70, facecolor="none", edgecolor=DARK, linewidth=1.5)
    dx = 0.35 if g not in ("ZBTB16",) else -2.4
    ax.text(r.lfc + dx, r.y + 1, g, fontsize=13, color=DARK)
ax.axhline(-np.log10(0.05), color="#777", ls="--", lw=1)
ax.axvline(1, color="#999", ls=":", lw=1); ax.axvline(-1, color="#999", ls=":", lw=1)
ax.set_xlabel("log2 fold change (dexamethasone vs untreated)")
ax.set_ylabel("−log10 padj  (higher = surer)")
ax.set_xlim(-7, 9.5)
ax.text(-6.8, 2.5, "padj = 0.05", fontsize=12, color="#555")
save(fig, "fig15-volcano.svg")

fig, ax = plt.subplots(figsize=(9, 5.0))
ax.scatter(a.baseMean[~sig], a.lfc[~sig].clip(-6, 6), s=5, color=GREY, linewidth=0, rasterized=True)
ax.scatter(a.baseMean[sig], a.lfc[sig].clip(-6, 6), s=5, color=CRIMSON, linewidth=0, rasterized=True)
ax.set_xscale("log")
ax.axhline(0, color=DARK, lw=1)
ax.set_xlabel("mean normalised count (log scale)")
ax.set_ylabel("log2 fold change")
ax.set_ylim(-6.3, 6.3)
ax.scatter([], [], s=30, color=CRIMSON, label="padj < 0.05")
ax.scatter([], [], s=30, color=GREY, label="not significant")
ax.legend(frameon=False, loc="upper right", fontsize=13)
ax.annotate("few reads: wide spread,\nlarge changes often not significant", (20, 1.6), (40, 4.8),
            fontsize=13, color=DARK, arrowprops=dict(arrowstyle="->", color=DARK))
save(fig, "fig16-ma-plot.svg")
print("done")
