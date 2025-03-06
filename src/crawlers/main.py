from crawlers import Client
from crawlers.exceptions import LoginRequired
from datetime import datetime
from typing import List

import logging 
import json

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

ACCOUNT_USERNAME = "portofolionyatom"
ACCOUNT_PASSWORD = "641145fs"

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
    session = cl.load_settings(session_json_path)

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
    
    print("")

def crawl_hashtag(
    hashtag: str,
    amount: int = 1,
    delay_range: List[int] = [1, 3],
    session_json_path: str = "configs/session.json",
    save_raw: bool = False,
):
    """
    Crawl Instagram posts using a hashtag.
    """
    start_time = datetime.now()
    cl = login_user(ACCOUNT_USERNAME, ACCOUNT_PASSWORD, delay_range, session_json_path)
    hashtag_info = cl.hashtag_info(hashtag)
    hashtag_medias = cl.hashtag_medias_top(hashtag, amount)
    elapsed_time = datetime.now() - start_time

    raw = {
        "raw": {
            "data": {
                "info": hashtag_info,
                "items": hashtag_medias,

            },
            "metadata": {
                "crawltime": elapsed_time.total_seconds(),
                "hashtag": hashtag, 
                "url": cl.hashtag_medias_v1_url.format(name=hashtag),
            }
        }
    }

    if save_raw:
        fname_timestamp = start_time.strftime("%Y-%m-%s_%H:%M:%S")
        with open(f"{hashtag}_{fname_timestamp}.json", "w") as f:
            json.dump(raw, f, indent=4)

    return hashtag_medias

if __name__ == "__main__":
    #cl = login_user(ACCOUNT_USERNAME, ACCOUNT_PASSWORD, session_json_path="session.json")
    #user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
    #medias = cl.user_medias(user_id, 20)
    #hashtag_medias = cl.fbsearch_topserp('#nolimitindonesia')
    #hashtag_medias = cl.hashtag_medias_top('nolimitindonesia', amount=1)
    
    hashtag_medias = crawl_hashtag('nolimitindonesia', amount=1, session_json_path="session.json", save_raw=True)
    
    #hashtag_medias_recent = cl.hashtag_medias_recent('nolimit')
    #with open("hashtag_new.json", "w") as f:
    #    json.dump(hashtag_medias, f, indent=4)

