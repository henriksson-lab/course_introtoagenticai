#!/usr/bin/env Rscript
# make-figs.R: analysis behind the result plots in the lecture of
# "Track A: Bulk RNA-seq" (figures from real numbers, not drawn by hand).
#
# Runs DESeq2 on the synthetic data (synthetic-rnaseq.zip, made by
# make-data.R) and on the public airway dataset (Bioconductor package
# "airway"), and writes small CSV files to the folder given as argument.
# make-figs.py then turns them into the SVG figures.
#
#   Rscript make-figs.R <outdir>
#   python3 make-figs.py <outdir> ..
#
# Needs: DESeq2, airway. Prints the numbers quoted in lec.qmd and exercise.qmd.
suppressMessages({library(DESeq2); library(airway)})
args <- commandArgs(TRUE); out <- if (length(args)) args[1] else "figdata"
dir.create(out, showWarnings = FALSE)
here <- getwd()
tmp <- tempfile(); dir.create(tmp); unzip("synthetic-rnaseq.zip", exdir = tmp)
cts <- read.csv(file.path(tmp, "synthetic-rnaseq/counts.csv"), row.names = 1, check.names = FALSE)
sh <- read.csv(file.path(tmp, "synthetic-rnaseq/samples.csv"))
truth <- read.csv("truth.csv")
rownames(sh) <- sh$sample_id
sh <- sh[colnames(cts), ]                       # match by name, not by position
sh$treatment <- factor(sh$treatment, levels = c("control", "treated"))
sh$batch <- factor(sh$batch)
write.csv(data.frame(sample = colnames(cts), reads = colSums(cts), treatment = sh$treatment),
          file.path(out, "libsizes.csv"), row.names = FALSE)

fit <- function(sheet, design) {
  d <- DESeq(DESeqDataSetFromMatrix(as.matrix(cts), sheet, design), quiet = TRUE)
  list(dds = d, res = results(d, name = "treatment_treated_vs_control"))
}
summ <- function(r, label) {
  sig <- which(r$padj < 0.05); raw <- which(r$pvalue < 0.05)
  data.frame(analysis = label, called = length(sig), planted = sum(truth$planted[sig]),
             raw_p05 = length(raw), raw_p05_not_planted = sum(!truth$planted[raw]))
}
a <- fit(sh, ~ batch + treatment)
fx <- sh; fx["S08", "treatment"] <- "treated"; fx["S11", "treatment"] <- "control"
b <- fit(fx, ~ batch + treatment)
c2 <- fit(fx, ~ treatment)
keep <- setdiff(colnames(cts), c("S08", "S11"))
d <- DESeq(DESeqDataSetFromMatrix(as.matrix(cts[, keep]), sh[keep, ], ~ batch + treatment), quiet = TRUE)
rd <- results(d, name = "treatment_treated_vs_control")
sig_d <- which(rd$padj < 0.05)
tab <- rbind(summ(a$res, "sheet as given"), summ(b$res, "swap corrected"),
             summ(c2$res, "swap corrected, batch left out"),
             data.frame(analysis = "S08 and S11 left out", called = length(sig_d),
                        planted = sum(truth$planted[sig_d]), raw_p05 = NA, raw_p05_not_planted = NA))
print(tab); write.csv(tab, file.path(out, "synthetic_summary.csv"), row.names = FALSE)
vsd <- vst(a$dds)
p <- plotPCA(vsd, intgroup = c("treatment", "batch"), returnData = TRUE)
write.csv(data.frame(sample = rownames(p), PC1 = p$PC1, PC2 = p$PC2, treatment = p$treatment,
                     batch = p$batch, pv1 = attr(p, "percentVar")[1], pv2 = attr(p, "percentVar")[2]),
          file.path(out, "pca.csv"), row.names = FALSE)
write.csv(round(cor(assay(vsd)), 4), file.path(out, "cor.csv"))
print(round(sizeFactors(a$dds), 2))

# airway
data(airway)
airway$dex <- relevel(airway$dex, ref = "untrt")
dds <- DESeqDataSet(airway, design = ~ cell + dex)
dds <- dds[rowSums(counts(dds) >= 10) >= 4, ]
dds <- DESeq(dds, quiet = TRUE)
res <- results(dds, name = "dex_trt_vs_untrt")
cat("airway genes tested:", nrow(res), " padj<0.05:", sum(res$padj < 0.05, na.rm = TRUE),
    " up:", sum(res$padj < 0.05 & res$log2FoldChange > 0, na.rm = TRUE),
    " and |LFC|>1:", sum(res$padj < 0.05 & abs(res$log2FoldChange) > 1, na.rm = TRUE), "\n")
ok <- !is.na(res$padj)
write.csv(data.frame(gene = rowData(dds)$gene_name[ok], baseMean = signif(res$baseMean[ok], 3),
                     lfc = round(res$log2FoldChange[ok], 3), padj = signif(res$padj[ok], 3)),
          file.path(out, "airway_res.csv"), row.names = FALSE)
