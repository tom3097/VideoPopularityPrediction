import json
import requests
import glob
from time import strftime

HEADERS = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
session = requests.session()
videos_filenames = glob.glob('/home/tbochens/VideoCrawlers/results/FiltYoutube/youtube_video_*.json')

with open('log.txt', 'w') as f:
    pass

# Count total videos 
tot_len = 0
for video_file in videos_filenames:
    with open(video_file, 'r') as v_file:
        tmp = {}
        videos = json.load(v_file)
        tot_len += len(videos)
        for vid in videos:
            tmp[vid['id']] = None
        if len(tmp.items()) != len(videos):
            with open('log.txt', 'w') as l_file:
                l_file.write("Count error in: {}\n".format(video_file))
with open('log.txt', 'w') as l_file:
    l_file.write("Total videos: {}\n".format(tot_len))

# Start downloading thumbnails


total_downloaded = 0
total_failed = 0
try:
    for video_file in videos_filenames:
        vid_number = 0
        failures = 0
        with open('log.txt', 'a') as f:
            f.write('[{}] Start: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), video_file))
        with open(video_file, 'r') as v_file:
            videos = json.load(v_file)
            for vid in videos:
                try:
                    output_filename = '{}.jpg'.format(vid["id"])
                    response = session.get(vid["snippet"]["thumbnails"]['high']["url"], headers=HEADERS)
                    if not response.ok:
                        failures += 1
                        total_failed += 1
                        continue
                    with file(output_filename, "wb") as img_file:
                        img_file.write(response.content)
                    vid_number += 1
                    total_downloaded += 1
                except Exception as e:
                    with open('log.txt', 'a') as f:
                        f.write('[{}] Error: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), str(e)))
        with open('log.txt', 'a') as f:
            f.write('[{}] Finished. Miniatures obtained: {}, Failures: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), vid_number, failures))
    with open('log.txt', 'a') as f:
        f.write('[{}] FINISHED. TOTAL DOWNLOADED: {}, TOTAL FAILED: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), total_downloaded, total_failed))
except Exception as e:
    with open('log.txt', 'a') as f:
        f.write('[{}] Error: {}.\n'.format(strftime('%Y-%m-%d %H:%M:%S'), str(e)))


