from db import db, schema


class Click:
    @staticmethod
    def create(payload):
        return db.insert(schema, "clicks", [payload])
