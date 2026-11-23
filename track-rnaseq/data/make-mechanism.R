#!/usr/bin/env Rscript
# make-mechanism.R: analysis behind the numbers in the deck "From gene lists
# to mechanisms" (lec-mechanism.qmd) and its exercise (exercise-mechanism.qmd).
#
#   Rscript make-mechanism.R          (run from this folder)
#
# 1. Synthetic pilot: DESeq2 (swap corrected, ~ batch + treatment), then
#    regulator activity with decoupleR (ulm, mlm) on the Wald statistic,
#    using regulons.csv; over-representation per regulator; the RegD decoy
#    rerun without the targets it shares with RegA; comparison with
#    truth.csv (column program).
# 2. airway: DESeq2 (~ cell + dex, reference untrt), gene symbols from
#    org.Hs.eg.db, TF activity with CollecTRI (ulm) and pathway activity
#    with PROGENy (top 500, mlm); expression of NR3C1, PGR, AR; overlap of
#    the PGR and NR3C1 regulons; top-gene rankings by padj and by |log2FC|.
#
# Needs: DESeq2, airway, decoupleR, OmnipathR, org.Hs.eg.db, and internet
# access (CollecTRI and PROGENy are downloaded from OmniPath). Numbers in the
# deck are from R 4.6.2, DESeq2 1.52.0, airway 1.32.0, decoupleR 2.17.0,
# OmnipathR 4.0.4, run on 2026-11-23. The figures fig29 to fig31 are drawn by
# make-figs-mechanism.py from these numbers.
suppressMessages({
  library(DESeq2); library(airway); library(decoupleR); library(org.Hs.eg.db)
})

## ---- 1. synthetic pilot ---------------------------------------------------
tmp <- tempfile(); dir.create(tmp); unzip("synthetic-rnaseq.zip", exdir = tmp)
cts <- read.csv(file.path(tmp, "synthetic-rnaseq/counts.csv"), row.names = 1, check.names = FALSE)
sh <- read.csv(file.path(tmp, "synthetic-rnaseq/samples.csv"))
rownames(sh) <- sh$sample_id; sh <- sh[colnames(cts), ]
sh$treatment[sh$sample_id == "S08"] <- "treated"   # the confirmed swap
sh$treatment[sh$sample_id == "S11"] <- "control"
sh$treatment <- factor(sh$treatment, c("control", "treated")); sh$batch <- factor(sh$batch)
d <- DESeq(DESeqDataSetFromMatrix(as.matrix(cts), sh, ~ batch + treatment), quiet = TRUE)
res <- as.data.frame(results(d))
net <- read.csv("regulons.csv"); truth <- read.csv("truth.csv")
mat <- matrix(res$stat, dimnames = list(rownames(res), "stat")); mat <- mat[!is.na(mat[, 1]), , drop = FALSE]

cat("\n== synthetic: regulator activity, ulm ==\n")
a <- run_ulm(mat, net, .source = "source", .target = "target", .mor = "mor", minsize = 5)
print(as.data.frame(a[order(a$p_value), c("source", "score", "p_value")]))
cat("\n== synthetic: regulator activity, mlm ==\n")
a <- run_mlm(mat, net, .source = "source", .target = "target", .mor = "mor", minsize = 5)
print(as.data.frame(a[order(a$p_value), c("source", "score", "p_value")]))

sig <- rownames(res)[!is.na(res$padj) & res$padj < 0.05]
cat("\n== synthetic: over-representation (padj < 0.05) ==\n")
for (r in sort(unique(net$source))) {
  t <- intersect(net$target[net$source == r], rownames(mat)); s <- intersect(t, sig)
  cat(r, "targets", length(t), "significant", length(s),
      "up", sum(res[s, "log2FoldChange"] > 0), "down", sum(res[s, "log2FoldChange"] < 0), "\n")
}
shared <- intersect(net$target[net$source == "RegD"], net$target[net$source == "RegA"])
a <- run_ulm(mat, net[!(net$source == "RegD" & net$target %in% shared), ],
             .source = "source", .target = "target", .mor = "mor", minsize = 5)
