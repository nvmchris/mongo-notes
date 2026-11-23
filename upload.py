"""Upload script: enter funny jokes via the console and store them in MongoDB Atlas."""
from datetime import datetime, timezone

from db import connect, jokes_collection


def ask_yes_no(prompt):
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("Please answer y or n.")


def main():
    jokes = jokes_collection(connect())
    print("Enter jokes. Leave the joke empty to finish.\n")
    count = 0
    while True:
        text = input("Joke: ").strip()
        if not text:
            break
        jokes.insert_one({
            "text": text,
            "fsk18": ask_yes_no("FSK18 (adults only)?"),
            "author": input("Author (optional): ").strip() or "anonymous",
            "created_at": datetime.now(timezone.utc),
        })
        count += 1
        print("Saved.\n")
    print(f"Uploaded {count} joke(s). Total in database: {jokes.count_documents({})}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
