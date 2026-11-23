# mongo-notes – MongoDB data manager

Small interactive Python command-line app to manage any collection in MongoDB Atlas:

- choose a database and collection (or type a new name to create one)
- overview: document count and a preview
- download the whole collection or only documents matching a filter to a JSON file
- upload a JSON file (one object or a list) into a collection, optionally replacing by `_id`
- delete all or filtered documents (with confirmation)

Filters use MongoDB query syntax as JSON, for example `{"status": "active"}` or
`{"age": {"$gte": 18}}`. Files use MongoDB Extended JSON, so `_id` and dates survive a
download/upload round trip.

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
   python main.py
   ```

## Workflow
- One issue + one branch per feature: `feat/<issue>-<name>`
- Commits: Conventional Commits (`feat(scope): add thing`)
- Merge via pull request into `main`
