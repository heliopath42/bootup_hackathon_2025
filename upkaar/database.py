import subprocess
import time
import io
import os
from pymongo import MongoClient
from pymongo.database import Database
from typing import Callable, Tuple

def start_mongod(db_path: str = "./local_mongo_data", port: int = 27017):
    os.makedirs(db_path, exist_ok=True)
    # Launch mongod as a background process
    proc = subprocess.Popen([
        "/home/mihir/Projects/bootup_hackathon_2025/mongo_local_db/mongodb-linux-x86_64-ubuntu2204-8.2.1/bin/mongod",
        "--dbpath", db_path,
        "--port", str(port),
        "--bind_ip", "127.0.0.1",
        "--quiet"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Give it a moment to start
    time.sleep(1)
    return proc

def stop_mongod(proc):
    proc.terminate()
    proc.wait()

def get_database(db_name: str) -> Tuple[Database, Callable[[], None]]:
    mongod_proc = start_mongod()
    client: MongoClient = MongoClient("mongodb://127.0.0.1:27017/")
    def close():
        client.close()
        stop_mongod(mongod_proc)
    return (client[db_name], close)

# Example usage
if __name__ == "__main__":
    DB_DIR = "./local_mongo_data"
    mongod_proc = start_mongod(DB_DIR)

    client: MongoClient = MongoClient("mongodb://127.0.0.1:27017/")
    db = client["mydb"]
    coll = db["people"]

    print(list(coll.find()))
    # Clean up
    client.close()
    stop_mongod(mongod_proc)
