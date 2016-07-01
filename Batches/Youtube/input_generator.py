#!/usr/bin/env python2

import math
import json
import glob
from pprint import pprint
import random

RANGES_NUMBER = 2
TRAIN_PROPORTION = 0.8

train_output = 'train_2.txt'
val_output = 'val_2.txt'

ranges_filename = '/home/tbochens/CNN/Split/binarySplit.json'
channels_filename = '/home/tbochens/VideoCrawlers/results/Youtube/youtube_channels.json'
videos_filenames = glob.glob('/home/tbochens/VideoCrawlers/results/FiltYoutube/youtube_video_*.json')

ranges = {}
with open(ranges_filename, 'r') as r_file:
    ranges = json.load(r_file)

followers = {}
with open(channels_filename, 'r') as ch_file:
    channels = json.load(ch_file)
    for chan in channels:
        followers[chan['channel_UC']] = chan['items'][0]['statistics']['subscriberCount']
		
zero_followers = 0
amount = {}
for idx in xrange(RANGES_NUMBER):
    amount[idx] = 0

popularity = {}
for idx in xrange(RANGES_NUMBER):
    popularity[idx] = []
	

for video_file in videos_filenames:
    with open(video_file, 'r') as v_file:
        videos = json.load(v_file)
        for vid in videos:
            name = '{}.jpg'.format(vid['id'])
            view_count = float(vid['statistics']['viewCount'])
            followers_count = float(followers[vid['channel_UC']])
            if followers_count == 0.0:
                zero_followers += 1
                continue
            score = math.log((view_count+1) / followers_count, 2)
            date = vid['snippet']['publishedAt'][:len('yyyy-mm')]
            label = None
            idx = 0
            for idx in xrange(RANGES_NUMBER-1):
                if score <= ranges[date][idx]:
                    label = idx
                    break
                idx += 1
            if label is None:
                label = idx
            amount[label] += 1
            data_line = (name, label)
            popularity[label].append(data_line)

train_list = []
val_list = []
for idx in xrange(RANGES_NUMBER):
    random.shuffle(popularity[idx])
    list_len = len(popularity[idx])
    train_end = int(TRAIN_PROPORTION * list_len)
    train_list.extend(popularity[idx][:train_end])
    val_list.extend(popularity[idx][train_end:])

random.shuffle(train_list)
random.shuffle(val_list)
	
with open(val_output, 'w') as val_file:
    for data_line in val_list:
        val_file.write("%s %s\n" % (data_line[0], data_line[1]))
		
with open(train_output, 'w') as train_file:
    for data_line in train_list:
        train_file.write("%s %s\n" % (data_line[0], data_line[1])) 


print ("Videos with 0 followers: %s" % zero_followers)
for idx in xrange(RANGES_NUMBER):
    print ("Label: %s, amount: %s" % (idx, amount[idx]))
	
