# -*- coding:utf-8 -*-

import os
import atexit
import logging

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from config import JOBSTORES, EXECUTORS, JOB_DEFAULTS, LOGGER, LOG_TO
from utils import Logger

app = Flask(__name__)
app.config.from_object('config')

if not os.path.exists(LOG_TO):
    os.makedirs(LOG_TO)

fh = logging.FileHandler(os.path.join(LOG_TO, LOGGER.get('file')))
fh.setLevel(LOGGER.get('level'))
fh.setFormatter(LOGGER.get('formatter'))

log = Logger("Roller", fh)

log.info("Service started!")

sched_log = Logger("apscheduler.executors.default", fh)

scheduler = BackgroundScheduler(jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS)
scheduler.start()

log.info("Scheduler started!")


def onstop():
    # Shut down the scheduler when exiting the app
    scheduler.shutdown()
    log.info("Scheduler shutdown")
    log.info("Service stopped!")

atexit.register(onstop)

from admin import views
