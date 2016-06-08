import os
import logging
from datetime import date

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
    reestr_file="reestrs_{date:%Y-%m-%d}.log".format(date=date.today()),
    btransfer_file="balance_transfers_{date:%Y-%m-%d}.log".format(date=date.today()),
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
