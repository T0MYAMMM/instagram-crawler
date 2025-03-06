from crawlers import Client
from crawlers.exceptions import LoginRequired
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

if __name__ == "__main__":
    cl = login_user()
    #user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
    #medias = cl.user_medias(user_id, 20)
    print("")
    #hashtag_medias = cl.fbsearch_topserp('#nolimitindonesia')
    hashtag_medias = cl.hashtag_medias_top('nolimitindonesia', amount=10)
    
    #print(hashtag_medias)
    #hashtag_medias_recent = cl.hashtag_medias_recent('nolimit')

    #with open("hashtag_new.json", "w") as f:
    #    json.dump(hashtag_medias, f, indent=4)