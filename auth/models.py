from db import db, schema
from flask_login import UserMixin
from harperdb.exceptions import HarperDBError

table = "accounts"


class Accounts:
    @staticmethod
    def create(username: str, password: str):
        payload = dict(username=username, password=password)
        return db.insert(schema, table, [payload])

    @staticmethod
    def get(username):
        try:
            user = db.search_by_value(schema, table, "username", username)
        except HarperDBError:
            user = None
        return user


class User(UserMixin):
    def __init__(self, username: str) -> None:
        super().__init__()
        self.id = username
