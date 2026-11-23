"""Download script: fetch all mods or only filtered ones from MongoDB Atlas."""
import re

from bson import json_util

from db import LOADERS, connect, mods_collection


def build_filter():
    """Ask for optional filters; empty answers mean 'any'."""
    query = {}
    print("Loader filter: " + ", ".join(f"{i}) {l}" for i, l in enumerate(LOADERS, 1)))
    loader = input("Loader (empty = all): ").strip()
    if loader.isdigit() and 1 <= int(loader) <= len(LOADERS):
        query["loader"] = LOADERS[int(loader) - 1]
    version = input("Minecraft version (empty = all): ").strip()
    if version:
        query["mc_version"] = version
    word = input("Name contains (empty = all): ").strip()
    if word:
        query["name"] = {"$regex": re.escape(word), "$options": "i"}
    return query


def main():
    mods = mods_collection(connect())
    query = build_filter()
    results = list(mods.find(query).sort("name", 1))
    print(f"\n{len(results)} mod(s) found\n")
    for mod in results:
        print(f"- {mod['name']}  [{mod['loader']}, {mod['mc_version']}]")

    path = input("\nSave to JSON file (empty = don't save): ").strip()
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_util.dumps(results, indent=2, ensure_ascii=False))
        print(f"Saved {len(results)} mod(s) to {path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
