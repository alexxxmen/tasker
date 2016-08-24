import logging
from datetime import date

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from utils import Struct

LOCALE = 'ru_UA.UTF-8'

LOG_TO = "/home/alex/logs/roller"

# Logging settings
LOGGER = Struct(
    level=logging.DEBUG,
    formatter=logging.Formatter(
                    "%(asctime)s [%(thread)d:%(threadName)s] [%(levelname)s] - %(name)s:%(message)s"),
    file="log_{date:%Y-%m-%d}.log".format(date=date.today()),
)


DB_CONFIG = dict(
    user='postgres',
    password='postgres',
    host='localhost',
    port=5432,
    database='tasker'
)

# APScheduler params
JOBSTORE_URL = 'postgresql://%s:%s@%s:%s/%s' % (DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['host'],
                                                DB_CONFIG['port'], DB_CONFIG['database'])
THREADS = 10

JOBSTORES = {'default': SQLAlchemyJobStore(url=JOBSTORE_URL)}
EXECUTORS = {'default': ThreadPoolExecutor(THREADS)}
JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 3,
    'misfire_grace_time': 5,
}

SECRET_KEY = 'mbXPvOOm6uBrsJdAjolJ'

SMTP_SETTINGS = dict(
    server='',
    port='',
    use_tls=True,
    username='',
    password=''
)

ERROR_EMAILS = ['']
