# -*- coding: utf-8 -*-

import logging
import csv
from collections import namedtuple

from peewee import fn

from utils import get_day_range, format_date, get_period_range
from config import PAYMENT_INFO_DIR, PS_FEE_INCORRECT_DIR, INCORRECT_INVOICES_DIR
from models import (Shop,
                    Invoice,
                    InvoicePayway,
                    Withdraw,
                    Account,
                    ShopPurse,
                    SystemShopTransfer,
                    SystemInvoice,
                    SystemWithdraw,
                    ShopInvoiceTransaction,
                    ShopWithdrawTransaction,
                    ShopSystemInvoiceTransaction,
                    ShopSystemWithdrawTransaction,
                    ShopTransferWriteOffTransaction,
                    ShopTransferReceiveTransaction,
                    Project)


log = logging.getLogger(__name__)


SUCCESS_INVOICE_STATUS = 3
SUCCESS_WITHDRAW_STATUS = 5

MIN_DIFFERENCE = 0.01


ShopPaymentInfo = namedtuple('ShopPaymentInfo', ['operation_id',
                                                 'processed',
                                                 'shop_refund',
                                                 'shop_write_off',
                                                 'shop_fee',
                                                 'currency',
                                                 'shop_balance',
                                                 'shop_id',
                                                 'shop_payment_id',
                                                 'desc',
                                                 'comments'])


def round_number(number, ndigits=2):
    return round(number, ndigits)


def divide_decimals(number1, number2):
    try:
        return round_number(number1 / number2)
    except ZeroDivisionError:
        raise


def subtract_decimals(number1, number2):
    return round_number(number1 - number2)


def format_number(number):
    return str(number).replace('.', ',')


