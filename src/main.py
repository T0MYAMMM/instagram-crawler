#from libs.beans import Worker
#from workers.worker_instagram import (
#    worker_instagram_account,
#    worker_instagram_comment, worker_instagram_comment_preprocess
#)
#from workers.worker_twitter import WorkerTwitter
#from workers.worker_instagram2 import WorkerInstagram
#from workers.worker_cookie import worker_cookie_instagram, worker_sleeping_cookies
#import sentry_sdk
#from settings import SENTRY
#from sentry_sdk import set_tags

import argparse

if __name__ == '__main__':
    choices = [
        'worker_instagram_keyword',
        'worker_instagram_account_post', 'worker_instagram_comment',
        'worker_instagram_comment_next_page',
        'worker_instagram_account_post_preprocess',
        'worker_instagram_account_post_v2',
        'worker_instagram_account_post_v2_preprocess',
        'worker_instagram_account_post_v2_large_message_preprocess',
        'worker_instagram_comment_preprocess',
        'worker_instagram_comment_v2',
        'worker_instagram_post_detail',
        'worker_instagram_post_detail_preprocess',
        'worker_cookie_instagram',
        'worker_twitter_account',
        'worker_twitter_account_recovery',
        'worker_twitter_keyword',
        'worker_twitter_keyword_recovery',
        'worker_twitter_account_tweets',
        'worker_twitter_account_tweets_preprocess',
        'worker_twitter_account_preprocess', 'worker_twitter_keyword_preprocess',
        'worker_twitter_reply', 'worker_twitter_retweet',
        'worker_sleeping_cookies',
        'worker_twitter_reply_preprocess', 'worker_twitter_retweet_preprocess',
        'worker_twitter_quote', 'worker_twitter_quote_preprocess',
        'worker_twitter_tweet_detail',
        'worker_twitter_tweet_detail_preprocess'
    ]
    parser = argparse.ArgumentParser(description='Worker Facebook',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', '--mode', metavar='', type=str,
                        help='Worker Mode',
                        choices=choices)
    parser.add_argument('--max-page', metavar='', type=int,
                        help='Max page to be crawled',
                        default=20)
    parser.add_argument('-c', '--config', metavar='', type=str,
                        help='Config File', default='default')
    parser.add_argument('--allowed-usage', metavar='', type=str,
                        help='Cookie Allowed Usage', default='for_auto')
    parser.add_argument('--cookie',
                        help='Use Cookie', action='store_true')
    
    parser.set_defaults(cookie=False)
    
    args = parser.parse_args()
    mode = args.mode
    allowed_usage = args.allowed_usage
    config = args.config

    '''
    
    sentry_sdk.init(
        dsn=SENTRY[config]['dsn'],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        environment=SENTRY[config]['env']
    )

    if mode == 'worker_instagram_keyword':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_keyword'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_keyword()
    elif mode == 'worker_instagram_account_post':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_account_post'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_account_post()
        # worker_instagram_account_post(config)
    elif mode == 'worker_instagram_account_post_preprocess':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_account_post_preprocess'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_account_post_preprocess()
    elif mode == 'worker_instagram_post_detail':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_post_detail'})
        worker_instagram = WorkerInstagram(allowed_usage=allowed_usage)
        if args.cookie:
            worker_instagram.worker_instagram_post_detail_cookie()
        else:
            worker_instagram.worker_instagram_post_detail()
    elif mode == 'worker_instagram_post_detail_preprocess':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_post_detail_preprocess'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_post_detail_preprocess()
    elif mode == 'worker_instagram_comment':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_comment'})
        worker_instagram_comment(config)
    elif mode == 'worker_instagram_comment_next_page':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_comment_next_page'})
        worker_instagram_comment(config, next_page=True)
    elif mode == 'worker_instagram_comment_preprocess':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_comment_preprocess'})
        worker_instagram_comment_preprocess(config)
    elif mode == 'worker_instagram_comment_v2':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_comment_v2'})
        worker_instagram = WorkerInstagram(allowed_usage=allowed_usage)
        worker_instagram.worker_instagram_comment_v2()
    elif mode == 'worker_instagram_account_post_v2':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_account_post_v2'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_account_post_v2()
    elif mode == 'worker_instagram_account_post_v2_preprocess':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_account_post_v2_preprocess'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_account_post_v2_preprocess()
    elif mode == 'worker_instagram_account_post_v2_large_message_preprocess':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_instagram_account_post_v2_large_messages_preprocess'})
        worker_instagram = WorkerInstagram()
        worker_instagram.worker_instagram_account_post_v2_large_message_preprocess()
    elif mode == 'worker_cookie_instagram':
        set_tags({'process.social_media': 'instagram',
                 'process.name': 'worker_cookie_instagram'})
        worker_cookie_instagram(config)
    elif mode == 'worker_twitter_account':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_account'})
        # worker_twitter_account(config)
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_account()
    elif mode == 'worker_twitter_account_recovery':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_account_recovery'})
        # worker_twitter_account(config)
        worker_twitter = WorkerTwitter('for_auto')
        worker_twitter.worker_twitter_account_recovery()
    elif mode == 'worker_twitter_keyword_recovery':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_keyword_recovery'})
        # worker_twitter_account(config)
        worker_twitter = WorkerTwitter('for_auto')
        worker_twitter.worker_twitter_keyword_recovery()
    elif mode == 'worker_twitter_keyword':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_keyword'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_keyword(args.max_page)
    elif mode == 'worker_twitter_account_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_account_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_account_preprocess()
    elif mode == 'worker_twitter_keyword_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_keyword_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_keyword_preprocess()
    elif mode == 'worker_twitter_reply':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_reply'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_reply()
    elif mode == 'worker_twitter_retweet':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_retweet'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_retweet()
    elif mode == 'worker_twitter_reply_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_reply_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_reply_preprocess()
    elif mode == 'worker_twitter_retweet_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_retweet_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_retweet_preprocess()
    elif mode == 'worker_twitter_quote':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_quote'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_quote()
    elif mode == 'worker_twitter_quote_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_quote_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_quote_preprocess()
    elif mode == 'worker_twitter_tweet_detail':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_tweet_detail'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_tweet_detail()
    elif mode == 'worker_twitter_tweet_detail_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_tweet_detail_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_tweet_detail_preprocess()
    elif mode == 'worker_twitter_account_tweets':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_account_tweets'})
        worker_twitter = WorkerTwitter(allowed_usage=allowed_usage)
        if args.cookie:
            worker_twitter.worker_twitter_account_tweets_cookie()
        else:
            worker_twitter.worker_twitter_account_tweets()
    elif mode == 'worker_twitter_account_tweets_preprocess':
        set_tags({'process.social_media': 'twitter',
                 'process.name': 'worker_twitter_account_tweets_preprocess'})
        worker_twitter = WorkerTwitter()
        worker_twitter.worker_twitter_account_tweets_preprocess()
    elif mode == 'worker_sleeping_cookies':
        worker_sleeping_cookies(config)'
    
    '''