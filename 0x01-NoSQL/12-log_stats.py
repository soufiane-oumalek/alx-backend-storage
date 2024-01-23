#!/usr/bin/env python3
""" log stats """


import pymongo
from pymongo import MongoClient


def log_stats():
    """
    provides some stats about Nginx logs stored in MongoDB """

    client = MongoClient('mongodb://127.0.0.1:27017')
    logs_collection = client.logs.nginx

    total_logs = logs_collection.count_documents({})
    print(f"{total_logs} logs")

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print("Methods:")
    for method in methods:
        method_count = logs_collection.count_documents({"method": method})
        print(f"    method {method}: {method_count}")

    status_check_count = logs_collection.count_documents({
      "method": "GET", "path": "/status"})
    print(f"{status_check_count} status check")


if __name__ == "__main__":

    log_stats()
