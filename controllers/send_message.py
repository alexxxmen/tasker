# -*- coding:utf8 -*-

import requests

from tasker import fh
from utils import Logger


class SendMessageController(object):
    def __init__(self, token):
        self.log = Logger(self.__class__.__name__, fh)
        self._token = token

    def call(self, url, id, text):
        response = requests.get(self._make_url(url, self._token, chat_id=id, text=unicode(text)), verify=False)
        self.log.debug("Response text=%s, response code=%s" % (response.text, response.status_code))
        if response.status_code != 200:
            self.log.exception("Response status code not 200. code=%s" % response.status_code)
            raise Exception('Message doesn\'t send')

    def _make_url(self, url, token, **kwargs):
        data = u'&'.join([u'%s=%s' % (key, value) for key, value in kwargs.items()])
        return url + token + '/sendMessage?' + data
