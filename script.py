# -*- coding: utf-8 -*-
import logging
import argparse

from utils import send_email
from config import MAIL_USERNAME, MAIL_SERVER, MAIL_PORT, MAIL_PASSWORD, MODERATORS


logger = logging.getLogger(__name__)


class Script(object):
    """Base script for regular tasks."""
    @classmethod
    def execute(cls, options):
        raise NotImplementedError("Override `execute` method")

    @classmethod
    def parser(cls):
        parser = argparse.ArgumentParser()
        return parser

    @classmethod
    def run(cls):
        options = cls.parser().parse_args()
        try:
            logger.info("The script %s has started to execute" % cls.__name__)
            cls.execute(options)
            logger.info("The script %s finished" % cls.__name__)
        except Exception as e:
            logger.exception(e)
            subject = 'Произошла ошибка в скрипте %s' % cls.__name__
            send_email(subject, e.message,
                       send_from=MAIL_USERNAME,
                       server=MAIL_SERVER,
                       port=MAIL_PORT,
                       user=MAIL_USERNAME,
                       passwd=MAIL_PASSWORD,
                       dest_to=MODERATORS)
