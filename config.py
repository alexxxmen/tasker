import os
import logging
from datetime import date

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from utils import Struct


ADMIN_DB_CONFIG = DB_CONFIG = dict(
    database="admin",
    user="postgres",
    password="test",
    host="localhost",
    port=5432,
    max_connections=None,
    stale_timeout=600,
    register_hstore=False,
    server_side_cursors=False
)

TRIO_DB_CONFIG = dict(
    database="trio_db",
    user="admin",
    password="adminP@ss",
    host="test.pay-trio.com",
    port=5433,
    max_connections=None,
    stale_timeout=600,
    register_hstore=False,
    server_side_cursors=False
)

LOCALE = 'ru_UA.UTF-8'

# Roller base folder
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LOG_TO = os.path.join(BASE_DIR, 'logs')

# Logging settings
LOGGER = Struct(
    level=logging.DEBUG,
    formatter=logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s:%(message)s"),
    file="log_{date:%Y-%m-%d}.log".format(date=date.today()),
    reestr_file="reestrs_{date:%Y-%m-%d}.log".format(date=date.today()),  # Log file for reestrs
    btransfer_file="balance_transfers_{date:%Y-%m-%d}.log".format(date=date.today()),  # Log file for balance transfer
    script_file="script_{date:%Y-%m-%d}.log".format(date=date.today()),  # Log file for overall scripts info
)

# SMTP settings
MAIL_SERVER = "mail.pay-trio.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "reestr@pay-trio.com"
MAIL_PASSWORD = "yBT36qt7YS"

# Reports directories settings
REPORTS_DIR = os.path.join(BASE_DIR, 'reestrs/reports')
INVOICE_STATISTIC_DIR = os.path.join(REPORTS_DIR, 'invoice_statistic')
WITHDRAW_STATISTIC_DIR = os.path.join(REPORTS_DIR, 'withdraw_statistic')
PAYMENT_INFO_DIR = os.path.join(REPORTS_DIR, 'payment_info')
PS_FEE_INCORRECT_DIR = os.path.join(REPORTS_DIR, 'ps_fee_incorrect')
INCORRECT_INVOICES_DIR = os.path.join(REPORTS_DIR, 'incorrect_invoices')

# A list of people who get error notifications
MODERATORS = ["odiscort@gmail.com", "rychyk@pay-trio.com"]

# A list of people who get a reports
DIRECTORS = ["odiscort@gmail.com", "rychyk@pay-trio.com"]

# Trio API params
TRIO_URL = "https://test-main.pay-trio.com"
TRIO_SECRET = "admin_test"

# APScheduler params
JOBSTORE_URL = 'postgresql://daemon:12345@localhost:5432/daemon'  # TODO
THREADS = 10

JOBSTORES = {'default': SQLAlchemyJobStore(url=JOBSTORE_URL)}
EXECUTORS = {'default': ThreadPoolExecutor(THREADS)}
JOB_DEFAULTS = {
    'coalesce': True,
    'max_instances': 1
}

SECRET_KEY = 'SECRET'  # TODO

# Telegram params
TELEGRAM_BOT_TOKEN = '269816990:AAF9MFxKiiixplndKlJ0CxnXIl0xBAi0PsY'
TELEGRAM_BOT_API_URL = "https://api.telegram.org/bot"