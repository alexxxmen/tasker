# -*- coding: utf-8 -*-
import os
import logging
import argparse

from reestrs.registry import Registry
from models import ReportConfig
from utils import Logger, send_email, parse_date, get_yesterday_date
from config import MAIL_USERNAME, MAIL_SERVER, MAIL_PORT, MAIL_PASSWORD, LOG_TO, LOGGER
from script import Script


file_handler = logging.FileHandler(os.path.join(LOG_TO, LOGGER.reestr_file))
file_handler.setLevel(LOGGER.level)
file_handler.setFormatter(LOGGER.formatter)
logger = Logger('reestrs', file_handler)


def get_report_config(report_config_id):
    try:
        return ReportConfig.get(ReportConfig.id == report_config_id)
    except ReportConfig.DoesNotExist:
        raise Exception('Config c id=%s не найден.' % report_config_id)


class RegistryScript(Script):

    @classmethod
    def execute(cls, options):
        logger.info("Начало работы скрипта reestr за %s" % options.date)
        report_config = get_report_config(options.report_config_id)
        config = report_config.get_config()

        registry = Registry()
        report = registry.get_report(report_config.report_type, config, options.date)
        recipients = config.get('emails')
        if not recipients:
            raise Exception("Отсутствует поле 'emails' в конфигурации. Текущая конфигурация: %s" % config)

        subject = report.get_subject()
        attachments = report.get_data()

        send_email(subject, subject + '. Хорошего дня!',
                   send_from=MAIL_USERNAME,
                   dest_to=recipients,
                   server=MAIL_SERVER,
                   port=MAIL_PORT,
                   user=MAIL_USERNAME,
                   passwd=MAIL_PASSWORD,
                   attachments=attachments)
        logger.info("Отчет %s отправлен получателям %s" % (report_config.report_type, recipients))

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


if __name__ == '__main__':
    RegistryScript.run()
