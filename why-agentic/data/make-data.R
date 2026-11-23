# make-data.R -- generates the synthetic example data for "Why agentic AI?"
#
# seedlings.csv: heights of 24 pea seedlings (8 per light treatment: low,
# medium, high) measured every second day from day 0 to day 14.
# The data are SYNTHETIC (random numbers from a simple growth model). Two
# realistic flaws are planted on purpose, because the annotated agent session
# in the exercise is about noticing them:
#   1. Plants h07 and h08 were entered by "another student" with the label
#      "High" instead of "high" (so a naive plot shows four treatments).
#   2. One measurement (m03, day 10) is missing (empty cell).
#
# Run from this folder:  Rscript make-data.R
set.seed(2026)
treatments <- c(low = 1.6, medium = 2.6, high = 3.4)   # mean growth, mm/day
days <- seq(0, 14, by = 2)
rows <- list()
for (tr in names(treatments)) {
  for (i in 1:8) {
    id <- sprintf("%s%02d", substr(tr, 1, 1), i)
    h0 <- round(runif(1, 8, 14), 1)
    rate <- rnorm(1, treatments[[tr]], 0.35)
    h <- h0 + rate * days + rnorm(length(days), 0, 1.2)
    h <- round(pmax(h, h0), 1)
    label <- if (tr == "high" && i >= 7) "High" else tr
    rows[[length(rows) + 1]] <- data.frame(plant_id = id, treatment = label,
                                           day = days, height_mm = h)
  }
}
d <- do.call(rbind, rows)
d$height_mm[d$plant_id == "m03" & d$day == 10] <- NA
write.csv(d, "seedlings.csv", row.names = FALSE, na = "")
cat("wrote seedlings.csv:", nrow(d), "rows\n")

# growth_plot_first_try.png: what the agent's FIRST script produced, before it
# noticed the "High"/"high" problem (shown in the exercise). The final plot,
# growth_plot.png, is made by plot_growth.R.
if (requireNamespace("ggplot2", quietly = TRUE)) {
  library(ggplot2)
  d1 <- read.csv("seedlings.csv")
  d1 <- d1[!is.na(d1$height_mm), ]
  s1 <- aggregate(height_mm ~ treatment + day, d1, mean)
  p1 <- ggplot(s1, aes(day, height_mm, colour = treatment)) +
    geom_line(linewidth = 0.8) + geom_point(size = 2) +
    labs(x = "Day", y = "Seedling height (mm)", colour = "Light",
         title = "Seedling growth under three light levels") +
    theme_minimal(base_size = 14)
  ggsave("growth_plot_first_try.png", p1, width = 7, height = 4.5, dpi = 150)
  source("plot_growth.R")
}
