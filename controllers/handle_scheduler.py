# -*- coding:utf-8 -*-

from flask import url_for, redirect, flash

from constants import APSchedulerStatus
from controllers import SchedulerController


class HandleSchedulerController(SchedulerController):
    def __init__(self, request, scheduler):
        super(HandleSchedulerController, self).__init__(request, scheduler)

    def _call(self, action):
        if action == 'resume' and self._scheduler.state == APSchedulerStatus.Pause:
            self._scheduler.resume()
            flash('Scheduler resumed', 'info')

        elif action == 'pause' and self._scheduler.state == APSchedulerStatus.Start:
            self._scheduler.pause()
            flash('Scheduler paused', 'info')

        return redirect(url_for('.index'))
