<?php

require_once __DIR__ . '/vendor/autoload.php';

use Facebook\Facebook;

function get_long_access_token()
{
    $api_id = '';
    $app_secret = '';
    $fb = new Facebook([
        'app_id' => $api_id,
        'app_secret' => $app_secret,
        'default_graph_version' => 'v2.5',
    ]);
    $accessToken = 'EAAOqXuFK7G8BACIRIRijxLRbtxiuuJZAVhxL4dfdOQPSWlqgZBIRrYuXmVDVeZAtooWay2TnDUCvgoccB0QeAgdaY4y6UtMK9n97F6GxB3OIX25gub3Xd7ZA5VCBm1kK0icT7hu6A6gyvqsRsDJYmgvsZClrZBft9FMnsAtCcbMwZDZD';
    $oAuth2Client = $fb->getOAuth2Client();
    $longLivedAccessToken = $oAuth2Client->getLongLivedAccessToken($accessToken);
    return $longLivedAccessToken;
}

$longLivedAccessToken = get_long_access_token();
print($longLivedAccessToken);

?>
