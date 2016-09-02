## Make sure the latest distributions of "pandoc" is installed
## If PDF report needed Tex also should be installed
## Also require all following packages, uncomment the following line for installation from CRAN

## install.packages(c("RCurl", "XML", "data.table", "ggplot2", "scales", "rmarkdown"))


## Enter information for the source script

## Enter URL
base.url <- "https://data.healthysleep.monash.edu/survey/"

## Enter username and password has to be in the format of "username:password"
usernamepwd <- "USERNAME:PASSWORD"

## Replace what's in "" with the path to the folder where the report source is stored,html and PDF files of report will be generated in that location

setwd("~/Dropbox/02 Projects/Healthy Sleep Clinic/Database")

library(RCurl)
library(XML)
library(data.table)
library(ggplot2)
library(scales)
library(rmarkdown)

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

    res <- tryCatch({
    render("Diary Report.Rmd", output_format = "html_document",
           output_file = paste0("Diary_", ID, ".html"))

    ## Uncomment the following two lines if PDF is needed
    ## render("Diary Report.Rmd", output_format = "pdf_document",
    ##        output_file = paste0("Diary_", ID, ".pdf"))

    },
      error = function(e) "error")

    if (identical(res, "error")) {
        error.ids <- c(error.ids, i)
    }
}



## if (length(error.ids)) {
##     ## take some action
## }
