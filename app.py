"""Simple web UI for the Minecraft mods collection: add, edit, delete, filter, sort.

Run:  .venv/bin/python app.py   ->  http://127.0.0.1:5000
"""
import re
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, abort, redirect, render_template_string, request, url_for

from db import LOADERS, connect, mods_collection

app = Flask(__name__)
mods = mods_collection(connect())

SORTS = {"name": "name", "loader": "loader", "mc_version": "mc_version", "created_at": "created_at"}

PAGE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mod Manager</title>
<style>
:root{--bg:#fff;--fg:#1c1c1e;--muted:#6b7280;--line:#e5e7eb;--card:#f8f9fb;--accent:#2f7d32}
@media(prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e8e8ea;--muted:#9aa0a8;--line:#2c3036;--card:#1e2126;--accent:#6fcf74}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif}
main{max-width:900px;margin:0 auto;padding:24px 16px}
h1{margin:0 0 16px;font-size:22px}
form.row{display:flex;flex-wrap:wrap;gap:8px;align-items:end;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:16px}
label{display:flex;flex-direction:column;font-size:12px;color:var(--muted);gap:3px}
input,select,button{font:inherit;padding:6px 9px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
button,.btn{background:var(--accent);color:#fff;border:0;cursor:pointer;border-radius:6px;padding:7px 12px;text-decoration:none;font-size:14px}
button.ghost,.btn.ghost{background:transparent;color:var(--fg);border:1px solid var(--line)}
button.del{background:#c0392b}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line)}
th a{color:inherit;text-decoration:none}th{font-size:12px;color:var(--muted);text-transform:uppercase}
td.act{white-space:nowrap;text-align:right}td.act form{display:inline}
.tag{padding:2px 8px;border-radius:10px;background:var(--card);border:1px solid var(--line);font-size:12px}
.count{color:var(--muted);margin:0 0 8px}
</style></head><body><main>
<h1>Minecraft Mod Manager</h1>

<form class="row" method="post" action="{{ url_for('add') }}">
  <label>Name<input name="name" required placeholder="z.B. Sodium"></label>
  <label>Loader<select name="loader">{% for l in loaders %}<option>{{ l }}</option>{% endfor %}</select></label>
  <label>MC-Version<input name="mc_version" placeholder="1.21.1" size="8"></label>
  <button>Hinzufügen</button>
</form>

<form class="row" method="get">
  <label>Suche<input name="q" value="{{ q }}" placeholder="Name enthält…"></label>
  <label>Loader<select name="loader"><option value="">Alle</option>{% for l in loaders %}<option {{ 'selected' if l==loader }}>{{ l }}</option>{% endfor %}</select></label>
  <label>MC-Version<select name="version"><option value="">Alle</option>{% for v in versions %}<option {{ 'selected' if v==version }}>{{ v }}</option>{% endfor %}</select></label>
  <input type="hidden" name="sort" value="{{ sort }}"><input type="hidden" name="dir" value="{{ direction }}">
  <button>Filtern</button><a class="btn ghost" href="{{ url_for('index') }}">Zurücksetzen</a>
</form>

<p class="count">{{ items|length }} Mod(s)</p>
<table>
<tr>{% for key,label in [('name','Name'),('loader','Loader'),('mc_version','Version'),('created_at','Erstellt')] %}
<th><a href="{{ url_for('index', q=q, loader=loader, version=version, sort=key, dir=('desc' if sort==key and direction=='asc' else 'asc')) }}">{{ label }}{{ ' ▲' if sort==key and direction=='asc' else (' ▼' if sort==key else '') }}</a></th>{% endfor %}<th></th></tr>
{% for m in items %}
<tr><td>{{ m.name }}</td><td><span class="tag">{{ m.loader }}</span></td><td>{{ m.mc_version }}</td>
<td>{{ m.created_at.strftime('%d.%m.%Y') if m.created_at else '' }}</td>
<td class="act"><a class="btn ghost" href="{{ url_for('edit', id=m._id) }}">Bearbeiten</a>
<form method="post" action="{{ url_for('delete', id=m._id) }}" onsubmit="return confirm('{{ m.name|e }} löschen?')"><button class="del">Löschen</button></form></td></tr>
{% else %}<tr><td colspan="5">Keine Mods gefunden.</td></tr>{% endfor %}
</table>
</main></body></html>"""

EDIT = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mod bearbeiten</title>
<style>
:root{--bg:#fff;--fg:#1c1c1e;--line:#e5e7eb;--accent:#2f7d32}
@media(prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e8e8ea;--line:#2c3036;--accent:#6fcf74}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif}
main{max-width:420px;margin:0 auto;padding:24px 16px}
label{display:flex;flex-direction:column;gap:3px;margin-bottom:12px;font-size:13px}
input,select{font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
button,a.b{background:var(--accent);color:#fff;border:0;border-radius:6px;padding:8px 14px;font:inherit;cursor:pointer;text-decoration:none}
a.b{background:transparent;color:var(--fg);border:1px solid var(--line)}
</style></head><body><main><h1>Mod bearbeiten</h1>
<form method="post">
<label>Name<input name="name" value="{{ m.name }}" required></label>
<label>Loader<select name="loader">{% for l in loaders %}<option {{ 'selected' if l==m.loader }}>{{ l }}</option>{% endfor %}</select></label>
<label>MC-Version<input name="mc_version" value="{{ m.mc_version }}"></label>
<button>Speichern</button> <a class="b" href="{{ url_for('index') }}">Abbrechen</a>
</form></main></body></html>"""


def get_mod(id):
    try:
        doc = mods.find_one({"_id": ObjectId(id)})
    except InvalidId:
        abort(404)
    if not doc:
        abort(404)
    return doc


def form_data():
    loader = request.form.get("loader")
    return {
        "name": request.form.get("name", "").strip(),
        "loader": loader if loader in LOADERS else LOADERS[0],
        "mc_version": request.form.get("mc_version", "").strip() or "unknown",
    }


@app.get("/")
def index():
    q = request.args.get("q", "").strip()
    loader = request.args.get("loader", "")
    version = request.args.get("version", "")
    sort = request.args.get("sort", "name")
    direction = request.args.get("dir", "asc")
    if sort not in SORTS:
        sort = "name"
    query = {}
    if q:
        query["name"] = {"$regex": re.escape(q), "$options": "i"}
    if loader in LOADERS:
        query["loader"] = loader
    if version:
        query["mc_version"] = version
    items = list(mods.find(query).sort([(SORTS[sort], -1 if direction == "desc" else 1), ("name", 1)]))
    versions = sorted(mods.distinct("mc_version"), reverse=True)
    return render_template_string(PAGE, items=items, q=q, loader=loader, version=version, sort=sort,
                                  direction=direction, loaders=LOADERS, versions=versions)


@app.post("/add")
def add():
    data = form_data()
    if data["name"]:
        data["created_at"] = datetime.now(timezone.utc)
        mods.insert_one(data)
    return redirect(url_for("index"))


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    m = get_mod(id)
    if request.method == "POST":
        data = form_data()
        if data["name"]:
            mods.update_one({"_id": m["_id"]}, {"$set": data})
        return redirect(url_for("index"))
    return render_template_string(EDIT, m=m, loaders=LOADERS)


@app.post("/delete/<id>")
def delete(id):
    mods.delete_one({"_id": get_mod(id)["_id"]})
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False)
