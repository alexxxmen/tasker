# -*- coding:utf-8 -*-

from flask import redirect, url_for

from controllers import SchedulerController


class HandleJobController(SchedulerController):
    def __init__(self, request, scheduler, job_id):
        self.job_id = job_id
        super(HandleJobController, self).__init__(request, scheduler)

    def _call(self, action):
        job = self._scheduler.get_job(self.job_id)
        if not job:
            return redirect(url_for('.index'))
        if action == 'pause':
            if job.next_run_time:
                job.pause()

        elif action == 'resume':
            if not job.next_run_time:
                job.resume()

        return redirect(url_for('.index'))
