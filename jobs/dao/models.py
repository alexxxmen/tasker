# -*- coding: utf8 -*-
import json

from peewee import (CharField, DateTimeField, TextField, datetime as peewee_datetime)
from jobs.dao import BaseModel


class Flat(BaseModel):
    class Meta:
        db_table = 'flat'

    title = CharField()
    url = TextField()
    price = CharField()
    offer_datetime = CharField()
    created = DateTimeField(default=peewee_datetime.datetime.now())
