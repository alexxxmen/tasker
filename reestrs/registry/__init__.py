# -*- coding: utf-8 -*-

from .workbooks import ShopInvoiceWorkBook, PaywayInvoiceWorkBook, PaysytemInvoiceWorkBook, PaymethodInvoiceWorkBook,\
    ShopWithdrawWorkBook, PaywayWithdrawWorkBook, PaysytemWithdrawWorkBook, PaymethodWithdrawWorkBook,\
    ProjectInvoiceWorkBook
from .csv_files import AccountShopOperationsFile, PsFeeIncorrectFile, IncorrectInvoicesFile, PsFeeDifferenceFile


class Registry(object):

    def __init__(self):
        self.invoice_workbooks = []
        self.withdraw_workbooks = []

    def create_invoice_workbooks(self, date):
        self.create_shop_invoice_workbook(date)
        self.create_payway_invoice_workbook(date)
        self.create_pasysytem_invoice_work_book(date)
        self.create_paymethod_invoice_work_book(date)

    def create_withdraw_workbooks(self, date):
        self.create_shop_withdraw_workbook(date)
        self.create_payway_withdraw_workbook(date)
        self.create_paysystem_withdraw_workbook(date)
        self.create_paymethod_withdraw_workbook(date)

    def create_shop_invoice_workbook(self, date):
        """Создать ежедневный отчет статистики Invoice по магазинам."""
        wb = ShopInvoiceWorkBook('Invoice shops statistic', date)
        self.invoice_workbooks.append(wb)
        return wb

    def create_payway_invoice_workbook(self, date):
        """Создать eжедневный отчет статистики Invoice по Платежным направлениям"""
        wb = PaywayInvoiceWorkBook('Invoice payways statistic', date)
        self.invoice_workbooks.append(wb)
        return wb

    def create_pasysytem_invoice_work_book(self, date):
        """Создать eжедневный отчет статистики Invoice по Платежным системам"""
        wb = PaysytemInvoiceWorkBook('Invoice paysytems statistic', date)
        self.invoice_workbooks.append(wb)
        return wb

    def create_paymethod_invoice_work_book(self, date):
        """Создать eжедневный отчет статистики Invoice по Платежным методам"""
        wb = PaymethodInvoiceWorkBook('Invoice paymethods statistic', date)
        self.invoice_workbooks.append(wb)
        return wb

    def create_shop_withdraw_workbook(self, date):
        wb = ShopWithdrawWorkBook('Withdraw shops statistic', date)
        self.withdraw_workbooks.append(wb)
        return wb

    def create_payway_withdraw_workbook(self, date):
        """Создать eжедневный отчет статистики Withdraw по Платежным направлениям"""
        wb = PaywayWithdrawWorkBook('Withdraw payways statistic', date)
        self.withdraw_workbooks.append(wb)
        return wb

    def create_paysystem_withdraw_workbook(self, date):
        """Создать eжедневный отчет статистики Withdraw по Платежным системам"""
        wb = PaysytemWithdrawWorkBook('Withdraw paysytems statistic', date)
        self.withdraw_workbooks.append(wb)
        return wb

    def create_paymethod_withdraw_workbook(self, date):
        """Создать eжедневный отчет статистики Withdraw по Платежным методам"""
        wb = PaymethodWithdrawWorkBook('Withdraw paymethods statistic', date)
        self.withdraw_workbooks.append(wb)
        return wb

    def create_shop_operations_report(self, account_id, shop_id, date):
        return AccountShopOperationsFile(account_id, shop_id, date)

    def create_ps_fee_incorrect_report(self, date):
        return PsFeeIncorrectFile(date)

    def get_workbook_locations(self, wb_list):
        return tuple([wb.location for wb in wb_list])

    def get_invoice_workbook_locations(self):
        return self.get_workbook_locations(self.invoice_workbooks)

    def get_withdraw_workbook_locations(self):
        return self.get_workbook_locations(self.withdraw_workbooks)

    def create_project_invoice_workbook(self, date, shop_id):
        """Создать ежедневный отчет статистики Invoice по проектам."""
        return ProjectInvoiceWorkBook('Invoice projects statistic', date, shop_id)

    def create_incorrect_invoices_report(self, shop_id, date):
        return IncorrectInvoicesFile(shop_id, date)

    def create_ps_fee_difference_report(self, date):
        return PsFeeDifferenceFile(date)
