"""Shared MongoDB Atlas connection helper."""
import os

from dotenv import load_dotenv
from pymongo import MongoClient

JOKE_DB = "fun_db"
JOKE_COLLECTION = "jokes"


def connect():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set. Copy .env.example to .env and fill it in.")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


def jokes_collection(client):
    """Return the jokes collection, creating database and collection if missing."""
    db = client[JOKE_DB]
    if JOKE_COLLECTION not in db.list_collection_names():
        db.create_collection(JOKE_COLLECTION)
        print(f"Created database '{JOKE_DB}' with collection '{JOKE_COLLECTION}'.")
    coll = db[JOKE_COLLECTION]
    coll.create_index("fsk18")
    return coll
