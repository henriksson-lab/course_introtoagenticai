# make-data.R
# Generates the synthetic example dataset for the unit "Shiny apps" of the course
# "Introduction to agentic AI".
#
# water-quality.csv: invented water samples from four invented sites, taken twice a
# month from January 2022 to December 2024. Nothing here is a real measurement.
# Columns: site, date, temperature_c, ph, nitrate_mg_l, oxygen_mg_l
# A few values are missing on purpose (a broken probe), so the app must cope with NA.
#
# Run from the unit folder:  Rscript data/make-data.R
# Writes data/water-quality.csv and a copy in example-app/water-quality.csv.

set.seed(20261123)

sites <- data.frame(
  site      = c("Alder Lake", "Mill Creek", "North Pond", "Stone River"),
  temp_mean = c(11, 9, 12, 10),      # yearly mean water temperature (C)
  temp_amp  = c(8, 6, 9, 7),         # summer-winter swing (C)
  ph_mean   = c(7.4, 6.8, 7.9, 7.2),
  no3_mean  = c(0.6, 2.4, 0.9, 1.5)  # nitrate, mg/L
)

days <- c(sapply(2022:2024, function(y) sapply(1:12, function(m)
  format(as.Date(sprintf("%d-%02d-%02d", y, m, c(5, 19))), "%Y-%m-%d"))))
days <- sort(as.character(unlist(days)))

rows <- list()
for (i in seq_len(nrow(sites))) {
  s <- sites[i, ]
  d <- as.Date(days)
  doy <- as.numeric(format(d, "%j"))
  season <- -cos(2 * pi * (doy - 15) / 365)          # -1 mid-January, +1 mid-July
  temp <- s$temp_mean + s$temp_amp * season + rnorm(length(d), 0, 1.2)
  temp <- pmax(temp, 0.5)
  ph <- s$ph_mean + 0.15 * season + rnorm(length(d), 0, 0.12)
  # nitrate higher in winter (run-off), slowly rising at Mill Creek
  trend <- if (s$site == "Mill Creek") 0.25 * (as.numeric(d - as.Date("2022-01-01")) / 365) else 0
  no3 <- s$no3_mean * (1 - 0.35 * season) + trend + rnorm(length(d), 0, 0.15 * s$no3_mean)
  no3 <- pmax(no3, 0.05)
  # dissolved oxygen falls as water warms (roughly 14.6 mg/L at 0 C to 8 mg/L at 25 C)
  oxy <- 14.6 - 0.27 * temp + rnorm(length(d), 0, 0.4)
  rows[[i]] <- data.frame(site = s$site, date = days,
                          temperature_c = round(temp, 1), ph = round(ph, 2),
                          nitrate_mg_l = round(no3, 2), oxygen_mg_l = round(oxy, 1))
}
wq <- do.call(rbind, rows)
wq <- wq[order(wq$date, wq$site), ]

# A broken oxygen probe at North Pond in summer 2023, and two lost pH readings.
wq$oxygen_mg_l[wq$site == "North Pond" & wq$date >= "2023-06-01" & wq$date <= "2023-07-31"] <- NA
wq$ph[wq$site == "Stone River" & wq$date %in% c("2022-03-05", "2024-10-19")] <- NA

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
unit <- dirname(here)
write.csv(wq, file.path(unit, "data", "water-quality.csv"), row.names = FALSE)
write.csv(wq, file.path(unit, "example-app", "water-quality.csv"), row.names = FALSE)
cat("Wrote", nrow(wq), "rows\n")
