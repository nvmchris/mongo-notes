"""Interactive command-line app that stores jokes in MongoDB Atlas."""
import os
import re
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from pymongo import MongoClient


def connect():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set. Copy .env.example to .env and fill it in.")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client["joke_box"]["jokes"]


def add_joke(jokes):
    text = input("Enter your joke: ").strip()
    if not text:
        print("Nothing entered.")
        return
    author = input("Your name (optional): ").strip() or "anonymous"
    jokes.insert_one({"text": text, "author": author, "created_at": datetime.now(timezone.utc)})
    print("Joke saved!")


def show(joke):
    print(f"[{joke['_id']}] {joke['text']}  -- {joke['author']}")


def list_jokes(jokes):
    found = False
    for joke in jokes.find().sort("created_at", -1):
        show(joke)
        found = True
    if not found:
        print("No jokes yet.")


def random_joke(jokes):
    sample = list(jokes.aggregate([{"$sample": {"size": 1}}]))
    show(sample[0]) if sample else print("No jokes yet.")


def search_jokes(jokes):
    word = input("Search for: ").strip()
    results = list(jokes.find({"text": {"$regex": re.escape(word), "$options": "i"}}))
    for joke in results:
        show(joke)
    print(f"{len(results)} joke(s) found.")


def delete_joke(jokes):
    try:
        joke_id = ObjectId(input("ID of the joke to delete: ").strip())
    except InvalidId:
        print("Invalid ID.")
        return
    deleted = jokes.delete_one({"_id": joke_id}).deleted_count
    print("Joke deleted." if deleted else "No joke with that ID.")


MENU = {
    "1": ("Enter a joke", add_joke),
    "2": ("List all jokes", list_jokes),
    "3": ("Random joke", random_joke),
    "4": ("Search jokes", search_jokes),
    "5": ("Delete a joke", delete_joke),
}


def main():
    jokes = connect()
    print("Connected to MongoDB Atlas. Welcome to the Joke Box!")
    while True:
        print()
        for key, (label, _) in MENU.items():
            print(f"{key}) {label}")
        print("q) Quit")
        choice = input("> ").strip().lower()
        if choice == "q":
            break
        if choice in MENU:
            MENU[choice][1](jokes)
        else:
            print("Unknown choice.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
