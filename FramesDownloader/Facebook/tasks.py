from celery import Celery
from os import path
from subprocess import Popen, PIPE, call
import urllib
from os import makedirs

app = Celery('tasks', backend='redis://', broker='amqp://')

@app.task
def do_sample():
    return -1

@app.task
def download_frames(video_id, long_lived_access_token, result_path, source_path):
    source_proc = Popen(['php', source_path, video_id, long_lived_access_token], stdout=PIPE)
    source = source_proc.communicate()[0]
    downloader = urllib.FancyURLopener()
    video_name = '{}.mp4'.format(video_id)
    downloader.retrieve(source, video_name)
    if not path.exists(path.join(result_path, video_id)):
        makedirs(path.join(result_path, video_id))
    frame_names = path.join(result_path, video_id, '{}_%d.jpg'.format(video_id))
    frame_proc = call('ffmpeg -i "{}" -an -sn -vsync 0 -vf select="not(mod(n\,8))" -t 6 "{}"'.format(video_name, frame_names), shell=True)
    rm_proc = call('rm {}'.format(video_name), shell=True)
    return video_id
	
