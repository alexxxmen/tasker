# -*- coding: utf8 -*-

import json

from peewee import Model, CharField, DateTimeField, ForeignKeyField, TextField, IntegerField, DecimalField,\
    BooleanField
from playhouse.pool import PooledPostgresqlExtDatabase
from config import TRIO_DB_CONFIG, ADMIN_DB_CONFIG

SUCCESS_INVOICE_STATUS = 3

admin_db = PooledPostgresqlExtDatabase(**ADMIN_DB_CONFIG)
admin_db.commit_select = True
admin_db.autorollback = True


class ReportConfig(Model):
    class Meta:
        database = admin_db
        db_table = "report_configs"

    report_type = IntegerField()
    config = TextField()
    description = TextField()


trio_db = PooledPostgresqlExtDatabase(**TRIO_DB_CONFIG)
trio_db.commit_select = True
trio_db.autorollback = True


class BaseModel(Model):
    class Meta:
        database = trio_db

    def save(self, **kwds):
        with trio_db.transaction():
            Model.save(self, **kwds)

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.get(cls.id == id)
        except cls.DoesNotExist:
            return None


class Currency(BaseModel):
    class Meta:
        db_table = "currency"

    code = IntegerField(primary_key=True)
    alias = CharField()


class PayMethod(BaseModel):
    class Meta:
        db_table = "pay_methods"

    name = CharField()
    description = CharField()

    def __repr__(self):
        return self.name.encode('utf-8')


class Paysystem(BaseModel):
    class Meta:
        db_table = "paysystems"

    name = CharField()

    def __repr__(self):
        return self.name


class InvoicePayway(BaseModel):
    class Meta:
        db_table = "invoice_payways"

    name = CharField()
    paysystem = ForeignKeyField(Paysystem)
    pay_method = ForeignKeyField(PayMethod)

    def __repr__(self):
        return self.name.encode('utf-8')


class WithdrawPayway(BaseModel):
    class Meta:
        db_table = "withdraw_payways"

    name = CharField()
    paysystem = ForeignKeyField(Paysystem)
    pay_method = ForeignKeyField(PayMethod)


class Account(BaseModel):
    class Meta:
        db_table = "accounts"

    email = CharField()

    def __unicode__(self):
        return self.email


class Shop(BaseModel):
    class Meta:
        db_table = "shops"

    account = ForeignKeyField(Account, related_name="shops")
    status = IntegerField()
    name = CharField()
    description = CharField()
    url = CharField()
    protocol_config = TextField()
    shop_type = IntegerField()


class Project(BaseModel):
    class Meta:
        db_table = "projects"

    shop = ForeignKeyField(Shop)
    url = CharField()
    description = CharField()
    config = TextField(null=True)
    is_active = BooleanField(default=False)


class Invoice(BaseModel):
    class Meta:
        db_table = "invoices"

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(InvoicePayway)
    status = IntegerField()
    created = DateTimeField()
    description = CharField()
    add_ons = TextField()
    shop_invoice_id = CharField()
    shop_currency = IntegerField()
    shop_amount = DecimalField()
    exch_rate = DecimalField()
    ps_currency = IntegerField()
    client_price = DecimalField()
    ps_refund = DecimalField()
    shop_refund = DecimalField()
    processed = DateTimeField()
    ps_amount = DecimalField()
    shop_fee = DecimalField()
    ps_fee = DecimalField()
    ps_comission_amount = DecimalField()

    project = ForeignKeyField(Project, null=True)

    @property
    def paymethod(self):
        return self.payway.pay_method

    @property
    def ik_shop_url(self):
        add_ons = json.loads(self.add_ons) if self.add_ons else {}
        return add_ons.get("ik_shop_url", "")


class Withdraw(BaseModel):
    class Meta:
        db_table = "withdraws"

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(WithdrawPayway)
    status = IntegerField()
    created = DateTimeField()
    shop_payment_id = CharField()
    shop_currency = IntegerField()

    account = TextField()
    description = CharField()
    add_ons = TextField()
    exch_rate = DecimalField()
    exch_fee_percent = DecimalField()
    ps_currency = IntegerField()

    shop_amount = DecimalField()
    ps_amount = DecimalField()

    payee_receive = DecimalField()
    ps_transfer = DecimalField()
    ps_fee = DecimalField()
    exch_fee = DecimalField()
    fee = DecimalField()
    ps_write_off = DecimalField()
    shop_write_off = DecimalField()
    total_fee_inc = DecimalField()
    net_fee_inc = DecimalField()

    processed = DateTimeField()
    ps_payment_id = CharField()
    ps_processed = DateTimeField()
    ps_data = TextField()
    ps_comission_amount = DecimalField()


