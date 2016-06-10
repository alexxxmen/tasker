# -*- coding: utf-8 -*-
import os
import smtplib
import json
import logging
import calendar
import hashlib
from datetime import date, timedelta, datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate


LOCALE = 'ru_UA.UTF-8'


class Error(Exception):
    pass


class Logger(object):
    def __init__(self, logger_name, file_handler):
        self._log = logging.getLogger(logger_name)
        self._log.addHandler(file_handler)
        self._log.setLevel(file_handler.level)

    def __getattr__(self, *args, **kwds):
        return getattr(self._log, *args, **kwds)


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def to_dict(self):
        return self.__dict__

    def __nonzero__(self):
        return bool(self.__dict__)

    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return "<{class_name}: ({data}) >".format(class_name=self.__class__.__name__, data=', '.join(args))


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def is_valid_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def md5_sign_string(string_to_sign):
    return hashlib.md5(string_to_sign).hexdigest()


def get_yesterday_date():
    return date.today() - timedelta(1)


def convert_to_datetime(dt):
    return datetime(dt.year, dt.month, dt.day, 0, 0)


def format_date_range(dt):
    start, end = dt
    end -= timedelta(days=1)
    fmt = '%d.%m.%Y'
    return '%s-%s' % (start.strftime(fmt), end.strftime(fmt))


def get_period_range(dt):
    """Returns the end and beginning of the reporting date.
    :param dt <datetime.date>"""
    _date = dt
    end = convert_to_datetime(_date) + timedelta(days=1)
    start = _date.replace(day=1)
    return start, end


def get_day_range(dt):
    """Returns the end and beginning of the reporting day.
    :param dt <datetime.date>"""
    start = convert_to_datetime(dt)
    end = start + timedelta(days=1)
    return start, end


def format_date(dt, fmt='%d-%m-%Y'):
    """Returns represantative date"""
    return dt.strftime(fmt)


def previous_month_day(dt):
    """
    Дата отчета за отчетный день в предыдущем месяце. Если отчет формируется 12.11.2015,
    то данная дата будет – 11.10.2015. Если количество дней в месяце не совпадает, то берется последний день месяца
    """
    date_ = dt
    first = date_.replace(day=1)
    prev_month_date = first - timedelta(days=1)
    monthrange = calendar.monthrange(prev_month_date.year, prev_month_date.month)[1]

    day = monthrange if date_.day > monthrange else date_.day
    return date(year=prev_month_date.year, month=prev_month_date.month, day=day)


def get_month_name(month_no):
    with calendar.TimeEncoding(LOCALE) as encoding:
        s = calendar.month_name[month_no]
        if encoding is not None:
            s = s.decode(encoding)
        return s


def get_dynamic_range(curr, prev):
    return "%s-%s" % (get_month_name(curr.month), get_month_name(prev.month))


def send_email(subject, text, send_from, dest_to, server, port, user, passwd, attachments=None):
    """Send an email with(out) attachments

    Args:
        subject (str): The mail's subject
        text (str): The message's text
        send_from (str): A sender's email address
        dest_to (list): A list of receivers' email addresses
        attachments (tuple): A list of attachments files
        server (str): The smtp server
        port (int): The smtp server port
        user (str): The smtp server user
        passwd (str): The smtp server password
    """
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = send_from
    message["To"] = COMMASPACE.join(list(dest_to))
    message["Date"] = formatdate(localtime=True)
    message.attach(MIMEText(text))

    # For all type of attachments
    if attachments:
        for att_file in attachments:
            with open(att_file, 'rb') as attmnt:
                att = MIMEBase("application", "octet-stream")
                att.set_payload(attmnt.read())
            encoders.encode_base64(att)
            att.add_header("content-disposition", "attachment",
                           filename=os.path.basename(att_file))
            message.attach(att)

    smtp_server = None
    try:
        smtp_server = smtplib.SMTP()
        smtp_server.connect(server, port)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(user, passwd)
        smtp_server.sendmail(send_from, dest_to, message.as_string())
    finally:
        if smtp_server:
            smtp_server.quit()


def parse_date(date_str, fmt="%d.%m.%Y"):
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        raise Error("Ошибка парсинга даты. Ожидаемый формат: 'дд.мм.гггг'. Текущий формат: %s" % date_str)


def make_path(dir_path, filename):
    """Makes the absolute path fo filename"""
    return os.path.join(dir_path, filename)


def as_text(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)


def as_unicode(s):
    if isinstance(s, str):
        return s.decode('utf-8')
    return unicode(s)
