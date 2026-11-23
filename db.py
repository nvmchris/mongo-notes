"""MongoDB Atlas connection helper used by upload.py and download.py."""
import os

from dotenv import load_dotenv
from pymongo import MongoClient

DB_NAME = "minecraft"
COLLECTION_NAME = "mods"
LOADERS = ["Fabric", "Forge", "NeoForge", "Quilt"]


def connect():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set. Copy .env.example to .env and fill it in.")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


def mods_collection(client):
    """Return the mods collection, creating database and collection if missing."""
    db = client[DB_NAME]
    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)
        print(f"Created database '{DB_NAME}' with collection '{COLLECTION_NAME}'.")
    coll = db[COLLECTION_NAME]
    coll.create_index("loader")
    coll.create_index("mc_version")
    return coll
