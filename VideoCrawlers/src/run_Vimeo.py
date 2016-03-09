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
YOUR_ACCESS_TOKEN = ''
YOUR_CLIENT_ID = ''
YOUR_CLIENT_SECRET = ''


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
    

def get_channel_data(vim, id):
    try:
        channel_response = vim.get('/channels/{}'.format(id))
        if channel_response is not None:
            channel_response = {
                'id': id,
                'channels_meta': channel_response.json()['metadata'],
                'user_meta': channel_response.json()['user']['metadata'],
            }
    except Exception:
        return None
    return channel_response
    

def get_video_data(vim, cmd):
    try:
        response = vim.get(cmd)
    except Exception:
        return None
    return response.json()
    

def start_crawling(id_file, log_file, video_file, channel_file):
    v = VimeoClient(token=YOUR_ACCESS_TOKEN, key=YOUR_CLIENT_ID, secret=YOUR_CLIENT_SECRET)
    open(log_file, 'w').close()
    open(video_file, 'w').close()
    open(channel_file, 'w').close() 
    nameid_list = read_data_from_csv(id_file)
    if nameid_list is None:
        log = '[{}] File: {} does not exist.\n'.format(strftime('%x %X'), id_file)
        with open(log_file, 'a') as f:
            f.write(log)
        return
    vimeo_channels = []
    vimeo_videos = []
    requests_counter = 0
    for id in nameid_list:
        channel_response = get_channel_data(v, id)
        if channel_response is not None:
            vimeo_channels.append(channel_response)
            with open(channel_file, 'w') as f:
                j_str = dumps(vimeo_channels, indent=4, sort_keys=True)
                f.write(j_str)
        fields = {
            'uri', 'name', 'description', 'link', 'duration',
            'width', 'height', 'language', 'created_time',
            'modified_time', 'privacy', 'pictures', 'tags',
            'stats', 'metadata', 'user.uri',
        }
        cmd = '/channels/{}/videos?fields={}&per_page=50&page=1'.format(id, ','.join(fields))
        while True:
            video_response = get_video_data(v, cmd)
            if video_response is None:
                break
            if 'data' not in video_response:
                break
            log = '[{}] From: {} Responce size: {}.\n'.format(strftime('%x %X'), id, len(video_response['data']))
            with open(log_file, 'a') as f:
                f.write(log)
            for ele in video_response['data']:
                ele['date_time'] = strftime('%x %X')
                vimeo_videos.append(ele)
            requests_counter = requests_counter + 1
            if requests_counter == 20:
                requests_counter = 0
                with open(video_file, 'w') as f:
                    j_str = dumps(vimeo_videos, indent=4, sort_keys=True)
                    f.write(j_str)          
            cmd = video_response['paging']['next']
            if not cmd:
                break
    with open(video_file, 'w') as f:
        j_str = dumps(vimeo_videos, indent=4, sort_keys=True)
        f.write(j_str) 
                
                
if __name__ == '__main__':
    parser = ArgumentParser(description='Vimeo videos metadata downloader.')
    parser.add_argument('--filename', help='path to csv file with creators data (csv pattern: creator_name, creator_id_name)', required=True)
    args = parser.parse_args() 
    r_path = path.dirname(path.realpath(__file__))
    results_path = path.join(r_path, '..', 'results')
    logs_path = path.join(r_path, '..', 'logs')  
    if not path.exists(results_path):
        makedirs(results_path)
    if not path.exists(logs_path):
        makedirs(logs_path) 
    start_crawling(args.filename, path.join(logs_path, 'vimeo_logs.log'), path.join(results_path, 'vimeo_video.json'), path.join(results_path,'vimeo_channels.json'))
    