# -*- coding: utf-8 -*-
import os
import smtplib
import logging
from decimal import Decimal
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate


LOCALE = 'ru_UA.UTF-8'


class Logger(object):
    def __init__(self, logger_name, file_handler):
        self._log = logging.getLogger(logger_name)
        self._log.addHandler(file_handler)
        self._log.setLevel(file_handler.level)

    def __getattr__(self, *args, **kwds):
        return getattr(self._log, *args, **kwds)


class Struct(object):
    def __init__(self, **kwds):
        for k, v in kwds.items():
            if isinstance(v, dict):
                setattr(self, k, Struct(**v))
            elif isinstance(v, Decimal):
                setattr(self, k, float(v))
            else:
                setattr(self, k, v)

    def __str__(self):
        _buffer = ""
        for key, value in self.items():
            if not isinstance(value, list):
                _buffer += "%s=%s" % (key, unicode(value)) + ", "
            else:
                _buffer += "%s=%s" % (key, "[%s]" % ", ".join(unicode(item) for item in value)) + ", "

        return "{ %s }" % _buffer[:-1]

    def __iter__(self):
        return iter(self.__dict__)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def __nonzero__(self):
        return bool(self.items())

    def to_dict(self):
        return self.__dict__


def get_request_info(request):
    if request.method == "GET":
        request_data = ""
    else:
        request_data = dict(request.json.items() if request.json else request.form.items())

    return Struct(data=request_data, url=request.url, method=request.method, headers=request.headers)


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
