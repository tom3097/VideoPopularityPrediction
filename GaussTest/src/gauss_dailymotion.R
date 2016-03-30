library(argparse)
library(rjson)
parser <- ArgumentParser(description = 'Histogram creator for dailymotion')
parser$add_argument('--date', help = 'Year and month, format: yyyy-mm', required = T)
parser$add_argument('--directory', help = 'Path to directory with dailymotion data', required = T)
parser$add_argument('--user_pattern', help = 'Pattern for JSON file with users data', required = T)
parser$add_argument('--video_pattern', help = 'Pattern for JSON file with videos data', required = T)
args <- parser$parse_args()

r_path <- dirname(getwd())
dir.create(file.path(r_path, 'results'), showWarnings = FALSE)
dir.create(file.path(r_path, 'results', 'Dailymotion'), showWarnings = FALSE)

user_files <- list.files(path = args$directory, pattern = args$user_pattern)
video_files <- list.files(path = args$directory, pattern = args$video_pattern)

followers_names <- vector()
followers_count <- vector()
for (us_file in user_files)
{
    file_path <- file.path(args$directory, us_file)
    json_channels <- fromJSON(file = file_path)
    for (user_info in json_channels)
    {
        followers_names <- c(followers_names, user_info$id)
        followers_count <- c(followers_count, user_info$followers_total)
    }
}
names(followers_count) <- followers_names

views_count <- vector()
users_followers <- vector()
for (vid_file in video_files)
{
    file_path <- file.path(args$directory, vid_file)
    json_videos <- fromJSON(file = file_path)
    for (video_info in json_videos)
    {
        if (substr(video_info$created_time, 1, nchar(args$date)) == args$date)
        {
            users_followers <- c(users_followers, followers_count[[video_info$name_id]])
            views_count <- c(views_count, video_info$views_total)
        }
    }
}

views_count <- views_count + 1
views_count <- views_count / users_followers
views_count <- log2(views_count)

wd = getwd()
setwd(file.path(r_path, 'results', 'Dailymotion'))
png(filename = paste(args$date, '_views.png', sep = ''))
hist(views_count, breaks = 50)
dev.off()
setwd(wd)



