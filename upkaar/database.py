import click
from flask import current_app, g, Flask
from pymongo import MongoClient
from pymongo.database import Database
# from typing import Callable, Tuple

import subprocess
import time
import os


def get_db(db_name: str = "upkaar") -> Database:
    if 'db' not in g:
        g.proc = start_mongod(os.path.join(
            current_app.instance_path, "local_mongo_data"))
        client: MongoClient = MongoClient("mongodb://127.0.0.1:27017/")
        g.db = client[db_name]
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.client.close()
        stop_mongod(g.proc)


def start_mongod(db_path: str, port: int = 27017):
    os.makedirs(db_path, exist_ok=True)
    # Launch mongod as a background process
    proc = subprocess.Popen([
        os.path.join(current_app.instance_path, "mongod"),
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


@click.command("init-db")
def init_db():
    db = get_db("upkaar")
    if "users" not in db.list_collection_names():
        db.create_collection(
            "users",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["username", "password_salt"],
                    "properties": {
                        "username": {
                            "bsonType": "string",
                            "description": "required, non-empty string"
                        },
                        "password_salt": {
                            "bsonType": "string",
                            "description": "SHA 256 hash of the password"
                        },
                        "requests_created": {
                            "bsonType": "array",
                            "description": "Array of uuids"
                        },
                        "requests_ongoing": {
                            "bsonType": "array",
                            "description": "Array of uuids"
                        }

                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )

    if "user_request" not in db.list_collection_names():
        db.create_collection(
            "user_request",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["owner", "r_uuid"],
                    "properties": {
                        "owner": {
                            "bsonType": "string",
                            "description": "required, non-empty string"
                        },
                        "r_uuid": {
                            "bsonType": "string",
                            "description": "required UUID v4"
                        },
                        "created_timestamp": {
                            "bsonType": "date",
                            "description": "timestamp of creation"
                        },
                        "reward": {
                            "bsonType": "string",
                            "description": "Reward set by the user",
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)

# def get_database(db_name: str) -> Tuple[Database, Callable[[], None]]:
#     mongod_proc = start_mongod()
#     client: MongoClient = MongoClient("mongodb://127.0.0.1:27017/")
#     def close():
#         client.close()
#         stop_mongod(mongod_proc)
#     return (client[db_name], close)

# Example usage
# if __name__ == "__main__":
#     DB_DIR = "./local_mongo_data"
#     mongod_proc = start_mongod(DB_DIR)
#
#     client: MongoClient = MongoClient("mongodb://127.0.0.1:27017/")
#     db = client["mydb"]
#     coll = db["people"]
#
#     print(list(coll.find()))
#     # Clean up
#     client.close()
#     stop_mongod(mongod_proc)
