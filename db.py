import os

import harperdb

db = harperdb.HarperDB(
    url=os.getenv("HARPER_INSTANCE"),
    username=os.getenv("HARPER_USERNAME"),
    password=os.getenv("HARPER_PASSWORD"),
)


schema = "amalytics"
