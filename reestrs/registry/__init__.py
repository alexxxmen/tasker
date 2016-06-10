# -*- coding: utf-8 -*-

from utils import format_date, get_month_name
from .workbooks import ShopInvoiceWorkBook, PaywayInvoiceWorkBook, PaysytemInvoiceWorkBook, PaymethodInvoiceWorkBook,\
    ShopWithdrawWorkBook, PaywayWithdrawWorkBook, PaysytemWithdrawWorkBook, PaymethodWithdrawWorkBook,\
    ProjectInvoiceWorkBook
from .csv_files import AccountShopOperationsFile, PsFeeIncorrectFile, IncorrectInvoicesFile, PsFeeDifferenceFile


class Report(object):
    """Base report class"""
    def __init__(self, date, **params):
        self.date = date

    def get_subject(self):
        raise NotImplementedError("Override `get_subject` method")

    def get_data(self):
        raise NotImplementedError("Override `get_data` method")


class InvoiceStatisticReport(Report):
    """Отчет статистики Invoice по магазинам, платежным направлениям, платежным методам, платежным системам"""
    def __init__(self, date, **params):
        super(InvoiceStatisticReport, self).__init__(date, **params)
        self.workbooks = [
            ShopInvoiceWorkBook('Invoice shops statistic', date),
            PaywayInvoiceWorkBook('Invoice payways statistic', date),
            PaysytemInvoiceWorkBook('Invoice paysytems statistic', date),
            PaymethodInvoiceWorkBook('Invoice paymethods statistic', date),
        ]

    def get_subject(self):
        return 'Отчеты статистики по Invoice за {}'.format(format_date(self.date))

    def get_data(self):
        return tuple([wb.location for wb in self.workbooks])


class WithdrawStatisticReport(Report):
    """Отчет статистики Withdraw по магазинам, платежным направлениям, платежным методам, платежным системам"""
    def __init__(self, date, **params):
        super(WithdrawStatisticReport, self).__init__(date, **params)
        self.workbooks = [
            ShopWithdrawWorkBook('Withdraw shops statistic', date),
            PaywayWithdrawWorkBook('Withdraw payways statistic', date),
            PaysytemWithdrawWorkBook('Withdraw paysytems statistic', date),
            PaymethodWithdrawWorkBook('Withdraw paymethods statistic', date),
        ]

    def get_subject(self):
        return 'Отчеты статистики по Withdraw за {}'.format(format_date(self.date))

    def get_data(self):
        return tuple([wb.location for wb in self.workbooks])


class ShopUploadingReport(Report):
    """Отчет статистики по выводам"""
    def __init__(self, date, **params):
        super(ShopUploadingReport, self).__init__(date, **params)
        self.account_id = str(params.get('account_id', ''))
        self.shop_id = str(params.get('shop_id', ''))
        self.shop_report = AccountShopOperationsFile(self.account_id, self.shop_id, date)

    def get_subject(self):
        subject = 'Реестр операций для аккаунта (%s) за дату (%s)' % (self.account_id, format_date(self.date))
        if self.shop_id:
            subject = 'Реестр операций для магазина (%s) за дату (%s)' % (self.shop_id, format_date(self.date))

        return subject

    def get_data(self):
        return self.shop_report.filename


class PsFeeIncorrectReport(Report):
    """Отчет по расхождению комиссий"""
    def __init__(self, date, **params):
        super(PsFeeIncorrectReport, self).__init__(date, **params)
        self.report = PsFeeIncorrectFile(date)

    def get_subject(self):
        return 'Реестр по расхождению комиссий за {}'.format(format_date(self.date))

    def get_data(self):
        return self.report.filename


class ProjectStatisticReport(Report):
    """Отчеты статистики по проектам"""
    def __init__(self, date, **params):
        super(ProjectStatisticReport, self).__init__(date, **params)
        assert 'shop_id' in params, "Укажите shop_id для этой конфигурации: %s" % params
        self.shop_id = str(params['shop_id'])
        self.workbook = ProjectInvoiceWorkBook('Invoice projects statistic', self.date, self.shop_id)

    def get_subject(self):
        return 'Отчеты статистики по проектам по магазину {0} за {1}'.format(self.shop_id, format_date(self.date))

    def get_data(self):
        return self.workbook.location


class IncorrectInvoicesReport(Report):
    """Отчет некорректных инвойсов"""
    def __init__(self, date, **params):
        super(IncorrectInvoicesReport, self).__init__(date, **params)
        assert 'ik_shop_id' in params, "Укажите ik_shop_id для этой конфигурации: %s" % params
        self.shop_id = str(params['ik_shop_id'])
        self.report = IncorrectInvoicesFile(self.shop_id, self.date)

    def get_subject(self):
        return 'Отчет некорректных инвойсов по магазину {0} за {1}'.format(self.shop_id, format_date(self.date))

    def get_data(self):
        return self.report.filename


class PsFeeDifferenceReport(Report):
    """Отчет по расхождению комиссий"""
    def __init__(self, date, **params):
        super(PsFeeDifferenceReport, self).__init__(date, **params)
        self.report = PsFeeDifferenceFile(date)

    def get_subject(self):
        return 'Реестр по расхождению комиссий за {}'.format(get_month_name(self.date.month).encode('utf-8'))

    def get_data(self):
        return self.report.filename


class Registry(object):
    """Class Registry contains all reports and registries."""
    def __init__(self):
        self.report_types = {
            "1": InvoiceStatisticReport,
            "2": WithdrawStatisticReport,
            "3": ShopUploadingReport,
            "4": PsFeeIncorrectReport,
            "5": ProjectStatisticReport,
            "6": IncorrectInvoicesReport,
            "7": PsFeeDifferenceReport,
        }

    def get_report(self, report_type, config, date):
        if str(report_type) not in self.report_types:
            raise Exception("Неизвестный тип отчета: %s" % report_type)

        return self.report_types[str(report_type)](date, **config)
