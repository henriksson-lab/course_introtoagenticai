# Sample images from BBBC039

Three fields of view from the public dataset **BBBC039** (nuclei of U2OS
cells, Hoechst stain, from a chemical screen), shown here as small 8-bit
**preview** PNGs so they can be viewed in a browser:

| File | What it shows |
|---|---|
| `A16_s2_preview.png` | a typical field; some debris |
| `A12_s7_preview.png` | fragmented nuclei (the hand-drawn masks count each fragment) |
| `C07_s5_preview.png` | a crowded field with many touching nuclei |

The previews are contrast-stretched (camera values 120 to 1200 mapped to
0 to 255). **They are for looking only, not for analysis.** The exercise
downloads the original 16-bit TIFF files.

`true-counts.csv` gives, for the 10 images used in the exercise (the first
10 in `metadata/test.txt` of BBBC039), the number of nuclei in the
hand-drawn masks and their median area in square micrometres
(pixel size 0.656 micrometres, from the BBBC022 page). Counts were decoded
by labelling the connected pieces of each mask colour separately.

## Source, licence and citation

- Source: Broad Bioimage Benchmark Collection,
  <https://bbbc.broadinstitute.org/BBBC039>
- Licence: **CC0**. The contributors have waived all copyright and related
  rights to BBBC039v1.
- Requested citation: "We used image set BBBC039v1 Caicedo et al. 2018,
  available from the Broad Bioimage Benchmark Collection
  [Ljosa et al., Nature Methods, 2012]."

Made by `../make-figs.py` from the downloaded dataset.