class AccountShopOperationsFile(object):

    def __init__(self, account_id, shop_id, date):
        self.account_id = account_id
        self.shop_id = shop_id
        self._date = date
        self.filename = PAYMENT_INFO_DIR + 'Payment_info_%s.csv' % format_date(date)

        if account_id:
            self._verify_account()

        if shop_id:
            self._verify_shop()
            self.shop_ids = (shop_id,)
        else:
            self.shop_ids = self._get_shop_ids()

        self._save()

    def _get_shop_ids(self):
        shops = Shop.select(Shop.id).where(Shop.account == self.account_id).order_by(Shop.id)
        return [shop.id for shop in shops]

    def _verify_account(self):
        account = Account.get_by_id(self.account_id)
        if account is None:
            raise ValueError('Аккаунт с account_id=%s не существует' % self.account_id)

    def _verify_shop(self):
        shop = Shop.get_by_id(self.shop_id)
        if shop is None:
            raise ValueError('Магазин с shop_id=%s не существует' % self.shop_id)

    def _get_date_range(self):
        return get_day_range(self._date)

    def _get_statement(self):
        shop_purses = ShopPurse.select(ShopPurse.id).where(ShopPurse.shop << self.shop_ids)
        date_range = self._get_date_range()

        statement = []

        # Get shop invoice data & add it to info
        invoice_transactions = (ShopInvoiceTransaction
                                .select(ShopInvoiceTransaction, Invoice)
                                .join(Invoice)
                                .where(
                                    (Invoice.status == SUCCESS_INVOICE_STATUS) &
                                    (ShopInvoiceTransaction.shop_purse << shop_purses) &
                                    (ShopInvoiceTransaction.processed.between(*date_range)))
                                .order_by(ShopInvoiceTransaction.processed.desc()))

        for t in invoice_transactions:
            shop_fee = divide_decimals(t.invoice.shop_fee, t.invoice.exch_rate)
            statement.append(ShopPaymentInfo(
                operation_id=t.invoice.id,
                processed=t.invoice.processed,
                shop_refund=t.invoice.shop_refund,
                shop_write_off='',
                shop_fee=shop_fee,
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.invoice.shop_id,
                shop_payment_id=t.invoice.shop_invoice_id,
                desc='invoice',
                comments=t.invoice.description))

        # Get shop withdraw data & add it to info
        withdraw_transactions = (ShopWithdrawTransaction
                                 .select(ShopWithdrawTransaction, Withdraw)
                                 .join(Withdraw)
                                 .where(
                                    (Withdraw.status == SUCCESS_WITHDRAW_STATUS) &
                                    (ShopWithdrawTransaction.shop_purse << shop_purses) &
                                    (ShopWithdrawTransaction.processed.between(*date_range)))
                                 .order_by(ShopWithdrawTransaction.processed.desc()))

        for t in withdraw_transactions:
            shop_fee = divide_decimals(t.withdraw.fee, t.withdraw.exch_rate)
            statement.append(ShopPaymentInfo(
                operation_id=t.withdraw.id,
                processed=t.withdraw.processed,
                shop_refund='',
                shop_write_off=t.withdraw.shop_write_off,
                shop_fee=shop_fee,
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.withdraw.shop_id,
                shop_payment_id=t.withdraw.shop_payment_id,
                desc='withdraw',
                comments=t.withdraw.description))

        # Get shop sys_invoice data & add it to info
        sys_invoice_transactions = (ShopSystemInvoiceTransaction
                                    .select(ShopSystemInvoiceTransaction, SystemInvoice)
                                    .join(SystemInvoice)
                                    .where(
                                        (ShopSystemInvoiceTransaction.shop_purse << shop_purses) &
                                        (ShopSystemInvoiceTransaction.processed.between(*date_range)))
                                    .order_by(ShopSystemInvoiceTransaction.processed.desc()))

        for t in sys_invoice_transactions:
            statement.append(ShopPaymentInfo(
                operation_id=t.invoice.id,
                processed=t.invoice.created,
                shop_refund=t.invoice.shop_refund_amount,
                shop_write_off='',
                shop_fee='',
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.invoice.shop_id,
                shop_payment_id='',
                desc='system_invoice',
                comments=t.invoice.msg))

        # Get shop sys_withdraw data & add it to info
        sys_withdraw_transactions = (ShopSystemWithdrawTransaction
                                     .select(ShopSystemWithdrawTransaction, SystemWithdraw)
                                     .join(SystemWithdraw)
                                     .where(
                                         (ShopSystemWithdrawTransaction.shop_purse << shop_purses) &
                                         (ShopSystemWithdrawTransaction.processed.between(*date_range)))
                                     .order_by(ShopSystemWithdrawTransaction.processed.desc()))

        for t in sys_withdraw_transactions:
            statement.append(ShopPaymentInfo(
                operation_id=t.withdraw.id,
                processed=t.withdraw.created,
                shop_refund='',
                shop_write_off=t.withdraw.shop_write_off_amount,
                shop_fee='',
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.withdraw.shop_id,
                shop_payment_id='',
                desc='system_withdraw',
                comments=t.withdraw.msg))

        target_shop_ids = (SystemShopTransfer
                           .select(SystemShopTransfer.target_shop)
                           .where(SystemShopTransfer.target_shop << self.shop_ids)
                           .distinct())

        target_shop_purses = (ShopPurse
                              .select(ShopPurse.id, ShopPurse.shop)
                              .where(ShopPurse.shop << target_shop_ids)
                              .alias('target_shop_purses'))

        transfer_transactions = (ShopTransferReceiveTransaction
                                 .select(ShopTransferReceiveTransaction, SystemShopTransfer)
                                 .join(SystemShopTransfer)
                                 .join(target_shop_purses, on=(
                                    (ShopTransferReceiveTransaction.shop_purse == target_shop_purses.c.id) &
                                    (SystemShopTransfer.target_shop == target_shop_purses.c.shop_id)))
                                 .where(ShopTransferReceiveTransaction.processed.between(*date_range))
                                 .order_by(ShopTransferReceiveTransaction.processed.desc()))

        for t in transfer_transactions:
            shop_fee = subtract_decimals(t.transfer.target_amount, t.transfer.target_receive)
            statement.append(ShopPaymentInfo(
                operation_id=t.transfer.id,
                processed=t.transfer.created,
                shop_refund=t.transfer.target_receive,
                shop_write_off='',
                shop_fee=shop_fee,
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.transfer.target_shop_id,
                shop_payment_id='',
                desc='system_transfer',
                comments=t.transfer.comments))

        source_shop_ids = (SystemShopTransfer
                           .select(SystemShopTransfer.source_shop)
                           .where(SystemShopTransfer.source_shop << self.shop_ids)
                           .distinct())

        source_shop_purses = (ShopPurse
                              .select(ShopPurse.id, ShopPurse.shop)
                              .where(ShopPurse.shop << source_shop_ids)
                              .alias('source_shop_purses'))

        transfer_transactions = (ShopTransferWriteOffTransaction
                                 .select(ShopTransferWriteOffTransaction, SystemShopTransfer)
                                 .join(SystemShopTransfer)
                                 .join(source_shop_purses, on=(
                                    (ShopTransferWriteOffTransaction.shop_purse == source_shop_purses.c.id) &
                                    (SystemShopTransfer.source_shop == source_shop_purses.c.shop_id)))
                                 .where(ShopTransferWriteOffTransaction.processed.between(*date_range))
                                 .order_by(ShopTransferWriteOffTransaction.processed.desc()))

        for t in transfer_transactions:
            shop_fee = subtract_decimals(t.transfer.source_write_off, t.transfer.source_amount)
            statement.append(ShopPaymentInfo(
                operation_id=t.transfer.id,
                processed=t.transfer.created,
                shop_refund='',
                shop_write_off=t.transfer.source_write_off,
                shop_fee=shop_fee,
                currency=t.currency,
                shop_balance=t.shop_purse_balance,
                shop_id=t.transfer.source_shop_id,
                shop_payment_id='',
                desc='system_transfer',
                comments=t.transfer.comments))

        return statement

    def _save(self):
        header = ["ID операции", "Время проведения", "Зачислено на магазин", "Списано с магазина", "Комиссия",
                  "Валюта", "Баланс", "ID магазина", "ID платежа магазина", "Описание", "Комментарий"]

        with open(self.filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # Write header
            writer.writerow(header)

            statement = self._get_statement()
            for record in sorted(statement, key=lambda r: r.processed, reverse=True):
                writer.writerow([
                    record.operation_id,
                    record.processed.strftime('%d-%m-%Y %H:%M:%S') if record.processed else '',
                    round_number(record.shop_refund) if record.shop_refund else 0,
                    round_number(record.shop_write_off) if record.shop_write_off else 0,
                    record.shop_fee if record.shop_fee else 0,
                    record.currency,
                    round_number(record.shop_balance) if record.shop_balance else 0,
                    record.shop_id,
                    record.shop_payment_id,
                    record.desc,
                    record.comments.encode('utf-8') if record.comments else '',
                ])

        log.info("Файл %s успешно создан." % self.filename)


class PsFeeIncorrectFile(object):

    def __init__(self, date):
        self._date = date
        self.filename = PS_FEE_INCORRECT_DIR + 'ps_fee_incorrect_%s.csv' % format_date(date)
        self._save()

    def _get_date_range(self):
        return get_day_range(self._date)

    def _get_query(self):
        date_range = self._get_date_range()

        query = (Invoice
                 .select(
                    Invoice.id,
                    Invoice.shop,
                    Invoice.ps_fee,
                    Invoice.ps_comission_amount,
                    Invoice.payway,
                    Invoice.ps_currency,
                    Invoice.processed,
                    InvoicePayway.name)
                 .join(InvoicePayway)
                 .where(
                    ~(Invoice.ps_comission_amount >> None) &
                    (Invoice.status == SUCCESS_INVOICE_STATUS) &
                    (fn.ABS(Invoice.ps_fee - Invoice.ps_comission_amount) > MIN_DIFFERENCE) &
                    (Invoice.processed.between(*date_range))))
        return query

    def _save(self):
        header = ["shop_id", "id invoice", "payway_id", "payway_name", "ps_fee",
                  "ps_comission_amount", "difference", "ps_currency", "processed"]

        with open(self.filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Write header
            writer.writerow(header)

            for invoice in self._get_query():
                writer.writerow([
                    invoice.shop_id,
                    invoice.id,
                    invoice.payway_id,
                    invoice.payway.name,
                    format_number(invoice.ps_fee),
                    format_number(invoice.ps_comission_amount),
                    format_number(invoice.ps_fee - invoice.ps_comission_amount),
                    invoice.ps_currency,
                    invoice.processed.strftime('%d-%m-%Y %H:%M:%S') if invoice.processed else '',
                ])

        log.info("Файл %s успешно создан." % self.filename)


class IncorrectInvoicesFile(object):
    def __init__(self, shop_id, date):
        self._verify_shop(shop_id)
        self._date = date
        self._shop_id = shop_id
        self.filename = INCORRECT_INVOICES_DIR + 'ik_incorrect_invoices_%s.csv' % format_date(date)
        self._save()

    def _get_query(self):
        date_range = self._get_date_range()

        query = (Invoice
                 .select(Invoice, Project.url, InvoicePayway.name)
                 .join(Project)
                 .switch(Invoice)
                 .join(InvoicePayway)
                 .where(
                    (Invoice.shop == self._shop_id) &
                    (Invoice.created.between(*date_range)))
                 .order_by(Invoice.id))

        return query

    def _get_incorrect_invoices(self):
        invoices = self._get_query()
        return [inv for inv in invoices if self._is_invoice_incorrect(inv)]

    def _is_invoice_incorrect(self, invoice):
        return invoice.project.url != invoice.ik_shop_url

    def _get_date_range(self):
        return get_day_range(self._date)

    def _verify_shop(self, shop_id):
        shop = Shop.get_by_id(shop_id)
        if shop is None:
            raise ValueError('Магазин с shop_id=%s не существует' % self.shop_id)

    def _save(self):
        header = ["invoice_id", "shop_invoice_id", "created", "status", "shop_amount",
                  "shop_currency", "payway (id)", "project_id", "project_url", "ik_shop_url"]

        with open(self.filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Write header
            writer.writerow(header)

            for invoice in self._get_incorrect_invoices():
                writer.writerow([
                    invoice.id,
                    invoice.shop_invoice_id,
                    invoice.created.strftime('%d-%m-%Y %H:%M:%S'),
                    invoice.status,
                    invoice.shop_amount,
                    invoice.shop_currency,
                    '{0} ({1})'.format(invoice.payway.name, invoice.payway_id),
                    invoice.project_id,
                    invoice.project.url,
                    invoice.ik_shop_url,
                ])

        log.info("Файл %s успешно создан." % self.filename)


class PsFeeDifferenceFile(object):

    def __init__(self, date):
        self._date = date
        self.filename = PS_FEE_INCORRECT_DIR + 'ps_fee_difference_%s.csv' % format_date(date)
        self._save()

    def _get_date_range(self):
        return get_period_range(self._date)

    def _get_query(self):
        date_range = self._get_date_range()

        query = (Invoice
                 .select(fn.SUM(Invoice.ps_fee).alias('ps_fee'),
                         fn.SUM(Invoice.ps_comission_amount).alias('ps_comission_amount'),
                         Invoice.ps_currency,
                         InvoicePayway.name)
                 .join(InvoicePayway)
                 .where(
                    ~(Invoice.ps_comission_amount >> None) &
                    (Invoice.status == SUCCESS_INVOICE_STATUS) &
                    (fn.ABS(Invoice.ps_fee - Invoice.ps_comission_amount) > MIN_DIFFERENCE) &
                    (Invoice.processed.between(*date_range)))
                 .group_by(InvoicePayway.name, Invoice.ps_currency))
        return query

    def _save(self):
        header = ["payway_name", "ps_fee", "ps_comission_amount", "difference", "ps_currency"]

        with open(self.filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Write header
            writer.writerow(header)

            for invoice in self._get_query():
                writer.writerow([
                    invoice.payway.name,
                    format_number(invoice.ps_fee),
                    format_number(invoice.ps_comission_amount),
                    format_number(invoice.ps_fee - invoice.ps_comission_amount),
                    invoice.ps_currency,
                ])

        log.info("Файл %s успешно создан." % self.filename)
