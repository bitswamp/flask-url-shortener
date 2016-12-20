from peewee import SqliteDatabase, Model, PrimaryKeyField, CharField, BooleanField, DateTimeField

urls = SqliteDatabase("urls.db")
auth = SqliteDatabase("auth.db")

class Url(Model):
    id = PrimaryKeyField()
    url = CharField()
    class Meta:
        database = urls


class Token(Model):
    user = CharField()  # store email address or other identifier
    token = CharField()
    valid = BooleanField()
    class Meta:
        database = auth


class Ip(Model):
    ip = CharField(index = True)
    token = CharField(index = True)
    time = DateTimeField(index = True)
    class Meta:
        database = auth


