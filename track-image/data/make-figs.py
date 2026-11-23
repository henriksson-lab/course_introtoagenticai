#!/usr/bin/env python3
"""
make-figs.py: result figures and sample images for "Track C: Image analysis
in Python", from the public BBBC039 dataset.

BBBC039 (Caicedo et al. 2018, Broad Bioimage Benchmark Collection, Ljosa et
al., Nature Methods 2012) is released under CC0. Download images.zip,
masks.zip and metadata.zip from https://bbbc.broadinstitute.org/BBBC039 and
unzip them into one folder, so that it contains images/, masks/ and
metadata/. Then, from this folder:

    python3 make-figs.py <bbbc039-folder>

Writes:
  ../fig*.jpg, ../fig*.svg   lecture figures (into the unit folder)
  sample/*_preview.png       3 images as 8-bit previews (display only)
  sample/true-counts.csv     true counts for the 10 test images used in the
                             exercise, decoded from the hand-drawn masks

Two pipelines are compared with the decoded ground truth:
  simple   : Gaussian smoothing (sigma 1.5), one global Otsu threshold
  careful  : smoothing, background subtraction (grey opening on a 4x
             downsampled image), Otsu, remove objects <= 30 px, fill holes,
             split touching nuclei (distance transform + watershed,
             min_distance 7)
The 10 images are the first 10 in metadata/test.txt. It prints the numbers
quoted in lec.qmd and exercise.qmd.
Needs numpy, pandas, matplotlib, scipy, scikit-image (0.26 used).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage import feature, filters, io, measure, morphology, segmentation, transform

SRC = sys.argv[1]
OUT = ".."
PX = 0.656                       # micrometres per pixel (BBBC022 page: 20x, 0.656 um/pixel)
VMIN, VMAX = 120, 1200           # display range for previews
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
DARK = "#333333"
plt.rcParams.update({
    "svg.fonttype": "none", "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 15,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#666",
    "figure.facecolor": "white", "svg.hashsalt": "fig",
})


# --- analysis ---------------------------------------------------------------
def decode_mask(path):
    """Masks reuse colours; each connected piece of one colour is one nucleus."""
    m = io.imread(path)[..., :3].astype(int)
    code = m[..., 0] * 65536 + m[..., 1] * 256 + m[..., 2]
    lab = np.zeros(code.shape, int)
    n = 0
    for c in np.unique(code):
        if c == 0:
            continue
        pieces, k = ndi.label(code == c)
        lab[pieces > 0] = pieces[pieces > 0] + n
        n += k
    return lab


def simple(im):
    sm = filters.gaussian(im, 1.5, preserve_range=True)
    t = filters.threshold_otsu(sm)
    return measure.label(sm > t), t, sm


def background(sm):
    small = sm[::4, ::4]
    op = morphology.opening(small, morphology.disk(8))
    return transform.resize(filters.gaussian(op, 2, preserve_range=True), sm.shape, preserve_range=True)


def careful(im):
    sm = filters.gaussian(im, 1.5, preserve_range=True)
    th = sm - background(sm)
    m = th > filters.threshold_otsu(th)
    m = morphology.remove_small_objects(m, max_size=30)
    m = ndi.binary_fill_holes(m)
    lab = measure.label(m)
    dist = ndi.distance_transform_edt(m)
    pk = feature.peak_local_max(dist, min_distance=7, labels=lab, exclude_border=False)
    mk = np.zeros_like(lab)
    mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
    return segmentation.watershed(-dist, mk, mask=m)


# --- output helpers ---------------------------------------------------------
def fix_fonts(path):
    """matplotlib may write the font it found (DejaVu Sans); use a portable stack."""
    t = open(path).read()
    t = t.replace("font-family: 'DejaVu Sans'", "font-family: Helvetica, Arial, sans-serif")
    open(path, "w").write(t)


def save(fig, name, dpi=100):
    path = os.path.join(OUT, name)
    if name.endswith(".jpg"):
        fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", pil_kwargs={"quality": 82})
    else:
        fig.savefig(path, format="svg", bbox_inches="tight", dpi=100, metadata={"Date": None})
        fix_fonts(path)
    plt.close(fig)


def show(ax, im, title=None, vmax=VMAX):
    ax.imshow(im, cmap="gray", vmin=VMIN, vmax=vmax)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    if title:
        ax.set_title(title, fontsize=15, color=DARK)


def outline(ax, lab, color, lw=1.0):
    ax.contour(segmentation.find_boundaries(lab, mode="inner"), levels=[0.5], colors=[color], linewidths=lw)


def short(name):
    p = name.split("_")
    return p[1] + "_" + p[2]


def main():
    test = [l.strip()[:-4] for l in open(os.path.join(SRC, "metadata", "test.txt")) if l.strip()]
    names = test[:10]
    img = {short(b): io.imread(os.path.join(SRC, "images", b + ".tif")).astype(float) for b in names}
    full = {short(b): b for b in names}
    truth = {short(b): decode_mask(os.path.join(SRC, "masks", b + ".png")) for b in names}

    rows = []
    seg_s, seg_c = {}, {}
    for k, im in img.items():
        ls, _, _ = simple(im)
        lc = careful(im)
        seg_s[k], seg_c[k] = ls, lc
        rows.append(dict(image=full[k] + ".tif", short=k, true_count=truth[k].max(),
                         simple_count=ls.max(),
                         simple_small_objects=int(sum(p.area <= 30 for p in measure.regionprops(ls))),
                         careful_count=lc.max(),
                         true_median_area_um2=round(np.median([p.area for p in measure.regionprops(truth[k])]) * PX * PX, 1)))
    res = pd.DataFrame(rows)
    print(res.to_string())
    print("totals: true", res.true_count.sum(), "simple", res.simple_count.sum(), "careful", res.careful_count.sum())
    print("abs error simple", (res.simple_count - res.true_count).abs().sum(),
          "careful", (res.careful_count - res.true_count).abs().sum())
    os.makedirs("sample", exist_ok=True)
    res[["image", "true_count", "true_median_area_um2"]].to_csv("sample/true-counts.csv", index=False)

    # sample previews (8-bit, display only)
    for k in ("A16_s2", "A12_s7", "C07_s5"):
        u8 = (np.clip((img[k] - VMIN) / (VMAX - VMIN), 0, 1) * 255).astype(np.uint8)
        io.imsave(os.path.join("sample", f"{k}_preview.png"), u8, check_contrast=False)

    # fig01: 12 fields (the 10 test images and the next 2 in the test list)
    tiles = list(img.items()) + [(short(b), io.imread(os.path.join(SRC, "images", b + ".tif")).astype(float))
                                 for b in test[10:12]]
    fig, axs = plt.subplots(3, 4, figsize=(12.5, 7.4))
    for ax, (k, im) in zip(axs.flat, tiles):
        show(ax, im, k.replace("_", " "))
    fig.tight_layout()
    save(fig, "fig01-fields.jpg", dpi=80)

    # fig05: pixels as numbers (hand-written SVG from real values)
    k = "B02_s9"
    im = img[k]
    cand = [p for p in measure.regionprops(truth[k]) if 60 < p.centroid[0] < 460 and 60 < p.centroid[1] < 636]
    p = sorted(cand, key=lambda q: q.area)[len(cand) // 2]
    cy, cx = map(int, p.centroid)
    r = int(p.equivalent_diameter_area / 2)
    row = filters.gaussian(im, 1, preserve_range=True)[cy]
    half = (row[cx] + np.percentile(im, 5)) / 2
    xe = cx + int(np.argmax(row[cx:] < half))      # first pixel right of centre below half height
    x0 = xe - 4
    crop = im[cy - 4:cy + 4, x0:x0 + 8].astype(int)
    big = im[cy - 40:cy + 40, cx - 40:cx + 40]
    vmax5 = np.percentile(big, 99.5)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 470" width="1000" height="470" font-family="Helvetica, Arial, sans-serif">',
           '<rect width="1000" height="470" fill="#fff"/>']
    bs = big.reshape(20, 4, 20, 4).mean(axis=(1, 3))
    for i in range(20):
        for j in range(20):
            g = int(np.clip((bs[i, j] - VMIN) / (vmax5 - VMIN), 0, 1) * 255)
            svg.append(f'<rect x="{30 + j * 19}" y="{40 + i * 19}" width="19" height="19" fill="rgb({g},{g},{g})"/>')
    bx = 30 + (40 + x0 - cx) / 4 * 19
    by = 40 + (40 - 4) / 4 * 19
    svg.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="38" height="38" fill="none" stroke="{OCHRE}" stroke-width="3"/>')
    svg.append(f'<line x1="{bx + 38:.0f}" y1="{by:.0f}" x2="500" y2="40" stroke="{OCHRE}" stroke-width="2"/>')
    svg.append(f'<line x1="{bx + 38:.0f}" y1="{by + 38:.0f}" x2="500" y2="440" stroke="{OCHRE}" stroke-width="2"/>')
    svg.append('<text x="220" y="25" font-size="18" text-anchor="middle" fill="#333">one nucleus, zoomed in</text>')
    for i in range(8):
        for j in range(8):
            v = crop[i, j]
            g = int(np.clip((v - VMIN) / (vmax5 - VMIN), 0, 1) * 255)
            fg = "#000" if g > 140 else "#fff"
            svg.append(f'<rect x="{500 + j * 50}" y="{40 + i * 50}" width="50" height="50" fill="rgb({g},{g},{g})" stroke="#ccc" stroke-width="0.5"/>')
            svg.append(f'<text x="{525 + j * 50}" y="{71 + i * 50}" font-size="16" text-anchor="middle" fill="{fg}">{v}</text>')
    svg.append('<text x="700" y="25" font-size="18" text-anchor="middle" fill="#333">8 x 8 pixels: each is one number</text>')
    svg.append('<text x="915" y="200" font-size="17" fill="#333">inside:</text><text x="915" y="222" font-size="17" fill="#333">high</text>')
    svg.append('<text x="915" y="280" font-size="17" fill="#333">outside:</text><text x="915" y="302" font-size="17" fill="#333">low</text>')
    svg.append('<text x="30" y="460" font-size="16" fill="#555">real values from BBBC039, image B02_s9 (camera range 0 to 4095)</text>')
    svg.append('</svg>')
    open(os.path.join(OUT, "fig05-pixels.svg"), "w").write("\n".join(svg))

    # fig06: display range
    raw16 = io.imread(os.path.join(SRC, "images", full["B02_s9"] + ".tif"))
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.9))
    axs[0].imshow(raw16, cmap="gray", vmin=0, vmax=65535)
    axs[0].set_title("shown as 0 to 65 535 (16-bit range):\nlooks black", fontsize=15, color=DARK)
    show(axs[1], raw16.astype(float))
    axs[1].set_title(f"shown as {VMIN} to {VMAX}:\nsame file, same numbers", fontsize=15, color=DARK)
    for ax in axs:
        ax.set_xticks([]); ax.set_yticks([])
    save(fig, "fig06-display-range.jpg", dpi=80)

    # fig09: image, mask as stored, decoded labels
    k = "A22_s8"
    m = io.imread(os.path.join(SRC, "masks", full[k] + ".png"))[..., :3]
    ncol = len(np.unique(m.reshape(-1, 3), axis=0)) - 1
    codes = np.unique(m.reshape(-1, 3), axis=0)
    palette = {tuple(c): col for c, col in zip(codes, [(1, 1, 1), (0.66, 0.2, 0.29), (0.16, 0.5, 0.56),
                                                       (0.42, 0.31, 0.63), (0.54, 0.42, 0.07), (0.3, 0.3, 0.3)] * 5)}
    shown = np.zeros(m.shape[:2] + (3,))
    for c, col in palette.items():
        shown[(m == np.array(c)).all(axis=-1)] = col
    sl = (slice(150, 370), slice(250, 520))
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9))
    show(axs[0], img[k][sl], "image")
    axs[1].imshow(shown[sl], interpolation="nearest")
    axs[1].set_title(f"mask as stored: {ncol} colours, reused", fontsize=15, color=DARK)
    t = truth[k][sl]
    rng = np.random.default_rng(5)
    lut = np.vstack([[1, 1, 1], rng.uniform(0.2, 0.9, (truth[k].max() + 1, 3))])
    axs[2].imshow(lut[t], interpolation="nearest")
    axs[2].set_title(f"decoded: {len(np.unique(t)) - 1} nuclei in this crop", fontsize=15, color=DARK)
    for ax in axs:
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    save(fig, "fig09-masks.jpg", dpi=90)
    print("mask", k, "colours", ncol, "nuclei", truth[k].max())

    # fig10: Otsu histogram
    k = "B02_s9"
    _, t, sm = simple(img[k])
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    bins = np.arange(100, 2000, 15)
    h = np.histogram(sm.ravel(), bins=bins)[0]
    ax.hist(sm.ravel(), bins=bins, color="#9aa", log=True)
    ax.axvline(t, color=CRIMSON, lw=2.5)
    ax.text(t + 30, h.max() * 0.6, f"Otsu threshold\n= {t:.0f}", color=CRIMSON, fontsize=15)
    peak = bins[np.argmax(h)]
    ax.annotate("background (most pixels)", (peak + 10, h.max() * 0.8), (950, h.max() * 0.08), fontsize=14,
                color=DARK, arrowprops=dict(arrowstyle="->", color=DARK))
    ax.text(1300, 150, "nuclei", fontsize=14, color=DARK)
    ax.set_xlabel("pixel value (after light smoothing)")
    ax.set_ylabel("number of pixels (log scale)")
    save(fig, "fig10-otsu-histogram.svg")
    print("otsu B02_s9", round(t))

    # fig11: image, threshold, labels (crop)
    k = "C07_s5"
    ls, t, sm = simple(img[k])
    sl = (slice(0, 200), slice(0, 260))
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9))
    show(axs[0], img[k][sl], "1. image")
    axs[1].imshow((sm > t)[sl], cmap="gray")
    axs[1].set_title("2. threshold: yes or no per pixel", fontsize=15, color=DARK)
    sub = measure.label(ls[sl] > 0)
    lut = np.vstack([[1, 1, 1], rng.uniform(0.25, 0.85, (sub.max() + 1, 3))])
    axs[2].imshow(lut[sub], interpolation="nearest")
    for pr in measure.regionprops(sub):
        y, x = pr.centroid
        axs[2].text(x, y, str(pr.label), fontsize=9, ha="center", va="center", color="black")
    axs[2].set_title("3. label: one number per blob", fontsize=15, color=DARK)
    for ax in axs[1:]:
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    save(fig, "fig11-mask-labels.jpg", dpi=90)

    # fig13: overlay of the simple result, with what went wrong
    k = "C07_s5"
    ls = seg_s[k]
    tl = truth[k]
    fig, ax = plt.subplots(figsize=(9.6, 7.6))
    show(ax, img[k])
    outline(ax, ls, "#00e5ff", 0.9)
    merged = missed = debris = 0
    for pr in measure.regionprops(ls):
        y, x = pr.centroid
        inside = np.unique(tl[ls == pr.label])
        inside = inside[inside > 0]
        if pr.area <= 30:
            ax.add_patch(plt.Circle((x, y), 9, fill=False, color="#ffb000", lw=2))
            debris += 1
        elif len(inside) >= 2:
            ax.add_patch(plt.Circle((x, y), np.sqrt(pr.area) * 0.75, fill=False, color="#ff4d6d", lw=1.8, ls="--"))
            merged += len(inside) - 1
    for pr in measure.regionprops(tl):
        if not (ls[tl == pr.label] > 0).any():
            y, x = pr.centroid
            ax.add_patch(plt.Circle((x, y), 15, fill=False, color="#c77dff", lw=2.2))
            missed += 1
    ax.set_title(f"{k}: the simple script counts {ls.max()}, people counted {tl.max()}", fontsize=16, color=DARK)
    fig.text(0.5, 0.03, "cyan: the script's outlines    red dashed: several nuclei in one outline\n"
             "purple: nucleus missed    orange: speck counted as a nucleus", ha="center", fontsize=13, color=DARK)
    save(fig, "fig13-overlay.jpg", dpi=90)
    print("overlay", k, "simple", ls.max(), "true", tl.max(), "nuclei hidden in merges", merged,
          "missed", missed, "specks", debris)

    # fig14: touching nuclei, simple vs careful
    ls, lc = seg_s[k], seg_c[k]
    best = None
    for pr in measure.regionprops(ls):
        y, x = pr.centroid
        if not (50 < y < 470 and 50 < x < 646):
            continue
        n_true = len(np.unique(tl[ls == pr.label])) - 1
        n_c = len(np.unique(lc[ls == pr.label])) - 1
        if n_true == 2 and n_c == 2 and (best is None or pr.area > best.area):
            best = pr
    y, x = map(int, best.centroid)
    sl = (slice(y - 45, y + 45), slice(x - 45, x + 45))
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 5))
    for ax, lab, title in ((axs[0], ls, "one threshold: 1 object"), (axs[1], lc, "split by watershed: 2 objects")):
        show(ax, img[k][sl], title, vmax=np.percentile(img[k][sl], 99.5))
        b = segmentation.find_boundaries(lab[sl], mode="inner")
        ax.imshow(np.ma.masked_where(~b, b), cmap=matplotlib.colors.ListedColormap(["#00e5ff"]),
                  interpolation="nearest")
    save(fig, "fig14-touching.jpg", dpi=90)

    # fig15: fragmented nuclei in A12_s7: what counts as one nucleus?
    k = "A12_s7"
    ls, tl = seg_s[k], truth[k]
    best = max(measure.regionprops(ls), key=lambda q: len(np.unique(tl[ls == q.label])))
    y, x = map(int, best.centroid)
    y = min(max(y, 60), 520 - 60); x = min(max(x, 60), 696 - 60)
    sl = (slice(y - 60, y + 60), slice(x - 60, x + 60))
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.6))
    show(axs[0], img[k], f"{k}: people counted {tl.max()}")
    axs[0].add_patch(plt.Rectangle((x - 60, y - 60), 120, 120, fill=False, color="#ffb000", lw=2))
    show(axs[1], img[k][sl], "hand-drawn: each fragment", vmax=np.percentile(img[k][sl], 99.7))
    for v in np.unique(tl[sl]):
        if v:
            axs[1].contour(tl[sl] == v, levels=[0.5], colors=["#ff4d6d"], linewidths=1.6)
    show(axs[2], img[k][sl], f"simple script: {ls.max()} in the image", vmax=np.percentile(img[k][sl], 99.7))
    for v in np.unique(ls[sl]):
        if v:
            axs[2].contour(ls[sl] == v, levels=[0.5], colors=["#00e5ff"], linewidths=1.6)
    fig.tight_layout()
    save(fig, "fig15-fragments.jpg", dpi=85)
    print("fragments: one script object holds", len(np.unique(tl[ls == best.label])) - 1, "hand-drawn objects")

    # fig18: errors that cancel (simple vs true)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    xs = np.arange(len(res))
    ax.bar(xs - 0.2, res.true_count, 0.4, color="#bbb", label="true count (hand-drawn masks)")
    ax.bar(xs + 0.2, res.simple_count, 0.4, color=CRIMSON, label="simple script")
    for i, r in res.iterrows():
        d = r.simple_count - r.true_count
        ax.text(i + 0.2, r.simple_count + 2, f"{d:+d}" if d else "0", ha="center", fontsize=12, color=DARK)
    ax.set_xticks(xs); ax.set_xticklabels(res.short, fontsize=12)
    ax.set_ylabel("nuclei per image"); ax.set_ylim(0, 190)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=13)
    save(fig, "fig18-cancelling-errors.svg")

    # fig19: script vs true
    fig, ax = plt.subplots(figsize=(6.4, 5.8))
    ax.plot([0, 180], [0, 180], color="#999", ls="--", lw=1)
    ax.scatter(res.true_count, res.simple_count, s=70, color=CRIMSON, label="simple", zorder=3, edgecolor="white")
    ax.scatter(res.true_count, res.careful_count, s=70, color=TEAL, marker="s", label="careful", zorder=3, edgecolor="white")
    r12 = res[res.short == "A12_s7"].iloc[0]
    ax.annotate("A12_s7: fragmented nuclei", (r12.true_count, r12.careful_count), (85, 12), fontsize=12, color=DARK,
                arrowprops=dict(arrowstyle="->", color=DARK))
    ax.set_xlabel("true count (hand-drawn masks)"); ax.set_ylabel("count by the script")
    ax.set_xlim(0, 180); ax.set_ylim(0, 180)
    ax.text(140, 152, "same count", color="#777", fontsize=13, rotation=45)
    ax.legend(frameon=False, loc="upper left", fontsize=13)
    save(fig, "fig19-auto-vs-true.svg")

    # fig21: area distribution, truth vs simple
    a_true = np.concatenate([[p.area * PX * PX for p in measure.regionprops(truth[k])] for k in img])
    a_simple = np.concatenate([[p.area * PX * PX for p in measure.regionprops(seg_s[k])] for k in img])
    med = np.median(a_true)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    bins = np.arange(0, 1400, 25)
    ax.hist(a_true, bins=bins, color="#bbb", label=f"hand-drawn masks ({len(a_true)} nuclei)")
    ax.hist(a_simple, bins=bins, histtype="step", color=CRIMSON, lw=2.2, label=f"simple script ({len(a_simple)} objects)")
    ax.set_xlabel("nucleus area (µm²)"); ax.set_ylabel("number of objects")
    ax.annotate("merged pairs and clumps:\nabout twice the usual area", (2.1 * med, 10), (2.6 * med, 70), fontsize=13,
                color=DARK, arrowprops=dict(arrowstyle="->", color=DARK))
    ax.legend(frameon=False, fontsize=13, loc="upper right")
    save(fig, "fig21-area-histogram.svg")
    print("median area um2 true", round(med, 1), "simple", round(np.median(a_simple), 1),
          "objects > 2x median: simple", int((a_simple > 2 * med).sum()), "true", int((a_true > 2 * med).sum()),
          "simple objects <= 30 px:", int((a_simple <= 30 * PX * PX).sum()))


if __name__ == "__main__":
    main()
