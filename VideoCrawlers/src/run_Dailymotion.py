#!/usr/bin/python

# Requirements:
# Dailymotion sdk python:
# https://github.com/dailymotion/dailymotion-sdk-python

from json import dumps
from dailymotion import Dailymotion
from time import strftime
from csv import reader
from os import path
from os import makedirs
		
	
def read_data_from_csv(id_file):
    nameid_list = []
    with open(id_file, 'r') as csvfile:
        r = reader(csvfile)
        for row in r:
            nameid_list.append(row[1])
    nameid_list.pop(0) 
    return nameid_list

    
def get_user_data(dailymot, id):
    user_parameters = {
        'fields': 'followers_total,videos_total,videostar.bookmarks_total,views_total',
    }  
    try:
        user_response = dailymot.get('/user/{}'.format(id), user_parameters)
    except Exception:
        return None
    return user_response
    

def get_video_data(dailymot, id, current_page):
    video_fields = {
        'id', 'title', 'thumbnail_url', 'tags', 'owner.id',
        'allow_comments', 'comments_total', 'bookmarks_total',
        'available_formats', 'views_last_day', 'views_last_hour',
        'views_last_month', 'views_last_week', 'views_total',
        'country', 'created_time', 'duration', 'embed_url',
        'filmstrip_60_url','language', 'description',
        'sprite_320x_url', 'aspect_ratio', 'url',
    }
    video_parameters = {
        'fields': ','.join(video_fields),
        'page': str(current_page),
        'limit': '100',
    }
    try:
        video_response = dailymot.get('/user/{}/videos'.format(id), video_parameters)
    except Exception:
        return None
    return video_response
	

def start_crawling(id_file, log_file, video_file, user_file):
    dailymot = Dailymotion()
    ydl = YoutubeDL({ 'quiet': 'True',})  
    open(log_file, 'w').close()
    open(video_file, 'w').close()
    open(user_file, 'w').close() 
    nameid_list = read_data_from_csv(id_file)  
    dailymotion_videos = []
    dailymotion_users = []    
    for id in nameid_list:
        user_response = get_user_data(dailymot, id)
        if user_response is not None:
            dailymotion_users.append(user_response)
            total_user_videos = user_response['videos_total']
            analyzed_videos = 0
            with open(user_file, 'w') as f:
                j_str = dumps(dailymotion_users, indent=4, sort_keys=True)
                f.write(j_str)	        
        current_page = 1
        requests_counter = 0
        while True:
            video_response = get_video_data(dailymot, id, current_page)
            if video_response is None:
                break
            if 'list' not in video_response:
                break
            analyzed_videos = analyzed_videos + len(video_response['list'])
            prog = float(analyzed_videos) / float(total_user_videos)
            log = '[{}] From: {} Responce size: {} Progress:{}\n'.format(strftime('%x %X'), id, len(video_response['list']), prog)
            with open(log_file, 'a') as f:
                f.write(log)
            for ele in video_response['list']:
                ele['date_time'] = strftime('%x %X')
                dailymotion_videos.append(ele) 
            requests_counter = requests_counter + 1
            if requests_counter == 10:
                requests_counter = 0
                with open(video_file, "w") as f:
                    j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
                    f.write(j_str)          
            current_page = current_page + 1
            has_more = video_response['has_more']
            if has_more == False:
                break
    with open(video_file, "w") as f:
        j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
        f.write(j_str)               
		
        
if __name__ == "__main__":
    if not path.exists('../results'):
        makedirs('../results')
    if not path.exists('../logs'):
        makedirs('../logs')
    start_crawling('../data/dailymotion.csv', '../logs/dailymotion_logs.log', '../results/dailymotion_video.json', '../results/dailymotion_users.json')
    