#!/usr/bin/python

# Requirements:
# Google APIs Client Library for Python:
# https://developers.google.com/api-client-library/python/start/installation#system-requirements

from requests import request
from json import loads
from csv import reader
from os import path
from os import makedirs

# Fill in Developer Key
DEVELOPER_KEY = ''
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

	
def add_UC_prefix(channel_name):
    return 'UC{}'.format(channel_name)
	

def parse_channels_file(youtube_channels_file, dest_file):
    youtube_channels = []

    with open(youtube_channels_file, 'r') as csvfile:
        r = reader(csvfile)
        for row in r:
            youtube_channels.append(row)
	youtube_channels.pop(0)
	
    with open(dest_file, 'a') as f:
        for channel in youtube_channels:
            to_save = '{},{}\n'.format(channel[0], add_UC_prefix(channel[1]))
            f.write(to_save)

			
def translate_name_to_channel(username, page_token):
    parameters = {
        'part': 'id',
        'maxResults': 50,
        'pageToken': page_token,
		'forUsername': username,
        'key': DEVELOPER_KEY,
    }
    url = 'https://www.googleapis.com/youtube/v3/channels'
    page = request(method='get', url=url, params=parameters)
    j_results = loads(page.text)
    return j_results

    
def parse_names_file(youtube_names_file, dest_file):
    youtube_names = []
	
    with open(youtube_names_file, 'r') as csvfile:
        r = reader(csvfile)
        for row in r:
            youtube_names.append(row)
	youtube_names.pop(0)
	
    page_token = ''
	
    with open(dest_file, 'a') as f:
        for name in youtube_names:
            for x in xrange(20):
                j_results = translate_name_to_channel(name[1], page_token)
                items = j_results.get('items', None)
                if items:
                    for item in items:
                        to_save = '{},{}\n'.format(name[0], item['id'])
                        f.write(to_save)
                    if 'nextPageToken' in j_results:
                        page_token = j_results['nextPageToken']
                    else:
                        break
                else:
                    break
			

def start_parsing(youtube_names_file, youtube_channels_file, dest_file):
    with open(dest_file, 'w') as f:
        f.write('creator, channel\n')
    parse_names_file(youtube_names_file, dest_file)
    parse_channels_file(youtube_channels_file, dest_file)
	
	
if __name__ == '__main__':
    if not path.exists('../results'):
        makedirs('../results')
    start_parsing('../data/youtube_name.csv', '../data/youtube_id.csv', '../data/results.csv')
	