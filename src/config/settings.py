BEANS = {
    'default': {
        'prefix': 'nolimit',
        'host': '167.99.72.45',
        'port': 11300
    }
}
REDIS = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379,
        'password': 'rahasia123'
    }
}

COOKIE_RESOURCE = {
    'default': {'allowed_usage': 'for_auto'}
}

PATH = {
    'default': {
        'rawpath': '/mnt/data/raw/',
        'preprocessedpath': '/mnt/data/buffer/',
        'cookiepath': '/mnt/data/cookies/',
        'agegen': '/mnt/data/agegen/'
    }
}

PROXIES = {
    'default': [
        {
            'server': 'http://159.223.48.21:2560/',
            'username': 'bandung',
            'password': '456xyz',
            'auth_url': 'http://bandung:456xyz@159.223.48.21:2560/'
        },{
            'server': 'http://103.129.220.27:3128/',
            'username': 'nolimit',
            'password': 'rahasia123',
            'auth_url': 'http://nolimit:rahasia123@103.129.220.27:3128/'
        },{
            'server': 'http://159.223.48.21:2560/',
            'username': 'raspi2',
            'password': 'kantorxyz',
            'auth_url': 'http://raspi2:kantorxyz@159.223.48.21:2560/'
        },{
            'server': 'http://159.223.48.21:2560/',
            'username': 'raspi1',
            'password': 'kantorxyz',
            'auth_url': 'http://raspi1:kantorxyz@159.223.48.21:2560/'
        },{
            'server': 'http://127.0.0.1:3128/',
            'username': 'nolimit',
            'password': 'rahasia123',
            'auth_url': 'http://nolimit:rahasia123@127.0.0.1:3128/'
        }
    ]
}

KAFKA = {
    'default': {
        'bootstrap_servers': ['10.130.137.101:9092', '10.130.137.99:9092', '10.130.137.100:9092']
    }
}

SENTRY = { 
    'default': {
        'dsn': "http://596c56d4797bc21f4b828a0492746250@188.166.250.30:9000/8",
        'env': 'production'
    }
}

MYSQL = {
    'trending_info': {
        'host': '127.0.0.1',
        'user': 'trending_1',
        'password': 'MainTrend9291!!',
        'dbname': 'trending_info',
        'port' : 3306
    }   
}

GET_COOKIES_SLEEP = 10

SLEEPING_COOKIES_DELAY = 3600

MINIO = {
    'default': {
        'host': '188.166.209.48:9000',
        'access_key': 'GVh5sxa5itTUjBkWxQb3',
        'secret_key': '7ofuZFQx3lFZWGbUrmQSsvBb74mHSKxfTR9J9ifL'
    }
}

ELASTICSEARCH = "http://esclient01:nolimitsukses27A!$@esnode02.dashboard.nolimit.id:80"