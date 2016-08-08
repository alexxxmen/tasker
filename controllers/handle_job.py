# -*- coding:utf-8 -*-

from flask import redirect, url_for, flash

from controllers import SchedulerController


class HandleJobController(SchedulerController):
    def __init__(self, request, scheduler, job_id):
        self.job_id = job_id
        super(HandleJobController, self).__init__(request, scheduler)

    def _call(self, action):
        job = self._scheduler.get_job(self.job_id)
        if not job:
            raise Exception("Job wasn't found. Job id=%s" % self.job_id)
        if action == 'pause' and job.next_run_time:
            job.pause()
            flash('Job was paused')
        elif action == 'resume' and not job.next_run_time:
            job.resume()
            flash('Job was resumed')

        return redirect(url_for('.index'))
