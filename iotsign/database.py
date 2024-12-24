import peewee
import uuid

__all__ = ["initialize", "Message"]

database = peewee.SqliteDatabase(None)

class BaseModel(peewee.Model):
    class Meta:
        database = database

class Message(BaseModel):
    message = peewee.TextField()
    dedupe = peewee.TextField(unique=True, default=uuid.uuid4, index=True)
    expiration_date = peewee.DateTimeField(null=True, default=None, index=True)


def initialize(filename):
    database.init(filename)
    database.connect()
    database.create_tables(BaseModel.__subclasses__())
