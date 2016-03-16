# -*- coding: utf-8 -*-

import logging

from models import WithdrawPayway, Withdraw, Paysystem, Shop, PayMethod
from utils import get_period_range, previous_month_day
from .sheets import calculations_by_dates, PaymethodSheet, PaysystemSheet, PaywaySheet, ShopSheet


log = logging.getLogger(__name__)


SUCCESS_WITHDRAW_STATUS = 5


class ShopWithdrawSheet(ShopSheet):
    def _get_shops(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки магазинов на вывод, которые будут включены в отчет
        shops = (Shop
                 .select(Shop.id)
                 .join(Withdraw)
                 .where(
                     (Withdraw.shop_currency == self._currency) &
                     (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                     (Withdraw.processed.between(*current_period)) |
                     (Withdraw.processed.between(*prev_month_period)))
                 .distinct())
        log.info("Полученны ID магазинов на вывод, которые будут включены в отчет по валюте %s" % self._currency)

        shops_with_aggregates = (Shop
                                 .select(Shop.id,
                                         Shop.url,
                                         Shop.name,
                                         *calculations_by_dates(self._date, Withdraw, Withdraw.shop_amount))
                                 .join(Withdraw)
                                 .where(
                                      (Shop.id << shops) &
                                      (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                                      (Withdraw.shop_currency == self._currency))
                                 .group_by(Shop.id)
                                 .order_by(Shop.id))
        log.info("Произведена калькуляция сумм и количеств для магазинов на вывод по валюте %s" % self._currency)
        return shops_with_aggregates


class PaywayWithdrawSheet(PaywaySheet):
    def _get_payways(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПН на ввод, которые будут включены в отчет
        payways = (WithdrawPayway
                   .select(WithdrawPayway.id)
                   .join(Withdraw)
                   .where(
                        (Withdraw.shop_currency == self._currency) &
                        (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                        (Withdraw.processed.between(*current_period)) |
                        (Withdraw.processed.between(*prev_month_period)))
                   .distinct())
        log.info("Полученны ID ПН на вывод, которые будут включены в отчет по валюте %s" % self._currency)

        payways_with_aggregates = (WithdrawPayway
                                   .select(WithdrawPayway.id,
                                           WithdrawPayway.name,
                                           WithdrawPayway.paysystem,
                                           *calculations_by_dates(self._date, Withdraw, Withdraw.payee_receive))
                                   .join(Withdraw)
                                   .join(Paysystem, on=(WithdrawPayway.paysystem == Paysystem.id))
                                   .where(
                                        (WithdrawPayway.id << payways) &
                                        (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                                        (Withdraw.ps_currency == self._currency))
                                   .group_by(WithdrawPayway.id)
                                   .order_by(WithdrawPayway.id))
        log.info("Произведена калькуляция сумм и количеств для ПН на вывод по валюте %s" % self._currency)
        return payways_with_aggregates


class PaysystemWithdrawSheet(PaysystemSheet):

    def _get_paysystems(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПС, которые будут включены в отчет
        paysystems = (Paysystem
                      .select(Paysystem.id)
                      .join(WithdrawPayway)
                      .join(Withdraw, on=(Withdraw.payway == WithdrawPayway.id))
                      .where(
                            (Withdraw.shop_currency == self._currency) &
                            (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                            (Withdraw.processed.between(*current_period)) |
                            (Withdraw.processed.between(*prev_month_period)))
                      .distinct())
        log.info("Полученны ID ПС на вывод, которые будут включены в отчет по валюте %s" % self._currency)

        paysystems_with_aggregates = (Paysystem
                                      .select(Paysystem.id,
                                              Paysystem.name,
                                              *calculations_by_dates(self._date, Withdraw, Withdraw.payee_receive))
                                      .join(WithdrawPayway)
                                      .join(Withdraw, on=(Withdraw.payway == WithdrawPayway.id))
                                      .where(
                                           (Paysystem.id << paysystems) &
                                           (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                                           (Withdraw.ps_currency == self._currency))
                                      .group_by(Paysystem.id)
                                      .order_by(Paysystem.id))
        log.info("Произведена калькуляция сумм и количеств для ПС на вывод по валюте %s" % self._currency)
        return paysystems_with_aggregates


class PaymethodWithdrawSheet(PaymethodSheet):

    def _get_paymethods(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПС, которые будут включены в отчет
        paymethods = (PayMethod
                      .select(PayMethod.id)
                      .join(WithdrawPayway)
                      .join(Withdraw, on=(Withdraw.payway == WithdrawPayway.id))
                      .where(
                            (Withdraw.shop_currency == self._currency) &
                            (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                            (Withdraw.processed.between(*current_period)) |
                            (Withdraw.processed.between(*prev_month_period)))
                      .distinct())
        log.info("Полученны ID Платежных методов на вывод, которые будут включены в отчет по валюте %s" % self._currency)

        paymethods_with_aggregates = (PayMethod
                                      .select(PayMethod.id,
                                              PayMethod.name,
                                              *calculations_by_dates(self._date, Withdraw, Withdraw.payee_receive))
                                      .join(WithdrawPayway)
                                      .join(Withdraw, on=(Withdraw.payway == WithdrawPayway.id))
                                      .where(
                                           (PayMethod.id << paymethods) &
                                           (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                                           (Withdraw.ps_currency == self._currency))
                                      .group_by(PayMethod.id)
                                      .order_by(PayMethod.id))
        log.info("Произведена калькуляция сумм и количеств для Платежных методов на вывод по валюте %s" % self._currency)
        return paymethods_with_aggregates
