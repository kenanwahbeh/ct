from flask import Flask, g, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

APP_TITLE = "سجل الأعضاء البسيط"
DB_PATH = Path("data.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"  # بدّلها في بيئة الإنتاج

# -----------------------------
# Database helpers
# -----------------------------

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            father_name TEXT,
            mother_name TEXT,
            nation_id INTEGER,
            addres TEXT,
            email TEXT,
            phone TEXT,
            id_link TEXT,
            status INTEGER DEFAULT 0,
            project TEXT,
            apartment TEXT,
            amount REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
        """
    )
    db.commit()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS f_account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            detail TEXT
        )
        """
    )
    db.commit()


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        father_name = request.form.get("father_name", "").strip() or None
        mother_name = request.form.get("mother_name", "").strip() or None
        nation_id = request.form.get("nation_id", "").strip() or None
        addres = request.form.get("addres", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        id_link = request.form.get("id_link", "").strip() or None
        email = request.form.get("email", "").strip() or None
        apartment = request.form.get("apartment", "").strip() or None
        amount_raw = request.form.get("amount", "0").strip()
        try:
            amount = float(amount_raw) if amount_raw else 0.0
        except ValueError:
            amount = 0.0

        if not name:
            flash("الاسم مطلوب", "error")
        else:
            db.execute(
                "INSERT INTO members (name, father_name, mother_name, nation_id, addres, id_link, email, phone, apartment, amount) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (name, father_name, mother_name, nation_id, addres, id_link, email, phone, apartment, amount),
            )
            db.commit()
            flash("تمت الإضافة بنجاح", "success")
        return redirect(url_for("index"))

    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            """
            SELECT * FROM members
            WHERE name LIKE ? OR apartment LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM members ORDER BY id DESC").fetchall()

    return render_template('index.html', title=APP_TITLE, members=rows, q=q)


@app.route("/edit/<int:member_id>", methods=["GET", "POST"])
def edit(member_id):
    db = get_db()
    row = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    if not row:
        flash("السجل غير موجود", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        apartment = request.form.get("apartment", "").strip() or None
        amount_raw = request.form.get("amount", "0").strip()
        try:
            amount = float(amount_raw) if amount_raw else 0.0
        except ValueError:
            amount = 0.0

        if not name:
            flash("الاسم مطلوب", "error")
            return redirect(url_for("edit", member_id=member_id))

        db.execute(
            "UPDATE members SET name=?, email=?, phone=?, apartment=?, amount=? WHERE id=?",
            (name, email, phone, apartment, amount, member_id),
        )
        db.commit()
        flash("تم تحديث البيانات", "success")
        return redirect(url_for("index"))

    return render_template('edit.html', title=APP_TITLE, m=row)


@app.route("/delete/<int:member_id>", methods=["POST"])
def delete(member_id):
    db = get_db()
    db.execute("DELETE FROM members WHERE id=?", (member_id,))
    db.commit()
    flash("تم حذف السجل", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # تشغيل التطبيق
    app.run(debug=True)
