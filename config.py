import logging
from datetime import date

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from utils import Struct

LOCALE = 'ru_UA.UTF-8'

LOG_TO = "/home/alex/work/logs/roller"

# Logging settings
LOGGER = Struct(
    level=logging.DEBUG,
    formatter=logging.Formatter(
                    "%(asctime)s [%(thread)d:%(threadName)s] [%(levelname)s] - %(name)s:%(message)s"),
    file="log_{date:%Y-%m-%d}.log".format(date=date.today()),
)

# APScheduler params
DB_CONFIG = dict(
    username='daemon',
    password=12345,
    host='localhost',
    port=5432,
    database='daemon'
)
JOBSTORE_URL = 'postgresql://%s:%s@%s:%s/%s' % (DB_CONFIG['username'], DB_CONFIG['password'], DB_CONFIG['host'],
                                                DB_CONFIG['port'], DB_CONFIG['database'])
THREADS = 10

JOBSTORES = {'default': SQLAlchemyJobStore(url=JOBSTORE_URL)}
EXECUTORS = {'default': ThreadPoolExecutor(THREADS)}
JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}

SECRET_KEY = 'mbXPvOOm6uBrsJdAjolJ'

SMTP_SETTINGS = dict(
    server='mail.pay-trio.com',
    port=587,
    use_tls=True,
    username='test-roller@pay-trio.com',
    password='85WPaLEb83'
)

ERROR_EMAILS = ['petrunin@pay-trio.com', 'krementar@pay-trio.com']
