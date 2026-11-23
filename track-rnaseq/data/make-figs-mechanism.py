#!/usr/bin/env python3
"""make-figs-mechanism.py: draws fig21 to fig36 of the deck "From gene lists to
mechanisms" (track-rnaseq/lec-mechanism.qmd) as SVG.

    python3 make-figs-mechanism.py ..        (run from this folder)

Plain Python, no libraries. Numbers in the bar charts (fig22, fig24, fig29 to
fig31, fig33) are typed in from the output of make-mechanism.R and from PubMed
counts (E-utilities, 2026-11-23); if you rerun the analysis, update them here.
fig35 integrates a small illustrative ODE (parameters below, not fitted).
"""
import math, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else ".."
TEAL, PURP, CRIM, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
G1, G2, G3 = "#333", "#777", "#bbb"
LT = {"teal": "#eef6f7", "purp": "#f3f0f8", "crim": "#f9ecef", "ochre": "#f6f1e1", "grey": "#f2f2f2"}
ARROW = "<defs>" + "".join(
    f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for k, c in [("a", "#777"), ("a2a7f8f", "#2a7f8f"), ("a6b4fa0", "#6b4fa0"), ("aa8324a", "#a8324a"), ("a8a6a12", "#8a6a12")]) + "</defs>"

def svg(name, h, body, w=1000):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'font-family="Helvetica, Arial, sans-serif">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{ARROW}\n{body}\n</svg>\n')
    open(os.path.join(OUT, name), "w").write(s)

def t(x, y, s, size=18, fill=G1, anchor="start", bold=False, italic=False):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    b = ' font-weight="bold"' if bold else ""
    i = ' font-style="italic"' if italic else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{b}{i}>{s}</text>'

