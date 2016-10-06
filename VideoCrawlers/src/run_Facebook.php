<?php

session_start();

require_once __DIR__ . '/vendor/autoload.php';

class Crawler {
    /**
     * Path to a file containing metadata from pages.
     *
     * @var string  $page_file
     */
    private $page_file;

    /**
     * Path to a file containing metadata from videos (without extension).
     *
     * @var string $video_file_name
     */
    private $video_file_name;

    /**
     * Extension for the path to a file containing metadata from videos.
     *
     * @var string $video_file_extension
     */
    private $video_file_extension;

    /**
     * Object used for sending requests and getting responses using Facebook Graph API.
     *
     * @var Facebook $fb
     */
    private $fb;

    /**
     * Array that stores metadata from pages.
     *
     * @var array $facebook_pages
     */
    private $facebook_pages;

    /**
     * Array that stores metadata from videos for currently analyzed page.
     *
     * @var array $page_videos
     */
    private $page_videos;

    /**
     * The number of requests after which metadata from videos for currently analyzed
     * page will be saved to file.
     *
     * @var int $max_requests_per_save
     */ 
    private $max_requests_per_save;

    /**
     * Object used for logging.
     *
     * @var Logger $logger
     */
    private $logger;

    /**
     * Array that stores IDs and names of the pages which will be analyzed.
     * 
     * @var array $name_id_array
     */
    private $name_id_array;

    /**
     * Array that stores permitted dates. Only them fulfill the conditions for filtering.
     *
     * @var array $condition_array
     */
    private $condition_array;

    /**
     * The total number of metadata from videos successfully obtained during crawling.
     *
     * @var int $total_videos
     */
    private $total_videos;

    /**
     * @brief Constructor.
     *
     * @param string $page_file           Path to a file where metadata from pages will be saved.
     * @param string $video_file          Path to a file where metadata from videos will be saved.
     * @param string $log_dir             Path to a directory where logs will be saved.
     * @param int $max_requests_per_save  The number of requests after which metadata from videos will
     *                                    be saved.
     * @param string $token               The access token for Facebook Graph API.
     */
    public function __construct($page_file, $video_file, $log_dir, $max_requests_per_save, $token) {
        $this->logger = new Katzgrau\KLogger\Logger($log_dir);
        $this->page_file = $page_file;
        $dot_idx = strrpos($video_file, '.');
        $this->video_file_name = substr($video_file, 0, $dot_idx);
        $this->video_file_extension = substr($video_file, $dot_idx);
        $api_id = '';
        $app_secret = '';
        $this->fb = new Facebook\Facebook([
            'app_id' => $api_id,
            'app_secret' => $app_secret,
            'default_graph_version' => 'v2.7',
        ]);
        $oAuth2Client = $this->fb->getOAuth2Client();
        $longLivedAccessToken = $oAuth2Client->getLongLivedAccessToken($token);
        $this->fb->setDefaultAccessToken($longLivedAccessToken);
        $this->facebook_pages = array();
        $this->page_videos = array();
        $this->name_id_array = array();
        $this->condition_array = array('2016-08', '2016-07', '2016-06');
        $this->max_requests_per_save = $max_requests_per_save;
        $this->total_videos = 0;
    }

    /**
     * @brief Adds IDs and names of the pages to be analyzed.
     * 
     * @param string $csv_file            Path to a csv file with IDs and names of the pages.
     */
    public function add_content_providers($csv_file) {
        $f = @fopen($csv_file, 'r');
        if(!$f) {
            throw new Exception('Can not read data from file: ' . $csv_file);
        }
        $data = fgetcsv($f);
        while (($data = fgetcsv($f)) !== FALSE) {
            array_push($this->name_id_array, $data[1]);
        }
        fclose($f);
    }

    /**
     * @brief Performs filtering. Checks whether the created time of the video meets the conditions.
     *
     * @param string $created_time        The time when the video was published.
     *
     * @return boolean                    TRUE if video meets the conditions, FALSE otherwise.
     */
    private function perform_filtering($created_time) {
        $date = substr($created_time, 0, 7);
        if(in_array($date, $this->condition_array)) {
            return TRUE;
        }
        return FALSE;
    }

