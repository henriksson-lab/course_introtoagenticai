# make-data.R
# Generates the SYNTHETIC example data for the unit "Reproducible figures"
# (Introduction to agentic AI). Nothing here is real: plants, lake and values
# are invented. Run from this folder with:  Rscript make-data.R
# Uses base R only. set.seed() makes the output identical on every run.
#
# Files written:
#   plant-biomass.csv         two-factor experiment, batch 1 (48 plants, 1 died)
#   plant-biomass-batch2.csv  the same experiment repeated (48 plants); three
#                             rows spell the fertiliser level "High" instead of
#                             "high", on purpose, to show why you check the
#                             groups and n after every rerun
#   lake-temperature.csv      daily water temperature at 1, 5 and 15 m depth in
#                             2024, long format; the 5 m sensor has a gap in July
#   figures-data.zip          the three CSV files above, zipped for download
#                             (made afterwards with any zip tool)
#
# reference/ holds one possible solution (plot_biomass.R, plot_lake.py) used
# to make the example figures in the lecture.

set.seed(20261123)

# ---- Two-factor experiment: fertiliser x watering -------------------------
make_batch <- function(batch, shift) {
  fert  <- c("none", "low", "high")
  water <- c("well-watered", "drought")
  # true means (mg dry biomass); fertiliser helps less under drought
  mu <- matrix(c(120, 165, 210,
                  95, 115, 125), nrow = 3,
               dimnames = list(fert, water))
  rows <- list()
  id <- 0
  for (w in water) for (f in fert) for (rep in 1:8) {
    id <- id + 1
    rows[[id]] <- data.frame(
      plant_id   = sprintf("B%d-%02d", batch, id),
      batch      = batch,
      block      = (rep - 1) %/% 2 + 1,
      fertiliser = f,
      watering   = w,
      biomass_mg = round(rnorm(1, mu[f, w] + shift, 14), 1),
      comment    = "",
      stringsAsFactors = FALSE)
  }
  d <- do.call(rbind, rows)
  # shuffle row order as in a real harvest sheet (sorted by block)
  d[order(d$block, sample(nrow(d))), ]
}

b1 <- make_batch(1, 0)
# one plant died: no biomass
died <- which(b1$fertiliser == "high" & b1$watering == "drought")[3]
b1$biomass_mg[died] <- NA
b1$comment[died] <- "died in week 2"
write.csv(b1, "plant-biomass.csv", row.names = FALSE, na = "")

b2 <- make_batch(2, 8)
hi <- which(b2$fertiliser == "high")[c(2, 5, 9)]
b2$fertiliser[hi] <- "High"          # typing inconsistency, on purpose
write.csv(b2, "plant-biomass-batch2.csv", row.names = FALSE, na = "")

# ---- Time series: lake temperature at three depths ------------------------
days  <- seq(as.Date("2024-01-01"), as.Date("2024-12-31"), by = "day")
doy   <- as.numeric(format(days, "%j"))
season <- pmax(0, sin(2 * pi * (doy - 95) / 365))   # warm half of the year
lake <- do.call(rbind, lapply(c(1, 5, 15), function(z) {
  amp  <- c(`1` = 18, `5` = 14, `15` = 3)[as.character(z)]
  base <- c(`1` = 2.5, `5` = 3.5, `15` = 4.0)[as.character(z)]
  lag  <- c(`1` = 0, `5` = 12, `15` = 40)[as.character(z)]
  s <- pmax(0, sin(2 * pi * (doy - 95 - lag) / 365))
  temp <- base + amp * s + as.numeric(stats::filter(rnorm(length(days), 0, 0.6),
                                                    rep(1/3, 3), circular = TRUE))
  data.frame(date = format(days), depth_m = z, temp_c = round(temp, 2))
}))
gap <- lake$depth_m == 5 & lake$date >= "2024-07-10" & lake$date <= "2024-07-24"
lake$temp_c[gap] <- NA
write.csv(lake, "lake-temperature.csv", row.names = FALSE, na = "")

cat("Wrote plant-biomass.csv (", nrow(b1), " rows), plant-biomass-batch2.csv (",
    nrow(b2), " rows), lake-temperature.csv (", nrow(lake), " rows)\n", sep = "")
