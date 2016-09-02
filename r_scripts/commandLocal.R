#!/usr/local/bin/Rscript
## Make sure the latest distributions of "pandoc" is installed
## If PDF report needed Tex also should be installed
## Also require all following packages, uncomment the following line for installation from CRAN

## install.packages(c("RCurl", "XML", "data.table", "ggplot2", "scales", "rmarkdown"))


## Enter information for the source script

## Enter URL

initLibraries <- function () {
  if (!require("pacman"))
    install.packages("pacman"); library(pacman)
  p_load(RCurl, XML, data.table, ggplot2, scales, rmarkdown)
}

initLibraries()

INPUT_CSV = commandArgs(1)

if (length(commandArgs(1)) > 0 && file.exists(INPUT_CSV)) {
  
  d <- as.data.table(read.csv(
    INPUT_CSV,
    na.strings = c(".B", ".E"), stringsAsFactors = FALSE
  ))
  
  d[, Date := as.Date(Date, format = "%Y-%m-%d")]

  d$BThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$BT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$BT))/60

  d$LOhr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$LO)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$LO))/60

  d$WThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$WT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$WT))/60

  d$RThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$RT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$RT))/60

  d[BThr >15 & BThr <= 24, BThr := BThr - 24]
  d[BThr > 6, BThr := BThr + 12 - 24]

  d[LOhr >16 & LOhr <= 24, LOhr := LOhr - 24]
  d[LOhr > 5.5, LOhr := LOhr + 12 - 24]

  # d[LOhr > WThr, c("LOhr", "BThr") := .(NA_real_, NA_real_)]

  d[, TIBhr := RThr - BThr]
  d[TIBhr < 0, TIBhr := NA_real_]
  d[, TSTshr := TST/60] #subjective TSThr
  d[, TSThr := TIBhr - SOL/60 - WASOT/60 - SNZ/60 - (RThr - WThr)]
  d[, SEs := TSTshr/TIBhr*100]
  d[SEs > 100, SEs := 100]
  
  ## Generate reports for every unique ID
  error.ids <- vector("character", 0)

  for (i in unique(d$User)) {
    ID <- i
    
    
    # path = "<this directory>/Reports/{ID}/"
    output_path = paste0("/srv/sleepvl/reports/", ID, "/")
    
    # make directory if it doesn't exist
    if (!dir.exists(output_path)) {
      dir.create(output_path)
    }

    # make a html file
    # make sure the DiaryReportGenerator.rmd in right location
    render(
      "/home/ec2-user/sleepvl_prod/sleepvl/r_scripts/DiaryReportGenerator.rmd", output_format = "html_document",
      output_file = paste0(output_path, ID , "-" , Sys.Date(), ".html")
    )

    # make a pdf file
    # make sure the DiaryReportGenerator.rmd in right location
    render(
      "/home/ec2-user/sleepvl_prod/sleepvl/r_scripts/DiaryReportGenerator.rmd", output_format = "pdf_document",
      output_file = paste0(output_path, ID , "-" , Sys.Date(), ".pdf")
    )
  }
  
} else {
  print("CSV input not found, please pass a valid file in as a parameter")
  quit(save = "no", status = 1)
}
