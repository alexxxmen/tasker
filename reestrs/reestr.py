# -*- coding: utf-8 -*-

import os
import json
import logging
import argparse
from functools import partial

from models import ReportConfig
from utils import is_valid_json, send_email, parse_date, get_yesterday_date, Error, format_date
from config import MAIL_USERNAME, MAIL_SERVER, MAIL_PORT, MAIL_PASSWORD, LOG_TO, LOGGER_FILE,\
    MODERATORS, LOGGER_LEVEL
from registry import Registry


log = logging.getLogger('registry')


send_email = partial(send_email, send_from=MAIL_USERNAME, server=MAIL_SERVER,
                     port=MAIL_PORT, user=MAIL_USERNAME, passwd=MAIL_PASSWORD)


class ReportType:
    InvoiceStatistic = 1
    WithdrawStatistic = 2
    ShopUploading = 3
    PsFeeIncorrect = 4
    ProjectStatistic = 5
    IncorrectInvoices = 6


class UploadOperations(object):

    @classmethod
    def execute(cls, options):
        report_config_id = options.report_config_id
        date_ = options.date
        log.info("Начало работы скрипта reestr за %s" % date_)

        report_config = cls.get_report_config(report_config_id)
        config = cls.get_config(report_config.config)
        recipients = cls.get_recipients(config)

        registry = Registry()
        if report_config.report_type == ReportType.InvoiceStatistic:
            registry.create_invoice_workbooks(date_)
            attachments = registry.get_invoice_workbook_locations()
            subject = 'Отчеты статистики по Invoice за %s ' % format_date(date_)

        elif report_config.report_type == ReportType.WithdrawStatistic:
            registry.create_withdraw_workbooks(date_)
            attachments = registry.get_withdraw_workbook_locations()
            subject = 'Отчеты статистики по Withdraw за %s ' % format_date(date_)

        elif report_config.report_type == ReportType.ShopUploading:
            account_id = str(config.get('account_id', ''))
            shop_id = str(config.get('shop_id', ''))

            shop_report = registry.create_shop_operations_report(account_id, shop_id, date_)
            attachments = (shop_report.filename,)
            subject = 'Реестр операций для аккаунта (%s) за дату (%s)' % (account_id, format_date(date_))
            if shop_id:
                subject = 'Реестр операций для магазина (%s) за дату (%s)' % (shop_id, format_date(date_))

        elif report_config.report_type == ReportType.PsFeeIncorrect:
            report = registry.create_ps_fee_incorrect_report(date_)
            attachments = (report.filename,)
            subject = 'Реестр по расхождению комиссий за %s ' % format_date(date_)

        elif report_config.report_type == ReportType.ProjectStatistic:
            assert 'shop_id' in config, "Укажите shop_id для этой конфигурации: %s" % config
            shop_id = str(config['shop_id'])

            work_book = registry.create_project_invoice_workbook(date_, shop_id)
            attachments = (work_book.location,)
            subject = 'Отчеты статистики по проектам по магазину %s за %s ' % (shop_id, format_date(date_))

        elif report_config.report_type == ReportType.IncorrectInvoices:
            assert 'ik_shop_id' in config, "Укажите ik_shop_id для этой конфигурации: %s" % config
            shop_id = str(config['ik_shop_id'])

            report = registry.create_incorrect_invoices_report(shop_id, date_)
            attachments = (report.filename,)
            subject = 'Отчет некорректных инвойсов по магазину %s за %s ' % (shop_id, format_date(date_))

        else:
            raise Error('Неизвестный тип отчета = %s' % report_config.report_type)

        send_email(subject, subject + '. Хорошего дня!', dest_to=recipients, attachments=attachments)
        log.info("Отчет %s отправлен получателям %s" % (report_config.report_type, recipients))

    @classmethod
    def get_report_config(cls, report_config_id):
        try:
            return ReportConfig.get(ReportConfig.id == report_config_id)
        except ReportConfig.DoesNotExist:
            raise Error('Config c id=%s не найден.' % report_config_id)

    @classmethod
    def get_recipients(cls, config):
        if 'emails' not in config:
            raise Error("Отсутствует поле 'emails' в конфигурации. Текущая конфигурация: %s" % config)
        return config['emails']

    @classmethod
    def get_config(cls, config):
        if not is_valid_json(config):
            raise Error("Поле 'config' должно быть в формате json. Config=%s" % config)
        return json.loads(config)

    @classmethod
    def parser(cls):
        parser = argparse.ArgumentParser(description="Create upload of all operations by shops")
        parser.add_argument("report_config_id",
                            type=int,
                            help="Specify id in `report_configs` table")
        parser.add_argument("date",
                            nargs='?',
                            default=get_yesterday_date(),
                            type=parse_date,
                            help="The date to create upload, if not - return yesterday")
        return parser

    @classmethod
    def main(cls):
        """Run script"""
        options = cls.parser().parse_args()
        try:
            cls.execute(options)
        except Exception as e:
            log.exception(e)
            subject = 'Ошибка при формировании статистики'
            error_msg = 'Ошибка: %s.' % e
            send_email(subject, error_msg, dest_to=MODERATORS)


if __name__ == '__main__':
    file_handler = logging.FileHandler(os.path.join(LOG_TO, LOGGER_FILE))
    file_handler.setLevel(LOGGER_LEVEL)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s:%(message)s"))
    log.addHandler(file_handler)
    log.setLevel(file_handler.level)

    UploadOperations.main()
