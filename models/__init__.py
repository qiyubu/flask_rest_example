#coding:utf-8

import uuid
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from peewee import MySQLDatabase, PostgresqlDatabase, Model, Field, BooleanField, DateTimeField, CharField, IntegerField

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB
from utils.functions import field_to_json


db = MySQLDatabase(MYSQL_DB, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD)

class UUIDField(Field):
    field_type = "char(32)"

    def db_value(self, value):
        if not isinstance(value, (str, uuid.UUID)):
            return value
        if isinstance(value, str):
            # value = uuid.UUID(value)
            try:
                value = uuid.UUID(value) # convert hex string to UUID
            except Exception as e:
                print("Failed to convert value {} to uuid".format(value))
        value = value.hex if isinstance(value, uuid.UUID) else str(value)  # convert UUID to hex string.
        return value
    
    def python_value(self, value):
        try:
            value = uuid.UUID(value) # convert hex string to UUID
        except Exception as e:
            print("Failed to convert value {} to uuid".format(value))
        return value


class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    uid    = UUIDField(null=False, primary_key=True, default=uuid.uuid4)
    status = BooleanField(default=True, null=False, help_text="0 delete, 1 normal")
    create_time = DateTimeField(default=datetime.now)

    class Meta:
        database = db
    
    @classmethod
    def get_with_uid(cls, uid):
        if not uid:
            return None
        return cls.get_or_none(cls.uid == uid, cls.status == True)
    
    @classmethod
    def remove(cls, uid):
        try:
            r = cls.get(cls.uid == uid)
            r.status = False
            r.save()
        except:
            r = None
        return r
    
    @classmethod
    def list(cls):
        return cls.select().where(cls.status == True)

    def to_json(self):
        r = model_to_dict(self)
        for k, v in r.items():
            r[k] = field_to_json(v)
        return r
