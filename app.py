from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS time_study (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operator TEXT,
            operation TEXT,
            avg_sec REAL,
            basic_sam REAL,
            allowance_sam REAL,
            capacity_hr REAL,
            capacity_day REAL,
            deviation_hr REAL,
            deviation_day REAL,
            remark TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            style TEXT,
            buyer TEXT,
            line TEXT,
            date TEXT,
            filename TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- SAVE OPERATION ----------
@app.route("/save", methods=["POST"])
def save_operation():
    data = request.json

    avg_sec = float(data["avgSec"])
    basic_sam = avg_sec / 60
    allowance_sam = basic_sam * 1.15
    capacity_hr = 60 / allowance_sam if allowance_sam else 0
    capacity_day = capacity_hr * 8
    user_target = float(data["userTargetHr"])
    deviation_hr = capacity_hr - user_target
    deviation_day = deviation_hr * 8

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO time_study 
        (operator, operation, avg_sec, basic_sam, allowance_sam,
         capacity_hr, capacity_day, deviation_hr, deviation_day, remark)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["operator"],
        data["operation"],
        avg_sec,
        basic_sam,
        allowance_sam,
        capacity_hr,
        capacity_day,
        deviation_hr,
        deviation_day,
        data["remark"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Saved Successfully"})

# ---------- GET ALL DATA ----------
@app.route("/data", methods=["GET"])
def get_data():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM time_study")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/save_report", methods=["POST"])
def save_report():
    data = request.json

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO reports (style, buyer, line, date, filename)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["style"],
        data["buyer"],
        data["line"],
        data["date"],
        data["filename"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Report saved"})






if __name__ == "__main__":
    app.run(debug=True)
