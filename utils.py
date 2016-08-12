# -*- coding: utf-8 -*-
import os
import logging
from decimal import Decimal


LOCALE = 'ru_UA.UTF-8'


class Logger(object):
    def __init__(self, logger_name, file_handler):
        self._log = logging.getLogger(logger_name)
        self._log.addHandler(file_handler)
        self._log.setLevel(file_handler.level)

    def __getattr__(self, *args, **kwds):
        return getattr(self._log, *args, **kwds)


class Struct(object):
    def __init__(self, **kwds):
        for k, v in kwds.items():
            if isinstance(v, dict):
                setattr(self, k, Struct(**v))
            elif isinstance(v, Decimal):
                setattr(self, k, float(v))
            else:
                setattr(self, k, v)

    def __iter__(self):
        return iter(self.__dict__)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def __nonzero__(self):
        return bool(self.items())

    def to_dict(self):
        return self.__dict__


def get_request_info(request):
    if request.method == "GET":
        request_data = ""
    else:
        request_data = dict(request.json.items() if request.json else request.form.items())

    return Struct(data=request_data, url=request.url, method=request.method, headers=request.headers)
