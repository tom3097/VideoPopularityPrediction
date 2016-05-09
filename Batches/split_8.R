library(rjson)

split_half <- function(container)
{
    sorted <- sort(container)
    med <- 0
    first_half = vector()
    second_half = vector()
    if(length(sorted) < 2)
    {
        toRet <- c(NA, as.vector(c(0)), as.vector(c(0)))
        return(toRet)
    }
    if(length(sorted) %% 2 == 0)
    {
        med <- 0.5 * (sorted[[length(sorted)/2]] + sorted[[(length(sorted)/2)+1]])
        first_half <- as.vector(sorted[1:(length(sorted)/2)])
        second_half <- as.vector(sorted[((length(sorted)/2)+1):(length(sorted))])
    }
    else
	{
        med = sorted[[(length(sorted)+1)/2]]
        first_half <- as.vector(sorted[1:(length(sorted)/2)])
        second_half <- as.vector(sorted[((length(sorted)/2)+2):(length(sorted))])
	}
    toRet <- list()
    toRet[[1]] <- med
    toRet[[2]] <- first_half
    toRet[[3]] <- second_half
    return(toRet)
}

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
multisplit <- list()
for (i in 1: length(views_count))
{
    split_list <- c()
    container = views_count[[i]]
    
    Split1_2 <- split_half(container)
    split_list <- c(split_list, Split1_2[[1]])
       
    Split1_4 <- split_half(Split1_2[[2]])
    split_list <- c(split_list, Split1_4[[1]])
    
    Split3_4 <- split_half(Split1_2[[3]])
    split_list <- c(split_list, Split3_4[[1]])
    
    Split1_8 <- split_half(Split1_4[[2]])
    split_list <- c(split_list, Split1_8[[1]])
    
    Split3_8 <- split_half(Split1_4[[3]])
    split_list <- c(split_list, Split3_8[[1]])
    
    Split5_8 <- split_half(Split3_4[[2]])
    split_list <- c(split_list, Split5_8[[1]])
    
    Split7_8 <- split_half(Split3_4[[3]])
    split_list <- c(split_list, Split7_8[[1]])
    
    split_list <- sort(split_list, na.last = TRUE)
    multisplit[[length(multisplit)+1]] <- split_list
    keys <- c(keys, names(views_count)[[i]])
}
names(multisplit) <- keys

jsonVal = toJSON(multisplit)
write(jsonVal, 'multisplit.json')




