#!/usr/bin/python

# Requirements:
# Google APIs Client Library for Python:
# https://developers.google.com/api-client-library/python/start/installation#system-requirements
# youtube-dl:
# https://github.com/rg3/youtube-dl

from json import dumps
from json import loads
from string import ascii_letters
from random import choice
from requests import request
from youtube_dl import YoutubeDL
from csv import reader
from os import path
from os import makedirs


# Fill in Developer Key
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class YoutubeVideo:
    def __init__(self, video_id, basic_metadata, source_url):
        self.info_dict = {
            'id': video_id,
            'snippet': basic_metadata['snippet'],
            'statistics': basic_metadata['statistics'],
            'source': source_url,
        }

    def __str__(self):
        return dumps(self.info_dict, indent=4, sort_keys=True) + '\n'
	
    def save_to_file_oneline(self, file_desc):
        jstr = dumps(self.info_dict, sort_keys=True) + '\n'
        file_desc.write(jstr)
		
    def save_to_file_pretty(self, file_desc):
        jstr = dumps(self.info_dict, indent=4, sort_keys=True) + '\n'
        file_desc.write(jstr)


def get_videos_ids(page_token, channel_id = ""):
    parameters = {
        "part": "id",
        "maxResults": 50,
        "pageToken": page_token,
        "type": "video",
		"channelId": channel_id,
        "key": DEVELOPER_KEY,
    }
    url = "https://www.googleapis.com/youtube/v3/search"
    try:
        page = request(method="get", url=url, params=parameters)
    except Exception:
        return None
    j_results = loads(page.text)
    return j_results
    

def get_metadata(video_id):
    parameters = {
        "part": "snippet, statistics",
        "id": video_id,
        "key": DEVELOPER_KEY,
    }
    url = "https://www.googleapis.com/youtube/v3/videos"
    try:
        page = request(method="get", url=url, params=parameters)
    except Exception:
        return None
    j_results = loads(page.text)
    return j_results
    
    
def get_stream_url(video_id, ydl_p):
    v_url = "https://www.youtube.com/watch?v={}".format(video_id)
    try:
        info = ydl_p.extract_info(v_url, download=False)
    except Exception:
        return None
    return info['url']

	
def get_video_meta(youtube_channel_file, dest_file):
    ydl = YoutubeDL({ 'quiet': 'True',})

    channel_id_list = []
    with open(youtube_channel_file, 'r') as csvfile:
        r = reader(csvfile)
        for row in r:
            channel_id_list.append(row[0])
    channel_id_list.pop(0)

    page_token = ''

    with open(dest_file, 'w') as f:
        for id in channel_id_list:
            print 'Channel id: {}'.format(id)
            for x in xrange(20):
                j_results = get_videos_ids(page_token, id)
                if j_results is None:
                    continue
                items = j_results.get("items", None)
                if items:
                    for item in items:
                        key = item["id"]["videoId"]
                        print 'Video id: {}'.format(key)
                        basic_metadata = get_metadata(key)
                        
                        if basic_metadata is None:
                            continue    
                        if "items" not in basic_metadata:
                            continue
                        basic_metadata = basic_metadata['items']
                        
                        try:
                            basic_metadata = basic_metadata[0]
                        except Exception:
                            continue
                        
                        v_url = get_stream_url(key, ydl)
                        new_video = YoutubeVideo(key, basic_metadata, v_url)
                        new_video.save_to_file_pretty(f)

                    if "nextPageToken" in j_results:
                        page_token = j_results["nextPageToken"]
                    else:
                        break
                else:
                    break
				

if __name__ == "__main__":
    if not path.exists('../results'):
        makedirs('../results')
    get_video_meta('../data/results.csv', '../results/youtube_res.json')