def box(x, y, w, h, fill, stroke, rx=8, sw=2, dash=False):
    d = ' stroke-dasharray="6,4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def arrow(x1, y1, x2, y2, col="#777", sw=2.5, dash=False):
    d = ' stroke-dasharray="7,5"' if dash else ""
    m = "a" if col == "#777" else "a" + col.lstrip("#")
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}" marker-end="url(#{m})"{d}/>'

# ---------- fig21: from gene list to mechanism ----------
steps = [("gene list", "DESeq2 results", TEAL, "teal"),
         ("top genes", "a rule you wrote", TEAL, "teal"),
         ("literature table", "verified PMIDs", OCHRE, "ochre"),
         ("regulators", "TF / pathway activity", PURP, "purp"),
         ("hypothesis", "evidence on each arrow", PURP, "purp"),
         ("predictions", "what would refute it", CRIM, "crim")]
b = []
for i, (a1, a2, c, l) in enumerate(steps):
    x = 15 + i * 165
    b.append(box(x, 60, 145, 110, LT[l], c))
    b.append(t(x + 72, 105, a1, 18, c, "middle", True))
    for j, line in enumerate(a2.split(" / ") if "/" in a2 and len(a2) > 18 else [a2]):
        pass
    words = a2.split(" ")
    lines, cur = [], ""
    for w_ in words:
        if len(cur + " " + w_) > 15 and cur:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    for j, ln in enumerate(lines):
        b.append(t(x + 72, 135 + j * 20, ln, 16, G1, "middle"))
    if i < 5:
        b.append(arrow(x + 147, 115, x + 163, 115))
b.append(t(15, 40, "Part 1: what is known about each gene", 18, OCHRE, bold=True))
b.append(t(510, 40, "Part 2: what could explain them all", 18, PURP, bold=True))
b.append(t(500, 225, "The agent searches, computes and drafts. You choose the rule, check every claim,", 18, G1, "middle"))
b.append(t(500, 252, "and decide which prediction is worth an experiment.", 18, G1, "middle"))
svg("fig21-list-to-mechanism.svg", 280, "\n".join(b))

# ---------- fig22: ranking choices ----------
cols = [("by padj", "smallest first", ["SPARCL1", "CACNB2", "DUSP1", "SAMHD1", "MAOA", "GPX3", "STEAP2", "NEXN", "MT2A", "ADAMTS1"], None),
        ("by |log2 fold change|", "largest first, no filter", ["ALOX15B", "ZBTB16", "LOC101928819", "GUCY2D", "MCHR1", "STEAP4", "LINC02997", "ANGPTL7", "PRODH", "SERTM2"],
         [67, 385, 56, 5.7, 6.6, 286, 8.8, 255, 55, 6.7]),
        ("|log2 FC|, mean count > 100", "5 up + 5 down", ["ZBTB16", "STEAP4", "ANGPTL7", "FAM107A", "RASL11B", "VCAM1", "FER1L6", "WNT2", "AQP3", "SLC7A14"], None)]
b = []
for i, (h1, h2, genes, bm) in enumerate(cols):
    x = 20 + i * 330
    c = [TEAL, CRIM, PURP][i]
    b.append(box(x, 15, 310, 70, LT[["teal", "crim", "purp"][i]], c))
    b.append(t(x + 155, 45, h1, 19, c, "middle", True))
    b.append(t(x + 155, 72, h2, 16, G1, "middle"))
    for j, g in enumerate(genes):
        y = 118 + j * 30
        col = G1
        if bm and bm[j] < 20:
            col = G2
        down = (i == 2 and j >= 5)
        b.append(t(x + 20, y, f"{j+1}.", 17, G2))
        b.append(t(x + 55, y, g, 17, CRIM if down else col, bold=False))
        if bm:
            b.append(t(x + 300, y, f"mean {bm[j]:g}", 15, G2 if bm[j] < 20 else G2, "end"))
        if down:
            b.append(t(x + 300, y, "down", 15, CRIM, "end"))
b.append(t(500, 435, "Top 20 by padj and top 20 by fold change share only 2 genes; with the count filter, 8.", 18, G1, "middle"))
b.append(t(500, 462, "Without a filter, fold change favours genes with a handful of reads (grey: mean count < 20).", 18, G1, "middle"))
b.append(t(20, 492, "airway, ~ cell + dex, DESeq2 1.52, genes with padj < 0.05. Unshrunken fold changes.", 15, G2))
svg("fig22-ranking-choices.svg", 505, "\n".join(b))

# ---------- fig23: query with context ----------
b = []
parts = [("(TSC22D3[tiab] OR GILZ[tiab])", "the gene: symbol AND aliases", TEAL, "teal", 20, 330),
         ("AND", "", G1, "grey", 360, 70),
         ("(glucocorticoid*[tiab] OR dexamethasone[tiab])", "the treatment", PURP, "purp", 440, 540)]
for s_, lab, c, l, x, w in parts:
    if s_ == "AND":
        b.append(t(x + 35, 75, "AND", 20, G1, "middle", True)); continue
    b.append(box(x, 40, w, 55, LT[l], c))
    b.append(t(x + w / 2, 75, s_, 18, c, "middle", True))
    b.append(t(x + w / 2, 125, lab, 17, G1, "middle"))
b.append(t(360, 190, "AND", 20, G1, "middle", True))
b.append(box(440, 160, 540, 55, LT["ochre"], OCHRE, dash=True))
b.append(t(710, 195, "optional: (smooth muscle[tiab] OR airway[tiab])", 18, OCHRE, "middle", True))
b.append(t(710, 245, "the tissue or cell type: add it when the gene has many hits", 17, G1, "middle"))
b.append(t(20, 300, "Gene alone: everything ever written about it, mostly other contexts.", 18, G1))
b.append(t(20, 330, "Gene + treatment: is this response already known?  Gene + treatment + tissue: known here?", 18, G1))
b.append(t(20, 360, "Run all three levels and keep the counts: they tell you how new the finding is.", 18, TEAL, bold=True))
svg("fig23-query-context.svg", 380, "\n".join(b))

# ---------- fig24: alias counts ----------
data = [("TSC22D3", "GILZ", 71, 423), ("DUSP1", "MKP-1", 81, 219), ("FKBP5", "FKBP51", 576, 739), ("ZBTB16", "PLZF", 40, 52), ("FAM107A", "DRR1", 9, 10)]
b = []
x0, sc = 260, 0.85
b.append(t(20, 30, "PubMed hits, title/abstract, AND (glucocorticoid* OR dexamethasone)", 18, G1, bold=True))
for i, (g, al, a, c) in enumerate(data):
    y = 60 + i * 78
    b.append(t(x0 - 15, y + 22, g, 19, G1, "end", True))
    b.append(t(x0 - 15, y + 50, f"+ {al}", 17, G2, "end"))
    b.append(f'<rect x="{x0}" y="{y+6}" width="{a*sc:.1f}" height="22" fill="{G3}"/>')
    b.append(t(x0 + a * sc + 8, y + 24, str(a), 17, G1))
    b.append(f'<rect x="{x0}" y="{y+34}" width="{c*sc:.1f}" height="22" fill="{TEAL}"/>')
    b.append(t(x0 + c * sc + 8, y + 52, str(c), 17, TEAL, bold=True))
b.append(f'<rect x="{x0}" y="460" width="18" height="16" fill="{G3}"/>' + t(x0 + 26, 474, "symbol only", 17, G1))
b.append(f'<rect x="{x0+180}" y="460" width="18" height="16" fill="{TEAL}"/>' + t(x0 + 206, 474, "symbol OR alias", 17, G1))
b.append(t(20, 505, "Searched 2026-11-23 via E-utilities; your counts will be a little higher.", 15, G2))
svg("fig24-alias-counts.svg", 520, "\n".join(b))

# ---------- fig25: gene table mock-up ----------
hdr = ["gene", "here", "known with GC?", "claim (short)", "PMID", "evidence"]
xs = [20, 135, 225, 395, 735, 845]
rows = [("FKBP5", "up 16x", "yes", "GC raise FKBP51 mRNA within 2 h", "12519866", "cell exp."),
        ("DUSP1", "up 8x", "yes, in ASM", "dex induces MKP-1; GR at promoter", "17513787", "cell exp."),
        ("KLF15", "up 22x", "yes, in ASM", "Klf15 is a GC target in ASM", "21257922", "cell + mouse"),
        ("ZBTB16", "up 160x", "yes, other SMC", "dex induces PLZF within 2 h", "12970399", "cell exp."),
        ("SPARCL1", "up 24x", "none found", "-", "-", "-"),
        ("VCAM1", "down 13x", "to check", "", "", "")]
b = [box(10, 10, 980, 44, LT["purp"], PURP, rx=4)]
for x, h_ in zip(xs, hdr):
    b.append(t(x, 39, h_, 17, PURP, bold=True))
for i, r in enumerate(rows):
    y = 90 + i * 44
    if i % 2:
        b.append(f'<rect x="10" y="{y-28}" width="980" height="44" fill="#fafafa"/>')
    for j, (x, v) in enumerate(zip(xs, r)):
        col = G1
        if j == 2 and v == "none found": col = OCHRE
        if j == 2 and v == "to check": col = G2
        if j == 4 and v not in ("-", ""): col = TEAL
        b.append(t(x, y, v, 16, col, bold=(j == 0)))
b.append(t(20, 365, "One row per gene and claim. PMID, title and quote are copied by a script and verified; the", 17, G1))
b.append(t(20, 390, "\"here\" column comes from your DESeq2 table. ASM: airway smooth muscle; SMC: smooth muscle cells.", 17, G1))
b.append(t(985, 412, "illustrative", 14, G3, "end"))
svg("fig25-gene-table.svg", 420, "\n".join(b))

# ---------- fig26: known / known elsewhere / little found ----------
bins = [("known in this context", "GC + airway or smooth muscle", ["TSC22D3 (22)", "FKBP5 (11)", "PER1 (4)", "ZBTB16 (4)"], TEAL, "teal",
         "confirms the experiment worked"),
        ("known elsewhere", "GC, but other tissues", ["FAM107A (brain)", "ANGPTL7 (eye)"], OCHRE, "ochre",
         "plausible here: cite the other context"),
        ("nothing found", "with GC, any tissue", ["SPARCL1 (0)", "RASL11B (0)", "FER1L6 (0)", "CACNB2 (0)"], CRIM, "crim",
         "candidate novelty, or a name problem")]
b = []
for i, (h1, h2, genes, c, l, foot) in enumerate(bins):
    x = 20 + i * 330
    b.append(box(x, 20, 310, 330, LT[l], c))
    b.append(t(x + 155, 55, h1, 20, c, "middle", True))
    b.append(t(x + 155, 82, h2, 16, G1, "middle"))
    for j, g in enumerate(genes):
        b.append(box(x + 55, 105 + j * 44, 200, 34, "#fff", c, rx=17, sw=1.5))
        b.append(t(x + 155, 128 + j * 44, g, 17, G1, "middle", True))
    b.append(t(x + 155, 335, foot, 16, c, "middle", True))
b.append(t(20, 385, "airway, strongly changed genes. In brackets: PubMed hits for gene (with aliases) AND glucocorticoid AND", 16, G2))
b.append(t(20, 407, "(airway OR smooth muscle), 2026-11-23. The bin is where reading starts, not a verdict.", 16, G2))
svg("fig26-known-unknown.svg", 420, "\n".join(b))

# ---------- fig27: enrichment vs mechanism ----------
b = []
b.append(box(20, 20, 450, 330, LT["teal"], TEAL))
b.append(t(245, 55, "Enrichment", 21, TEAL, "middle", True))
b.append(t(245, 82, "which themes are over-represented?", 17, G1, "middle"))
for j, (term, w) in enumerate([("response to glucocorticoid", 300), ("extracellular matrix", 240), ("circadian rhythm", 170), ("cell migration", 140)]):
    y = 115 + j * 50
    b.append(f'<rect x="50" y="{y}" width="{w}" height="30" fill="{TEAL}" opacity="0.75"/>')
    b.append(t(60, y + 21, term, 16, "#fff", bold=True))
b.append(t(245, 330, "a list of labels, no arrows", 17, TEAL, "middle", True))
b.append(box(530, 20, 450, 330, LT["purp"], PURP))
b.append(t(755, 55, "Mechanism", 21, PURP, "middle", True))
b.append(t(755, 82, "what caused the change, in which order?", 17, G1, "middle"))
chain = ["dexamethasone", "GR (NR3C1) active", "binds DNA near targets", "FKBP5, DUSP1, KLF15 ... up"]
for j, s_ in enumerate(chain):
    y = 105 + j * 55
    b.append(box(620, y, 270, 38, "#fff", PURP, rx=6, sw=1.5))
    b.append(t(755, y + 25, s_, 17, G1, "middle"))
    if j < 3:
        b.append(arrow(755, y + 39, 755, y + 54))
b.append(t(755, 330, "arrows you can test", 17, PURP, "middle", True))
b.append(t(500, 385, "Enrichment terms are illustrative. A mechanism needs direction and order; enrichment has neither.", 16, G2, "middle"))
svg("fig27-enrichment-vs-mechanism.svg", 400, "\n".join(b))

# ---------- fig28: footprint ----------
b = []
b.append(box(40, 150, 200, 80, LT["purp"], PURP))
b.append(t(140, 185, "regulator R", 20, PURP, "middle", True))
b.append(t(140, 212, "activity: ?", 17, G1, "middle"))
targets = [("T1", 2.1, 1), ("T2", 1.6, 1), ("T3", 2.6, 1), ("T4", 0.2, 1), ("T5", -1.9, -1), ("T6", -1.2, -1)]
for i, (n, st, mor) in enumerate(targets):
    y = 40 + i * 58
    col = TEAL if mor > 0 else CRIM
    b.append(f'<line x1="240" y1="190" x2="400" y2="{y+18}" stroke="{col}" stroke-width="2.5"/>')
    lab = "+" if mor > 0 else "-"
    b.append(t(392, y + 30, lab, 22, col, "end", True))
    b.append(box(405, y, 80, 36, "#fff", G2, rx=6, sw=1.5))
    b.append(t(445, y + 24, n, 17, G1, "middle", True))
    # bar for stat
    zero = 720
    w = st * 60
    x = zero if w >= 0 else zero + w
    b.append(f'<rect x="{x:.0f}" y="{y+6}" width="{abs(w):.0f}" height="24" fill="{TEAL if st > 0 else CRIM}" opacity="0.8"/>')
    b.append(t(zero + (w + 10 if w >= 0 else w - 10), y + 24, f"{st:+.1f}", 16, G1, "start" if w >= 0 else "end"))
b.append(f'<line x1="720" y1="30" x2="720" y2="380" stroke="{G2}" stroke-width="1.5"/>')
b.append(t(720, 20, "DE statistic in your data", 17, G1, "middle", True))
b.append(t(20, 420, "The network says which genes R activates (+) and represses (-). If the + targets go up and the - targets", 17, G1))
b.append(t(20, 445, "go down, R's activity score is high, even when R's own mRNA does not change.", 17, G1))
b.append(t(985, 470, "illustrative", 14, G3, "end"))
svg("fig28-footprint.svg", 480, "\n".join(b))

# ---------- bar chart helper ----------
def bars(name, title, items, zero, sc, h, notes, colfun, rowh=40, labw=170, foot=None):
    b = [t(20, 30, title, 18, G1, bold=True)]
    y0 = 55
    for i, (lab, v, extra) in enumerate(items):
        y = y0 + i * rowh
        c = colfun(lab, v)
        w = v * sc
        x = zero if w >= 0 else zero + w
        b.append(t(zero - 10 if w >= 0 else zero + 10, y + 21, lab, 17, G1, "end" if w >= 0 else "start", True))
        b.append(f'<rect x="{x:.1f}" y="{y+4}" width="{abs(w):.1f}" height="24" fill="{c}"/>')
        b.append(t(zero + w + (8 if w >= 0 else -8), y + 22, f"{v:+.1f}" + (f"  ({extra})" if extra else ""), 16, G1, "start" if w >= 0 else "end"))
    b.append(f'<line x1="{zero}" y1="{y0-5}" x2="{zero}" y2="{y0+len(items)*rowh}" stroke="{G2}" stroke-width="1.5"/>')
    yy = y0 + len(items) * rowh + 30
    for k, n in enumerate(notes):
        b.append(t(20, yy + k * 25, n, 17 if k < len(notes) - 1 or not foot else 15, G1 if not (foot and k == len(notes) - 1) else G2))
    svg(name, yy + len(notes) * 25 - 5, "\n".join(b))

syn = [("RegA", 50.9, ""), ("RegC", 34.2, ""), ("RegD", 10.8, "decoy"), ("RegE", 0.8, ""), ("RegH", -0.4, ""), ("RegJ", -0.5, ""),
       ("RegF", -0.5, ""), ("RegG", -0.5, ""), ("RegI", -0.7, ""), ("RegB", -34.9, "")]
bars("fig29-synthetic-activity.svg", "Synthetic pilot: regulator activity (decoupler ulm on the DESeq2 statistic)", syn, 470, 6.5, 0,
     ["Planted: RegA on, RegB off, RegC on (activates 40 genes, represses 60). Decoys D to J: unchanged genes.",
      "RegD is a decoy, yet p < 1e-25: it shares 20 targets with RegA's program.",
      "Swap corrected, ~ batch + treatment; network data/regulons.csv; decoupleR 2.17."],
     lambda l, v: TEAL if l in ("RegA", "RegC") else (CRIM if l == "RegB" else (OCHRE if l == "RegD" else G3)), rowh=36, foot=True)

air = [("PGR", 6.1, "mean count 6"), ("NR3C1", 5.7, "mean count 2811"), ("TCF21", 5.4, ""), ("SMAD7", 4.8, ""), ("MYOCD", 4.8, ""),
       ("KLF15", 4.3, ""), ("SALL2", -4.8, ""), ("WT1", -5.0, ""), ("JDP2", -5.3, ""), ("ATF3", -5.6, "")]
bars("fig30-airway-activity.svg", "airway: top transcription factors by p-value (CollecTRI regulons, ulm)", air, 470, 38, 0,
     ["Rank 1 is the progesterone receptor, which these cells barely express (mean count 6).",
      "The glucocorticoid receptor, NR3C1, is rank 2. Its regulon shares 44 targets with PGR's 133.",
      "~ cell + dex, DESeq2 stat; CollecTRI via OmnipathR 4.0.4, decoupleR 2.17; 2026-11-23."],
     lambda l, v: PURP if l == "NR3C1" else (OCHRE if l == "PGR" else (TEAL if v > 0 else CRIM)), rowh=36, foot=True)

prog = [("Androgen", 8.9, ""), ("MAPK", 3.5, ""), ("NFkB", 2.7, ""), ("TGFb", 1.3, ""), ("VEGF", 1.1, ""), ("TNFa", -2.3, ""),
        ("JAK-STAT", -4.1, ""), ("p53", -4.5, "")]
bars("fig31-progeny.svg", "airway: PROGENy pathway activities (top 500 genes per pathway, mlm)", prog, 470, 30, 0,
     ["PROGENy has 14 pathways and none for glucocorticoids. The steroid signal lands on \"Androgen\":",
      "its footprint includes ZBTB16 and KLF15. The cells were never given an androgen.",
      "decoupleR 2.17, get_progeny(top = 500); scores are t-values."],
     lambda l, v: OCHRE if l == "Androgen" else (TEAL if v > 0 else CRIM), rowh=36, foot=True)

# ---------- fig32: generic chain with evidence labels ----------
EV = {"measured": (TEAL, "seen in your own data: fold change, padj"), "cited": (OCHRE, "a paper says so: PMID, and is it the same cell type?"),
      "inferred": (PURP, "a tool or an argument, from your data plus a network"), "speculation": (CRIM, "plausible, but no support yet")}
b = []
nodes = ["stimulus", "receptor", "signalling", "TF", "target genes", "phenotype"]
evs = ["cited", "inferred", "cited", "measured", "speculation"]
for i, n in enumerate(nodes):
    x = 10 + i * 166
    b.append(box(x, 40, 126, 60, LT["grey"], G1))
    b.append(t(x + 63, 77, n, 17, G1, "middle", True))
    if i < 5:
        c = EV[evs[i]][0]
        dash = evs[i] in ("inferred", "speculation")
        b.append(arrow(x + 128, 70, x + 164, 70, c, 4, dash))
        b.append(box(x + 84, 120, 126, 30, "#fff", c, rx=15, sw=2))
        b.append(t(x + 147, 141, evs[i], 16, c, "middle", True))
for k, (key, (c, lab)) in enumerate(EV.items()):
    y = 200 + k * 40
    dash = ' stroke-dasharray="7,5"' if key in ("inferred", "speculation") else ""
    b.append(f'<line x1="40" y1="{y}" x2="110" y2="{y}" stroke="{c}" stroke-width="4"{dash}/>')
    b.append(t(125, y + 6, key, 18, c, bold=True))
    b.append(t(260, y + 6, lab, 18, G1))
b.append(t(20, 375, "A chain is as strong as its weakest arrow. Solid: evidence you can show. Dashed: a guess, however plausible.", 17, G1))
svg("fig32-chain-generic.svg", 390, "\n".join(b))

# ---------- fig33: airway chain ----------
b = []
def node(x, y, w, s1, s2=None, c=G1, l="grey"):
    o = [box(x, y, w, 56 if s2 else 40, LT[l], c)]
    o.append(t(x + w / 2, y + 26, s1, 17, c, "middle", True))
    if s2: o.append(t(x + w / 2, y + 47, s2, 15, G1, "middle"))
    return "\n".join(o)
def lab(x, y, kind, ref, anchor="start"):
    c = EV[kind][0]
    return t(x, y, f"{kind}" + (f": {ref}" if ref else ""), 15, c, anchor, True)
b.append(node(380, 10, 240, "dexamethasone, 1 µM 18 h", None))
b.append(arrow(500, 52, 500, 88, EV["cited"][0], 3.5)); b.append(lab(512, 76, "cited", "21257922"))
b.append(node(330, 90, 340, "glucocorticoid receptor (NR3C1)", "activity rank 2 of 730 TFs scored; mRNA down 2x", PURP, "purp"))
b.append(lab(680, 112, "inferred", "decoupler")); b.append(lab(680, 132, "measured", "mRNA"))
b.append(arrow(500, 148, 500, 186, EV["cited"][0], 3.5)); b.append(lab(512, 174, "cited", "17513787, 28375666"))
b.append(node(250, 188, 500, "GR binds DNA near target genes", "GR ChIP at DUSP1 (ASM), genome-wide GR ChIP-seq (ASM)", OCHRE, "ochre"))
b.append(arrow(500, 246, 500, 282, EV["measured"][0], 3.5)); b.append(lab(512, 270, "measured", "this data"))
b.append(node(170, 284, 660, "FKBP5, TSC22D3, PER1, DUSP1, KLF15 up 8- to 22-fold; ZBTB16 up 160-fold", None, TEAL, "teal"))
# branch DUSP1
b.append(arrow(330, 326, 230, 380, EV["cited"][0], 3.5)); b.append(lab(150, 360, "cited", "17513787", "end"))
b.append(node(20, 382, 410, "DUSP1 (MKP-1) dephosphorylates JNK", "less GRO-α release from ASM cells", OCHRE, "ochre"))
# branch KLF15
b.append(arrow(670, 326, 770, 380, EV["cited"][0], 3.5)); b.append(lab(850, 360, "cited", "28375666"))
b.append(node(570, 382, 410, "KLF15 regulates PLCD1", "but PLCD1 unchanged here (padj 0.33)", CRIM, "crim"))
b.append(arrow(225, 440, 400, 492, EV["speculation"][0], 3.5, True))
b.append(arrow(775, 440, 600, 492, EV["speculation"][0], 3.5, True))
b.append(lab(500, 482, "speculation", "", "middle"))
b.append(node(300, 494, 400, "less inflammation, less ASM growth", "not measured in this experiment", CRIM, "crim"))
b.append(t(20, 578, "ZBTB16: induced by GC in other smooth muscle (12970399), but that study found no GR response in its promoter.", 15, G2))
svg("fig33-airway-chain.svg", 590, "\n".join(b))

# ---------- fig34: prediction card ----------
b = [box(20, 15, 960, 360, "#fff", CRIM, sw=2.5)]
b.append(t(45, 55, "Prediction 1: the induction needs the glucocorticoid receptor", 21, CRIM, bold=True))
rows = [("Intervention", "siRNA against NR3C1 (and a non-targeting control), then dexamethasone"),
        ("Read-out", "qPCR of FKBP5, TSC22D3, PER1, DUSP1, KLF15; GAPDH unchanged"),
        ("Expected", "induction of all five clearly smaller with NR3C1 knock-down"),
        ("Refuted if", "knock-down confirmed (GR protein down) but induction unchanged"),
        ("Also tells", "PGR versus NR3C1: a PGR knock-down should change nothing"),
        ("Evidence now", "inferred (TF activity) + cited (GR at DUSP1 in ASM)")]
for i, (k, v) in enumerate(rows):
    y = 100 + i * 45
    b.append(t(45, y, k, 18, G1, bold=True))
    b.append(t(220, y, v, 18, G1))
b.append(t(500, 395, "Specific genes, a direction, a control, and a result that would prove it wrong.", 17, G2, "middle"))
svg("fig34-prediction-card.svg", 405, "\n".join(b))

# ---------- fig35: ODE ----------
# primary: dP/dt = k*G - d*P, G=1 for t>=0; P(0)=1 baseline; steady state 8 (fold)
# secondary: K protein from primary mRNA; S driven by K
def sim(tmax=24, dt=0.01):
    dP, dK, dS = math.log(2) / 1.0, math.log(2) / 3.0, math.log(2) / 2.0
    P, K, S = 1.0, 1.0, 1.0
    kP = 8 * dP
    out = []
    tt = 0.0
    while tt <= tmax + 1e-9:
        out.append((tt, P, K, S))
        # baseline production keeps steady state at 1 without dex
        Pn = P + dt * (kP - dP * P)
        Kn = K + dt * (dK * P - dK * K)
        # S induced by K above baseline: production = dS*(1 + 0.4*(K-1))
        Sn = S + dt * (dS * (1 + 0.43 * (K - 1)) - dS * S)
        P, K, S = Pn, Kn, Sn
        tt += dt
    return out
res = sim()
X0, Y0, W, H = 110, 360, 820, 300
def px(tt): return X0 + tt / 24 * W
def py(v): return Y0 - math.log2(v) / 3.2 * H
b = []
b.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0+W}" y2="{Y0}" stroke="{G1}" stroke-width="1.5"/>')
b.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0-H-10}" stroke="{G1}" stroke-width="1.5"/>')
for hh in [0, 2, 4, 6, 12, 18, 24]:
    b.append(f'<line x1="{px(hh):.1f}" y1="{Y0}" x2="{px(hh):.1f}" y2="{Y0+6}" stroke="{G1}"/>')
    b.append(t(px(hh), Y0 + 26, str(hh), 16, G1, "middle"))
