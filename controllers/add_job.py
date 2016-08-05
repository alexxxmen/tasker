# -*- coding:utf-8 -*-

import ast

from flask import redirect, url_for, render_template, flash
from apscheduler.triggers.cron import CronTrigger

from controllers import SchedulerController


class AddJobController(SchedulerController):
    def __init__(self, request, scheduler):
        super(AddJobController, self).__init__(request, scheduler)

    def _call(self):
        if self._request.method == "GET":
            return render_template('add.html')
        elif not self._request.method == "POST":
            raise Exception("Unexpected request method type '%s'" % self._request.method)

        job_data = self._verify_job_data()
        trigger_data = self._verify_trigger_data()

        job = self._scheduler.add_job(trigger=CronTrigger(timezone=None, **trigger_data), **job_data)

        if job:
            return redirect(url_for('.index'))
        flash("Job wasn't added")
        return render_template('add.html')

    def _verify_job_data(self):
        required_attrs = ("name", "func", "kwargs", "id")

        data = self._request.form
        if not data:
            raise Exception('Request data is empty')
        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request. Parameter "%s" not found in "%s"' % (attr, data))  # TODO Ex msg

        result = {
            'id': data['id'],
            'func': data['func'],
            'name': data['name'] or None,
            'kwargs': ast.literal_eval(data['kwargs'])
        }
        return result

    def _verify_trigger_data(self):
        required_attrs = ("year", "month", "day", "week", "day_of_week", "hour",
                          "minute", "second", "start_date", "end_date")

        data = self._request.form
        if not data:
            raise Exception('Request data is empty')
        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request. Parameter "%s" not found in "%s"' % (attr, data))  # TODO Ex msg

        result = {
            'year': data['year'] or None,
            'month': data['month'] or None,
            'day': data['day'] or None,
            'week': data['week'] or None,
            'day_of_week': data['day_of_week'] or None,
            'hour': data['hour'] or None,
            'minute': data['minute'] or None,
            'second': data['second'] or None,
            'start_date': data['start_date'] or None,
            'end_date': data['end_date'] or None,
        }
        return result
