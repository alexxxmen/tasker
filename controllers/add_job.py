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
            return render_template('job_details.html', status=self._scheduler.state)
        elif self._request.method != "POST":
            raise Exception("Unexpected request method type '%s'" % self._request.method)

        required_attrs = ("name", "func", "kwargs", "id", "year", "month", "day", "week", "day_of_week", "hour",
                          "minute", "second", "start_date", "end_date")
        data = self._verify_form_data(required_attrs)

        job_data = self._verify_job_data(data)
        trigger_data = self._verify_trigger_data(data)

        job = self._scheduler.add_job(trigger=CronTrigger(timezone=None, **trigger_data), **job_data)

        if job:
            return redirect(url_for('.index'))
        flash("Job wasn't added")
        return render_template('job_details.html', status=self._scheduler.state)

    def _verify_job_data(self, data):
        result = {
            'id': data['id'],
            'func': data['func'],
            'name': data['name'] or None,
            'kwargs': ast.literal_eval(data['kwargs'])
        }
        return result

    def _verify_trigger_data(self, data):
        result = {
            'year': data['year'] or '*',
            'month': data['month'] or '*',
            'day': data['day'] or '*',
            'week': data['week'] or '*',
            'day_of_week': data['day_of_week'] or '*',
            'hour': data['hour'] or '*',
            'minute': data['minute'] or '*',
            'second': data['second'] or '*',
            'start_date': data['start_date'] or None,
            'end_date': data['end_date'] or None,
        }
        return result

    def _verify_form_data(self, required_attrs):
        data = self._request.form

        if not data:
            raise Exception('Request data is empty')
        for attr in required_attrs:
            if attr not in data:
                raise Exception('Invalid request data. Parameter "%s" not found in "%s"' % (attr, data))
        return data
