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
from argparse import ArgumentParser
		
	
def read_data_from_csv(id_file):
    nameid_list = []
    try:
        with open(id_file, 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                nameid_list.append(row[1])
        nameid_list.pop(0)
    except Exception:
        return None
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
    open(log_file, 'w').close()
    open(video_file, 'w').close()
    open(user_file, 'w').close() 
    nameid_list = read_data_from_csv(id_file)
    if nameid_list is None:
        log = '[{}] File: {} does not exist.\n'.format(strftime('%x %X'), id_file)
        with open(log_file, 'a') as f:
            f.write(log)
        return
    dailymotion_videos = []
    dailymotion_users = []
    requests_counter = 0
    for id in nameid_list:
        user_response = get_user_data(dailymot, id)
        if user_response is not None:
            user_response['id'] = id
            dailymotion_users.append(user_response)
            with open(user_file, 'w') as f:
                j_str = dumps(dailymotion_users, indent=4, sort_keys=True)
                f.write(j_str)	        
        current_page = 1
        while True:
            video_response = get_video_data(dailymot, id, current_page)
            if video_response is None:
                break
            if 'list' not in video_response:
                break
            log = '[{}] From: {} Responce size: {}\n'.format(strftime('%x %X'), id, len(video_response['list']))
            with open(log_file, 'a') as f:
                f.write(log)
            for ele in video_response['list']:
                ele['date_time'] = strftime('%x %X')
                dailymotion_videos.append(ele) 
            requests_counter = requests_counter + 1
            if requests_counter == 10:
                requests_counter = 0
                with open(video_file, 'w') as f:
                    j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
                    f.write(j_str)          
            current_page = current_page + 1
            has_more = video_response['has_more']
            if has_more == False:
                break
    with open(video_file, 'w') as f:
        j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
        f.write(j_str)               
		
        
if __name__ == '__main__':
    parser = ArgumentParser(description='Dailymotion videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    args = parser.parse_args() 
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    logs_path = path.join(r_path, '..', 'logs')  
    if not path.exists(results_path):
        makedirs(results_path)
    if not path.exists(logs_path):
        makedirs(logs_path) 
    start_crawling(args.filename, path.join(logs_path, 'dailymotion_logs.log'), path.join(results_path, 'dailymotion_video.json'), path.join(results_path,'dailymotion_users.json'))
    