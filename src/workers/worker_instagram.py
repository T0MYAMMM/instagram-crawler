from datetime import datetime, timedelta
from ssl import SSLError
from libs.beans import Worker, Pusher
from libs.cookies_manager import (
    get_cookies, release_cookies,
    release_cookies_with_error, renew_cookies)
from libs.exc import HTTPStatusException, InvalidCookieException
from libs.kafka_helpers import publish_kafka
from libs.logger import printerror, printinfo
#from libs.runsingle import process_runsingle
from libs.proxies import get_proxy_cycle
#from libs.playwright_helpers import get_context_cycle, get_next_context
from redis import Redis
from playwright.sync_api import Error
from libs.graceful_killer import GracefulKiller
from requests.exceptions import ProxyError, ConnectionError
#from services.service_instagram import (
#    crawl_comment2, crawl_post, crawl_comment,
#    crawl_hashtag
#)
#from services.service_general import store_raw
from config.settings import BEANS, REDIS, PATH
#from sentry_sdk import capture_exception
from time import sleep, time
from urllib.parse import urlparse
import json
import os
import socket
import subprocess
import sys
import traceback


HOSTNAME = socket.gethostname()

def get_next_proxy(proxies, conn_redis: Redis):
    run = True
    while run:
        _next = next(proxies)
        cooldown_until = conn_redis.get('instagram_proxy_cooldown:{}'.format(
            _next['redis-key']))
        if cooldown_until:
            cooldown_until = int(cooldown_until)
        else:
            cooldown_until = 0
        if cooldown_until == 0 or cooldown_until < int(time()):
            run = False
    return _next

