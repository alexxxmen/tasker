# -*- coding:utf-8 -*-

import os
import atexit
import logging

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from config import JOBSTORES, EXECUTORS, JOB_DEFAULTS, LOGGER, LOG_TO


app = Flask(__name__)
app.config.from_object('config')

fh = logging.FileHandler(os.path.join(LOG_TO, LOGGER['file']))
fh.setLevel(LOGGER['level'])
fh.setFormatter(LOGGER['formatter'])

scheduler = BackgroundScheduler(jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

from admin import views
