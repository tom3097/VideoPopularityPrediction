##### Histogram creator for vimeo

usage: gauss_vimeo.R [-h] --date DATE --directory DIRECTORY --channel_pattern
                     CHANNEL_PATTERN --video_pattern VIDEO_PATTERN

optional arguments:
  -h, --help            show this help message and exit
  --date DATE           Year and month, format: yyyy-mm
  --directory DIRECTORY
                        Path to directory with vimeo data
  --channel_pattern CHANNEL_PATTERN
                        Pattern for JSON file with channels data
  --video_pattern VIDEO_PATTERN
                        Pattern for JSON file with videos data
                        
##### Histogram creator for youtube

usage: gauss_youtube.R [-h] --date DATE --directory DIRECTORY
                       --channel_pattern CHANNEL_PATTERN --video_pattern
                       VIDEO_PATTERN

optional arguments:
  -h, --help            show this help message and exit
  --date DATE           Year and month, format: yyyy-mm
  --directory DIRECTORY
                        Path to directory with youtube data
  --channel_pattern CHANNEL_PATTERN
                        Pattern for JSON file with channels data
  --video_pattern VIDEO_PATTERN
                        Pattern for JSON file with videos data

##### Histogram creator for facebook

usage: gauss_facebook.R [-h] --date DATE --directory DIRECTORY --page_pattern
                        PAGE_PATTERN --video_pattern VIDEO_PATTERN

optional arguments:
  -h, --help            show this help message and exit
  --date DATE           Year and month, format: yyyy-mm
  --directory DIRECTORY
                        Path to directory with facebook data
  --page_pattern PAGE_PATTERN
                        Pattern for JSON file with users data
  --video_pattern VIDEO_PATTERN
                        Pattern for JSON file with videos data
                        
##### Histogram creator for dailymotion

usage: gauss_dailymotion.R [-h] --date DATE --directory DIRECTORY
                           --user_pattern USER_PATTERN --video_pattern
                           VIDEO_PATTERN

optional arguments:
  -h, --help            show this help message and exit
  --date DATE           Year and month, format: yyyy-mm
  --directory DIRECTORY
                        Path to directory with dailymotion data
  --user_pattern USER_PATTERN
                        Pattern for JSON file with users data
  --video_pattern VIDEO_PATTERN
                        Pattern for JSON file with videos data
