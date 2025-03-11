import json
import logging
import os
import psycopg2
import random
import redis

from datetime import datetime, timedelta
from crawlers import Client
from crawlers.exceptions import LoginRequired

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, pg_conn_params=None, redis_host='localhost', redis_port=6379, session_ttl=3600):
        """
        Initializes the session manager.

        :param redis_host: Redis server hostname.
        :param redis_port: Redis server port.
        :param session_ttl: Session expiration time in seconds (default: 1 hour).
        """
        if pg_conn_params is None:
            self.pg_conn_params = {
                "dbname": "instagram",
                "user": "onm_admin",
                "password": "onmdb",
                "host": "localhost",
                "port": 5432
            }
        else:
            self.pg_conn_params = pg_conn_params

        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password="gbEacMK8vfY5CBV/W5HmN4h9Ype5TgKa6rHBhBGmx5BkoZ/l/AelxJ4inoiohxWz6T6h7tD0E2cTSw/D",
            decode_responses=True
        )
        self.session_ttl = session_ttl
        self.crawler_client = Client()
        self.proxy_list = self.load_proxies()

    def get_random_proxy(self):
        """Returns a random proxy from the list."""
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    def load_proxies(self):
        """Loads proxies from Redis or fallback to a default list."""
        proxies = self.redis_client.lrange("proxy_list", 0, -1)
        if not proxies:
            logger.warning("No proxies found in Redis. Using default proxy list.")
            proxies = ["http://bandung:456xyz@159.223.48.21:2560", "http://nolimit:rahasia123@103.129.220.27:3128", "http://raspi2:kantorxyz@159.223.48.21:2560", "http://raspi1:kantorxyz@159.223.48.21:2560"]
        return proxies

    def get_valid_account(self):
        """Fetches a non-banned Instagram account from PostgreSQL."""
        try:
            with psycopg2.connect(**self.pg_conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT username, password FROM accounts WHERE is_banned = FALSE LIMIT 5;")
                    accounts = cur.fetchall()
                    logger.info(f"Fetched accounts: {len(accounts)}")
                    
                    for username, password in accounts:
                        if not list(self.redis_client.scan_iter(f"session:{username}:*")):
                            return username, password
        except psycopg2.Error as e:
            logger.error(f"Failed to fetch account: {e}")
        return None

    def create_session(self):
        """Creates a new session by logging into Instagram."""
        account = ("portofolionyatom", "641145fs") #self.get_valid_account()
        if not account:
            logger.error("No valid accounts available for login.")
            return {"status": "failed", "message": "No valid accounts available."}

        username, password = account
        proxy = self.get_random_proxy()
        old_session = self.crawler_client.get_settings()
        self.crawler_client.set_settings({})
        self.crawler_client.set_uuids(old_session["uuids"])

        try:
            #self.crawler_client.set_proxy(proxy)
            self.crawler_client.login(username, password)
            session = self.crawler_client.get_settings()
            session["proxy"] = proxy
            session["account"] = { "username": username, "password": password }
            session["created_at"] = datetime.now().isoformat()
            self.redis_client.setex(f"session:{username}", self.session_ttl, json.dumps(session))
            logger.info(f"Session created successfully for {username}")
            return {"status": "success", "username": username, "session": session}
        except LoginRequired:
            logger.warning(f"Login required for account: {username}")
            self.mark_account_banned(username)
            return {"status": "failed", "username": username, "message": "Login required."}
        except Exception as e:
            logger.error(f"Failed to log in with account {username}: {e}")
            return {"status": "failed", "username": username, "message": str(e)}

    def get_active_session(self):
        """Retrieves an active session from Redis or creates a new one if expired."""
        for key in self.redis_client.scan_iter("session:*"):
            session_data = json.loads(self.redis_client.get(key))
            created_at = datetime.fromisoformat(session_data["created_at"])
            if datetime.now() - created_at < timedelta(seconds=self.session_ttl):
                logger.info(f"Using active session for {key.split(':')[1]}")
                return {"status": "success", "session": session_data}
        
        logger.info("No active session found. Creating a new session.")
        return self.create_session()
    
    def mark_account_banned(self, username):
        """Marks an account as banned in the database."""
        try:
            with psycopg2.connect(**self.pg_conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE accounts SET is_banned = TRUE WHERE username = %s", (username,))
                    conn.commit()
                    logger.info(f"Marked account {username} as banned.")
        except psycopg2.Error as e:
            logger.error(f"Failed to mark account {username} as banned: {e}")

if __name__ == "__main__":
    session_manager = SessionManager()
    session = session_manager.get_active_session()
    if session["status"] == "failed":
        logger.error("Failed to create a valid session. Job needs to be re-evaluated.")
    else:
        logger.info("Session ready for use.")
