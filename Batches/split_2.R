library(rjson)

directory = '/home/tbochens/VideoCrawlers/results/Youtube'

channel_files <- list.files(path = directory, pattern ='youtube_channels')
video_files <- list.files(path = directory, pattern = 'youtube_video')

followers_names <- vector()
followers_count <- vector()

for (ch_file in channel_files)
{
    file_path <- file.path(directory, ch_file)
    json_channels <- fromJSON(file = file_path)
    for (channel_info in json_channels)
    {
        followers_names <- c(followers_names, channel_info$channel_UC)
        followers_count <- c(followers_count, channel_info$items[[1]]$statistics$subscriberCount)
    }
}
names(followers_count) <- followers_names

views_count <- list()
for (vid_file in video_files)
{
	file_path <- file.path(directory, vid_file)
    json_videos <- fromJSON(file = file_path)
    for (video_info in json_videos)
    {
        key = substr(video_info$snippet$publishedAt, 1, nchar('yyyy-mm'))
		if (exists(key, where = views_count))
		{
			viewCount_numerical = as.numeric(video_info$statistics$viewCount)
			followersCount_numerical = as.numeric(followers_count[[video_info$channel_UC]])
			value = log2((viewCount_numerical+1) / followersCount_numerical)
			views_count[[key]] <- c(views_count[[key]], value)
        }
        else
		{
			viewCount_numerical = as.numeric(video_info$statistics$viewCount)
			followersCount_numerical = as.numeric(followers_count[[video_info$channel_UC]])
			value = log2((viewCount_numerical+1) / followersCount_numerical)
			views_count[[key]] <- c(value)
		}
    }
}

keys <- c()
binary_split <- c()
for (i in 1: length(views_count))
{
    sorted <- sort(views_count[[i]])
    med <- 0
    if(length(sorted) %% 2 == 0)
    {
        med <- 0.5 * (sorted[[length(sorted)/2]] + sorted[[(length(sorted)/2)+1]])
        binary_split <- c(binary_split, med)
        keys <- c(keys, names(views_count)[[i]])
    }
    else
	{
        med = sorted[[(length(sorted)+1)/2]]
        binary_split <- c(binary_split, med)
        keys <- c(keys, names(views_count)[[i]])
	}
}
names(binary_split) <- keys

jsonVal = toJSON(binary_split)
write(jsonVal, 'binarySplit.json')





