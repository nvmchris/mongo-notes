"""Upload script: enter Minecraft mods via the console and store them in MongoDB Atlas.

This is a mockup: only mod names and metadata are stored, not the mod files.
"""
from datetime import datetime, timezone

from db import LOADERS, connect, mods_collection


def ask_loader():
    for i, loader in enumerate(LOADERS, 1):
        print(f"  {i}) {loader}")
    while True:
        answer = input("Mod loader (number): ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(LOADERS):
            return LOADERS[int(answer) - 1]
        print(f"Please enter a number from 1 to {len(LOADERS)}.")


def main():
    mods = mods_collection(connect())
    print("Enter mods. Leave the name empty to finish.\n")
    count = 0
    while True:
        name = input("Mod name: ").strip()
        if not name:
            break
        mods.insert_one({
            "name": name,
            "loader": ask_loader(),
            "mc_version": input("Minecraft version (e.g. 1.21.1): ").strip() or "unknown",
            "created_at": datetime.now(timezone.utc),
        })
        count += 1
        print("Saved.\n")
    print(f"Uploaded {count} mod(s). Total in database: {mods.count_documents({})}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
