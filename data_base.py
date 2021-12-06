from peewee import *

mysql_db = MySQLDatabase('chat database', user='****', password='****',
                         host='localhost')


class Users(Model):
    user_id = AutoField()
    username = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True)
    is_online = BooleanField(default=False)
    sid = CharField(default=None)
    last_login = DateTimeField(default=None)

    class Meta:
        database = mysql_db  # This model uses the "mysql.db" database.

