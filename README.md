# mongo-notes – Minecraft mod management (mockup)

Python scripts to upload and download Minecraft mod entries to a cloud database
(MongoDB Atlas). It's a mockup: only mod names and metadata (loader, Minecraft version)
are stored, not the mod files.

## Scripts
| Script | What it does |
|---|---|
| `upload.py` | Creates database `minecraft` with collection `mods` (if missing) and lets you enter mods in the console: name, loader (Fabric, Forge, NeoForge, Quilt) and Minecraft version. |
| `download.py` | Downloads all mods, or filters by loader, Minecraft version and/or part of the name. Prints them and can save them to a JSON file. |

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
   python upload.py     # enter mods
   python download.py   # get all or filtered mods
   ```

## Workflow
- One issue + one branch per feature: `feat/<issue>-<name>`
- Commits: Conventional Commits (`feat(scope): add thing`)
- Merge via pull request into `main`
