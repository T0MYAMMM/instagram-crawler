# Instagram Crawler

This project is an Instagram crawler designed to automate various tasks such as fetching posts, comments, and other data from Instagram. It supports multiple modes of operation and can handle different social media platforms.

## Project Structure
. ├── .gitignore
  ├── requirements-test.txt
  ├── requirements.txt
  ├── src/ 
  │ ├── config/ 
  │ │ ├── settings.py 
  │ │ ├── settings.template.py 
  │ ├── crawlers/ 
  │ │ ├── __init__.py 
  │ │ ├── mixins/ 
  │ │ │ ├── auth.py 
  │ │ │ ├── notification.py 
  │ │ │ ├── album.py 
  │ │ │ ├── story.py 
  │ ├── libs/ 
  │ │ ├── cookies_manager.py 
  │ │ ├── exc.py 
  │ ├── main.py 
  │ ├── workers/ 
  │ │ ├── worker_instagram.py 
  │ │ ├── worker_twitter.py 

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/instagram-crawler.git
    cd instagram-crawler
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the crawler, use the [main.py](http://_vscodecontentref_/11) script with the appropriate mode. For example:

```sh
python src/main.py --mode worker_instagram_account_post
```

## Available Modes
worker_instagram_keyword
worker_instagram_account_post
worker_instagram_account_post_preprocess
worker_instagram_post_detail
worker_instagram_post_detail_preprocess
worker_instagram_comment
worker_twitter_quote_preprocess
worker_twitter_tweet_detail
worker_twitter_tweet_detail_preprocess
worker_twitter_account_tweets
worker_twitter_account
worker_twitter_account_recovery


## Configuration
Configuration settings are stored in settings.py. You can create a custom configuration by copying settings.template.py to settings.py and modifying it as needed.

## Error Handling
Custom exceptions are defined in exc.py to handle various error scenarios such as HTTP status errors, invalid cookies, and unavailable resources.