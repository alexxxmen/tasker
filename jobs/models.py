# -*- coding: utf8 -*-
import json

from peewee import (Model, CharField, DateTimeField, ForeignKeyField, TextField, IntegerField, DecimalField,
                    BooleanField, datetime as peewee_datetime)
from playhouse.pool import PooledPostgresqlExtDatabase
from jobs_config import TRIO_DB_CONFIG

SUCCESS_INVOICE_STATUS = 3

trio_db = PooledPostgresqlExtDatabase(**TRIO_DB_CONFIG)
trio_db.commit_select = True
trio_db.autorollback = True


class BaseModel(Model):
    class Meta:
        database = trio_db

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.get(cls.id == id)
        except cls.DoesNotExist:
            return None


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



class Paysystem(BaseModel):
    class Meta:
        db_table = "paysystems"

    name = CharField()

    def __repr__(self):
        return self.name


class PaysystemPurse(BaseModel):
    class Meta:
        db_table = "paysystem_purses"

    name = CharField()
    currency = IntegerField()
    paysystem = ForeignKeyField(Paysystem)
    balance = DecimalField()   # рассчетный баланс
    ps_balance = DecimalField()  # баланс в ПС, получаемый от Бинга или Геллера
    updated = DateTimeField(default=peewee_datetime.datetime.now)


class ShopPurse(BaseModel):
    class Meta:
        db_table = "shop_purses"

    name = CharField()
    currency = IntegerField()
    shop = ForeignKeyField(Shop, related_name="purses")
    balance = DecimalField()
    frozen = DecimalField()
    is_active = BooleanField()


class CurrencyRate(BaseModel):
    class Meta:
        db_table = "currency_rates"

    from_currency = IntegerField()
    to_currency = IntegerField()
    input_rate = DecimalField()  # курс, используемый при рассчетах на ввод
    input_fee_percent = DecimalField()  # процент конвертационной комиссии, при рассчетах на ввод
    output_rate = DecimalField()    # курс, используемый при рассчетах на вывод
    output_fee_percent = DecimalField()  # процент конвертационной комиссии, при рассчетах на вывод
    updated = DateTimeField()
    protocol_config = TextField()


class CashGapHistory(BaseModel):
    class Meta:
        db_table = "cash_gap_history"

    created = DateTimeField(default=peewee_datetime.datetime.now)
    cash_gap = DecimalField()
    courses = TextField()  # TODO rename currency_rates

    def get_courses(self):
        return json.loads(self.courses)