    /**
     * @brief Gets metadata from page.
     * @details Metadata obtained from page: 'id', 'name', 'description', 'category', 'category_list', 'fan_count',
     * 'talking_about_count' and 'about'.
     *
     * @param string $page                ID or name of the page.
     *
     * @return array                      The array with basic page informations (keys: 'page_name_id', 'page_name',
     *                                    'page_likes').
     */
    private function analyze_page($page) {
        $fields = '?fields=id,name,description,about,category,category_list,fan_count,talking_about_count';
        $page_request = $this->fb->request('GET', '/' . $page . $fields);
        try {
            $page_response = $this->fb->getClient()->sendRequest($page_request);
        }
        catch(Exception $e) {
            throw new Exception('Request for page id ' . $page . ' failed: ' . $e->getMessage());
        }
        $page_response = $page_response->getGraphNode();
        $page_response = json_decode($page_response, true);
        $page_response['page_name_id'] = $page;
        array_push($this->facebook_pages, $page_response);
        $j_str = json_encode($this->facebook_pages, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        $res = @file_put_contents($this->page_file, $j_str);
        if(!$res) {
            throw new Exception('Can not save facebook pages to file.');
        }
        $page_info = array();
        $page_info['page_name_id'] = $page;
        $page_info['page_name'] = $page_response['name'];
        $page_info['page_likes'] = $page_response['fan_count'];
        return $page_info;
    }

    /**
     * @brief Saves metadata from videos for currently analyzed page to a file.
     *
     * @param string $video_file          Path to a file where metadata from videos for currently analyzed
     *                                    page will be saved.
     * @param int $total_page_videos      The number of metadata from videos successfully obtained
     *                                    for currently analyzed page.
     */
    private function save_videos($video_file, $total_page_videos) {
        $this->logger->info('Saving to file...');
        $this->logger->info('Total page videos: ' . $total_page_videos);
        $j_str = json_encode($this->page_videos, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        $res = @file_put_contents($video_file, $j_str);
        if(!$res) {
            throw new Exception('Can not save videos to file.');
        }
        $this->logger->info('Saving finished.');
    }

    /**
     * @brief Gets metadata from videos.
     * @details Metadata obtained from video: 'content_category', 'backdated_time', 'backdated_time_granularity',
     * 'created_time', 'description', 'event', 'from', 'id', 'length', 'permalink_url', 'picture',
     * 'place', 'scheduled_publish_time', 'source', 'title', 'captions', 'updated_time', 'tags',
     * 'thumbnails'.
     *
     * @param string $page                The page from which videos will be analyzed.
     * @param array $page_info            The array with basic page informations (keys: 'page_name_id', 'page_name',
     *                                    'page_likes').
     *
     */
    private function analyze_page_videos($page, $page_info) {
        $this->page_videos = array();
        $integrity_array = array();
        $video_file = $this->video_file_name . '_' . $page . $this->video_file_extension;
        $request_counter = 0;
        $total_page_videos = 0;
        $fields = '/videos?fields=content_category,backdated_time,backdated_time_granularity,created_time,'
        . 'description,event,from,id,length,permalink_url,picture,place,scheduled_publish_time,source,'
        . 'title,captions,updated_time,tags,thumbnails';
        $video_request = $this->fb->request('GET', '/' . $page . $fields);
        try {
            $video_response = $this->fb->getClient()->sendRequest($video_request);
        }
        catch(Exception $e) {
            $this->logger->error('Request for video data from page: ' . $page . ' failed: ' . $e->getMessage());
            return;
        }
        $video_response = $video_response->getGraphEdge();
        while(!is_null($video_response)) {
            $request_counter += 1;
            $video_data = json_decode($video_response, true);
            foreach($video_data as $video_d) {
                if(Crawler::perform_filtering($video_d['created_time']['date'])) {
                    if(in_array($video_d['id'], $integrity_array)) {
                        continue;
                    }
                    try {
                        array_push($integrity_array, $video_d['id']);
                        $video_stats = $this->get_video_count_stat($video_d['id'], $video_d['permalink_url']);
                        $result_array = array_merge($video_d, $video_stats, $page_info);
                        array_push($this->page_videos, $result_array);
                        $total_page_videos += 1;
                        $this->total_videos += 1;
                    }
                    catch(Exception $e) {
                        $this->logger->error($e->getMessage());
                    }
                }
            }
            if($request_counter == $this->max_requests_per_save) {
                $request_counter = 0;
                $this->save_videos($video_file, $total_page_videos);
            }
            try {
                $video_response = $this->fb->next($video_response);
            }
            catch(Exception $e) {
                $this->logger->error('Can not get next videos from page ' . $page . $e->getMessage());
                break;
            }
        }
        $this->save_videos($video_file, $total_page_videos);
        $this->logger->info('Total videos: ' . $this->total_videos);
    }

    /**
     * @brief Gets the number of views for the post with a video.
     *
     * @param string $url                 The url to the post.
     *
     * @return int                        The number of views for the post.
     */
    private static function get_video_views($url) {
        $c = curl_init();
        curl_setopt($c, CURLOPT_URL, $url);
        curl_setopt($c, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($c, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($c, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($c, CURLOPT_USERAGENT, "Mozilla/5.0");
        curl_setopt($c, CURLOPT_COOKIE, 'CookieName1=Value;');
        curl_setopt($c, CURLOPT_MAXREDIRS, 10);
        $follow_allowed = ( ini_get('open_basedir') || ini_get('safe_mode')) ? false : true;
        if ($follow_allowed) {
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
        if ($status['http_code'] != 200) {
            throw new Exception('Can not get video views count for url ' . $this->url . $e->getMessage());
        }
        $res = preg_match("/>([^>]*)\s(Views)</", $data, $matches);
        if($res == 0) {
            throw new Exception('Pattern not found when looking for views count.');
        }
        try {
            $trash_views = $matches[1];
        }
        catch (Exception $e) {
            throw new Exception('Pattern not found when looking for views count.');
        }
        $arr = str_split($trash_views);
        $views_count = 0;
        for($i = 0; $i < strlen($trash_views); ++$i) {
            if (is_numeric($arr[$i])) {
                $views_count = 10 * $views_count + $arr[$i];
            }
        }
        return $views_count;
    }

    /**
     * @brief Gets video's count statistics.
     * @details Gets video's likes count, comments count, sharedposts count and views count.
     * 
     * @param string $video_id            The id of the video.
     * @param string $video_permalink     The video's permalink url.
     *
     * @return array                      The array with count statistics (keys: 'likesCount', 'commentsCount'
     *                                    'sharedpostsCount' and 'viewsCount').
     */
    private function get_video_count_stat($video_id, $video_permalink) {
        $video_likes_request = $this->fb->request('GET', '/' . $video_id . '/likes', array ('summary' => 1, 'limit' => 0));
        $video_comments_request = $this->fb->request('GET', '/' . $video_id . '/comments', array ('summary' => 1, 'limit' => 0));
        $video_sharedposts_request = $this->fb->request('GET', '/' . $video_id . '/sharedposts', array ('summary' => 1, 'limit' => 0));
        try {
            $video_likes_response = $this->fb->getClient()->sendRequest($video_likes_request)->getGraphEdge()->getTotalCount();
            $video_comments_response = $this->fb->getClient()->sendRequest($video_comments_request)->getGraphEdge()->getTotalCount();
            $video_sharedposts_response = $this->fb->getClient()->sendRequest($video_sharedposts_request)->getGraphEdge()->getTotalCount();
        }
        catch (Exception $e) {
            throw new Exception('Request for video count stats ' . $video_id . ' failed: ' . $e->getMessage());
        }
        $video_stats = array();
        $video_stats['likesCount'] =  $video_likes_response;
        $video_stats['commentsCount'] = $video_comments_response;
        $video_stats['sharedpostsCount'] = $video_sharedposts_response;
        $url = 'https://www.facebook.com' . $video_permalink;
        $video_stats['viewsCount'] = Crawler::get_video_views($url);  
        return $video_stats;
    }

    /**
     * @brief Starts crawling.
     */
    public function start() {
        $this->logger->info('Start crawling.');
        foreach($this->name_id_array as $page) {
            $this->logger->info('Analyzing page: ' . $page);
            try {
                $page_info = $this->analyze_page($page);
                $this->analyze_page_videos($page, $page_info);
            }
            catch(Exception $e) {
                $this->logger->error($e->getMessage());
            }
        }
        $this->logger->info('Crawling finished.');
    }
}

$page_file = '/home/tbochens/VideoCrawlers/results/Facebook/facebook_pages.json';
$video_file = '/home/tbochens/VideoCrawlers/results/Facebook/facebook_videos.json';
$log_dir = '/home/tbochens/VideoCrawlers/logs/facebook_logs';
$content_path = '/home/tbochens/VideoCrawlers/data/facebook_creators.csv';

$token = 'EAAOqXuFK7G8BAEPeqtccJmIoO0BzI97sJQap2lgGVGNE2F6GV6DyavAzvCLrv8npn8MfCb03uQQL1K9M4Khrq'
. 'qQZAk1nL91pY5yP9EqZCz7zivgGnYV6tZAr12qVCyVns8dV68sn0qJZAWrwMqFIXZBi6v1fbIV0FRL03dvDqMAZDZD';

$crawler = new Crawler($page_file, $video_file, $log_dir, 10, $token);
$crawler->add_content_providers($content_path);
$crawler->start();
?>
