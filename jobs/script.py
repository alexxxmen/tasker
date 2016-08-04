# -*- coding:utf-8 -*-

import os
import datetime
import psycopg2
import logging

import config
from utils import Logger

fh = logging.FileHandler(os.path.join("/home/alex/work/roller", config.LOGGER['file']))
fh.setLevel(config.LOGGER['level'])
fh.setFormatter(config.LOGGER['formatter'])

log = Logger(fh, 'Script Logger')


def run(**kwargs):
    required_attrs = ("database", "user", "password", "host", "port", "count")
    for attr in required_attrs:
        if attr not in kwargs:
            raise Exception('Missed "%s" argument in "%s"' % (attr, kwargs))

    log.debug('Script started at %s' % datetime.datetime.now())
    try:
        connect = psycopg2.connect(database=kwargs['database'], user=kwargs['user'],
                                   password=kwargs['password'], host=kwargs['host'])
    except Exception:
        log.exception('Connection error')
        raise

    cursor = connect.cursor()

    try:
        cursor.execute("""SELECT * FROM payments ORDER BY datetime""")
    except psycopg2.Error, e:
        log.exception('Execute error=%s' % e.pgerror)

    rows = cursor.fetchall()[-kwargs['count']:]
    for row in rows:
        log.info('Payment: %s' % row)

    del rows
    cursor.close()
