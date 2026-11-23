# plot_growth.R -- the script the agent wrote in the annotated session
# (exercise "Watch an agent work"). Reads seedlings.csv, plots mean height per
# light treatment over time with +/- 1 standard error, saves growth_plot.png.
library(ggplot2)

d <- read.csv("seedlings.csv")

# Treatment labels were typed inconsistently ("High" and "high"): make them
# lower case so they form one group.
d$treatment <- tolower(trimws(d$treatment))
d$treatment <- factor(d$treatment, levels = c("low", "medium", "high"))

# One measurement is missing; leave it out of the means.
n_missing <- sum(is.na(d$height_mm))
d <- d[!is.na(d$height_mm), ]
message("Rows with missing height removed: ", n_missing)

summ <- aggregate(height_mm ~ treatment + day, data = d,
                  FUN = function(x) c(mean = mean(x), se = sd(x) / sqrt(length(x)), n = length(x)))
summ <- do.call(data.frame, summ)
names(summ) <- c("treatment", "day", "mean", "se", "n")
message("Plants per treatment: ",
        paste(names(table(unique(d[, c("plant_id", "treatment")])$treatment)),
              table(unique(d[, c("plant_id", "treatment")])$treatment), collapse = ", "))

p <- ggplot(summ, aes(day, mean, colour = treatment)) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.3) +
  scale_colour_manual(values = c(low = "#8a6a12", medium = "#2a7f8f", high = "#6b4fa0")) +
  labs(x = "Day", y = "Seedling height (mm)", colour = "Light",
       title = "Seedling growth under three light levels",
       subtitle = "Mean ± 1 standard error, 8 plants per treatment") +
  theme_minimal(base_size = 14)

ggsave("growth_plot.png", p, width = 7, height = 4.5, dpi = 150)
