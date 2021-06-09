from db import db, schema
from harperdb.exceptions import HarperDBError

table = "websites"


class Website:
    @staticmethod
    def create(url: str, username: str):
        payload = dict(username=username, url=url)
        return db.insert(schema, table, [payload])

    @staticmethod
    def get_all_websites(username: str):
        try:
            websites = db.search_by_value(schema, table, "username", username)
        except HarperDBError:
            websites = None
        return websites
