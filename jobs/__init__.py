# -*- coding:utf-8 -*-
from roller import fh
from utils import Logger, send_email, as_text
from config import MAIL_USERNAME, MAIL_SERVER, MAIL_PORT, MAIL_PASSWORD, MODERATORS

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
            subject = 'Произошла ошибка в скрипте %s' % self.__class__.__name__
            send_email(subject, as_text(e.message),
                       send_from=MAIL_USERNAME,
                       server=MAIL_SERVER,
                       port=MAIL_PORT,
                       user=MAIL_USERNAME,
                       passwd=MAIL_PASSWORD,
                       dest_to=MODERATORS)

    def _execute(self, **kwargs):
        raise NotImplementedError("%s._execute" % self.__class__.__name__)

    @classmethod
    def run(cls, **kwargs):
        log.debug("in _Job.run!")
        return cls().execute(**kwargs)
