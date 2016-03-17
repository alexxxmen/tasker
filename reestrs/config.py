import os
import logging
from datetime import date


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

LOG_TO = os.path.dirname(os.path.realpath(__file__)) + '/logs'

MAIL_SERVER = "mail.pay-trio.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "reestr@pay-trio.com"
MAIL_PASSWORD = "yBT36qt7YS"

LOGGER_FILE = "reestrs_{date:%Y-%m-%d}.log".format(date=date.today())
LOGGER_LEVEL = logging.DEBUG
LOGGER_NAME = "reestr"

MODERATORS = ["odiscort@gmail.com", "rychyk@pay-trio.com"]
DIRECTORS = ["odiscort@gmail.com", "rychyk@pay-trio.com"]

REPORTS_DIR = 'reports/'
INVOICE_STATISTIC_DIR = REPORTS_DIR + 'invoice_statistic/'
WITHDRAW_STATISTIC_DIR = REPORTS_DIR + 'withdraw_statistic/'
PAYMENT_INFO_DIR = REPORTS_DIR + 'payment_info/'
PS_FEE_INCORRECT_DIR = REPORTS_DIR + 'ps_fee_incorrect/'
INCORRECT_INVOICES_DIR = REPORTS_DIR + 'incorrect_invoices/'

LOCALE = 'ru_UA.UTF-8'
