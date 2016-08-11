# -*- coding:utf-8 -*-

import ast

from apscheduler.triggers.cron import CronTrigger
from flask import redirect, url_for, render_template

from controllers import SchedulerController


class JobEditController(SchedulerController):
    def __init__(self, request, scheduler, job_id):
        self.job_id = job_id
        super(JobEditController, self).__init__(request, scheduler)

    def _call(self):

        job = self._scheduler.get_job(self.job_id)
        if not job:
            self.log.debug('Job not found. Job id=%s' % self.job_id)
            return redirect(url_for('.index'))
        trig_data = {}
        for field in job.trigger.fields:
            trig_data[field.name] = str(field)

        if self._request.method == 'GET':
            return render_template('edit.html', job=job, trigger_data=trig_data)

        elif not self._request.method == "POST":
            return redirect(url_for('.index'))

        job_form_data = self._verify_job_data()
        trigger_form_data = self._verify_trigger_data()
        try:
            job.modify(trigger=CronTrigger(**trigger_form_data), **job_form_data)
        except Exception, e:
            return redirect(url_for('.job_edit', job_id=job.id, errors=[e.message]))
        return redirect(url_for('.index'))

    def _verify_job_data(self):
        required_attrs = ("name", "func", "kwargs")

        data = self._request.form
        if not data:
            raise Exception('Form is empty!')  # TODO Ex msg

        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request. Parameter "%s" not found in "%s"' % (attr, data))  # TODO Ex msg

        result = {}
        for attr in required_attrs:
            if data[attr]:
                result[attr] = data[attr] if attr != 'kwargs' else ast.literal_eval(data['kwargs'])
        return result

    def _verify_trigger_data(self):
        required_attrs = ("year", "month", "day", "week", "day_of_week", "hour", "minute", "second")

        data = self._request.form
        if not data:
            raise Exception('Form is empty!')  # TODO Ex msg
        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request. Parameter "%s" not found in "%s"' % (attr, data))  # TODO Ex msg

        result = {}
        for attr in required_attrs:
            if data[attr]:
                result[attr] = data[attr]
        return result