b.append(t(X0 + W / 2, Y0 + 52, "hours after dexamethasone", 17, G1, "middle"))
for l2 in [0, 1, 2, 3]:
    b.append(f'<line x1="{X0-6}" y1="{py(2**l2):.1f}" x2="{X0}" y2="{py(2**l2):.1f}" stroke="{G1}"/>')
    b.append(t(X0 - 12, py(2 ** l2) + 6, str(l2), 16, G1, "end"))
b.append(f'<text x="40" y="{Y0 - H/2}" font-size="17" fill="{G1}" text-anchor="middle" transform="rotate(-90 40 {Y0 - H/2})">log2 fold change</text>')
pts1 = " ".join(f"{px(a):.1f},{py(p):.1f}" for a, p, k, s in res[::20])
pts2 = " ".join(f"{px(a):.1f},{py(s):.1f}" for a, p, k, s in res[::20])
pts3 = " ".join(f"{px(a):.1f},{py(1):.1f}" for a, p, k, s in res[::20])
b.append(f'<polyline points="{pts1}" fill="none" stroke="{PURP}" stroke-width="3.5"/>')
b.append(f'<polyline points="{pts2}" fill="none" stroke="{OCHRE}" stroke-width="3.5"/>')
b.append(f'<polyline points="{pts3}" fill="none" stroke="{OCHRE}" stroke-width="3" stroke-dasharray="8,6"/>')
b.append(f'<line x1="{px(18)}" y1="{Y0-H}" x2="{px(18)}" y2="{Y0}" stroke="{G3}" stroke-width="2" stroke-dasharray="4,4"/>')
b.append(t(px(18) + 6, Y0 - H + 4, "airway samples: 18 h", 15, G2))
b.append(t(px(2.6), py(2 ** 2.5), "primary target (GR binds it)", 17, PURP, bold=True))
b.append(t(px(11), py(2 ** 1.2), "secondary target (needs a new protein)", 17, OCHRE, bold=True))
b.append(t(px(8.5), py(1) - 10, "secondary + cycloheximide: flat", 16, OCHRE))
b.append(t(20, 440, "dP/dt = k·GR(t) − d·P.  Half-lives 1 h (mRNA), 3 h (protein), 2 h (secondary mRNA). Illustrative, not fitted.", 16, G2))
svg("fig35-ode.svg", 455, "\n".join(b))

