"""Download script: fetch all jokes or only filtered ones from MongoDB Atlas."""
import re

from bson import json_util

from db import connect, jokes_collection

FILTERS = {
    "1": ("All jokes", {}),
    "2": ("Only youth-friendly (no FSK18)", {"fsk18": False}),
    "3": ("Only FSK18", {"fsk18": True}),
}


def main():
    jokes = jokes_collection(connect())
    for key, (label, _) in FILTERS.items():
        print(f"{key}) {label}")
    label, query = FILTERS.get(input("Choose filter: ").strip(), FILTERS["1"])
    word = input("Only jokes containing (optional): ").strip()
    if word:
        query = {**query, "text": {"$regex": re.escape(word), "$options": "i"}}

    results = list(jokes.find(query).sort("created_at", 1))
    print(f"\n{label}: {len(results)} joke(s)\n")
    for joke in results:
        tag = "FSK18" if joke.get("fsk18") else "all ages"
        print(f"- [{tag}] {joke['text']}  -- {joke.get('author', 'anonymous')}")

    path = input("\nSave to JSON file (empty = don't save): ").strip()
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_util.dumps(results, indent=2, ensure_ascii=False))
        print(f"Saved {len(results)} joke(s) to {path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
