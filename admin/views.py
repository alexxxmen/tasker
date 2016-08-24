# -*- coding:utf-8 -*-

from tasker import app, scheduler
from controllers.handle_scheduler import HandleSchedulerController
from controllers.add_job import AddJobController
from controllers.job_edit import JobEditController
from controllers.handle_job import HandleJobController
from controllers.job_remove import JobRemoveController
from controllers.index import IndexController

from flask import request


@app.route("/")
def index():
    return IndexController(request, scheduler).call()


@app.route("/pause")
def pause():
    return HandleSchedulerController(request, scheduler).call('pause')


@app.route("/resume")
def resume():
    return HandleSchedulerController(request, scheduler).call('resume')


@app.route("/job/add", methods=["GET", "POST"])
def job_add():
    return AddJobController(request, scheduler).call()


@app.route("/job/edit/<job_id>", methods=["GET", "POST"])
def job_edit(job_id):
    return JobEditController(request, scheduler, job_id).call()


@app.route("/job/pause/<job_id>")
def job_pause(job_id):
    return HandleJobController(request, scheduler, job_id).call('pause')


@app.route("/job/resume/<job_id>")
def job_resume(job_id):
    return HandleJobController(request, scheduler, job_id).call('resume')


@app.route("/job/remove/<job_id>")
def job_remove(job_id):
    return JobRemoveController(request, scheduler, job_id).call()


