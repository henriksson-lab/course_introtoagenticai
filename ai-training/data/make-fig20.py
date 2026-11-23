"""Make fig20-detect-vs-segment.png: outlines vs boxes on a real BBBC039 crop (CC0).
Run from the repo root: python3 ai-training/data/make-fig20.py
Source image: track-image/data/sample/C07_s5_preview.png (BBBC039v1, Caicedo et al. 2018, CC0)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from skimage import filters, measure, morphology, segmentation, feature
from scipy import ndimage as ndi

img = np.asarray(Image.open("track-image/data/sample/C07_s5_preview.png"), dtype=float)
crop = img[60:330, 120:480]
smooth = filters.gaussian(crop, 1.5)
mask = smooth > filters.threshold_otsu(smooth)
mask = morphology.remove_small_objects(mask, max_size=40)
# split touching nuclei with a distance-transform watershed
dist = ndi.distance_transform_edt(mask)
peaks = feature.peak_local_max(dist, min_distance=9, labels=measure.label(mask), exclude_border=False)
markers = np.zeros_like(mask, dtype=int); markers[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
lab = segmentation.watershed(-dist, markers, mask=mask)
props = [p for p in measure.regionprops(lab) if p.area >= 40]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.9), dpi=120)
for ax, title in zip(axes, ["Segmentation: an outline per object", "Detection: a box per object"]):
    ax.imshow(crop, cmap="gray", vmin=np.percentile(crop, 1), vmax=np.percentile(crop, 99.5))
    ax.set_title(title, fontsize=17, pad=8)
    ax.axis("off")
bound = morphology.binary_dilation(segmentation.find_boundaries(lab, mode="inner"), morphology.disk(1))
over = np.zeros(crop.shape + (4,)); over[bound] = (0.10, 0.85, 0.95, 1)
axes[0].imshow(over)
for p in props:
    r0, c0, r1, c1 = p.bbox
    axes[1].add_patch(Rectangle((c0 - 1.5, r0 - 1.5), c1 - c0 + 2, r1 - r0 + 2, fill=False, ec="#e0a000", lw=1.8))
    axes[1].plot(*p.centroid[::-1], "+", color="#e0a000", ms=5, mew=1.2)
for ax in axes:
    ax.set_xlim(-0.5, crop.shape[1] - 0.5); ax.set_ylim(crop.shape[0] - 0.5, -0.5)
axes[0].text(0.01, -0.06, "label: every pixel of the outline · gives area, shape", transform=axes[0].transAxes, fontsize=13, color="#333")
axes[1].text(0.01, -0.06, f"label: 4 numbers per object · gives count ({len(props)}), position", transform=axes[1].transAxes, fontsize=13, color="#333")
fig.text(0.99, 0.01, "Real image: BBBC039v1 (Caicedo et al. 2018), CC0. Objects found with a simple threshold and watershed, for illustration.",
         ha="right", fontsize=10, color="#777")
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.11, wspace=0.04)
fig.savefig("ai-training/fig20-detect-vs-segment.png")
print(len(props), "objects")
