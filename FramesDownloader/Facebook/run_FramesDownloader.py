#!/usr/bin/python

from tasks import do_sample
from tasks import download_frames
from subprocess import Popen, PIPE, call
from os import path
from os import makedirs
import glob
import json
import urllib
import logging
import time

TASK_ARRAY_SIZE = 20

if __name__ == '__main__':
    real_path = path.dirname(path.realpath(__file__))
    real_path = path.join(real_path, '..', '..')
	
    log_path = path.join(real_path, 'logs', 'facebook_log.log')
    result_path = path.join(real_path, 'results', 'Facebook')
    token_path = path.join(real_path, 'src', 'Facebook', 'get_long_access_token.php')
    source_path = path.join(real_path, 'src', 'Facebook', 'get_source.php')
    metadata_path = '/home/tbochens/VideoCrawlers/results/Facebook/facebook_video*'

    logging.basicConfig(filename=log_path,level=logging.DEBUG)
    logger = logging.getLogger(__name__)
	
    # Getting long lived access token
    logger.info('Getting long lived access token')
    token_proc = Popen(['php', token_path], stdout=PIPE)
    llac = token_proc.communicate()[0]
    logger.info('Long lived access token obtained: %s', llac)

    metadata_files = glob.glob(metadata_path)
    for meta_file in metadata_files:
        try:
            # saving video ids
            file_name = meta_file[(meta_file.rfind('/')+1):]
            ids_array = []
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                for element in meta:
                    ids_array.append(element['id'])
            ids_arr_len = len(ids_array)
            logger.info('Analyzing file: %s. Number of videos: %s.', file_name, ids_arr_len)
	except Exception as e:
            logger.error('Error before downloadinf frames from: %s.', meta_file)
            continue	
        # initialize tasks array
        tasks_array = [ None ] * TASK_ARRAY_SIZE
        for i in xrange(TASK_ARRAY_SIZE):
            tasks_array[i] = do_sample.delay()
        
        # downloading frames
        idx = 0
        counter = 0
        finished = False
        while not finished:
            for i in xrange(TASK_ARRAY_SIZE):
                if(tasks_array[i].ready()):
                    try:
                        id = tasks_array[i].get(timeout=1)
                        if id != -1:
                            logger.info('Video id: %s analyzed', id)
                            counter += 1
                            if(counter %20 == 0):
                                logger.info('Total video: %s', counter)
                    except Exception as e:
                        logger.error('Error: %s', str(e))
                    if idx == ids_arr_len:
                        finished = True
                        break
                    tasks_array[i] = download_frames.delay(ids_array[idx], llac, result_path, source_path)
                    idx += 1
            time.sleep(2)
			
        # waiting for the rest to finish downloading frames
        for i in xrange(TASK_ARRAY_SIZE):
            while not tasks_array[i].ready():
                time.sleep(2)
            try:
                id = tasks_array[i].get()
                logger.info('Video id: %s analyzed', id)
                counter += 1
                if(counter %20 == 0):
                    logger.info('Total video: %s', counter)
            except Exception as e:
                logger.error('Error: %s', str(e))

