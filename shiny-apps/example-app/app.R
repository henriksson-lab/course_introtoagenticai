# app.R: explore the (synthetic) water-quality samples from four sites.
# Example app for the unit "Shiny apps" of the course "Introduction to agentic AI".
#
# Run it locally from R or RStudio:   shiny::runApp("example-app")
# or from a terminal in this folder:  Rscript -e 'shiny::runApp(".")'
# Export it as a static Shinylive site (runs in the visitor's browser):
#   shinylive::export("example-app", "site")
# Everything in this folder, including water-quality.csv, is sent to every visitor.

library(shiny)
library(ggplot2)

# ---- Data ---------------------------------------------------------------------
wq <- read.csv("water-quality.csv")
wq$date <- as.Date(wq$date)

# The measurements the user can choose, with readable labels.
measures <- c(
  "Water temperature (°C)"   = "temperature_c",
  "pH"                            = "ph",
  "Nitrate (mg/L)"                = "nitrate_mg_l",
  "Dissolved oxygen (mg/L)"       = "oxygen_mg_l"
)
site_names <- sort(unique(wq$site))
site_colours <- setNames(c("#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12")[seq_along(site_names)],
                         site_names)

# ---- User interface -------------------------------------------------------------
ui <- fluidPage(
  titlePanel("Water quality at four sites, 2022-2024 (synthetic data)"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sites", "Sites", choices = site_names, selected = site_names),
      dateRangeInput("dates", "Dates",
                     start = min(wq$date), end = max(wq$date),
                     min = min(wq$date), max = max(wq$date)),
      selectInput("measure", "Measurement", choices = measures, selected = "nitrate_mg_l"),
      checkboxInput("smooth", "Show a trend line per site", value = FALSE),
      downloadButton("download", "Download the selected rows (CSV)"),
      width = 3
    ),
    mainPanel(
      plotOutput("timeplot", height = "380px"),
      h4("Summary of the selected rows"),
      tableOutput("summary"),
      h4("The selected rows"),
      textOutput("nrows"),
      tableOutput("rows"),
      width = 9
    )
  )
)

# ---- Server: what happens when the user changes an input --------------------------
server <- function(input, output, session) {

  # The rows that match the filters. Everything below uses this.
  selected <- reactive({
    validate(need(length(input$sites) > 0, "Choose at least one site."))
    d <- wq[wq$site %in% input$sites &
              wq$date >= input$dates[1] & wq$date <= input$dates[2], ]
    validate(need(nrow(d) > 0, "No samples in this date range."))
    d
  })

  measure_label <- reactive(names(measures)[measures == input$measure])

  output$timeplot <- renderPlot({
    d <- selected()
    d$value <- d[[input$measure]]
    p <- ggplot(d[!is.na(d$value), ], aes(date, value, colour = site)) +
      geom_line(alpha = 0.5) +
      geom_point(size = 2) +
      scale_colour_manual(values = site_colours) +
      labs(x = NULL, y = measure_label(), colour = "Site") +
      theme_minimal(base_size = 15)
    if (input$smooth) p <- p + geom_smooth(method = "lm", formula = y ~ x, se = FALSE, linewidth = 1.2)
    p
  })

  output$summary <- renderTable({
    d <- selected()
    v <- d[[input$measure]]
    out <- do.call(rbind, lapply(split(v, d$site), function(x) data.frame(
      samples = length(x),
      missing = sum(is.na(x)),
      mean    = mean(x, na.rm = TRUE),
      min     = min(x, na.rm = TRUE),
      max     = max(x, na.rm = TRUE)
    )))
    cbind(site = rownames(out), out)
  }, digits = 2)

  output$nrows <- renderText({
    n <- nrow(selected())
    if (n > 20) paste(n, "rows selected; the first 20 are shown. Download them all with the button.")
    else paste(n, "rows selected.")
  })

  output$rows <- renderTable({
    d <- head(selected(), 20)
    d$date <- format(d$date)
    d
  })

  output$download <- downloadHandler(
    filename = function() "water-quality-selected.csv",
    content = function(file) write.csv(selected(), file, row.names = FALSE)
  )
}

shinyApp(ui, server)
