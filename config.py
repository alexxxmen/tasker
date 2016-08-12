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

# APScheduler params
JOBSTORE_URL = 'postgresql://daemon:12345@localhost:5432/daemon'  # TODO
THREADS = 10

JOBSTORES = {'default': SQLAlchemyJobStore(url=JOBSTORE_URL)}
EXECUTORS = {'default': ThreadPoolExecutor(THREADS)}
JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}

SECRET_KEY = 'mbXPvOOm6uBrsJdAjolJ'

SMTP_SETTINGS = dict(
    server='',
    port='',
    use_tls=True,
    username='',
    password=''
)

ERROR_EMAILS = ['petrunin@pay-trio.com', 'krementar@pay-trio.com']
