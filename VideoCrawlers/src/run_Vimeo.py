#!/usr/bin/python

# Requirements:
# PyVimeo:
# https://github.com/vimeo/vimeo.py
# youtube-dl:
# https://github.com/rg3/youtube-dl

from youtube_dl import YoutubeDL
from time import strftime
from csv import reader
from vimeo import VimeoClient
from json import dumps
from os import path
from os import makedirs

# Fill in Access Token, Client Id, Client Secret
YOUR_ACCESS_TOKEN = ''
YOUR_CLIENT_ID = ''
YOUR_CLIENT_SECRET = ''


class VimeoVideo:
    def __init__(self, basic_metadata, stream_url):
        self.info_dict = {
            'uri': basic_metadata['uri'],
            'name': basic_metadata['name'],
            'description': basic_metadata['description'],
            'link': basic_metadata['link'],
            'duration': basic_metadata['duration'],
            'width': basic_metadata['width'],
            'height': basic_metadata['height'],
            'language': basic_metadata['language'],
            'created_time': basic_metadata['created_time'],
            'modified_time': basic_metadata['modified_time'],
            'privacy': basic_metadata['privacy'],
            'pictures': basic_metadata['pictures'],
            'tags': basic_metadata['tags'],
            'stats': basic_metadata['stats'],
            'metadata': basic_metadata['metadata'],
            'user_uri': basic_metadata['user']['uri'],
            'source': stream_url,
            'current_date': strftime("%x"),
            'current_time': strftime("%X"),
        }

    def __str__(self):
        return dumps(self.info_dict, indent=4, sort_keys=True) + '\n'

    def save_to_file_oneline(self, file_desc):
        jstr = dumps(self.info_dict, sort_keys=True) + '\n'
        file_desc.write(jstr)
		
    def save_to_file_pretty(self, file_desc):
        jstr = dumps(self.info_dict, indent=4, sort_keys=True) + '\n'
        file_desc.write(jstr)

   
   
def get_stream_url(link, ydl_p):
    try:
        info = ydl_p.extract_info(link, download=False)      
    except Exception:
        return None
    return info['url']
    

def get_metadata(vim, video_uri):
    fields = {
        'uri', 'name', 'description', 'link', 'duration',
        'width', 'height', 'language', 'created_time',
        'modified_time', 'privacy', 'pictures', 'tags',
        'stats', 'metadata', 'user.uri',
    }
    cmd = "{}?fields={}".format(video_uri, ','.join(fields))
    try:
        response = vim.get(cmd)
    except Exception:
        return None
    return response.json()
    

def get_video_meta(vimeo_id_file, dest_file):

    v = VimeoClient(token=YOUR_ACCESS_TOKEN, key=YOUR_CLIENT_ID, secret=YOUR_CLIENT_SECRET)
    ydl = YoutubeDL({ 'quiet': 'True',})
    
    nameid_list = []
    with open(vimeo_id_file, "r") as csvfile:
        r = reader(csvfile)
        for row in r:
            nameid_list.append(row[1])
    nameid_list.pop(0)
    
    with open(dest_file, "w") as f:
        for id in nameid_list:
            print "Name: {}".format(id)
            cmd = "/channels/{}/videos?fields=uri&per_page=50&page=1".format(id)
            for x in xrange(20):
                try:
                    response = v.get(cmd)
                except Exception:
                    continue
                response = response.json()
                
                if "data" not in response:
                    break
                    
                for ele in response["data"]:
                    video_uri = ele['uri']
                    print "Video uri: {}".format(video_uri)
                    basic_metadata = get_metadata(v, video_uri)
                    if basic_metadata is None:
                        continue
                    link = basic_metadata['link']
                    source = get_stream_url(link, ydl)
                    new_video = VimeoVideo(basic_metadata, source)
                    new_video.save_to_file_pretty(f)
                
                cmd = response["paging"]["next"]
                if not cmd:
                    break
                
                
if __name__ == "__main__":
    if not path.exists('../results'):
        makedirs('../results')
    get_video_meta('../data/vimeo.csv', '../results/vimeo_res.json')
