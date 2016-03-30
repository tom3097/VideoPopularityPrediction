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

MAX_VIDEOS_PER_FILE = 240000
MAX_REQUESTS_PER_SAVE = 100


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


def get_channel_data(id, log_file):
    parameters = {
        'part': 'id,statistics',
        'id': id,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/channels'
    try:
        page = request(method='get', url=url, params=parameters)
    except Exception as e:
        log = '[{}] ERROR Request for channel data {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    j_results = loads(page.text)
    return j_results


def get_video_ids(page_token, channel_id, log_file):
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
    except Exception as e:
        log = '[{}] ERROR Request for video ids {} page token {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), channel_id, page_token, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    j_results = loads(page.text)
    return j_results


def get_video_data(video_ids, channel_id, log_file):
    parameters = {
        'part': 'id,snippet,statistics',
        'id': ','.join(video_ids),
        'maxResults': 50,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/videos'
    try:
        page = request(method='get', url=url, params=parameters)
    except Exception as e:
        log = '[{}] ERROR Request for video data {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), channel_id, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    j_results = loads(page.text)
    return j_results


def start_crawling(id_file, log_file, video_file, channel_file, initial_number):
    open(log_file, 'w').close()
    dot_idx = video_file.rfind('.')
    video_file_name = video_file[:dot_idx]
    video_file_format = video_file[dot_idx:]
    nameid_list = read_data_from_csv(id_file, log_file)
    if nameid_list is None:
        return
    youtube_channels = []
    youtube_videos = []
    requests_counter = 0
    for id in nameid_list:
        video_file_number = initial_number
        video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
        channel_response = get_channel_data(id, log_file)
        if channel_response is not None:
            channel_response['channel_UC'] = id
            youtube_channels.append(channel_response)
            try:
                with open(channel_file, 'w') as f:
                    j_str = dumps(youtube_channels, indent=4, sort_keys=True)
                    f.write(j_str)
            except Exception as e:
                log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), channel_file, str(e))
                with open(log_file, 'a') as f:
                    f.write(log)
                return
        page_token = ''
        while True:
            video_ids = get_video_ids(page_token, id, log_file)
            if video_ids is None:
                break
            if 'items' not in video_ids:
                break
            video_ids_list = []
            for ele in video_ids['items']:
                video_ids_list.append(ele['id']['videoId'])
            log = '[{}] From {} Id response size {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, len(video_ids_list))
            with open(log_file, 'a') as f:
                f.write(log)
            video_response = get_video_data(video_ids_list, id, log_file)
            if video_response is None:
                break
            if 'items' not in video_response:
                break
            for ele in video_response['items']:
                ele['channel_UC'] = id
                ele['date_time'] = strftime('%Y-%m-%d %H:%M:%S')
                youtube_videos.append(ele)
            log = '[{}] From {} Responce size {} Videos in list {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, len(video_response['items']), len(youtube_videos))
            with open(log_file, 'a') as f:
                f.write(log)
            requests_counter = requests_counter + 1
            if requests_counter == MAX_REQUESTS_PER_SAVE:
                requests_counter = 0
                log = '[{}] Saving to file...\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                with open(log_file, 'a') as f:
                        f.write(log)
                try:
                    with open(video_file, 'w') as f:
                        j_str = dumps(youtube_videos, indent=4, sort_keys=True)
                        f.write(j_str)
                except Exception as e:
                    log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file, str(e))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    return
                log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                with open(log_file, 'a') as f:
                    f.write(log)
                if len(youtube_videos) >= MAX_VIDEOS_PER_FILE:
                    log = '[{}] Creating new file.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    video_file_number = video_file_number + 1
                    video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
                    youtube_videos = []
            if 'nextPageToken' in video_ids:
                page_token = video_ids['nextPageToken']
            else:
                break
        log = '[{}] Saving to file...\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        with open(video_file, 'w') as f:
            j_str = dumps(youtube_videos, indent=4, sort_keys=True)
            f.write(j_str)
        log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        youtube_videos = []


if __name__ == '__main__':
    parser = ArgumentParser(description='Youtube videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    parser.add_argument('--firstFileNumber', help='number of the FIRST file containing videos, defauly value = 1', default=1, type=int)
    args = parser.parse_args()
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    if not path.exists(results_path):
        makedirs(results_path)
    results_path = path.join(results_path, 'Youtube')
    if not path.exists(results_path):
        makedirs(results_path)
    logs_path = path.join(r_path, '..', 'logs')
    if not path.exists(logs_path):
        makedirs(logs_path)
    start_crawling(args.filename, path.join(logs_path, 'youtube_logs.log'), path.join(results_path, 'youtube_video.json'), path.join(results_path,'youtube_channels.json'), args.firstFileNumber)
