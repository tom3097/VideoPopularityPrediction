#!/usr/bin/python

# Requirements:
# Dailymotion sdk python:
# https://github.com/dailymotion/dailymotion-sdk-python
# youtube-dl:
# https://github.com/rg3/youtube-dl

from json import dumps
from dailymotion import Dailymotion
from youtube_dl import YoutubeDL
from time import strftime
from csv import reader
from os import path
from os import makedirs


class DailymotionVideo:
    def __init__(self, basic_metadata, stream_url):
        self.info_dict = {
            'id': basic_metadata['id'],
            'allow_comments': basic_metadata['allow_comments'],
            'available_formats': basic_metadata['available_formats'],
            'aspect_ratio': basic_metadata['aspect_ratio'],
            'bookmarks_total': basic_metadata['bookmarks_total'],
            'comments_total': basic_metadata['comments_total'],
            'country': basic_metadata['country'],
            'created_time': basic_metadata['created_time'],
            'duration': basic_metadata['duration'],
            'description': basic_metadata['description'],
            'sprite_320x_url': basic_metadata['sprite_320x_url'],
            'embed_url': basic_metadata['embed_url'],
            'filmstrip_60_url': basic_metadata['filmstrip_60_url'],
            'language': basic_metadata['language'],
            'owner_id': basic_metadata['owner.id'],
            'tags': basic_metadata['tags'],
            'thumbnail_url': basic_metadata['thumbnail_url'],
            'title': basic_metadata['title'],
            'url': basic_metadata['url'],
            'views_last_day': basic_metadata['views_last_day'],
            'views_last_hour': basic_metadata['views_last_hour'],
            'views_last_month': basic_metadata['views_last_month'],
            'views_last_week': basic_metadata['views_last_week'],
            'views_total': basic_metadata['views_total'],
            'current_date': strftime("%x"),
            'current_time': strftime("%X"),
            'source': stream_url,
        }
		
    def __str__(self):
        return dumps(self.info_dict, indent=4, sort_keys=True) + '\n'
	
    def save_to_file_oneline(self, file_desc):
        jstr = dumps(self.info_dict, sort_keys=True) + '\n'
        file_desc.write(jstr)
		
    def save_to_file_pretty(self, file_desc):
        jstr = dumps(self.info_dict, indent=4, sort_keys=True) + '\n'
        file_desc.write(jstr)
		
				
def get_metadata(dailym, video_id):
    fields = {
        'id', 'title', 'thumbnail_url', 'tags', 'owner.id',
        'allow_comments', 'comments_total', 'bookmarks_total',
        'available_formats', 'views_last_day', 'views_last_hour',
        'views_last_month', 'views_last_week', 'views_total',
        'country', 'created_time', 'duration', 'embed_url',
        'filmstrip_60_url','language', 'description',
        'sprite_320x_url', 'aspect_ratio', 'url',
		
    }
    try:
        response = dailym.get('/video/{}'.format(video_id), {'fields': ','.join(fields)})
    except Exception:
        return None
    return response
	
		
def get_stream_url(embed_url, ydl_p):
    try:
        info = ydl_p.extract_info(embed_url, download=False)
    except Exception:
        return None
    return info['url']
	

def get_video_meta(dailymotion_id_file, dest_file):
    dailymot = Dailymotion()
    ydl = YoutubeDL({ 'quiet': 'True',})
	
    nameid_list = []
    with open(dailymotion_id_file, "r") as csvfile:
        r = reader(csvfile)
        for row in r:
            nameid_list.append(row[1])
    nameid_list.pop(0)
	
    with open(dest_file, "w") as f:
        for id in nameid_list:
            print "Name: {}".format(id)
            current_page = 1
            for x in xrange(10):
                parameters = {
                    'fields': 'id',
                    'page': str(current_page),
                    'limit': '100',
                }
                try:
                    response = dailymot.get("/user/{}/videos".format(id), parameters)
                except Exception:
                    continue

                if "list" not in response:
                    break
	
                for ele in response['list']:
                    video_id = ele['id']
                    print "Video id: {}".format(video_id)
                    basic_metadata = get_metadata(dailymot, video_id)
                    if basic_metadata is None:
                        continue
                    eurl = basic_metadata['embed_url']
                    stream_url = get_stream_url(eurl, ydl)
                    new_video = DailymotionVideo(basic_metadata, stream_url)
                    new_video.save_to_file_pretty(f)
				
                current_page = current_page + 1
                parameters['page'] = str(current_page)
                has_more = response['has_more']
                if has_more == False:
                    break
                
		
if __name__ == "__main__":
    if not path.exists('../results'):
        makedirs('../results')
    get_video_meta('../data/dailymotion.csv', '../results/dailymotion_res.json')

