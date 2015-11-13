#!/usr/local/bin/R
## Make sure the latest distributions of "pandoc" is installed
## If PDF report needed Tex also should be installed
## Also require all following packages, uncomment the following line for installation from CRAN

## install.packages(c("RCurl", "XML", "data.table", "ggplot2", "scales", "rmarkdown"))


## Enter information for the source script

## Enter URL
base.url <- "https://test.healthysleep.monash.edu/survey/"

## Grabs username and password from the environmental variable in the format of "username:password"

usernamepwd <- Sys.getenv("SLEEPVL_LOGIN")

# If user login is not specified in env var then fail with an error
if (usernamepwd != "") { 
  
  initLibraries <- function () {
    if (!require("pacman")) install.packages("pacman"); library(pacman)
    p_load(RCurl, XML, data.table, ggplot2, scales, rmarkdown)
  }
  
  initLibraries()
  
  h <- getURL(base.url, userpw = usernamepwd, followlocation=TRUE)
  
  parsed <- htmlTreeParse(h, asText = TRUE, useInternal = TRUE)
  
  value <- xpathApply(parsed, '//a', xmlValue)
  files <- unlist(value[sapply(value, function(x) grepl(".*\\.csv$", x))])
  times <- as.POSIXlt(substr(files, 17, 35), format = "%Y_%m_%d_%H_%M_%S")
  
  mostrecent <- files[which(times == max(times))]
  
  file.url <- paste0(base.url, mostrecent)
  
  mostrecent.data <- getURL(file.url, userpw = usernamepwd, followlocation=TRUE)
  
  d <- as.data.table(read.csv(textConnection(mostrecent.data),
                              na.strings = c(".B", ".E"), stringsAsFactors = FALSE))
  
  d[, Date := as.Date(Date, format = "%Y-%m-%d")]
  
  d$BThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$BT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$BT))/60
  
  d$LOhr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$LO)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$LO))/60
  
  d$WThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$WT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$WT))/60
  
  d$RThr <- as.numeric(gsub("(.*):(.*)$", "\\1", d$RT)) +
    as.numeric(gsub("(.*):(.*)$", "\\2", d$RT))/60
  
  d[BThr >12, BThr := BThr - 24]
  d[LOhr >12, LOhr := LOhr - 24]
  d[LOhr > WThr, c("LOhr", "BThr") := .(LOhr -12, BThr -12)]
  
  d[, TIBhr := RThr - BThr]
  d[, TSTshr := TST/60] #subjective TSThr
  d[, TSThr := TIBhr - SOL/60 - WASOT/60 - SNZ/60 - (RThr - WThr)]
  d[, SEs := TSTshr/TIBhr*100]
  d[SEs > 100, SEs := 100]
  
  ## Generate reports for every unique ID
  
  for (i in unique(d$User)) {
    ID <- i
    
    render("Diary Report.Rmd", output_format = "html_document",
           output_file = paste0("Diary_", ID, ".html"))
    
    ## Uncomment if PDF needed
    ## render("Diary Report.Rmd", output_format = "pdf_document",
    ##        output_file = paste0("Diary_", ID, ".pdf"))
  }
  
} else {
  print("Please define SleepVL login credentials in SLEEPVL_LOGIN before running this script. \n
        e.g: SLEEPVL_LOGIN=username:password Rscript CMD commandHTTP.R")
  quit(save = "no", status = 1)
}

