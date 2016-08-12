# -*- coding:utf-8 -*-

import json
import urllib
from decimal import Decimal

import requests
from peewee import fn

from utils import Struct
from constants import ShopType
from jobs_config import TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_API_URL
from models import PaysystemPurse, ShopPurse, Shop, CurrencyRate, CashGapHistory

from jobs import _Job

NOT_SYSTEM_SHOP_ID = 300000

EXCEPTIONAL_SYSTEM_SHOPS = ("100100", "100200", "100300")

CURRENCIES = {'USD': 840, 'RUR': 643, 'EUR': 978, 'UAH': 980}  # TODO, get from DB


class CashGapCheckJob(_Job):
    def _execute(self, **kwargs):
        self.log.debug("Started")
        required_attrs = ("alarm_list", "delta")
        for attr in required_attrs:
            if attr not in kwargs:
                self.log.debug('Missed "%s" argument in "%s"' % (attr, kwargs))
                raise Exception('Missed "%s" argument in "%s"' % (attr, kwargs))

        alarm_list = kwargs['alarm_list']
        delta = kwargs['delta']
        if not len(alarm_list) and not delta:
            self.log.debug('Empty parameters. Alarm list=%s, delta=%s' % (alarm_list, delta))
            raise Exception('Empty parameters. Alarm list=%s, delta=%s' % (alarm_list, delta))

        ps_purses = (PaysystemPurse
                     .select(
                        fn.Sum(PaysystemPurse.ps_balance).alias('ps_balance'),
                        fn.Sum(PaysystemPurse.balance).alias('balance'),
                        PaysystemPurse.currency)
                     .group_by(PaysystemPurse.currency))

        total_ps_balances = [Struct(currency=p.currency, total_trio_balance=p.balance) for p in ps_purses]

        total_diff_balances = []

        not_system_shop_balances = _get_not_system_shop_balances()
        for ps in total_ps_balances:
            for shop in not_system_shop_balances:
                if ps.currency == shop.currency:
                    d = ps.total_trio_balance - shop.total_shop_balance
                    balance = _make_diff_balance(shop.currency, ps.total_trio_balance, shop.total_shop_balance, d)
                    total_diff_balances.append(balance)

        total_uah = _get_total_uah(total_diff_balances)
        diff = total_uah.diff
        prev_diff = CashGapHistory.select(CashGapHistory.cash_gap).order_by(-CashGapHistory.created).first().cash_gap or 0

        courses = json.dumps({
            'UAH': {
                    'USD': _get_exch_rate(CURRENCIES['USD']),
                    'EUR': _get_exch_rate(CURRENCIES['EUR']),
                    'RUR': _get_exch_rate(CURRENCIES['RUR'])
            }
        })

        CashGapHistory.create(cash_gap=diff, currency_rates=courses)
        if Decimal(str(diff)) < prev_diff:
            difference = abs(Decimal(str(diff)) - prev_diff)
            text = 'Текущий кассовый разрыв %s грн., предыдущий %s грн.\nРазница составила %s, при дельте %s.' % \
                   (diff, prev_diff, difference.quantize(Decimal('.0000')), delta)
            if difference >= delta:
                for id in alarm_list:
                    send_alarm_message(TELEGRAM_BOT_API_URL, TELEGRAM_BOT_TOKEN, id, text)


def send_alarm_message(url, token, id, text):
    url = make_url(url, token, id, text)
    response = requests.get(url)
    if response.status_code == 200:
        return True
    return False


def make_url(url, token, id, text):
    return "%s%s/sendMessage?" % (url, token) + urllib.urlencode({'chat_id': id, 'text': str(text)})


def _make_diff_balance(currency, trio_balance, shop_balance, diff):
    return Struct(currency=currency, trio_balance=trio_balance, shop_balance=shop_balance, diff=diff)


def _get_not_system_shop_balances():
    # Get not system shop ids & update them by debit/credit/exchange shops
    shop_ids_query = (Shop
                      .select(Shop.id)
                      .where(
                        (Shop.id >= NOT_SYSTEM_SHOP_ID) &
                        (Shop.shop_type != ShopType.System)))

    shop_ids = [s.id for s in shop_ids_query]
    shop_ids.extend(EXCEPTIONAL_SYSTEM_SHOPS)

    query = (ShopPurse
             .select(fn.Sum(ShopPurse.balance).alias('balance'),
                     fn.Sum(ShopPurse.frozen).alias('frozen'),
                     ShopPurse.currency)
             .join(Shop)
             .where(Shop.id << shop_ids)
             .group_by(ShopPurse.currency))
    return [Struct(currency=p.currency, total_shop_balance=p.balance + p.frozen) for p in query]


def _get_total_uah(total_balances):
    total_uah = Struct(trio_balance=0, shop_balance=0, diff=0)

    for b in total_balances:

        # Add UAH balance without rate multiplying
        if b.currency == CURRENCIES['UAH']:
            total_uah = _update_total_uah(total_uah, b)
            continue

        rate = _get_exch_rate(b.currency)
        if not rate:
            continue

        trio_balance = round_number(b.trio_balance * rate, 4)
        shop_balance = round_number(b.shop_balance * rate, 4)
        diff = trio_balance - shop_balance
        uah_b = Struct(currency=b.currency, trio_balance=trio_balance, shop_balance=shop_balance, diff=diff)

        total_uah = _update_total_uah(total_uah, uah_b)

    return total_uah


def _update_total_uah(total_uah_balance, total_balance):
    total_uah = total_uah_balance

    total_uah.trio_balance += total_balance.trio_balance
    total_uah.shop_balance += total_balance.shop_balance
    total_uah.diff = total_uah.trio_balance - total_uah.shop_balance

    return total_uah


def _get_exch_rate(currency):
    rate = (CurrencyRate
            .select()
            .where(
                (CurrencyRate.from_currency == currency) &
                (CurrencyRate.to_currency == CURRENCIES['UAH']))
            .first())
    return avg_rate(rate.input_rate, rate.output_rate) if rate else None


def avg_rate(input_rate, output_rate):
    return round_number(float(input_rate + output_rate) / 2.0, 4)


def round_number(number, ndigits=2):
    return round(number, ndigits)
