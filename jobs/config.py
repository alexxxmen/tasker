# Telegram params
TELEGRAM_BOT_TOKEN = '269816990:AAF9MFxKiiixplndKlJ0CxnXIl0xBAi0PsY'
TELEGRAM_BOT_API_URL = "https://api.telegram.org/bot"

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

# SMTP settings
MAIL_SERVER = ""
MAIL_PORT = ''
MAIL_USE_TLS = True
MAIL_USERNAME = ""
MAIL_PASSWORD = ""

MODERATORS = ['petrunin@pay-trio.com', 'krementar@pay-trio.com']
