# -*- coding:utf-8 -*-

from flask import render_template

from roller import fh
from utils import Logger, get_request_info


class SchedulerController(object):
    def __init__(self, request, scheduler):
        self.log = Logger(self.__class__.__name__, fh)
        self._request = request
        self._scheduler = scheduler

    def call(self, *args, **kwargs):
        try:
            self.log.debug("Start process request: %s" % get_request_info(self._request))
            data = self._call(*args, **kwargs)
            self.log.debug('Finished')
            return data
        except Exception, e:
            self.log.exception('Error during %s call' % self.__class__.__name__)
            return render_template('error.html', error=e.message)  # TODO шаблон

    def _call(self, *args, **kwargs):
        raise NotImplementedError
