#!/usr/bin/env python3
"""Insert a document"""


def insert_school(mongo_collection, **kwargs):
    """ inserts a new document in a collection based on kwargs"""

    rslt = mongo_collection.insert_one(kwargs)
    return rslt.inserted_id
