from libs.beans import Worker
from redis import Redis
from config.settings import REDIS, MINIO
#from minio import Minio
from libs.proxies import get_proxy_cycle


class BaseWorker():
    def __init__(self, config='default', *args, **kwargs):
        self.config = config
        self.conn_redis = None
        self.headers = None
        self.cookies = None
        self.resource_id = None
        self.user_credential = None
        self.complete_cookie = None
        self.from_file = False
        self.worker: Worker = None
        self.kill_now = False
        self.invalid_cookie_error = False
        self.release_cookie = True
        self.minio_client = None
        self.proxy_cycle = None
        self.worker = None

    def set_conn_redis(self):
        self.conn_redis = Redis(host=REDIS[self.config]['host'],
                                port=REDIS[self.config]['port'], decode_responses=True,
                                password=REDIS[self.config]['password'])
                                

    #def set_minio_client(self):
    #    self.minio_client = Minio(
    #        MINIO['default']['host'],
    #        access_key=MINIO['default']['access_key'],
    #        secret_key=MINIO['default']['secret_key'],
    #        secure=False
    #    )

    def set_proxy_cycle(self):
        proxy_cycle = get_proxy_cycle()
        self.proxy_cycle = proxy_cycle