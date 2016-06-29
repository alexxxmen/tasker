# -*- coding: utf-8 -*-
import os
import json
import logging
from datetime import datetime

import requests

from script import Script
from models import Shop, ShopPurse
from utils import md5_sign_string, format_date, Logger
from config import TRIO_URL, TRIO_SECRET, LOGGER, LOG_TO


file_handler = logging.FileHandler(os.path.join(LOG_TO, LOGGER.btransfer_file))
file_handler.setLevel(LOGGER.level)
file_handler.setFormatter(LOGGER.formatter)
logger = Logger('balance_transfer', file_handler)


requests.packages.urllib3.disable_warnings()


SOURCE_SHOP = 300267
TARGET_SHOP = 300222

DEFAULT_CURRENCY = 643

MIN_AMOUNT = 1

# Default articles
DEFAULT_SOURCE_AMOUNT_ARTICLE = 1
DEFAULT_TARGET_AMOUNT_ARTICLE = 1
DEFAULT_SOURCE_FEE_ARTICLE = 1
DEFAULT_TARGET_FEE_ARTICLE = 1


class Transfer(object):
    def __init__(self, shop_purse):
        self.shop_purse = shop_purse

    def get_data(self):
        return {
            "source_shop": str(SOURCE_SHOP),
            "target_shop": str(TARGET_SHOP),
            "source_currency": str(DEFAULT_CURRENCY),
            "target_currency": str(DEFAULT_CURRENCY),
            "amount": str(int(self.shop_purse.balance)),  # Without cents
            "amount_type": "source_amount",
            "comments": u"Перевод от %s" % format_date(datetime.now(), fmt="%d.%m.%Y %H:%M:%S"),
            "exch_rate": "1",
            "exch_fee_percent": "0",
            "source_exch_fee": True,
            "source_fee_fix": "0",
            "target_fee_fix": "0",
            "source_amount_article": str(DEFAULT_SOURCE_AMOUNT_ARTICLE),
            "target_amount_article": str(DEFAULT_TARGET_AMOUNT_ARTICLE),
            "source_fee_article": str(DEFAULT_SOURCE_FEE_ARTICLE),
            "target_fee_article": str(DEFAULT_TARGET_FEE_ARTICLE),
        }


class TrioException(Exception):
    pass


class Trio(object):
    def __init__(self, url, secret):
        self._url = url
        self._secret = secret

    def shop_transfer(self, source_shop, target_shop, source_currency, target_currency, amount,
                      amount_type, comments, exch_rate, exch_fee_percent, source_exch_fee,
                      source_fee_fix, target_fee_fix, source_amount_article,
                      target_amount_article, source_fee_article, target_fee_article):
        data = {
            "source_shop": source_shop,
            "target_shop": target_shop,
            "source_currency": source_currency,
            "target_currency": target_currency,
            "amount": amount,
            "amount_type": amount_type,
            "comments": comments,
            "exch_rate": exch_rate,
            "exch_fee_percent": exch_fee_percent,
            "source_exch_fee": str(source_exch_fee),  # str необходим для string_to_sign
            "source_fee_fix": source_fee_fix,
            "target_fee_fix": target_fee_fix,
            "source_amount_article": source_amount_article,
            "target_amount_article": target_amount_article,
            "source_fee_article": source_fee_article,
            "target_fee_article": target_fee_article,
        }
        self._sign_request(data, sign_keys=data.keys())
        data.update({"source_exch_fee": bool(source_exch_fee)})
        resp = self._send_request(self._url + '/shop_transfer', data=data)
        return self._check_response(resp)

    def _send_request(self, url, data, headers={"Content-Type": "application/json"}):
        logger.info("Started request with params: %s on url=%s" % (str(data), url))
        response = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)
        logger.info("Response=%s" % response.text)
        return response

    def _sign_request(self, request, sign_keys):
        sign_keys = sorted(sign_keys)
        string_to_sign = ":".join([request[k] for k in sign_keys]) + self._secret
        request["sign"] = md5_sign_string(string_to_sign.encode('utf-8'))

    def _check_response(self, response):
        if response.status_code not in (200, 201):
            raise TrioException("Trio error: %s" % response.text)

        response_data = response.json()
        for attr in ("result", "data", "message"):
            if attr not in response_data:
                raise TrioException("Trio response error: '%s' is not set" % attr)

        if not response_data['data']:
            raise TrioException(response_data['message'])

        return response_data


class TransferBalanceScript(Script):
    @classmethod
    def execute(cls, options):
        logger.info("Начало работы скрипта transer")
        shop = Shop.get_by_id(SOURCE_SHOP)
        if shop is None:
            raise Exception("Магазин-источник, id=%s не найден" % SOURCE_SHOP)

        shop_purse = ShopPurse.get(ShopPurse.currency == DEFAULT_CURRENCY, ShopPurse.shop == shop)
        if shop_purse is None:
            raise Exception("Кошелек магазина=%s с валютой=%s не найден" % (shop.id, DEFAULT_CURRENCY))

        if shop_purse.balance < MIN_AMOUNT:
            raise Exception("Минимальная сумма для перевода должна быть больше %s" % MIN_AMOUNT)

        transer = Transfer(shop_purse)
        trio = Trio(TRIO_URL, TRIO_SECRET)
        trio.shop_transfer(**transer.get_data())
        logger.info("Скрипт transer успешно отработал")

if __name__ == "__main__":
    TransferBalanceScript.run()
