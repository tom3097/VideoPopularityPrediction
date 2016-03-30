#!/usr/bin/python

# Requirements:
# PyVimeo:
# https://github.com/vimeo/vimeo.py

from time import strftime
from csv import reader
from vimeo import VimeoClient
from json import dumps
from os import path
from os import makedirs
from argparse import ArgumentParser

# Fill in Access Token, Client Id, Client Secret
YOUR_ACCESS_TOKEN = 'c7238d5d9379fd1bf459d454c32ee017'
YOUR_CLIENT_ID = 'ce75fa1502db7225af8af39df54a1bb075780c99'
YOUR_CLIENT_SECRET = '+FQhhYI+Exi93mSemN80ztNbve83A3bF0HDXF3COgrbJz20OHXaT/5/ifjGdHgRLmIoSFxciiApkVFbSFyTUeH3x75QFT1y3yfXF8PaTA1FYPtwFwt97YQ1bf5TKd1Bg'

MAX_VIDEOS_PER_FILE = 130000
MAX_REQUESTS_PER_SAVE = 200


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
    

def get_channel_data(vim, id, log_file):
    try:
        channel_response = vim.get('/channels/{}'.format(id))
        if channel_response is not None:
            channel_response = {
                'id': id,
                'channels_meta': channel_response.json()['metadata'],
                'user_meta': channel_response.json()['user']['metadata'],
            }
    except Exception as e:
        log = '[{}] ERROR Request for user data {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    return channel_response
    

def get_video_data(vim, cmd, log_file):
    try:
        response = vim.get(cmd)
    except Exception as e:
        log = '[{}] ERROR Request for video data {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), cmd, str(e))
        with open(log_file, 'a') as f:
            f.write(log)
        return None
    return response.json()
    

def start_crawling(id_file, log_file, video_file, channel_file, initial_number):
    v = VimeoClient(token=YOUR_ACCESS_TOKEN, key=YOUR_CLIENT_ID, secret=YOUR_CLIENT_SECRET)
    open(log_file, 'w').close()
    dot_idx = video_file.rfind('.')
    video_file_name = video_file[:dot_idx]
    video_file_format = video_file[dot_idx:]
    nameid_list = read_data_from_csv(id_file, log_file)
    if nameid_list is None:
        return
    vimeo_channels = []
    vimeo_videos = []
    requests_counter = 0
    for id in nameid_list:
        video_file_number = initial_number
        video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
        channel_response = get_channel_data(v, id, log_file)
        if channel_response is not None:
            channel_response['name_id'] = id
            vimeo_channels.append(channel_response)
            try:
                with open(channel_file, 'w') as f:
                    j_str = dumps(vimeo_channels, indent=4, sort_keys=True)
                    f.write(j_str)
            except Exception as e:
                log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), channel_file, str(e))
                with open(log_file, 'a') as f:
                    f.write(log)
                return
        fields = {
            'uri', 'name', 'description', 'link', 'duration',
            'width', 'height', 'language', 'created_time',
            'modified_time', 'privacy', 'pictures', 'tags',
            'stats', 'metadata', 'user.uri',
        }
        cmd = '/channels/{}/videos?fields={}&per_page=50&page=1&sort=date&direction=asc'.format(id, ','.join(fields))
        while True:
            video_response = get_video_data(v, cmd, log_file)
            if video_response is None:
                break
            if 'data' not in video_response:
                break
            for ele in video_response['data']:
                ele['date_time'] = strftime('%Y-%m-%d %H:%M:%S')
                ele['name_id'] = id
                vimeo_videos.append(ele)
            eq_idx = cmd.rfind('=')
            page = cmd[eq_idx+1:]
            log = '[{}] From {} Responce size {} Page {} Videos in list {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), id, len(video_response['data']), page, len(vimeo_videos))
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
                        j_str = dumps(vimeo_videos, indent=4, sort_keys=True)
                        f.write(j_str)
                except Exception as e:
                    log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file, str(e))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    return
                log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                with open(log_file, 'a') as f:
                    f.write(log)
                if len(vimeo_videos) >= MAX_VIDEOS_PER_FILE:
                    log = '[{}] Creating new file.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
                    with open(log_file, 'a') as f:
                        f.write(log)
                    video_file_number = video_file_number + 1
                    video_file = '{}_{}_{}{}'.format(video_file_name, id, video_file_number, video_file_format)
                    vimeo_videos = []
            cmd = video_response['paging']['next']
            if not cmd:
                break
        log = '[{}] Saving to file...\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        try:
            with open(video_file, 'w') as f:
                j_str = dumps(vimeo_videos, indent=4, sort_keys=True)
                f.write(j_str)
        except Exception as e:
            log = '[{}] Save or open to file {} FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file, str(e))
            with open(log_file, 'a') as f:
                f.write(log)
            return
        log = '[{}] Successfully saved.\n'.format(strftime('%Y-%m-%d %H:%M:%S'))
        with open(log_file, 'a') as f:
            f.write(log)
        vimeo_videos = []
                
                
if __name__ == '__main__':
    parser = ArgumentParser(description='Vimeo videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    parser.add_argument('--firstFileNumber', help='number of the FIRST file containing videos, defauly value = 1', default=1, type=int)
    args = parser.parse_args() 
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    if not path.exists(results_path):
        makedirs(results_path)
    results_path = path.join(results_path, 'Vimeo')
    if not path.exists(results_path):
        makedirs(results_path)
    logs_path = path.join(r_path, '..', 'logs')
    if not path.exists(logs_path):
        makedirs(logs_path)
    start_crawling(args.filename, path.join(logs_path, 'vimeo_logs.log'), path.join(results_path, 'vimeo_video.json'), path.join(results_path,'vimeo_channels.json'), args.firstFileNumber)
    