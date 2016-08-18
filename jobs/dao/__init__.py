# -*- coding:utf-8 -*-

from peewee import Model
from playhouse.pool import PooledPostgresqlExtDatabase
from jobs.jobs_config import TRIO_DB_CONFIG

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