class ShopPurse(BaseModel):
    class Meta:
        db_table = "shop_purses"

    name = CharField()
    currency = IntegerField()
    shop = ForeignKeyField(Shop, related_name="purses")
    balance = DecimalField()


class SystemInvoice(BaseModel):
    class Meta:
        db_table = "system_invoices"

    shop = ForeignKeyField(Shop)
    comments = TextField()
    ps_receive_amount = DecimalField()  # Сумма, на которую необходимо увеличить баланс ПС
    shop_refund_amount = DecimalField()  # Сумма, на которую необходимо увеличить баланс магазина
    created = DateTimeField()
    margin_amount = DecimalField()
    ps_data = TextField()
    ps_processed = DateTimeField()
    ps_invoice_id = TextField()
    ps_comission_amount = DecimalField()
    ps_currency = IntegerField()
    shop_currency = IntegerField()

    def _get_comments(self):
        return json.loads(self.comments)

    @property
    def msg(self):
        return self._get_comments().get('msg')

    @property
    def exch_rate(self):
        return self._get_comments().get('exch_rate')


class SystemWithdraw(BaseModel):
    class Meta:
        db_table = "system_withdraws"

    shop = ForeignKeyField(Shop)
    comments = TextField()
    ps_write_off_amount = DecimalField()  # Сумма, на которую необходимо уменьшить баланс ПС
    shop_write_off_amount = DecimalField()  # Сумма, на которую необходимо уменьшить баланс магазина
    created = DateTimeField()
    margin_amount = DecimalField()
    ps_processed = DateTimeField()
    ps_withdraw_id = TextField()
    ps_comission_amount = DecimalField()
    ps_currency = IntegerField()
    shop_currency = IntegerField()

    def _get_comments(self):
        return json.loads(self.comments)

    @property
    def msg(self):
        return self._get_comments().get('msg')


class SystemShopTransfer(BaseModel):
    class Meta:
        db_table = "system_shop_transfers"

    # магазин, с которого происходит списание средств
    source_shop = ForeignKeyField(Shop, related_name="source_transfers")
    source_currency = IntegerField()   # валюта списания

    # магазин, куда происходит зачисление средств
    target_shop = ForeignKeyField(Shop, related_name="target_transfers")
    target_currency = IntegerField()  # валюта зачисления
    exch_rate = DecimalField()
    exch_fee_percent = DecimalField()

    source_amount = DecimalField()  # сумма списания без учета комиссий
    target_amount = DecimalField()  # сумма зачисления без учета комисий
    source_write_off = DecimalField()  # фактическая сумма списания с учетом комиссий
    target_receive = DecimalField()  # фактическая сумма зачисления с учетом комиссий
    source_fee_fix = DecimalField()  # комиссия списания
    target_fee_fix = DecimalField()  # комиссия зачисления

    source_exch_fee = DecimalField()  # конвертационная комиссия с отправителя
    target_exch_fee = DecimalField()  # конвертационная комиссия с получателя
    comments = CharField()
    created = DateTimeField()


class ShopInvoiceTransaction(BaseModel):
    class Meta:
        db_table = "shop_invoice_transactions"

    invoice = ForeignKeyField(Invoice)
    shop_purse = ForeignKeyField(ShopPurse)
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()


class ShopWithdrawTransaction(BaseModel):
    class Meta:
        db_table = "shop_withdraw_transactions"

    withdraw = ForeignKeyField(Withdraw)
    shop_purse = ForeignKeyField(ShopPurse)  # источник
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()


class ShopTransferWriteOffTransaction(BaseModel):
    class Meta:
        db_table = "shop_transfer_write_off_transactions"

    transfer = ForeignKeyField(SystemShopTransfer)
    shop_purse = ForeignKeyField(ShopPurse)
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()


class ShopTransferReceiveTransaction(BaseModel):
    class Meta:
        db_table = "shop_transfer_receive_transactions"

    transfer = ForeignKeyField(SystemShopTransfer)
    shop_purse = ForeignKeyField(ShopPurse)
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()


class ShopSystemWithdrawTransaction(BaseModel):
    class Meta:
        db_table = "shop_system_withdraw_transactions"

    withdraw = ForeignKeyField(SystemWithdraw)
    shop_purse = ForeignKeyField(ShopPurse)  # источник
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()


class ShopSystemInvoiceTransaction(BaseModel):
    class Meta:
        db_table = "shop_system_invoice_transactions"

    invoice = ForeignKeyField(SystemInvoice)
    shop_purse = ForeignKeyField(ShopPurse)
    amount = DecimalField()
    currency = IntegerField()
    processed = DateTimeField()
    shop_purse_balance = DecimalField()
