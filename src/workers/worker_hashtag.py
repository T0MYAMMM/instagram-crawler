from config.settings import BEANS, REDIS, PATH
from crawlers import Client
from crawlers.main import crawl_hashtag, crawl_reels
from crawlers.exceptions import LoginRequired
from datetime import datetime
from libs.beans import Worker, Pusher
from libs.cookies_manager import (
    get_cookies, release_cookies,
    release_cookies_with_error, renew_cookies)
from libs.exc import HTTPStatusException, InvalidCookieException
from libs.kafka_helpers import publish_kafka
from libs.graceful_killer import GracefulKiller
from libs.logger import printinfo, printerror

from typing import List


import logging 
import json

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

ACCOUNT_USERNAME = "xxyib.643"
ACCOUNT_PASSWORD = "643@asem777"

def login_user(
    USERNAME: str = ACCOUNT_USERNAME,
    PASSWORD: str = ACCOUNT_PASSWORD,
    delay_range: List[int] = [1, 3],
    session_json_path: str = "configs/session.json",
):
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """

    cl = Client()
    session = False #cl.load_settings(session_json_path)

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(USERNAME, PASSWORD)

            # check if session is valid
            try:
                cl.get_timeline_feed()
                cl.delay_range = delay_range
                login_via_session = True
                return cl
            
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(USERNAME, PASSWORD)

            login_via_session = True
            cl.delay_range = delay_range
            return cl
        
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                cl.delay_range = delay_range
                login_via_pw = True
                cl.dump_settings("session.json")
                return cl
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")

def save_json(data):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"{now}.json", "w") as f:
        json.dump(data, f, indent=4)

def worker_instagram_hashtag():
    config = 'default'
    tubename = 'nolimit_crawler_instagram_hashtag'
    worker = Worker(tubename, BEANS[config]['host'], BEANS[config]['port'])
    pusher = Pusher('nolimit_crawler_instagram_account_post_preprocess',
                    BEANS[config]['host'], BEANS[config]['port'])
    #cl = login_user()
    #proxy_cycle = get_proxy_cycle()
    killer = GracefulKiller()

    while not killer.kill_now:
        job = worker.getJob()
        if job:
            try:
                #proxy = get_next_proxy(proxy_cycle, conn_redis)
                _id = job.body
                printinfo(f'Processing Account ID: {_id}')
                if _id[0] == '#':
                    _id = _id[1:]
                
                #resp = crawl_post(_id, proxies=proxy)
                #resp = cl.hashtag_medias_top(_id, amount=30)
                resp = crawl_reels(_id, amount=30)
                save_json(resp)
                #if 300 > resp.status_code >= 200:
                #    save_json(resp.json())
                #    worker.deleteJob(job)
                #    published = publish_kafka('ingestion-pipeline_instagram_hashtag_raw',
                #                              resp)
                    #conn_redis.srem(tubename, job.body)
                    #conn_redis.hset('instagram_account:{}'.format(
                    #    _id), 'last_crawled', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                #else:
                #    raise HTTPStatusException(resp.status_code,
                #                              'Account ID: {}'.format(_id))
            except Exception as e:
                print(f"Error: {e}")

        break
            
'''
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

'''
        
if __name__ == "__main__":
    worker_instagram_hashtag()
        