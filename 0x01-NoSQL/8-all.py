#!/usr/bin/env python3
""" list all documents"""


def list_all(mongo_collection):
    """
    List all documents in MongoDB collection """

    documents = mongo_collection.find()
    return list(documents)