# ---------- fig36: rival mechanisms ----------
hyps = [("H1: GR acts directly", "dex → GR → targets", PURP, "purp"),
        ("H2: PR acts", "top TF hit was PGR", OCHRE, "ochre"),
        ("H3: indirect, via a new protein", "e.g. via KLF15", TEAL, "teal")]
tests = [("siRNA NR3C1", ["blocked", "unchanged", "blocked"]),
         ("siRNA PGR", ["unchanged", "blocked", "unchanged"]),
         ("mifepristone", ["blocked", "blocked", "blocked"]),
         ("+ cycloheximide", ["still up", "still up", "blocked"])]
b = []
cx = [300, 530, 760]
for i, (h1, h2, c, l) in enumerate(hyps):
    b.append(box(cx[i] - 110, 15, 220, 70, LT[l], c))
    b.append(t(cx[i], 45, h1.split(":")[0] + ":", 17, c, "middle", True))
    b.append(t(cx[i], 70, h1.split(": ")[1], 15, G1, "middle"))
b.append(t(20, 60, "experiment", 18, G1, bold=True))
for j, (tn, outc) in enumerate(tests):
    y = 125 + j * 55
    b.append(f'<line x1="20" y1="{y-30}" x2="870" y2="{y-30}" stroke="#ddd"/>')
    b.append(t(20, y, tn, 18, G1, bold=True))
    same = len(set(outc)) == 1
    for i, o in enumerate(outc):
        b.append(t(cx[i], y, o, 17, G2 if same else G1, "middle"))
    b.append(t(890, y, "no" if same else "yes", 17, CRIM if same else TEAL, "start", True))
b.append(t(890, 60, "tells", 17, G1, bold=True)); b.append(t(890, 80, "apart?", 17, G1, bold=True))
b.append(t(20, 350, "Mifepristone blocks both GR and PR (24205903), so it cannot tell H1 from H2. Ask the agent for this table.", 16, G2))
b.append(t(20, 372, "Expected outcomes for the target induction under each hypothesis; to be tested, not results.", 16, G2))
svg("fig36-rival-mechanisms.svg", 385, "\n".join(b))
print("ok")