cat("\nRegD without the", length(shared), "targets shared with RegA:\n")
print(as.data.frame(a[a$source == "RegD", c("source", "score", "p_value")]))
cat("\nGenes at padj < 0.05 by true program:\n"); print(table(truth$program[match(sig, truth$gene_id)]))
cat("Genes at padj < 0.05 in no regulon:", sum(!sig %in% net$target), "\n")

## ---- 2. airway ------------------------------------------------------------
data(airway); airway$dex <- relevel(airway$dex, "untrt")
d <- DESeq(DESeqDataSet(airway, ~ cell + dex), quiet = TRUE)
res <- as.data.frame(results(d, name = "dex_trt_vs_untrt"))
res$symbol <- suppressMessages(mapIds(org.Hs.eg.db, rownames(res), "SYMBOL", "ENSEMBL"))
s <- res[!is.na(res$padj) & res$padj < 0.05, ]
cat("\n== airway ==\npadj < 0.05:", nrow(s), "up", sum(s$log2FoldChange > 0), "down", sum(s$log2FoldChange < 0), "\n")
o1 <- s[order(s$padj), ]; o2 <- s[order(-abs(s$log2FoldChange)), ]
o3 <- s[s$baseMean > 100, ]; o3 <- o3[order(-abs(o3$log2FoldChange)), ]
cat("top 10 by padj:", head(o1$symbol, 10), "\n")
cat("top 10 by |log2FC|:", head(o2$symbol, 10), "\n  mean counts:", round(head(o2$baseMean, 10), 1), "\n")
cat("top 5 up / 5 down by |log2FC|, baseMean > 100:",
    head(o3$symbol[o3$log2FoldChange > 0], 5), "/", head(o3$symbol[o3$log2FoldChange < 0], 5), "\n")
cat("top 20 overlap, padj vs |log2FC|:", length(intersect(head(rownames(o1), 20), head(rownames(o2), 20))),
    "; padj vs |log2FC| with baseMean > 100:", length(intersect(head(rownames(o1), 20), head(rownames(o3), 20))),
    "; up among top 20 by padj:", sum(head(o1$log2FoldChange, 20) > 0), "\n")
for (g in c("NR3C1", "PGR", "AR", "FKBP5", "TSC22D3", "PER1", "DUSP1", "KLF15", "ZBTB16", "PLCD1", "SPARCL1")) {
  i <- which(res$symbol == g)[1]
  cat(sprintf("%-8s baseMean %8.1f  log2FC %6.2f  padj %.2g\n", g, res$baseMean[i], res$log2FoldChange[i], res$padj[i]))
}
r <- res[!is.na(res$stat) & !is.na(res$symbol), ]
r <- r[order(-abs(r$stat)), ]; r <- r[!duplicated(r$symbol), ]
mat <- matrix(r$stat, dimnames = list(r$symbol, "stat"))
collectri <- get_collectri(organism = "human", split_complexes = FALSE)
a <- run_ulm(mat, collectri, .source = "source", .target = "target", .mor = "mor", minsize = 5)
a <- as.data.frame(a[order(a$p_value), ]); a$rank <- seq_len(nrow(a))
cat("\nCollecTRI, ulm:", nrow(a), "TFs scored; top 15:\n"); print(head(a[, c("source", "score", "p_value", "rank")], 15))
print(a[a$source %in% c("NR3C1", "KLF15", "PGR"), c("source", "score", "rank")])
gr <- collectri$target[collectri$source == "NR3C1"]; pg <- collectri$target[collectri$source == "PGR"]
cat("NR3C1 regulon", length(gr), "PGR regulon", length(pg), "shared", length(intersect(gr, pg)), "\n")
cat("known targets in NR3C1 regulon:", intersect(c("FKBP5", "TSC22D3", "PER1", "DUSP1", "KLF15", "ZBTB16"), gr), "\n")
progeny <- get_progeny(organism = "human", top = 500)
b <- run_mlm(mat, progeny, .source = "source", .target = "target", .mor = "weight", minsize = 5)
cat("\nPROGENy, mlm:\n"); print(as.data.frame(b[order(b$p_value), c("source", "score", "p_value")]))
cat("\n"); cat("decoupleR", as.character(packageVersion("decoupleR")), "OmnipathR", as.character(packageVersion("OmnipathR")),
               "DESeq2", as.character(packageVersion("DESeq2")), "\n")
