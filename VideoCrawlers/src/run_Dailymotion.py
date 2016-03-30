#!/usr/bin/python

# Requirements:
# Dailymotion sdk python:
# https://github.com/dailymotion/dailymotion-sdk-python

from json import dumps
from dailymotion import Dailymotion
from time import strftime
from time import localtime
from csv import reader
from os import path
from os import makedirs
from argparse import ArgumentParser

MAX_VIDEOS_PER_FILE = 750000
MAX_REQUESTS_PER_SAVE = 100
MAX_PAGE_NUMBER = 100
		
	
def read_data_from_csv(id_file, log_file):
    nameid_list = []
    try:
        with open(id_file, 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                nameid_list.append(row[1])
        nameid_list.pop(0)
    except Exception as e:
        log = '[{}] ERROR File {} does not exist: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id_file, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    return nameid_list

    
def get_user_data(dailymot, id, log_file):
    user_parameters = {
        'fields': 'followers_total,videos_total,videostar.bookmarks_total,views_total',
    }  
    try:
        user_response = dailymot.get('/user/{}'.format(id), user_parameters)
    except Exception as e:
        log = '[{}] ERROR Request for user data {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    return user_response
    

def get_video_data(dailymot, id, current_page, log_file):
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
        'sort': 'recent',
    }
    try:
        video_response = dailymot.get('/user/{}/videos'.format(id), video_parameters)
    except Exception as e:
        log = '[{}] ERROR Request for video data {} page {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, current_page, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    return video_response
	

def start_crawling(id_file, log_file, video_file, user_file, initial_number):
    dailymot = Dailymotion()
    open(log_file, 'w').close()
    dot_idx = video_file.rfind('.')
    video_file_name = video_file[:dot_idx]
    video_file_format = video_file[dot_idx:]
    nameid_list = read_data_from_csv(id_file, log_file)
    if nameid_list is None:
        return
    dailymotion_videos = []
    dailymotion_users = []
    requests_counter = 0
    for id in nameid_list:
        video_file_number = initial_number
        video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
        user_response = get_user_data(dailymot, id, log_file)
        if user_response is not None:
            user_response['id'] = id
            dailymotion_users.append(user_response)
            try:
                with open(user_file, 'w') as f:
                    j_str = dumps(dailymotion_users, indent=4, sort_keys=True)
                    f.write(j_str)
            except Exception as e:
                log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), user_file, str(e))
                with open(log_file, 'a') as f:
                    f.write(log)
                return
        current_page = 1
        while True:
            video_response = get_video_data(dailymot, id, current_page, log_file)
            if video_response is None:
                break
            if 'list' not in video_response:
                break
            for ele in video_response['list']:
                ele['date_time'] = strftime('%Y-%m-%d %H:%M:%S')
                ele['name_id'] = id
                ele['created_time'] = strftime('%Y-%m-%d %H:%M:%S', localtime(ele['created_time']))
                dailymotion_videos.append(ele) 
            log = '[{}] From {} Responce size {} Page {} Videos in list {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, len(video_response['list']), current_page, len(dailymotion_videos))
            with open(log_file, 'a') as f:
                f.write(log)
            requests_counter = requests_counter + 1
            if requests_counter == MAX_REQUESTS_PER_SAVE:
                requests_counter = 0
                log = '[{}] Saving to file...\n'.format(strftime('%x %X'))
                with open(log_file, 'a') as f:
                        f.write(log)
                try:
                    with open(video_file, 'w') as f:
                        j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
                        f.write(j_str)
                except Exception as e:
                    log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file, str(e))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    return
                log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                with open(log_file, 'a') as f:
                    f.write(log)
                if len(dailymotion_videos) >= MAX_VIDEOS_PER_FILE:
                    log = '[{}] Creating new file.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    video_file_number = video_file_number + 1
                    video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
                    dailymotion_videos = []
            current_page = current_page + 1
            if current_page > MAX_PAGE_NUMBER:
                break
            has_more = video_response['has_more']
            if has_more == False:
                break
        log = '[{}] Saving to file...\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        try:
            with open(video_file, 'w') as f:
                j_str = dumps(dailymotion_videos, indent=4, sort_keys=True)
                f.write(j_str)
        except Exception as e:
            log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file, str(e))
            with open(log_file, 'a') as f:
                f.write(log)
            return
        log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        dailymotion_videos = []
		
        
if __name__ == '__main__':
    parser = ArgumentParser(description='Dailymotion videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    parser.add_argument('--firstFileNumber', help='number of the FIRST file containing videos, defauly value = 1', default=1, type=int)
    args = parser.parse_args() 
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    if not path.exists(results_path):
        makedirs(results_path)
    results_path = path.join(results_path, 'Dailymotion')
    if not path.exists(results_path):
        makedirs(results_path)
    logs_path = path.join(r_path, '..', 'logs')
    if not path.exists(logs_path):
        makedirs(logs_path) 
    start_crawling(args.filename, path.join(logs_path, 'dailymotion_logs.log'), path.join(results_path, 'dailymotion_video.json'), path.join(results_path,'dailymotion_users.json'), args.firstFileNumber)
    