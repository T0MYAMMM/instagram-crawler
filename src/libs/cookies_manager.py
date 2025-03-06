from libs.beans import Pusher
from redis import Redis
from libs.exc import NoAvailableResourceException
from config.settings import REDIS, BEANS, PATH
#from sentry_sdk import capture_exception
#from .logger import printerror, printinfo
import requests
import base64
import json
import sys


def get_cookies(filename, allowed_usage, social_media, config='default', save=True, retries=5):
    url = "https://crawlercluster.dashboard.nolimit.id/crawler-resource/fetch"
    params = {
        'allowed_usage': allowed_usage,
        'social_media': social_media,
        'client_id': 'periodic-crawler-worker-01',
        'with_valid_cookies': 'true'
    }
    run = True
    count = 0
    from_file = False
    while run:
        try:
            #printinfo(f'Attempt {count+1}')

            conn_redis = Redis(host=REDIS[config]['host'],
                               port=REDIS[config]['port'], decode_responses=True,
                               password=REDIS[config]['password'])
            #printinfo('Waking up sleeping cookies')
            resp_redis = conn_redis.lpop(
                f'{social_media}_cookie_stock')
            conn_redis.close()
            if resp_redis:
                #printinfo('Sleeping cookies available')
                content = json.loads(resp_redis)
                break
            #else:
                #printinfo('No sleeping cookies available')
            #printinfo('Requesting fresh cookies')
            resp = requests.get(url, params=params)
            content = resp.json()
            if len(content) > 0:
                # with open(f"{PATH['default']['cookiepath'].rstrip('/')}/{filename}.json", 'w') as f:
                #     f.write(json.dumps(content))
                #printinfo('Fresh cookies received')
                run = False
            else:
                count += 1
            if count >= retries:
                raise NoAvailableResourceException(
                    social_media, allowed_usage)
        except NoAvailableResourceException as e:
            run = False
            # capture_exception()
            #printinfo('No fresh cookies available')
            #printinfo('Reading cookies from file')
            with open(f"{PATH['default']['cookiepath'].rstrip('/')}/{filename}.json", 'r') as f:
                content = json.loads(f.read())
                from_file = True
        except Exception as e:
            run = False
            #capture_exception()
            sys.exit()

    if not content:
        raise NoAvailableResourceException(
            social_media, allowed_usage)
    cookies = content[0]['sessionInfo']['cookie']
    for cookie in cookies:
        value: str = cookie['value']
        if value.startswith('base64'):
            cookie['value'] = base64.b64decode(value[7:]).decode()
    resource_id = content[0]['originalId']
    if save:
        conn_redis = Redis(host=REDIS[config]['host'],
                           port=REDIS[config]['port'], decode_responses=True,
                           password=REDIS[config]['password'])
        conn_redis.sadd('cookies_resource', resource_id)
        conn_redis.close()
    user_credential = content[0]['crawlingAccessForm']['userCredential']

    return cookies, resource_id, user_credential, content, from_file


def release_cookies_with_error(resource_id, message='Token is invalid'):
    url = "https://crawlercluster.dashboard.nolimit.id/crawler-resource/error"
    body = {
        "resourceId": resource_id,
        "error": str(message),
        "validity": "invalid"
    }
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, data=json.dumps(body))


def release_cookies(resource_id):
    url = "https://crawlercluster.dashboard.nolimit.id/crawler-resource/release"
    body = {
        "resourceId": resource_id,
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, headers=headers, data=json.dumps(body))


def renew_cookies(credential, config='default'):
    conn_redis = Redis(host=REDIS[config]['host'],
                       port=REDIS[config]['port'], decode_responses=True,
                       password=REDIS[config]['password'])
    message = '{}|{}'.format(credential['username'], credential['password'])
    if not conn_redis.sismember('renew_cookie_instagram', message):
        pusher = Pusher('nolimit_renew_cookie_instagram', BEANS[config]
                        ['host'], BEANS[config]['port'])
        pusher.setJob(message)
        conn_redis.sadd('renew_cookie_instagram', message)
        pusher.close()


def empty_cookie_file(filename):
    with open(f"{PATH['default']['cookiepath'].rstrip('/')}/{filename}.json", 'w') as f:
        f.write("[]")
    #printerror('Cookie file emptied')