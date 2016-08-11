# -*- coding:utf-8 -*-

from flask import redirect, url_for

from controllers import SchedulerController


class JobRemoveController(SchedulerController):
    def __init__(self, request, scheduler, job_id):
        self.job_id = job_id
        super(JobRemoveController, self).__init__(request, scheduler)

    def _call(self, *args, **kwargs):
        job = self._scheduler.get_job(self.job_id)
        if job:
            job.remove()
        return redirect(url_for('.index'))
