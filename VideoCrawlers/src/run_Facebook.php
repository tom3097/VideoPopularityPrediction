<?php

# Requirements:
# Facebook SDK for PHP:
# https://developers.facebook.com/docs/php/gettingstarted -> Installing with Composer (recommended)

session_start();

require_once __DIR__ . '/vendor/autoload.php';

use Facebook\Facebook;

function get_view_count($url, $post_paramtrs = false)
{
    $c = curl_init();
    curl_setopt($c, CURLOPT_URL, $url);
    curl_setopt($c, CURLOPT_RETURNTRANSFER, 1);
    if ($post_paramtrs)
    {
        curl_setopt($c, CURLOPT_POST, TRUE);
        curl_setopt($c, CURLOPT_POSTFIELDS, "var1=bla&" . $post_paramtrs);
    }
    curl_setopt($c, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($c, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($c, CURLOPT_USERAGENT, "Mozilla/5.0");
    curl_setopt($c, CURLOPT_COOKIE, 'CookieName1=Value;');
    curl_setopt($c, CURLOPT_MAXREDIRS, 10);
    $follow_allowed = ( ini_get('open_basedir') || ini_get('safe_mode')) ? false : true;
    if ($follow_allowed)
    {
        curl_setopt($c, CURLOPT_FOLLOWLOCATION, 1);
    }
    curl_setopt($c, CURLOPT_CONNECTTIMEOUT, 9);
    curl_setopt($c, CURLOPT_REFERER, $url);
    curl_setopt($c, CURLOPT_TIMEOUT, 60);
    curl_setopt($c, CURLOPT_AUTOREFERER, true);
    curl_setopt($c, CURLOPT_ENCODING, 'gzip,deflate');
    $data = curl_exec($c);
    $status = curl_getinfo($c);
    curl_close($c);

    if ($status['http_code'] != 200)
    {
        return -1;
    }
	
    $res = preg_match("/>([^>]*)\s(Views)/", $data, $matches);
    if($res == 0)
    {
        return -1;
    }
    try
    {
        $trash_views = $matches[1];
    }
    catch (Exception $e)
    {
        return -1;
    }
	
    $arr = str_split($trash_views);
    $views_count = 0;
    for($i=0; $i<strlen($trash_views); $i++)
    {
        if (is_numeric($arr[$i]))
        {
            $views_count = 10 * $views_count + $arr[$i];
        }
    }
    return $views_count;
}


function read_data_from_csv($id_file, $log_file)
{
    $nameid_list = [];
    $f = @fopen($id_file, 'r');
    if ($f == FALSE)
    {
        $log = '[' . date('j-m-y H:i:s') . '] ERROR File ' . $id_file . ' does not exist: ' . PHP_EOL;
        file_put_contents($log_file, $log, FILE_APPEND);
        return null;
    }
    $data = fgetcsv($f);
    while (($data = fgetcsv($f)) !== FALSE)
    {
        array_push($nameid_list, $data[1]);
    }
    fclose($f);
    return $nameid_list;
}


function get_page_data($fb, $id, $log_file)
{
    $fields = '?fields=likes,id,name';
    $page_request = $fb->request('GET', '/' . $id . $fields, array ('limit' => 100));
    try
    {
        $page_response = $fb->getClient()->sendRequest($page_request);
    }
    catch(Exception $e)
    {
        $log = '[' . date('j-m-y H:i:s') . '] ERROR Request for page id ' . $id . ' FAILED: ' . $e->getMessage() . PHP_EOL;
        file_put_contents($log_file, $log, FILE_APPEND);
        return null;
    }
    return $page_response->getGraphNode();
}


function add_video_count_stat($fb, $videos, $log_file)
{
    $video_list = [];
    foreach($videos as $video)
    {
        $v_id = $video['id'];
        $video_likes_request = $fb->request('GET', '/' . $v_id . '/likes', array ('summary' => 1, 'limit' => 0));
        $video_comments_request = $fb->request('GET', '/' . $v_id . '/comments', array ('summary' => 1, 'limit' => 0));
        $video_sharedposts_request = $fb->request('GET', '/' . $v_id . '/sharedposts', array ('summary' => 1, 'limit' => 0));
        try
        {
            $video_likes_response = $fb->getClient()->sendRequest($video_likes_request)->getGraphEdge()->getTotalCount();
            $video_comments_response = $fb->getClient()->sendRequest($video_comments_request)->getGraphEdge()->getTotalCount();
            $video_sharedposts_response = $fb->getClient()->sendRequest($video_sharedposts_request)->getGraphEdge()->getTotalCount();
        }
        catch(Exception $e)
        {
            $log = '[' . date('j-m-y H:i:s') . '] ERROR while adding stats to video id ' . $video . ': ' . $e->getMessage() . PHP_EOL;
            file_put_contents($log_file, $log, FILE_APPEND);
            return null;
        }
        $video['likesCount'] =  $video_likes_response;
        $video['commentsCount'] = $video_comments_response;
        $video['sharedpostsCount'] = $video_sharedposts_response;
        $link = 'https://www.facebook.com' . $video['permalink_url'];
        $video['viewCount'] = get_view_count($link);
        array_push($video_list, $video);
    }
    return $video_list;
}


function start_crawling($id_file, $log_file, $video_file, $page_file, $initial_number)
{
    # Fill in api_id, app_secret and access token
    $MAX_VIDEOS_PER_FILE = 210000;
    $MAX_REQUESTS_PER_SAVE = 20;
    $api_id = '';
    $app_secret = '';
    $fb = new Facebook([
	'app_id' => $api_id,
	'app_secret' => $app_secret,
	'default_graph_version' => 'v2.5',
    ]);
    $accessToken = 'CAADM7X5FsYYBAN2ZChPKQhN7wVPIgBnEJ9qAR19TnJICjK0i38HfPLCb5Gd6WMOFK2xIwyXT3bfh1nc28H27PDsiz1QdKvlMr5ZC38TGF5eUZCA2tZBYrYwS9hsbk1w1m1e77OLaqB82sfJRgs4vw3D2fj55Sqt1YUk7qwv72Wqn0UrKXmZC1lSIWP4vNXRUx8H4DMZATxJZA29QEclrb8w';
    $oAuth2Client = $fb->getOAuth2Client();
    $longLivedAccessToken = $oAuth2Client->getLongLivedAccessToken($accessToken);
    $fb->setDefaultAccessToken($longLivedAccessToken);
    file_put_contents($log_file, '');
    $dot_idx = strrpos($video_file, '.');
    $video_file_name = substr($video_file, 0, $dot_idx);
    $video_file_format = substr($video_file, $dot_idx);
    $video_file_number = $initial_number;
    $video_file = $video_file_name . '_' . $video_file_number . $video_file_format;
    $nameid_list = read_data_from_csv($id_file, $log_file);
    if (is_null($nameid_list))
    {
        return;
    }
    $facebook_videos = [];
    $facebook_pages = [];
    $requests_counter = 0;
    foreach ($nameid_list as $page_id)
    {
        $page_response = get_page_data($fb, $page_id, $log_file);
        if (is_null($page_response))
        {
            continue;
        }
        $page_response = json_decode($page_response, true);
        $page_response['page_name_id'] = $page_id;
        array_push($facebook_pages, $page_response);
        $j_str = json_encode($facebook_pages, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        $res = @file_put_contents($page_file, $j_str);
        if($res == FALSE)
        {
            $log = '[' . date('j-m-y H:i:s') . '] Save or open to file ' . $page_file . ' FAILED: ' . PHP_EOL;
            file_put_contents($log_file, $log, FILE_APPEND);
            return null;
        }
        $fields = '/videos?fields=content_category,backdated_time,backdated_time_granularity,created_time,description,event,from,id,length,permalink_url,picture,place,scheduled_publish_time,source,title,captions,updated_time,tags,thumbnails';
        $video_request = $fb->request('GET', '/' . $page_id . $fields);
        try
        {
            $video_response = $fb->getClient()->sendRequest($video_request);
        }
        catch(Exception $e)
        {
            $log = '[' . date('j-m-y H:i:s') . '] Request for video data page id ' . $page_id . ' FAILED: ' . $e->getMessage() . PHP_EOL;
            file_put_contents($log_file, $log, FILE_APPEND);
            continue;
        }
        $graph_edge = $video_response->getGraphEdge();
        while (!is_null($graph_edge))
        {
            $videos_data = json_decode($graph_edge, true);
            $videos_data = add_video_count_stat($fb, $videos_data, $log_file);
            foreach ($videos_data as $video_d)
            {
                $video_d['time_date'] = date('j-m-y H:i:s');
                $video_d['page_name_id'] = $page_id;
                array_push($facebook_videos, $video_d);
            }
            $log = '[' . date('j-m-y H:i:s') . '] From ' . $page_id . ' Response size ' . count($videos_data) . ' Videos in list ' . count($facebook_videos) . PHP_EOL;
            file_put_contents($log_file, $log, FILE_APPEND);
            $requests_counter = $requests_counter + 1;
            if ($requests_counter == $MAX_REQUESTS_PER_SAVE)
            {
                $requests_counter = 0;
                $log = '[' . date('j-m-y H:i:s') . '] Saving to file...' . PHP_EOL;
                file_put_contents($log_file, $log, FILE_APPEND);
                $j_str = json_encode($facebook_videos, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
                $res = @file_put_contents($video_file, $j_str);
                if($res == FALSE)
                {
                    $log = '[' . date('j-m-y H:i:s') . '] Save or open to file ' . $video_file . ' FAILED: ' . PHP_EOL;
                    file_put_contents($log_file, $log, FILE_APPEND);
                    return null;
                }
                $log = '[' . date('j-m-y H:i:s') . '] Successfully saved.' . PHP_EOL;
                file_put_contents($log_file, $log, FILE_APPEND);
                if (count($facebook_videos) >= $MAX_VIDEOS_PER_FILE)
                {
                    $log = '[' . date('j-m-y H:i:s') . '] Creating new file.' . PHP_EOL;
                    file_put_contents($log_file, $log, FILE_APPEND);
                    $video_file_number = $video_file_number + 1;
                    $video_file = $video_file_name . '_' . $video_file_number . $video_file_format;
                    $facebook_videos = [];
                }
            }
            try
            {
                $graph_edge = $fb->next($graph_edge);
            }
            catch(Exception $e)
            {
                $log = '[' . date('j-m-y H:i:s') . '] ERROR Response from page id ' . $page_id . ' FAILED: ' . $e->getMessage() . PHP_EOL;
                file_put_contents($log_file, $log, FILE_APPEND);
                break;
            }   
        }
    }
    $log = '[' . date('j-m-y H:i:s') . '] Saving to file...' . PHP_EOL;
    file_put_contents($log_file, $log, FILE_APPEND);
    $j_str = json_encode($facebook_videos, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    $res = @file_put_contents($video_file, $j_str);
    if($res == FALSE)
    {
        $log = '[' . date('j-m-y H:i:s') . '] Save or open to file ' . $video_file . ' FAILED: ' . PHP_EOL;
        file_put_contents($log_file, $log, FILE_APPEND);
        return null;
    }
    $log = '[' . date('j-m-y H:i:s') . '] Successfully saved.' . PHP_EOL;
    file_put_contents($log_file, $log, FILE_APPEND);
}


$r_path = dirname(realpath(__FILE__));
$results_path = $r_path . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'results';
$logs_path = $r_path . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'logs';
if (!file_exists($results_path))
{
    mkdir($results_path, 0777, true);
}
if (!file_exists($logs_path))
{
    mkdir($logs_path, 0777, true);
}
$f_data = $r_path . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'data' . DIRECTORY_SEPARATOR . 'facebook_creators.csv';
$f_logs = $logs_path . DIRECTORY_SEPARATOR . 'facebook_logs.log';
$f_videos = $results_path . DIRECTORY_SEPARATOR . 'facebook_video.json';
$f_pages = $results_path . DIRECTORY_SEPARATOR . 'facebook_pages.json';
$f_initial_number = 1;
start_crawling($f_data, $f_logs, $f_videos, $f_pages, $f_initial_number);

?>