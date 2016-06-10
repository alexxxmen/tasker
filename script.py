# -*- coding: utf-8 -*-
import os
import time
import logging
import argparse

from utils import send_email, Logger, as_text
from config import MAIL_USERNAME, MAIL_SERVER, MAIL_PORT, MAIL_PASSWORD, MODERATORS, LOGGER, LOG_TO


file_handler = logging.FileHandler(os.path.join(LOG_TO, LOGGER.script_file))
file_handler.setLevel(LOGGER.level)
file_handler.setFormatter(LOGGER.formatter)
logger = Logger('script_logs', file_handler)


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
        start_time = time.time()
        options = cls.parser().parse_args()
        try:
            logger.info("The script %s has started to execute" % cls.__name__)
            cls.execute(options)
            logger.info("The script %s finished with the time=%s" % (cls.__name__, time.time() - start_time))
        except Exception as e:
            logger.exception("Occured error in %s" % cls.__name__)
            subject = 'Произошла ошибка в скрипте %s' % cls.__name__
            send_email(subject, as_text(e.message),
                       send_from=MAIL_USERNAME,
                       server=MAIL_SERVER,
                       port=MAIL_PORT,
                       user=MAIL_USERNAME,
                       passwd=MAIL_PASSWORD,
                       dest_to=MODERATORS)
