# -*- coding:utf-8 -*-

import ast

from flask import redirect, url_for, render_template
from apscheduler.triggers.cron import CronTrigger

from controllers import SchedulerController


class AddJobController(SchedulerController):
    def __init__(self, request, scheduler):
        super(AddJobController, self).__init__(request, scheduler)

    def _call(self):
        if self._request.method == "GET":
            return render_template('add.html')
        elif not self._request.method == "POST":
            return redirect(url_for('.index'))

        job_data = self._verify_job_data()
        trigger_data = self._verify_trigger_data()
        job = None
        try:
            job = self._scheduler.add_job(trigger=CronTrigger(timezone=None, **trigger_data), **job_data)
        except Exception:
            self.log.exception('Error while adding job')

        if job:
            return redirect(url_for('.index'))
        return render_template('add.html', errors=["Job wasn't added"])

    def _verify_job_data(self):
        required_attrs = ("name", "func", "kwargs", "id")

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
        required_attrs = ("year", "month", "day", "week", "day_of_week", "hour",
                          "minute", "second", "start_date", "end_date")

        data = self._request.form
        if not data:
            raise Exception('Form is empty!')  # TODO Ex msg
        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request. Parameter "%s" not found in "%s"' % (attr, data))  # TODO Ex msg

        result = {}
        for attr in required_attrs:
            if data[attr]:
                result[attr] = data[attr] or None
        return result
