"""Interactive command-line data manager for MongoDB Atlas.

Pick a database and collection, download all or filtered documents to a
JSON file, and upload JSON files into a collection.
"""
from bson import json_util
from pymongo.errors import PyMongoError

from db import connect

SYSTEM_DBS = {"admin", "local", "config"}


def choose(prompt, names):
    """Let the user pick a name by number or type a new one."""
    for i, name in enumerate(names, 1):
        print(f"  {i}) {name}")
    answer = input(f"{prompt} (number or new name): ").strip()
    if answer.isdigit() and 1 <= int(answer) <= len(names):
        return names[int(answer) - 1]
    return answer or None


def select_collection(client):
    dbs = [d for d in client.list_database_names() if d not in SYSTEM_DBS]
    db_name = choose("Database", dbs)
    if not db_name:
        return None
    db = client[db_name]
    coll_name = choose("Collection", sorted(db.list_collection_names()))
    if not coll_name:
        return None
    print(f"Selected {db_name}.{coll_name}")
    return db[coll_name]


def read_filter():
    """Ask for a MongoDB filter as JSON; empty means everything."""
    text = input('Filter as JSON, e.g. {"status": "active"} (empty = all): ').strip()
    if not text:
        return {}
    query = json_util.loads(text)
    if not isinstance(query, dict):
        raise ValueError("Filter must be a JSON object.")
    return query


def show_overview(coll):
    print(f"{coll.full_name}: {coll.count_documents({})} document(s)")
    for doc in coll.find().limit(3):
        print(" ", json_util.dumps(doc)[:200])


def download(coll):
    query = read_filter()
    docs = list(coll.find(query))
    if not docs:
        print("No documents match.")
        return
    default = f"{coll.name}.json"
    path = input(f"Save to file [{default}]: ").strip() or default
    with open(path, "w", encoding="utf-8") as f:
        f.write(json_util.dumps(docs, indent=2, ensure_ascii=False))
    print(f"Downloaded {len(docs)} document(s) to {path}")


def upload(coll):
    path = input("JSON file to upload: ").strip()
    with open(path, encoding="utf-8") as f:
        data = json_util.loads(f.read())
    docs = data if isinstance(data, list) else [data]
    if not docs or not all(isinstance(d, dict) for d in docs):
        print("File must contain a JSON object or a list of objects.")
        return
    replace = input("Replace documents with the same _id? [y/N]: ").strip().lower() == "y"
    if replace:
        for doc in docs:
            if "_id" in doc:
                coll.replace_one({"_id": doc["_id"]}, doc, upsert=True)
            else:
                coll.insert_one(doc)
    else:
        coll.insert_many(docs)
    print(f"Uploaded {len(docs)} document(s) to {coll.full_name}")


def delete(coll):
    query = read_filter()
    count = coll.count_documents(query)
    if not count:
        print("No documents match.")
        return
    if input(f"Delete {count} document(s)? Type 'yes' to confirm: ").strip() == "yes":
        print(f"Deleted {coll.delete_many(query).deleted_count} document(s).")
    else:
        print("Cancelled.")


MENU = {
    "1": ("Choose database / collection", None),
    "2": ("Overview", show_overview),
    "3": ("Download (all or filtered)", download),
    "4": ("Upload JSON file", upload),
    "5": ("Delete (all or filtered)", delete),
}


def main():
    client = connect()
    print("Connected to MongoDB. Welcome to the data manager!")
    coll = None
    while True:
        print(f"\nCurrent collection: {coll.full_name if coll is not None else '-'}")
        for key, (label, _) in MENU.items():
            print(f"{key}) {label}")
        print("q) Quit")
        choice = input("> ").strip().lower()
        if choice == "q":
            break
        if choice not in MENU:
            print("Unknown choice.")
            continue
        try:
            if choice == "1":
                selected = select_collection(client)
                if selected is not None:
                    coll = selected
            elif coll is None:
                print("Choose a collection first (1).")
            else:
                MENU[choice][1](coll)
        except (ValueError, OSError, PyMongoError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
