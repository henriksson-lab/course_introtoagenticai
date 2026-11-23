#!/usr/bin/env Rscript
# make-data.R: synthetic example data for "Track A: Bulk RNA-seq".
#
# Creates a small, fully synthetic bulk RNA-seq experiment with a KNOWN ANSWER:
#
#   synthetic-rnaseq/counts.csv     raw counts, 10 000 genes x 12 samples
#   synthetic-rnaseq/samples.csv    the sample sheet (deliberately in a
#                                   different order from the count columns)
#   synthetic-rnaseq/lab-notes.txt  a short lab note (mentions a possible
#                                   tube swap)
#   synthetic-rnaseq.zip            the three files above, for download (the
#                                   folder itself is deleted after zipping)
#   truth.csv                       ANSWER KEY: which genes were planted as
#                                   changed, and by how much (not in the zip)
#
# The story: cultured cells, vehicle ("control") or drug ("treated"), 6 + 6
# samples, RNA extracted on two days (batch day1 / day2, balanced: 3 control
# and 3 treated per day).
#
# Planted features (what a careful analysis should find):
#   - 400 of 10 000 genes change with treatment (200 up, 200 down),
#     true |log2 fold change| between 0.8 and 3.
#   - A batch effect (extraction day) on every gene, strong enough to be
#     the first principal component.
#   - Sample S03 was sequenced about 5 times less deeply than the others.
#     It is a good sample; size factors take care of depth.
#   - Samples S08 and S11 are SWAPPED in the sample sheet: S08 is labelled
#     control but is really treated, S11 is labelled treated but is really
#     control. lab-notes.txt mentions the possible swap. The PCA shows it.
#
# Needs only base R. Deterministic (fixed seed). Run from this folder:
#     Rscript make-data.R
# At the end it prints the numbers that exercise.qmd quotes. If you change
# anything here, update exercise.qmd.

set.seed(20261123)
G <- 10000
ids <- sprintf("g%05d", 1:G)
samples_true <- data.frame(
  sample_id = sprintf("S%02d", 1:12),
  treatment = rep(rep(c("control", "treated"), each = 3), 2),
  batch     = rep(c("day1", "day2"), each = 6)
)

# baseline expression (mean count at depth 20 M), lognormal
base <- exp(rnorm(G, log(150), 1.6))
# per-gene dispersion: biological variation between replicate cultures
disp <- 0.04 + 1.5 / base
disp <- pmin(disp, 2)

# treatment effect on 400 genes
de <- sample(G, 400)
lfc <- numeric(G)
lfc[de] <- sample(c(-1, 1), 400, replace = TRUE, prob = c(0.5, 0.5)) * runif(400, 0.8, 3)
# make it exactly 200 up / 200 down
up <- de[1:200]; dn <- de[201:400]
lfc[up] <- abs(lfc[up]); lfc[dn] <- -abs(lfc[dn])

# batch effect on every gene (log2 scale)
batch_eff <- rnorm(G, 0, 0.45)

# relative sequencing depth (20 = typical), S03 about 5 times shallower
depth <- c(21, 19, 4, 22, 18, 20, 23, 20, 19, 21, 22, 18)

mu <- matrix(0, G, 12)
for (j in 1:12) {
  l2 <- log2(base) +
        (samples_true$treatment[j] == "treated") * lfc +
        (samples_true$batch[j] == "day2") * batch_eff
  mu[, j] <- 2^l2 * depth[j] / 20
}
counts <- matrix(rnbinom(G * 12, mu = mu, size = 1 / disp), G, 12)
colnames(counts) <- samples_true$sample_id

# The sample sheet as the participant receives it keeps the planned labels
# (S08 control, S11 treated). In truth the tubes were swapped: S08 is
# treated and S11 is control.
sheet <- samples_true
samples_true$treatment[samples_true$sample_id == "S08"] <- "treated"
samples_true$treatment[samples_true$sample_id == "S11"] <- "control"
# The simulated counts above used the labels before this swap, so re-simulate
# the two columns with their true labels.
for (s in c("S08", "S11")) {
  j <- which(samples_true$sample_id == s)
  l2 <- log2(base) +
        (samples_true$treatment[j] == "treated") * lfc +
        (samples_true$batch[j] == "day2") * batch_eff
  counts[, j] <- rnbinom(G, mu = 2^l2 * depth[j] / 20, size = 1 / disp)
}
sheet$extraction_date <- ifelse(sheet$batch == "day1", "2026-03-10", "2026-03-12")
sheet$rin <- c(9.4, 9.1, 8.8, 9.3, 9.5, 9.0, 9.2, 9.6, 8.9, 9.1, 9.3, 9.4)
sheet <- sheet[order(sheet$treatment, sheet$batch, sheet$sample_id), ]

out <- "synthetic-rnaseq"
dir.create(out, showWarnings = FALSE)
write.csv(data.frame(gene_id = ids, counts, check.names = FALSE),
          file.path(out, "counts.csv"), row.names = FALSE, quote = FALSE)
write.csv(sheet, file.path(out, "samples.csv"), row.names = FALSE, quote = FALSE)
writeLines(c(
  "Lab notes, drug response pilot (synthetic example data)",
  "",
  "2026-03-10 (day 1): extracted RNA from S01-S06. All fine.",
  "2026-03-12 (day 2): extracted RNA from S07-S12. The label printer jammed",
  "  and tubes were relabelled by hand. S08 and S11 may have been swapped.",
  "  Not confirmed. Check before analysis.",
  "2026-03-20: all 12 libraries sent for sequencing. S03 had low input RNA,",
  "  expect fewer reads."
), file.path(out, "lab-notes.txt"))
write.csv(data.frame(gene_id = ids, true_log2fc = round(lfc, 3), planted = lfc != 0),
          "truth.csv", row.names = FALSE, quote = FALSE)
unlink("synthetic-rnaseq.zip")
zip("synthetic-rnaseq.zip", file.path(out, c("counts.csv", "samples.csv", "lab-notes.txt")),
    flags = "-q9X")
unlink(out, recursive = TRUE)   # keep only the zip in the repository

cat("library sizes (M):\n"); print(round(colSums(counts) / 1e6, 2))
cat("planted:", sum(lfc != 0), "up", sum(lfc > 0), "down", sum(lfc < 0), "\n")
