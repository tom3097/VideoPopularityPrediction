library(argparse)
library(rjson)
parser <- ArgumentParser(description = 'Histogram creator for facebook')
parser$add_argument('--date', help = 'Year and month, format: yyyy-mm', required = T)
parser$add_argument('--directory', help = 'Path to directory with facebook data', required = T)
parser$add_argument('--page_pattern', help = 'Pattern for JSON file with users data', required = T)
parser$add_argument('--video_pattern', help = 'Pattern for JSON file with videos data', required = T)
args <- parser$parse_args()

r_path <- dirname(getwd())
dir.create(file.path(r_path, 'results'), showWarnings = FALSE)
dir.create(file.path(r_path, 'results', 'Facebook'), showWarnings = FALSE)

page_files <- list.files(path = args$directory, pattern = args$page_pattern)
video_files <- list.files(path = args$directory, pattern = args$video_pattern)

followers_names <- vector()
followers_count <- vector()
for (pa_file in page_files)
{
    file_path <- file.path(args$directory, pa_file)
    json_channels <- fromJSON(file = file_path)
    for (page_info in json_channels)
    {
        followers_names <- c(followers_names, page_info$page_name_id)
        followers_count <- c(followers_count, page_info$likes)
    }
}
names(followers_count) <- followers_names

views_count <- vector()
pages_followers <- vector()
for (vid_file in video_files)
{
    file_path <- file.path(args$directory, vid_file)
    json_videos <- fromJSON(file = file_path)
    for (video_info in json_videos)
    {
        if (substr(video_info$created_time$date, 1, nchar(args$date)) == args$date)
        {
            pages_followers <- c(pages_followers, followers_count[[video_info$page_name_id]])
            views_count <- c(views_count, video_info$viewCount)
        }
    }
}

views_count <- views_count + 1
views_count <- views_count / pages_followers
views_count <- log2(views_count)

wd = getwd()
setwd(file.path(r_path, 'results', 'Facebook'))
png(filename = paste(args$date, '_views.png', sep = ''))
hist(views_count, breaks = 50)
dev.off()
setwd(wd)




