# mongo-notes – Fun with MongoDB Atlas and Python

Python scripts to upload and download funny data to a cloud database (MongoDB Atlas).

## Scripts
| Script | What it does |
|---|---|
| `upload.py` | Creates database `fun_db` with collection `jokes` (if missing) and lets you enter jokes in the console, each classified as FSK18 or not. |
| `download.py` | Downloads all jokes, or filters: only youth-friendly, only FSK18, optionally by a word. Prints them and can save them to a JSON file. |

`db.py` holds the shared connection code. Saved files use MongoDB Extended JSON, so `_id` and
dates are kept.

## Setup
1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/atlas), add a database user
   and allow your IP under *Network Access*.
2. Copy the connection string (*Connect → Drivers*) into `.env`:
   ```bash
   cp .env.example .env
   ```
3. Install and run:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python upload.py     # enter jokes
   python download.py   # get all or only youth-friendly jokes
   ```

## Workflow
- One issue + one branch per feature: `feat/<issue>-<name>`
- Commits: Conventional Commits (`feat(scope): add thing`)
- Merge via pull request into `main`
