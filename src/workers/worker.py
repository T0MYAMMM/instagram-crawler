import logging
import json
import redis
import psycopg2
import random
from datetime import datetime
from typing import List

from config.settings import BEANS, REDIS
from crawlers import Client
from crawlers.exceptions import LoginRequired
from libs.beans import Worker
from libs.graceful_killer import GracefulKiller
from libs.kafka_helpers import publish_kafka
from workers.session_manager import SessionManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class WorkerInstagram:
    def __init__(self, config: str = 'default'):
        self.config = config
        self.redis_client = redis.StrictRedis(
            host="localhost",
            port="6379",
            password="gbEacMK8vfY5CBV/W5HmN4h9Ype5TgKa6rHBhBGmx5BkoZ/l/AelxJ4inoiohxWz6T6h7tD0E2cTSw/D",
            decode_responses=True
        )
        self.session_manager = SessionManager()
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

    def session_login(self, username: str, password: str, delay_range: List[int] = [1, 3]) -> Client:
        """Attempts to log in using session or credentials."""
        cl = Client()
        cl.delay_range = delay_range

        proxy = self.get_random_proxy()
        #if proxy:
            #cl.set_proxy(proxy)
            #logger.info(f"Using proxy: {proxy}")

        session = self.session_manager.get_active_session()

        login_via_session = False
        login_via_pw = False

        if session and session["status"] != "failed":
            try:
                cl.set_settings(session)
                cl.login(session["session"]["account"]["username"], session["session"]["account"]["password"])
                cl.get_timeline_feed()
                return cl
            except LoginRequired:
                logger.info("Session expired, creating new session.")
                session = self.session_manager.create_session()
                cl.set_settings(session)

        try:
            cl.login(username, password)
            cl.delay_range = delay_range
            return cl
        except Exception as e:
            logger.error(f"Failed to log in: {e}")
            return None

    def crawl_hashtag(self, hashtag: str, cl: Client, amount: int = 30, save_raw: bool = False):
        """Crawl Instagram posts using a hashtag."""
        try:
            start_time = datetime.now()
            hashtag_info = cl.hashtag_info(hashtag)
            hashtag_medias = cl.hashtag_medias_top(hashtag, amount)
            elapsed_time = datetime.now() - start_time

            raw_data = {
                "data": {
                    "info": hashtag_info,
                    "items": hashtag_medias
                },
                "metadata": {
                    "crawltime": elapsed_time.total_seconds(),
                    "hashtag": hashtag,
                    "url": cl.hashtag_medias_v1_url.format(name=hashtag)
                }
            }

            if save_raw:
                self.save_json(hashtag, raw_data)

            return raw_data, True
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            return None, False

    def crawl_reels(self, hashtag: str, cl: Client, amount: int = 30, save_raw: bool = False):
        """Crawl Instagram reels using a hashtag."""
        try:
            start_time = datetime.now()
            hashtag_info = cl.hashtag_info(hashtag)
            reels_medias = cl.hashtag_medias_reels_v1(hashtag, amount)
            elapsed_time = datetime.now() - start_time

            raw_data = {
                "data": {
                    "info": hashtag_info,
                    "items": reels_medias
                },
                "metadata": {
                    "crawltime": elapsed_time.total_seconds(),
                    "hashtag": hashtag,
                    "url": cl.hashtag_medias_v1_url.format(name=hashtag)
                }
            }

            if save_raw:
                self.save_json(hashtag, raw_data)

            return raw_data, True
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            return None, False

    def save_json(self, filename: str, data):
        """Save crawled data to a JSON file."""
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = f"{filename}_{now}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data saved to {filepath}")

    def process_job(self, job, worker, job_type):
        """Process a single job for hashtag or reels crawling."""
        try:
            _id = job.body.lstrip('#')
            logger.info(f'Processing job: {_id}')
            
            cl = self.session_login(username="your_username", password="your_password")
            if not cl:
                logger.error("Failed to log in. Skipping job.")
                worker.buryJob(job)  # Bury job if login fails
                return
            
            logger.info(f"Session is valid, proceeding to crawl {_id}")

            from kafka import KafkaProducer

            def json_serializer(data):
                return json.dumps(data).encode("utf-8")
            
            producer = KafkaProducer(
                bootstrap_servers = ['10.130.137.101:9092', '10.130.137.99:9092', '10.130.137.100:9092'],#KAFKA['default']['bootstrap_servers'],
                value_serializer = json_serializer
                )
            

            
            if job_type == "hashtag":
                hashtag_medias, success = self.crawl_hashtag(_id, cl)
                #publish_kafka('ingestion-pipeline_instagram_keyword_raw', hashtag_medias)
                producer.send('ingestion-pipeline_instagram_keyword_raw', hashtag_medias)

            if job_type == "reels":
                reels_medias, success = self.crawl_reels(_id, cl)
                #publish_kafka('ingestion-pipeline_instagram_keyword_raw', reels_medias)
                producer.send('ingestion-pipeline_instagram_keyword_raw', hashtag_medias)

            if producer:
                producer.close()

            if success:
                worker.deleteJob(job)  # Mark job as successful
                logger.info(f"Successfully crawled {_id}")
            else:
                worker.buryJob(job)  # Bury failed job
                logger.error(f"Failed to crawl {_id}, job buried.")
        
        except Exception as e:
            logger.error(f"Error processing job {_id}: {e}")
            worker.releaseJob(job)  # Reserve the job for retry

    def run_worker(self, job_type: str, tubename: str):
        """Generic worker function to process hashtag or reels jobs."""
        worker = Worker(tubename, BEANS[self.config]['host'], BEANS[self.config]['port'])
        killer = GracefulKiller()

        while not killer.kill_now:
            job = worker.getJob()
            if job:
                self.process_job(job, worker, job_type)

            break

    def run_worker_hashtag(self):
        """Run worker to process hashtag crawling jobs."""
        self.run_worker("hashtag", "nolimit_crawler_instagram_hashtag")

    def run_worker_reels(self):
        """Run worker to process reels crawling jobs."""
        self.run_worker("reels", "nolimit_crawler_instagram_reels")


if __name__ == "__main__":
    worker = WorkerInstagram()
    worker.run_worker_hashtag()