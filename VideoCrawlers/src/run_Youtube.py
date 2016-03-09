#!/usr/bin/python

# Requirements:
# Google APIs Client Library for Python:
# https://developers.google.com/api-client-library/python/start/installation#system-requirements

from json import dumps
from json import loads
from requests import request
from csv import reader
from os import path
from os import makedirs
from argparse import ArgumentParser
from time import strftime

# Fill in Developer Key
DEVELOPER_KEY = 'AIzaSyAVbJNj-edqMejkOBVmrZQ3aW7AmSnOMts'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


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


def get_channel_data(id):
    parameters = {
        'part': 'id,statistics',
        'id': id,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/channels'
    try:
        page = request(method='get', url=url, params=parameters)
    except Exception:
        return None
    j_results = loads(page.text)
    return j_results
    

def get_video_ids(page_token, channel_id):
    parameters = {
        'part': 'id',
        'maxResults': 50,
        'pageToken': page_token,
        'type': 'video',
		'channelId': channel_id,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/search'
    try:
        page = request(method='get', url=url, params=parameters)
    except Exception:
        return None
    j_results = loads(page.text)
    return j_results

    
def get_video_data(video_ids):
    parameters = {
        'part': 'id,snippet,statistics',
        'id': ','.join(video_ids),
        'maxResults': 50,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/videos'
    try:
        page = request(method='get', url=url, params=parameters)
    except Exception:
        return None
    j_results = loads(page.text)
    return j_results
    
	
def start_crawling(id_file, log_file, video_file, channel_file):
    open(log_file, 'w').close()
    open(video_file, 'w').close()
    open(channel_file, 'w').close() 
    nameid_list = read_data_from_csv(id_file)
    if nameid_list is None:
        log = '[{}] File: {} does not exist.\n'.format(strftime('%x %X'), id_file)
        with open(log_file, 'a') as f:
            f.write(log)
        return
    youtube_channels = []
    youtube_videos = []
    requests_counter = 0
    for id in nameid_list:
        channel_response = get_channel_data(id)
        if channel_response is not None:
            youtube_channels.append(channel_response)
            with open(channel_file, 'w') as f:
                j_str = dumps(youtube_channels, indent=4, sort_keys=True)
                f.write(j_str)
        page_token = ''
        while True:
            video_ids = get_video_ids(page_token, id)
            if video_ids is None:
                break
            if 'items' not in video_ids:
                break
            video_ids_list = []
            for ele in video_ids['items']:
                video_ids_list.append(ele['id']['videoId'])
            video_response = get_video_data(video_ids_list)
            if video_response is None:
                break
            if 'items' not in video_response:
                break
            log = '[{}] From: {} Responce size: {}.\n'.format(strftime('%x %X'), id, len(video_response['items']))
            with open(log_file, 'a') as f:
                f.write(log)
            for ele in video_response['items']:
                ele['date_time'] = strftime('%x %X')
                youtube_videos.append(ele)
            requests_counter = requests_counter + 1
            if requests_counter == 20:
                requests_counter = 0
                with open(video_file, 'w') as f:
                    j_str = dumps(youtube_videos, indent=4, sort_keys=True)
                    f.write(j_str)
            if 'nextPageToken' in video_ids:
                page_token = video_ids['nextPageToken']
            else:
                break
    with open(video_file, 'w') as f:
        j_str = dumps(youtube_videos, indent=4, sort_keys=True)
        f.write(j_str) 


if __name__ == '__main__':
    parser = ArgumentParser(description='Youtube videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    args = parser.parse_args() 
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    logs_path = path.join(r_path, '..', 'logs')  
    if not path.exists(results_path):
        makedirs(results_path)
    if not path.exists(logs_path):
        makedirs(logs_path) 
    start_crawling(args.filename, path.join(logs_path, 'youtube_logs.log'), path.join(results_path, 'youtube_video.json'), path.join(results_path,'youtube_channels.json'))
