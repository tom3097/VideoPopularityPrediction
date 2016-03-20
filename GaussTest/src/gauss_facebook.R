library(argparse)
library(rjson)
parser <- ArgumentParser(description = 'Histogram creator for facebook')
parser$add_argument('--date', help = 'Year and month, format: yyyy-mm', required = T)
parser$add_argument('--filename_videos', help = 'Path to JSON file with video data', required = T)
parser$add_argument('--filename_pages', help = 'Path to JSON file with page data', required = T)
args <- parser$parse_args()

wd = getwd()
r_path = dirname(getwd())
dir.create(file.path(r_path, 'results'), showWarnings = FALSE)
dir.create(file.path(r_path, 'results', 'Facebook'), showWarnings = FALSE)

cat('Reading from file, this may take some time\n')
json_video_input <- fromJSON(file = args$filename_videos)
json_page_input <- fromJSON(file = args$filename_pages)
cat('Finished reading\n')

cat('Analyzing pages info\n')
followers_names <- vector()
followers_count <- vector()
for (page_info in json_page_input) {
    followers_names <- c(followers_names, page_info$page_name_id)
    followers_count <- c(followers_count, page_info$likes)
}
names(followers_count) <- followers_names
cat('Analyzing done\n')

cat('Looking for proper videos\n')
views_count <- vector()
pages_followers <- vector()
for (vid in json_video_input) {
    if (substr(vid$created_time$date, 1, nchar(args$date)) == args$date) {
        views_count <- c(views_count, vid$viewCount)
        pages_followers <- c(pages_followers, followers_count[[vid$page_name_id]])
    }
}
cat('Looking for videos done\n')

views_count <- views_count + 1
normalized_views_count <- views_count / pages_followers
views_count <- log2(views_count)
normalized_views_count <- log2(normalized_views_count)

cat('Creating histograms\n')
setwd(file.path(r_path, 'results', 'Facebook'))
png(filename = paste(args$date, '_views.png', sep = ''))
hist(views_count, breaks = 50)
dev.off()
png(filename = paste(args$date, '_normalized_views.png', sep = ''))
hist(normalized_views_count, breaks = 50)
dev.off()
setwd(wd)
cat('Creating done\n')



