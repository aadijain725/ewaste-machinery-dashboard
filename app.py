#!/usr/bin/env python3
"""E-Waste Plant Dashboard — Flask application."""

import json
import sqlite3
import os

from flask import Flask, g, render_template, request, jsonify

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ewaste.db")


# ── Database helpers ───────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()


def rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ── Template helpers ───────────────────────────────────────────

@app.context_processor
def inject_nav():
    return {"nav_items": [
        ("/", "Dashboard"),
        ("/categories", "Categories"),
        ("/machines", "Machines"),
        ("/economics", "Unit Economics"),
        ("/search", "Search"),
    ]}


# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    db = get_db()
    cats = rows_to_dicts(db.execute("SELECT * FROM categories ORDER BY priority, id").fetchall())
    total_machines = db.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
    configs = rows_to_dicts(db.execute("SELECT * FROM configurations").fetchall())

    # Revenue & cost summary for config2
    rev = db.execute(
        "SELECT SUM(revenue_per_tonne) as total FROM revenue_items WHERE config_id='config2'"
    ).fetchone()["total"] or 0
    cost_min = db.execute(
        "SELECT SUM(cost_per_tonne_min) as total FROM cost_items WHERE config_id='config2'"
    ).fetchone()["total"] or 0
    cost_max = db.execute(
        "SELECT SUM(cost_per_tonne_max) as total FROM cost_items WHERE config_id='config2'"
    ).fetchone()["total"] or 0

    # Sourcing
    sourcing = rows_to_dicts(db.execute(
        "SELECT s.*, c.name as cat_name FROM sourcing_profile s LEFT JOIN categories c ON s.category_id=c.id ORDER BY s.percentage DESC"
    ).fetchall())

    return render_template("dashboard.html",
        categories=cats,
        total_machines=total_machines,
        configs=configs,
        revenue_per_tonne=rev,
        cost_min=cost_min,
        cost_max=cost_max,
        margin_min=rev - cost_max,
        margin_max=rev - cost_min,
        sourcing=sourcing,
    )


@app.route("/categories")
def categories():
    db = get_db()
    cats = rows_to_dicts(db.execute("SELECT * FROM categories ORDER BY priority, id").fetchall())
    for cat in cats:
        cat["materials"] = rows_to_dicts(db.execute(
            "SELECT * FROM materials WHERE category_id=? ORDER BY pct DESC", (cat["id"],)
        ).fetchall())
        cat["machines"] = rows_to_dicts(db.execute(
            """SELECT m.*, cm.requirement FROM category_machines cm
               JOIN machines m ON cm.machine_id=m.id
               WHERE cm.category_id=? ORDER BY m.id""", (cat["id"],)
        ).fetchall())

        # Compute revenue per tonne for this category
        tonne = 1000
        cat["revenue_per_tonne"] = 0
        for mat in cat["materials"]:
            kg = (mat["pct"] / 100) * tonne
            if mat["material"] == "gold":
                # Gold: pct gives grams from 1000kg, price is per gram
                grams = (mat["pct"] / 100) * tonne
                cat["revenue_per_tonne"] += grams * mat["price_per_unit"]
            elif mat["material"] != "plastic":
                cat["revenue_per_tonne"] += kg * mat["price_per_unit"]
            else:
                cat["revenue_per_tonne"] += kg * mat["price_per_unit"]

    return render_template("categories.html", categories=cats)


@app.route("/machines")
def machines():
    db = get_db()
    groups = {}
    group_order = ["core", "appliance", "specialized", "support"]
    group_labels = {
        "core": "Core Processing (1-6)",
        "appliance": "Appliance Line (7-10)",
        "specialized": "Specialized (11-15)",
        "support": "Support Infrastructure (16-21)",
    }
    for grp in group_order:
        groups[grp] = {
            "label": group_labels[grp],
            "machines": rows_to_dicts(db.execute(
                "SELECT * FROM machines WHERE group_name=? ORDER BY id", (grp,)
            ).fetchall()),
        }
    return render_template("machines.html", groups=groups, group_order=group_order)


@app.route("/economics")
def economics():
    db = get_db()
    configs = rows_to_dicts(db.execute("SELECT * FROM configurations ORDER BY price_min_lakhs").fetchall())
    revenue_items = rows_to_dicts(db.execute(
        "SELECT * FROM revenue_items WHERE config_id='config2'").fetchall())
    cost_items = rows_to_dicts(db.execute(
        "SELECT * FROM cost_items WHERE config_id='config2'").fetchall())
    rentals = rows_to_dicts(db.execute("SELECT * FROM rental_locations").fetchall())
    zones = rows_to_dicts(db.execute("SELECT * FROM space_zones").fetchall())
    total_sqm = db.execute("SELECT SUM(required_sqm) FROM space_zones").fetchone()[0]

    rev_total = sum(r["revenue_per_tonne"] for r in revenue_items)
    cost_min = sum(c["cost_per_tonne_min"] for c in cost_items)
    cost_max = sum(c["cost_per_tonne_max"] for c in cost_items)

    return render_template("economics.html",
        configs=configs, revenue_items=revenue_items, cost_items=cost_items,
        rentals=rentals, zones=zones, total_sqm=total_sqm,
        rev_total=rev_total, cost_min=cost_min, cost_max=cost_max,
    )


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        db = get_db()
        results = rows_to_dicts(db.execute(
            """SELECT entity_type, entity_id, title, content,
                      rank as score
               FROM search_index
               WHERE search_index MATCH ?
               ORDER BY rank
               LIMIT 20""",
            (q,)
        ).fetchall())
    return render_template("search.html", query=q, results=results)


# ── API endpoints ──────────────────────────────────────────────

@app.route("/api/categories")
def api_categories():
    db = get_db()
    cats = rows_to_dicts(db.execute("SELECT * FROM categories").fetchall())
    for cat in cats:
        cat["materials"] = rows_to_dicts(db.execute(
            "SELECT material, pct, price_per_unit, unit FROM materials WHERE category_id=?",
            (cat["id"],)).fetchall())
    return jsonify(cats)


@app.route("/api/machines")
def api_machines():
    db = get_db()
    return jsonify(rows_to_dicts(db.execute("SELECT * FROM machines ORDER BY id").fetchall()))


@app.route("/api/economics")
def api_economics():
    db = get_db()
    return jsonify({
        "revenue": rows_to_dicts(db.execute("SELECT * FROM revenue_items").fetchall()),
        "costs": rows_to_dicts(db.execute("SELECT * FROM cost_items").fetchall()),
        "configurations": rows_to_dicts(db.execute("SELECT * FROM configurations").fetchall()),
    })


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    db = get_db()
    results = rows_to_dicts(db.execute(
        "SELECT entity_type, entity_id, title, content, rank as score FROM search_index WHERE search_index MATCH ? ORDER BY rank LIMIT 20",
        (q,)).fetchall())
    return jsonify(results)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found. Run `python seed.py` first.")
        exit(1)
    app.run(debug=True, port=5050)
