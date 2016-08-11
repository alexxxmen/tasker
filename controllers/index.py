# -*- coding:utf-8 -*-

from roller import fh
from utils import Logger

from flask import render_template

from controllers.jobs_list import JobListController


class IndexController(object):
    def __init__(self, request, scheduler):
        self.request = request
        self.scheduler = scheduler
        self.log = Logger(self.__class__.__name__, fh)

    def call(self):
        try:
            self.log.debug("Start process request:" % self.request)
            sched_status = self.scheduler.state
            job_list = JobListController(self.request, self.scheduler).call()
            data = render_template('index.html', data=job_list, status=sched_status)
            self.log.debug("Finished")
            return data
        except Exception, e:
            self.log.exception('Error during %s call' % self.__class__.__name__)
            return render_template('error.html', errors=[e.message])
