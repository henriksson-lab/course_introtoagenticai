# plot_biomass.R : one possible reference solution for the worked example in
# "Reproducible figures". Your agent's script will look different; compare the
# FIGURE and the numbers, not the code.
#
# Usage:  Rscript plot_biomass.R [input.csv] [output-name]
#   defaults: ../plant-biomass.csv  biomass_figure
# Writes <output-name>.pdf, .svg (if svglite is installed) and .png (300 dpi),
# 85 mm wide (a typical single journal column), plus <output-name>_summary.csv
# with n, mean and SD per group so the figure can be checked against the data.

suppressPackageStartupMessages(library(ggplot2))

args   <- commandArgs(trailingOnly = TRUE)
infile <- if (length(args) >= 1) args[1] else "../plant-biomass.csv"
out    <- if (length(args) >= 2) args[2] else "biomass_figure"

d <- read.csv(infile, stringsAsFactors = FALSE)
d <- d[!is.na(d$biomass_mg), ]                     # the plant that died
d$fertiliser <- factor(d$fertiliser, levels = c("none", "low", "high"))
d$watering   <- factor(d$watering, levels = c("well-watered", "drought"))
if (anyNA(d$fertiliser) || anyNA(d$watering))
  stop("Unexpected group label in the data: check fertiliser and watering")

# summary per group: written to a file AND used for the plot
s <- aggregate(biomass_mg ~ fertiliser + watering, d,
               function(x) c(n = length(x), mean = mean(x), sd = sd(x)))
s <- cbind(s[1:2], as.data.frame(s$biomass_mg))
write.csv(transform(s, mean = round(mean, 1), sd = round(sd, 1)),
          paste0(out, "_summary.csv"), row.names = FALSE)

okabe <- c("well-watered" = "#0072B2", "drought" = "#E69F00")
dodge <- position_dodge(width = 0.6)

p <- ggplot(d, aes(fertiliser, biomass_mg, colour = watering)) +
  geom_point(position = position_jitterdodge(jitter.width = 0.15,
                                             dodge.width = 0.6, seed = 1),
             size = 1.2, alpha = 0.7) +
  geom_errorbar(data = s, aes(y = mean, ymin = mean - sd, ymax = mean + sd),
                position = dodge, width = 0.2, linewidth = 0.4) +
  geom_point(data = s, aes(y = mean), position = dodge, size = 2.2, shape = 18) +
  geom_text(data = s, aes(y = 0, label = paste0("n=", n), group = watering),
            colour = "grey30", position = dodge, size = 2.2, vjust = 0,
            show.legend = FALSE) +
  scale_colour_manual(values = okabe, name = NULL) +
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Fertiliser", y = "Dry biomass (mg)") +
  theme_classic(base_size = 8) +
  theme(legend.position = "top")

w <- 85; h <- 70                                    # mm
ggsave(paste0(out, ".pdf"), p, width = w, height = h, units = "mm")
ggsave(paste0(out, ".png"), p, width = w, height = h, units = "mm", dpi = 300)
if (requireNamespace("svglite", quietly = TRUE))
  ggsave(paste0(out, ".svg"), p, width = w, height = h, units = "mm")
cat("Plotted", nrow(d), "plants from", infile, "\n")
print(s)
