# mongo-notes – Joke Box

Small interactive Python command-line app that stores jokes in MongoDB Atlas.
Enter jokes, list them, get a random one, search and delete.

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

Data goes to database `joke_box`, collection `jokes`.

## Workflow
- One issue + one branch per feature: `feat/<issue>-<name>`
- Commits: Conventional Commits (`feat(scope): add thing`)
- Merge via pull request into `main`
