<?php

# Requirements:
# Facebook SDK for PHP:
# https://developers.facebook.com/docs/php/gettingstarted -> Installing with Composer (recommended)

ini_set('max_execution_time', 36000);

session_start();

require_once __DIR__ . '/vendor/autoload.php';

use Facebook\Facebook;
use Facebook\FacebookRequest;
use Facebook\Exceptions\FacebookResponseException;
use Facebook\Exceptions\FacebookSDKException;

# Fill in api_id, app_secret and access token
$api_id = '';
$app_secret = '';

class FacebookVideo
{
	private $info_array = array(
		'id' => '',
		'title' => '',
		'content_category' => '',
		'length' => '',
		'source' => '',
		'created_time' => '',
		'thumbnails' => '',
		'commentsCount' => '',
		'likesCount' => '',
		'sharedpostsCount' => '',
		'viewCount' => '',
		'backdated_time' => '',
		'backdated_time_granularity' => '',
		'description' => '',
		'event' => '',
		'from' => '',
		'permalink_url' => '',
		'picture' => '',
		'place' => '',
		'scheduled_publish_time' => '',
		'captions' => '',
		'updated_time' => '',
		'date' => '',
	);

	function __construct($video_info, $statistics)
	{
		$this->info_array['date'] = getdate();
		$this->info_array['id'] = array_key_exists('id', $video_info) ? $video_info['id'] : 'None';
		$this->info_array['title'] = array_key_exists('title', $video_info) ? $video_info['title'] : 'None';
		$this->info_array['content_category'] = array_key_exists('content_category', $video_info) ? $video_info['content_category'] : 'None';
		$this->info_array['length'] = array_key_exists('length', $video_info) ? $video_info['length'] : 'None';
		$this->info_array['source'] = array_key_exists('source', $video_info) ? $video_info['source'] : 'None';
		$this->info_array['created_time'] = array_key_exists('created_time', $video_info) ? $video_info['created_time'] : 'None';
		$this->info_array['thumbnails'] = array_key_exists('thumbnails', $video_info) ? $video_info : 'None';
		$this->info_array['commentsCount'] = array_key_exists('commentsCount', $statistics) ? $statistics['commentsCount'] : 'None';
		$this->info_array['likesCount'] = array_key_exists('likesCount', $statistics) ? $statistics['likesCount'] : 'None';
		$this->info_array['sharedpostsCount'] = array_key_exists('sharedpostsCount', $statistics) ? $statistics['sharedpostsCount'] : 'None';
		$this->info_array['viewCount'] = array_key_exists('viewCount', $statistics) ? $statistics['viewCount']: 'None';
		$this->info_array['backdated_time'] = array_key_exists('backdated_time', $video_info) ? $video_info['backdated_time'] : 'None';
		$this->info_array['backdated_time_granularity'] = array_key_exists('backdated_time_granularity', $video_info) ? $video_info['backdated_time_granularity'] : 'None';
		$this->info_array['description'] = array_key_exists('description', $video_info) ? $video_info['description'] : 'None';
		$this->info_array['event'] = array_key_exists('event', $video_info) ? $video_info['event'] : 'None';
		$this->info_array['from'] = array_key_exists('from', $video_info) ? $video_info['from'] : 'None';
		$this->info_array['permalink_url'] = array_key_exists('permalink_url', $video_info) ? $video_info['permalink_url'] : 'None';
		$this->info_array['picture'] = array_key_exists('picture', $video_info) ? $video_info['picture'] : 'None';
		$this->info_array['place'] = array_key_exists('place', $video_info) ? $video_info['place'] : 'None';
		$this->info_array['scheduled_publish_time'] = array_key_exists('scheduled_publish_time', $video_info) ? $video_info['scheduled_publish_time'] : 'None';
		$this->info_array['captions'] = array_key_exists('captions', $video_info) ? $video_info['captions'] : 'None';
		$this->info_array['updated_time'] = array_key_exists('updated_time', $video_info) ? $video_info['updated_time'] : 'None';
	}
	
