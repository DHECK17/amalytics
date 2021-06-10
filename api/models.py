from db import db, schema
from harperdb.exceptions import HarperDBError


class Click:
    @staticmethod
    def create(payload):
        return db.insert(schema, "clicks", [payload])

    @staticmethod
    def get_click_data(website: str):
        try:
            data = db.search_by_value(schema, "clicks", "domain", website)
        except HarperDBError:
            data = None
        return data
