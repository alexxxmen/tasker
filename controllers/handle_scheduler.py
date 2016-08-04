# -*- coding:utf-8 -*-

from flask import url_for, redirect

from constants import APSchedulerStatus
from controllers import SchedulerController


class HandleSchedulerController(SchedulerController):
    def __init__(self, request, scheduler):
        super(HandleSchedulerController, self).__init__(request, scheduler)

    def _call(self, action):
        if action == 'resume':
            if self._scheduler.state == APSchedulerStatus.Pause:
                self._scheduler.resume()

        elif action == 'pause':
            if self._scheduler.state == APSchedulerStatus.Start:
                self._scheduler.pause()

        return redirect(url_for('.index'))
