<?php

# Requirements:
# Facebook SDK for PHP:
# https://developers.facebook.com/docs/php/gettingstarted -> Installing with Composer (recommended)

require_once __DIR__ . '/vendor/autoload.php';

use Facebook\Facebook;

function get_video_source($videoId, $longLivedAccessToken)
{
    $api_id = '';
    $app_secret = '';
    $fb = new Facebook([
	'app_id' => $api_id,
	'app_secret' => $app_secret,
	'default_graph_version' => 'v2.5',
    ]);
    $oAuth2Client = $fb->getOAuth2Client();
    $fb->setDefaultAccessToken($longLivedAccessToken);

    $fields = '?fields=source';
    $source_request = $fb->request('GET', '/' . $videoId . $fields);
    try
    {
        $source_response = $fb->getClient()->sendRequest($source_request);
    }
    catch(Exception $e)
    {
        return null;
    }
    $graph_node = $source_response->getGraphNode();
    if(!is_null($graph_node))
    {
        $source_data = json_decode($graph_node, true);
        return $source_data['source'];
    }
    return null;
}

$source = get_video_source($argv[1], $argv[2]);
print($source)

?>