	function print()
	{
		$json_string = json_encode($this->info_array, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
		echo $json_string, PHP_EOL;
	}
	
	function save_to_file_pretty($file_descriptor)
	{
		$json_string = json_encode($this->info_array, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
		fwrite($file_descriptor, $json_string . PHP_EOL);
	}
	
	function save_to_file_oneline($file_descriptor)
	{
		$json_string = json_encode($this->info_array, JSON_UNESCAPED_SLASHES);
		fwrite($file_descriptor, $json_string . PHP_EOL);
	}
}

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
	curl_setopt($c, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 6.1; rv:33.0) Gecko/20100101 Firefox/33.0");
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
	
	$res = preg_match("/>([^>]*)\s((wy..wietle..)|(wy..wietlenia))/", $data, $matches);
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
	
	# Translating encoded string to integer
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

if (!file_exists('../results'))
{
    mkdir('../results', 0777, true);
}

$fb = new Facebook([
	'app_id' => $api_id,
	'app_secret' => $app_secret,
	'default_graph_version' => 'v2.5',
]);

$helper = $fb->getRedirectLoginHelper();
try
{
	$accessToken = $helper->getAccessToken();
}
catch(Facebook\Exceptions\FacebookResponseException $e)
{
	echo 'Graph returned an error: ' . $e->getMessage(), PHP_EOL;
	exit;
}
catch(Facebook\Exceptions\FacebookSDKException $e)
{
	echo 'Facebook SDK returned an error: ' . $e->getMessage(), PHP_EOL;
	exit;
}

if(!isset($accessToken))
{
	# Access Token can be obtained here: https://developers.facebook.com/tools-and-support/ -> Tools -> Graph Api Explorer -> Get Token -> Get User Token
	$accessToken = '';
}

# Exchanging short-live access token to long-live one
$oAuth2Client = $fb->getOAuth2Client();
$longLivedAccessToken = $oAuth2Client->getLongLivedAccessToken($accessToken);
$fb->setDefaultAccessToken($longLivedAccessToken);

$pages_ids = [];

$creators_desc = fopen('../data/facebook_creators.csv', 'r');

# First line = creator, facebook_id
$data = fgetcsv($creators_desc);

while (($data = fgetcsv($creators_desc)) !== FALSE)
{
	array_push($pages_ids, $data[1]);
}

$f_desc = fopen('../results/facebook_res.json', 'w');

$max_page = 50;

$unsupported_pages = 0;
$unsupported_videos = 0;
$unsupported_next = 0;
foreach ($pages_ids as $p_id)
{
	echo 'Analyzing page ID: ' . $p_id, PHP_EOL;
	
	$pages_counter = 0;
	
	$request_videos_list = $fb->request('GET','/' . $p_id . '/videos', ['limit' => 20]);
	
	try
	{
		$response_videos_list = $fb->getClient()->sendRequest($request_videos_list);
	}
	catch(FacebookResponseException $e)
	{
		echo 'Graph returned an error: ' . $e->getMessage(), PHP_EOL;
		$unsupported_pages = $unsupported_pages + 1;
		continue;
	}
	catch(FacebookSDKException $e)
	{
		echo 'Facebook SDK returned an error: ' . $e->getMessage(), PHP_EOL;
		$unsupported_pages = $unsupported_pages + 1;
		continue;
	}
	
	$videos_list = $response_videos_list->getGraphEdge();
	
	
	while($videos_list and $pages_counter < $max_page)
	{
		$videos_ids = [];
		foreach ($videos_list as $v_unit)
		{
			array_push($videos_ids, $v_unit['id']);
		}
		
		foreach($videos_ids as $v_id)
		{
			echo 'Video ID: ' . $v_id, PHP_EOL;
			
			$fields = '?fields=content_category,backdated_time,backdated_time_granularity,created_time,description,event,from,id,length,permalink_url,picture,place,scheduled_publish_time,source,title,captions,updated_time,comments,likes,sharedposts,tags,thumbnails';
			# Getting all info about current video and saving
			$request_video_info = $fb->request('GET', '/' . $v_id . $fields);
			$request_video_likes = $fb->request('GET', '/' . $v_id . '/likes', array ('summary' => 1, 'limit' => 0));
			$request_video_comments = $fb->request('GET', '/' . $v_id . '/comments', array ('summary' => 1, 'limit' => 0));
			$request_video_sharedposts = $fb->request('GET', '/' . $v_id . '/sharedposts', array ('summary' => 1, 'limit' => 0));
			
			try
			{
				$response_video_info = $fb->getClient()->sendRequest($request_video_info);
				$response_video_likes = $fb->getClient()->sendRequest($request_video_likes);
				$response_video_comments = $fb->getClient()->sendRequest($request_video_comments);
				$response_video_sharedposts = $fb->getClient()->sendRequest($request_video_sharedposts);
			}
			catch(FacebookResponseException $e)
			{
				echo 'Graph returned an error: ' . $e->getMessage(), PHP_EOL;
				$unsupported_videos = $unsupported_videos + 1;
				continue;
			}
			catch(FacebookSDKException $e)
			{
				echo 'Facebook SDK returned an error: ' . $e->getMessage(), PHP_EOL;
				$unsupported_videos = $unsupported_videos + 1;
				continue;
			}
						
			$vid_info = $response_video_info->getGraphNode();
			$vid_info = json_decode($vid_info, true);
			
			$url = 'https://www.facebook.com' . $vid_info['permalink_url'];
			$viewCount = get_view_count($url);
			
			$stat = array(
				'commentsCount' => $response_video_comments->getGraphEdge()->getTotalCount(),
				'likesCount' => $response_video_likes->getGraphEdge()->getTotalCount(),
				'sharedpostsCount' => $response_video_sharedposts->getGraphEdge()->getTotalCount(),
				'viewCount' => $viewCount,
			);
			
			$new_facebook_video = new FacebookVideo($vid_info, $stat);
			$new_facebook_video->save_to_file_pretty($f_desc);
		}
		$pages_counter = $pages_counter + 1;
		
		try
		{
			$videos_list = $fb->next($videos_list);
		}
		catch(FacebookResponseException $e)
		{
			echo 'Graph returned an error: ' . $e->getMessage(), PHP_EOL;
			$unsupported_next = $unsupported_next + 1;
			continue;
		}
		catch(FacebookSDKException $e)
		{
			echo 'Facebook SDK returned an error: ' . $e->getMessage(), PHP_EOL;
			$unsupported_next = $unsupported_next + 1;
			continue;
		}
	}
}

echo 'FINISHED', PHP_EOL;
echo 'Unsupported pages: ' . strval($unsupported_pages), PHP_EOL;
echo 'Unsupported videos: ' . strval($unsupported_videos), PHP_EOL;
echo 'Unsupported next: ' . strval($unsupported_next), PHP_EOL;

?>