library(argparse)
library(rjson)
parser <- ArgumentParser(description = 'Histogram creator for youtube')
parser$add_argument('--date', help = 'Year and month, format: yyyy-mm', required = T)
parser$add_argument('--directory', help = 'Path to directory with youtube data', required = T)
parser$add_argument('--channel_pattern', help = 'Pattern for JSON file with channels data', required = T)
parser$add_argument('--video_pattern', help = 'Pattern for JSON file with videos data', required = T)
args <- parser$parse_args()

r_path <- dirname(getwd())
dir.create(file.path(r_path, 'results'), showWarnings = FALSE)
dir.create(file.path(r_path, 'results', 'Youtube'), showWarnings = FALSE)

channel_files <- list.files(path = args$directory, pattern = args$channel_pattern)
video_files <- list.files(path = args$directory, pattern = args$video_pattern)

followers_names <- vector()
followers_count <- vector()
for (ch_file in channel_files)
{
    file_path <- file.path(args$directory, ch_file)
    json_channels <- fromJSON(file = file_path)
    for (channel_info in json_channels)
    {
        followers_names <- c(followers_names, channel_info$channel_UC)
        followers_count <- c(followers_count, channel_info$items[[1]]$statistics$subscriberCount)
    }
}
names(followers_count) <- followers_names

views_count <- vector()
channels_followers <- vector()
for (vid_file in video_files)
{
    file_path <- file.path(args$directory, vid_file)
    json_videos <- fromJSON(file = file_path)
    for (video_info in json_videos)
    {
        if (substr(video_info$snippet$publishedAt, 1, nchar(args$date)) == args$date)
        {
            channels_followers <- c(channels_followers, followers_count[[video_info$channel_UC]])
            views_count <- c(views_count, video_info$statistics$viewCount)
        }
    }
}

views_count <- as.numeric(views_count)
channels_followers <- as.numeric(channels_followers)

views_count <- views_count + 1
views_count <- views_count / channels_followers
views_count <- log2(views_count)

wd = getwd()
setwd(file.path(r_path, 'results', 'Youtube'))
png(filename = paste(args$date, '_views.png', sep = ''))
hist(views_count, breaks = 50)
dev.off()
setwd(wd)
