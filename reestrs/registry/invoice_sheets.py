# -*- coding: utf-8 -*-

import logging

from models import InvoicePayway, Invoice, Paysystem, Shop, PayMethod, Project
from utils import get_period_range, previous_month_day
from .sheets import calculations_by_dates, PaymethodSheet, PaysystemSheet, PaywaySheet, ShopSheet, ProjectSheet


log = logging.getLogger(__name__)


SUCCESS_INVOICE_STATUS = 3


class ShopInvoiceSheet(ShopSheet):
    def _get_shops(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки магазинов на ввод, которые будут включены в отчет
        shops = (Shop
                 .select(Shop.id)
                 .join(Invoice)
                 .where(
                     (Invoice.shop_currency == self._currency) &
                     (Invoice.status == SUCCESS_INVOICE_STATUS) &
                     (Invoice.processed.between(*current_period)) |
                     (Invoice.processed.between(*prev_month_period)))
                 .distinct())
        log.info("Полученны ID магазинов на ввод, которые будут включены в отчет по валюте %s" % self._currency)

        shops_with_aggregates = (Shop
                                 .select(Shop.id,
                                         Shop.url,
                                         Shop.name,
                                         *calculations_by_dates(self._date, Invoice, Invoice.shop_amount))
                                 .join(Invoice)
                                 .where(
                                      (Shop.id << shops) &
                                      (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                      (Invoice.shop_currency == self._currency))
                                 .group_by(Shop.id)
                                 .order_by(Shop.id))
        log.info("Произведена калькуляция сумм и количеств для магазинов по валюте %s" % self._currency)
        return shops_with_aggregates


class PaywayInvoiceSheet(PaywaySheet):
    def _get_payways(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПН на ввод, которые будут включены в отчет
        payways = (InvoicePayway
                   .select(InvoicePayway.id)
                   .join(Invoice)
                   .where(
                        (Invoice.shop_currency == self._currency) &
                        (Invoice.status == SUCCESS_INVOICE_STATUS) &
                        (Invoice.processed.between(*current_period)) |
                        (Invoice.processed.between(*prev_month_period)))
                   .distinct())
        log.info("Полученны ID ПН на ввод, которые будут включены в отчет по валюте %s" % self._currency)

        payways_with_aggregates = (InvoicePayway
                                   .select(InvoicePayway.id,
                                           InvoicePayway.name,
                                           InvoicePayway.paysystem,
                                           *calculations_by_dates(self._date, Invoice, Invoice.ps_amount))
                                   .join(Invoice)
                                   .join(Paysystem, on=(InvoicePayway.paysystem == Paysystem.id))
                                   .where(
                                        (InvoicePayway.id << payways) &
                                        (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                        (Invoice.ps_currency == self._currency))
                                   .group_by(InvoicePayway.id)
                                   .order_by(InvoicePayway.id))
        log.info("Произведена калькуляция сумм и количеств для ПН на ввод по валюте %s" % self._currency)
        return payways_with_aggregates


class PaysystemInvoiceSheet(PaysystemSheet):
    def _get_paysystems(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПС, которые будут включены в отчет
        paysystems = (Paysystem
                      .select(Paysystem.id)
                      .join(InvoicePayway)
                      .join(Invoice, on=(Invoice.payway == InvoicePayway.id))
                      .where(
                            (Invoice.shop_currency == self._currency) &
                            (Invoice.status == SUCCESS_INVOICE_STATUS) &
                            (Invoice.processed.between(*current_period)) |
                            (Invoice.processed.between(*prev_month_period)))
                      .distinct())
        log.info("Полученны ID ПС на ввод, которые будут включены в отчет по валюте %s" % self._currency)

        paysystems_with_aggregates = (Paysystem
                                      .select(Paysystem.id,
                                              Paysystem.name,
                                              *calculations_by_dates(self._date, Invoice, Invoice.ps_amount))
                                      .join(InvoicePayway)
                                      .join(Invoice, on=(Invoice.payway == InvoicePayway.id))
                                      .where(
                                           (Paysystem.id << paysystems) &
                                           (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                           (Invoice.ps_currency == self._currency))
                                      .group_by(Paysystem.id)
                                      .order_by(Paysystem.id))
        log.info("Произведена калькуляция сумм и количеств для ПС на ввод по валюте %s" % self._currency)
        return paysystems_with_aggregates


class PaymethodInvoiceSheet(PaymethodSheet):
    def _get_paymethods(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки ПС, которые будут включены в отчет
        paymethods = (PayMethod
                      .select(PayMethod.id)
                      .join(InvoicePayway)
                      .join(Invoice, on=(Invoice.payway == InvoicePayway.id))
                      .where(
                            (Invoice.shop_currency == self._currency) &
                            (Invoice.status == SUCCESS_INVOICE_STATUS) &
                            (Invoice.processed.between(*current_period)) |
                            (Invoice.processed.between(*prev_month_period)))
                      .distinct())
        log.info("Полученны ID Платежных методов на ввод, которые будут включены в отчет по валюте %s" % self._currency)

        paymethods_with_aggregates = (PayMethod
                                      .select(PayMethod.id,
                                              PayMethod.name,
                                              *calculations_by_dates(self._date, Invoice, Invoice.ps_amount))
                                      .join(InvoicePayway)
                                      .join(Invoice, on=(Invoice.payway == InvoicePayway.id))
                                      .where(
                                           (PayMethod.id << paymethods) &
                                           (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                           (Invoice.ps_currency == self._currency))
                                      .group_by(PayMethod.id)
                                      .order_by(PayMethod.id))
        log.info("Произведена калькуляция сумм и количеств для Платежных методов на ввод по валюте %s" % self._currency)
        return paymethods_with_aggregates


class ProjectInvoiceSheet(ProjectSheet):
    def __init__(self, wb, title, currency, date, shop_id):
        self._shop_id = shop_id
        super(ProjectInvoiceSheet, self).__init__(wb, title, currency, date)

    def _get_projects(self):
        current_period = get_period_range(self._date)
        prev_month_period = get_period_range(previous_month_day(self._date))

        # ID'ки проектов на ввод, которые будут включены в отчет
        projects = (Project
                    .select(Project.id)
                    .join(Invoice)
                    .where(
                        (Project.shop_id == self._shop_id) &
                        (Invoice.shop_currency == self._currency) &
                        (Invoice.status == SUCCESS_INVOICE_STATUS) &
                        (Invoice.processed.between(*current_period)) |
                        (Invoice.processed.between(*prev_month_period)))
                    .group_by(Project.id))
        log.info("Полученны ID проектов на ввод, которые будут включены в отчет по валюте %s" % self._currency)

        projects_with_aggregates = (Project
                                    .select(Project.id,
                                            Project.url,
                                            *calculations_by_dates(self._date, Invoice, Invoice.shop_amount))
                                    .join(Invoice)
                                    .where(
                                         (Project.id << projects) &
                                         (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                         (Invoice.shop_currency == self._currency))
                                    .group_by(Project.id)
                                    .order_by(Project.id))
        log.info("Произведена калькуляция сумм и количеств для проектов по валюте %s" % self._currency)
        return projects_with_aggregates
