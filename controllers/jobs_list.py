# -*- coding:utf-8 -*-

from controllers import SchedulerController


class JobListController(SchedulerController):
    def __init__(self, request, scheduler):
        super(JobListController, self).__init__(request, scheduler)

    def _call(self):
        if self._scheduler.running:
            return [{'id': job.id, 'name': job.name, 'next_run_time': job.next_run_time, 'args': job.args,
                     'kwargs': job.kwargs, 'trigger': job.trigger, 'func_ref': job.func_ref}
                    for job in self._scheduler.get_jobs()]
        return None
