# -*- coding:utf-8 -*-
from roller import fh

from utils import Logger, send_email, as_text
from config import SMTP_SETTINGS, ERROR_EMAILS

log = Logger("General", fh)


class _Job(object):
    def __init__(self):
        self.log = Logger(self.__class__.__name__, fh)
        self.log.debug("Job is created")

    def execute(self, **kwargs):
        try:
            self._execute(**kwargs)
        except Exception, e:
            self.log.exception("Error during job execution")
            subject = 'Roller Information. Произошла ошибка в скрипте %s' % self.__class__.__name__
            send_email(subject, as_text(e.message),
                       send_from=SMTP_SETTINGS['username'],
                       server=SMTP_SETTINGS['server'],
                       port=SMTP_SETTINGS['port'],
                       user=SMTP_SETTINGS['username'],
                       passwd=SMTP_SETTINGS['password'],
                       dest_to=ERROR_EMAILS)

    def _execute(self, **kwargs):
        raise NotImplementedError("%s._execute" % self.__class__.__name__)

    @classmethod
    def run(cls, **kwargs):
        log.debug("in _Job.run!")
        return cls().execute(**kwargs)