def worker_instagram_account_post(config='default'):
    
    conn_redis = Redis(
        host=REDIS[config]['host'],
        port=REDIS[config]['port'], decode_responses=True,
        password=REDIS[config]['password']
    )

    tubename = 'nolimit_crawler_instagram_account_post'
    worker = Worker(tubename, BEANS[config]['host'], BEANS[config]['port'])
    pusher = Pusher('nolimit_crawler_instagram_account_post_preprocess',
                    BEANS[config]['host'], BEANS[config]['port'])
    
    proxy_cycle = get_proxy_cycle()
    killer = GracefulKiller()
    
    while not killer.kill_now:
        job = worker.getJob()
        if job:
            try:
                proxy = get_next_proxy(proxy_cycle, conn_redis)
                _id = job.body
                printinfo(f'Processing Account ID: {_id}')
                resp = crawl_post(_id, proxies=proxy)
                if 300 > resp.status_code >= 200:
                    fname = store_raw(resp, prefix='ig-post',
                                      account_id=_id, host=HOSTNAME)
                    printinfo('Save to: {}'.format(fname))
                    pusher.setJob(fname)
                    worker.deleteJob(job)
                    conn_redis.srem(tubename, job.body)
                    conn_redis.hset('instagram_account:{}'.format(
                        _id), 'last_crawled', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    raise HTTPStatusException(resp.status_code,
                                              'Account ID: {}'.format(_id))
            except Error as e:
                printerror('-------------------')
                printerror(e.message)
                if 'socket' in e.message or 'Socket' in e.message \
                        or 'Request timed out' in e.message:
                    printerror(proxy['https'])
                    worker.releaseJob(job)
                elif 'ECONNREFUSED' in e.message:
                    capture_exception()
                    worker.releaseJob(job)
                else:
                    capture_exception()
                    worker.buryJob(job)
            except HTTPStatusException as e:
                printerror('-------------------')
                printerror(str(e))
                printerror(proxy['https'])
                if e.status == 401:  # IP blocked
                    worker.releaseJob(job)
                    conn_redis.set('instagram_proxy_cooldown:{}'.format(proxy['redis-key']),
                                   int((datetime.now()+timedelta(minutes=10)).timestamp()))
                    conn_redis.expire('instagram_proxy_cooldown:{}'.format(
                        proxy['redis-key']), 600, nx=True)
                else:
                    worker.buryJob(job)
                    capture_exception()
            except (ProxyError, SSLError, ConnectionError) as e:
                worker.releaseJob(job)
                printerror(str(e))
                printerror(proxy['https'])
                capture_exception()
            except Exception as e:
                printerror('-------------------')
                printerror(str(e))
                worker.buryJob(job)
                capture_exception()

def worker_instagram_comment(config='default', next_page=False):
    conn_redis = Redis(host=REDIS[config]['host'],
                       port=REDIS[config]['port'], decode_responses=True,
                       password=REDIS[config]['password'])
    tubename = 'nolimit_crawler_instagram_comment'
    if next_page:
        tubename += '_next_page'
    worker = Worker(tubename, BEANS[config]
                    ['host'], BEANS[config]['port'])
    pusher = Pusher('nolimit_crawler_instagram_comment_preprocess', BEANS[config]
                    ['host'], BEANS[config]['port'])
    printinfo('Requesting Cookies')
    cookies, resource_id, user_credential, complete_cookie, from_file = get_cookies(
        'cookies_instagram_comment', 'for_auto', 'instagram')
    proxy_cycle = get_proxy_cycle()
    killer = GracefulKiller()
    while not killer.kill_now:
        job = worker.getJob(timeout=5)
        if job:
            try:
                proxy = get_next_proxy(proxy_cycle, conn_redis)
                shortcode_id, account_id, post_id = job.body.split('|')
                printinfo(f'Processing Post ID: {shortcode_id}')
                after = None
                if next_page:
                    after = conn_redis.get('instagram_post:end_cursor:{}'.format(
                        shortcode_id))
                resp = crawl_comment2(
                    shortcode_id, proxies=proxy, cookie=cookies, after=after)
                if 300 > resp.status_code >= 200:
                    fname = store_raw(resp, prefix='ig-comment', account_id=account_id,
                                      host=HOSTNAME, post_id=post_id,
                                      shortcode_id=shortcode_id, cookie=complete_cookie)
                    printinfo('Save to: {}'.format(fname))
                    pusher.setJob(fname)
                    worker.deleteJob(job)
                    conn_redis.srem(tubename, job.body)
                elif resp.status_code == 401:
                    raise InvalidCookieException(resource_id)
                else:
                    raise HTTPStatusException(resp.status_code,
                                              'Post ID: {}'.format(shortcode_id))
            except HTTPStatusException as e:
                printerror('-------------------')
                printerror(str(e))
                worker.buryJob(job)
                printerror('Releasing Cookie Resource with Error')
                release_cookies_with_error(resource_id)
                printerror('Resource: ' + resource_id + ' released')
                renew_cookies(user_credential)
                capture_exception()
                sys.exit()
            except (ProxyError, SSLError, ConnectionError) as e:
                worker.releaseJob(job)
                printerror(str(e))
                printerror(proxy['https'])
                capture_exception()
            except InvalidCookieException as e:
                printerror('Releasing Cookie Resource with Error')
                release_cookies_with_error(resource_id)
                printerror('Resource: ' + resource_id + ' released')
                worker.releaseJob(job)
                capture_exception()
                killer.kill_now = True
            except Exception as e:
                printerror('-------------------')
                printerror(type(e).__name__, str(e))
                capture_exception()
                worker.buryJob(job)
    printerror('Releasing Cookie Resource')
    release_cookies(resource_id)
    printerror('Resource: ' + resource_id + ' released')

def worker_instagram_tags(config='default'):
    
    conn_redis = Redis(
        host=REDIS[config]['host'],
        port=REDIS[config]['port'], decode_responses=True,
        password=REDIS[config]['password']
    )

    tubename = 'nolimit_crawler_instagram_hashtag'
    worker = Worker(tubename, BEANS[config]['host'], BEANS[config]['port'])
    pusher = Pusher('nolimit_crawler_instagram_account_post_preprocess',
                    BEANS[config]['host'], BEANS[config]['port'])
    
    proxy_cycle = get_proxy_cycle()
    killer = GracefulKiller()
    
    while not killer.kill_now:
        job = worker.getJob()
        if job:
            try:
                proxy = get_next_proxy(proxy_cycle, conn_redis)
                _id = job.body
                printinfo(f'Processing Account ID: {_id}')
                #resp = crawl_post(_id, proxies=proxy)
                
                
                
                
                if 300 > resp.status_code >= 200:
                    fname = store_raw(resp, prefix='ig-post',
                                      account_id=_id, host=HOSTNAME)
                    printinfo('Save to: {}'.format(fname))
                    pusher.setJob(fname)
                    worker.deleteJob(job)
                    conn_redis.srem(tubename, job.body)
                    conn_redis.hset('instagram_account:{}'.format(
                        _id), 'last_crawled', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    raise HTTPStatusException(resp.status_code,
                                              'Account ID: {}'.format(_id))
            except Error as e:
                printerror('-------------------')
                printerror(e.message)
                if 'socket' in e.message or 'Socket' in e.message \
                        or 'Request timed out' in e.message:
                    printerror(proxy['https'])
                    worker.releaseJob(job)
                elif 'ECONNREFUSED' in e.message:
                    capture_exception()
                    worker.releaseJob(job)
                else:
                    capture_exception()
                    worker.buryJob(job)
            except HTTPStatusException as e:
                printerror('-------------------')
                printerror(str(e))
                printerror(proxy['https'])
                if e.status == 401:  # IP blocked
                    worker.releaseJob(job)
                    conn_redis.set('instagram_proxy_cooldown:{}'.format(proxy['redis-key']),
                                   int((datetime.now()+timedelta(minutes=10)).timestamp()))
                    conn_redis.expire('instagram_proxy_cooldown:{}'.format(
                        proxy['redis-key']), 600, nx=True)
                else:
                    worker.buryJob(job)
                    capture_exception()
            except (ProxyError, SSLError, ConnectionError) as e:
                worker.releaseJob(job)
                printerror(str(e))
                printerror(proxy['https'])
                capture_exception()
            except Exception as e:
                printerror('-------------------')
                printerror(str(e))
                worker.buryJob(job)
                capture_exception()

