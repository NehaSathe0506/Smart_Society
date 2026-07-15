"""
SMART SOCIETY - SOCIETY MANAGEMENT SYSTEM
A Third Year B.Tech CSE Mini Project
Built using Flask + SQLite + HTML/CSS/JS (no external frameworks)

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

# -------------------------------------------------------------------
# APP SETUP
# -------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "smart_society_secret_key_2026"   # used to sign session cookies

DATABASE = "smart_society.db"


# -------------------------------------------------------------------
# DATABASE CONNECTION HELPERS
# -------------------------------------------------------------------
def get_db():
    """Opens a new database connection for the current request (if not already open)."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row   # lets us access columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Closes the database connection at the end of every request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def hash_password(password):
    """Hashes a plain text password using SHA-256 (standard library only)."""
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------------
def init_db():
    """Creates all tables (if they do not exist) and inserts sample data."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # ---------- TABLE: users ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            resident_id INTEGER
        )
    """)

    # ---------- TABLE: residents ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            flat_number TEXT NOT NULL,
            wing TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            resident_type TEXT
        )
    """)

    # ---------- TABLE: visitors ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT NOT NULL,
            phone TEXT,
            flat_number TEXT,
            purpose TEXT,
            entry_time TEXT,
            exit_time TEXT,
            status TEXT DEFAULT 'Inside',
            visit_date TEXT
        )
    """)

    # ---------- TABLE: workers ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT UNIQUE,
            worker_name TEXT NOT NULL,
            phone TEXT,
            worker_type TEXT
        )
    """)

    # ---------- TABLE: worker_attendance ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS worker_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            attendance_date TEXT,
            check_in TEXT,
            check_out TEXT,
            status TEXT DEFAULT 'Present'
        )
    """)

    # ---------- TABLE: notices ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            notice_date TEXT,
            priority TEXT DEFAULT 'Normal',
            created_by TEXT
        )
    """)

    # ---------- TABLE: complaints ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            flat_number TEXT,
            category TEXT,
            complaint_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # ---------- TABLE: rentals ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_name TEXT,
            flat_number TEXT,
            owner_name TEXT,
            phone TEXT,
            email TEXT,
            move_in_date TEXT,
            agreement_start_date TEXT,
            agreement_end_date TEXT,
            rental_status TEXT DEFAULT 'Pending Verification',
            created_by TEXT
        )
    """)

    # ---------- TABLE: emergency_contacts ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_name TEXT,
            contact_type TEXT,
            phone TEXT,
            description TEXT
        )
    """)

    # ---------- TABLE: notifications ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            notification_type TEXT,
            created_date TEXT,
            is_read INTEGER DEFAULT 0,
            user_role TEXT
        )
    """)

    conn.commit()

    # -----------------------------------------------------------
    # SAMPLE DATA (only inserted once)
    # -----------------------------------------------------------
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:

        # sample residents
        residents = [
            ("Aarav Sharma", "A-101", "A", "9820011111", "aarav.sharma@mail.com", "Owner"),
            ("Priya Mehta", "A-204", "A", "9820022222", "priya.mehta@mail.com", "Tenant"),
            ("Rohan Patil", "B-302", "B", "9820033333", "rohan.patil@mail.com", "Owner"),
            ("Sneha Joshi", "C-105", "C", "9820044444", "sneha.joshi@mail.com", "Owner"),
        ]
        cur.executemany(
            "INSERT INTO residents (full_name, flat_number, wing, phone, email, resident_type) VALUES (?, ?, ?, ?, ?, ?)",
            residents
        )

        # sample users (admin + resident)
        cur.execute(
            "INSERT INTO users (username, password, role, resident_id) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "admin", None)
        )
        cur.execute(
            "INSERT INTO users (username, password, role, resident_id) VALUES (?, ?, ?, ?)",
            ("resident", hash_password("resident123"), "resident", 1)
        )

        # sample workers
        workers = [
            ("WRK001", "Ramesh Kumar", "9870011111", "Housekeeping"),
            ("WRK002", "Suresh Yadav", "9870022222", "Security Guard"),
            ("WRK003", "Mahesh Patil", "9870033333", "Electrician"),
            ("WRK004", "Anil More", "9870044444", "Plumber"),
        ]
        cur.executemany(
            "INSERT INTO workers (worker_id, worker_name, phone, worker_type) VALUES (?, ?, ?, ?)",
            workers
        )

        # sample notices
        today = datetime.now().strftime("%Y-%m-%d")
        notices = [
            ("Water Supply Maintenance", "Water supply will be interrupted from 10 AM to 2 PM for maintenance work.", today, "Important", "admin"),
            ("Annual General Meeting", "AGM will be held in the community hall next Sunday at 6 PM.", today, "Normal", "admin"),
            ("Emergency Lift Maintenance", "Lift in Wing B is under emergency repair. Please use stairs.", today, "Urgent", "admin"),
        ]
        cur.executemany(
            "INSERT INTO notices (title, description, notice_date, priority, created_by) VALUES (?, ?, ?, ?, ?)",
            notices
        )

        # sample complaints
        complaints = [
            (1, "Water Leakage", "There is a water leakage near the parking area.", "A-101", "Water", today, "Pending"),
            (2, "Lift Not Working", "Lift in Wing A has stopped working since morning.", "A-204", "Lift", today, "In Progress"),
            (3, "Parking Issue", "Unauthorized vehicle parked in my designated slot.", "B-302", "Parking", today, "Resolved"),
        ]
        cur.executemany(
            "INSERT INTO complaints (resident_id, title, description, flat_number, category, complaint_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            complaints
        )

        # sample emergency contacts
        contacts = [
            ("Police Control Room", "Police", "100", "24x7 police helpline"),
            ("Fire Brigade", "Fire Brigade", "101", "24x7 fire emergency"),
            ("Ambulance", "Ambulance", "108", "24x7 ambulance service"),
            ("City Hospital", "Hospital", "02240001234", "Nearest multi-specialty hospital"),
            ("Society Security", "Society Security", "9876543210", "Main gate security desk"),
            ("Society Manager", "Society Manager", "9876501234", "Society administration office"),
        ]
        cur.executemany(
            "INSERT INTO emergency_contacts (contact_name, contact_type, phone, description) VALUES (?, ?, ?, ?)",
            contacts
        )

        conn.commit()

    conn.close()


# -------------------------------------------------------------------
# ACCESS CONTROL HELPERS
# -------------------------------------------------------------------
def login_required(func):
    """Decorator: user must be logged in."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """Decorator: user must be logged in AND be an admin."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("resident_dashboard"))
        return func(*args, **kwargs)
    return wrapper


def create_notification(title, message, notification_type, user_role="all"):
    """Helper to insert a new notification row."""
    db = get_db()
    db.execute(
        "INSERT INTO notifications (title, message, notification_type, created_date, is_read, user_role) VALUES (?, ?, ?, ?, 0, ?)",
        (title, message, notification_type, datetime.now().strftime("%Y-%m-%d %H:%M"), user_role)
    )
    db.commit()


def get_unread_count():
    """Returns number of unread notifications relevant to the current user's role."""
    if "role" not in session:
        return 0
    db = get_db()
    role = session["role"]
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE is_read = 0 AND (user_role = ? OR user_role = 'all')",
        (role,)
    ).fetchone()
    return row["cnt"] if row else 0


@app.context_processor
def inject_globals():
    """Makes unread_count and current user info available in every template."""
    return {
        "unread_count": get_unread_count() if "user_id" in session else 0,
        "current_role": session.get("role"),
        "current_username": session.get("username"),
    }


# -------------------------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and user["password"] == hash_password(password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["resident_id"] = user["resident_id"]
            flash(f"Welcome back, {user['username']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("dashboard"))
            return redirect(url_for("resident_dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# -------------------------------------------------------------------
# DASHBOARDS
# -------------------------------------------------------------------
@app.route("/dashboard")
@admin_required
def dashboard():
    db = get_db()

    total_residents = db.execute("SELECT COUNT(*) c FROM residents").fetchone()["c"]
    active_workers = db.execute("SELECT COUNT(*) c FROM workers").fetchone()["c"]
    today = datetime.now().strftime("%Y-%m-%d")
    today_visitors = db.execute("SELECT COUNT(*) c FROM visitors WHERE visit_date = ?", (today,)).fetchone()["c"]
    pending_complaints = db.execute("SELECT COUNT(*) c FROM complaints WHERE status = 'Pending'").fetchone()["c"]

    pending_c = db.execute("SELECT COUNT(*) c FROM complaints WHERE status='Pending'").fetchone()["c"]
    progress_c = db.execute("SELECT COUNT(*) c FROM complaints WHERE status='In Progress'").fetchone()["c"]
    resolved_c = db.execute("SELECT COUNT(*) c FROM complaints WHERE status='Resolved'").fetchone()["c"]

    recent_notices = db.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()

    return render_template(
        "dashboard.html",
        total_residents=total_residents,
        active_workers=active_workers,
        today_visitors=today_visitors,
        pending_complaints=pending_complaints,
        pending_c=pending_c, progress_c=progress_c, resolved_c=resolved_c,
        recent_notices=recent_notices
    )


@app.route("/resident-dashboard")
@login_required
def resident_dashboard():
    db = get_db()
    resident_id = session.get("resident_id")

    resident = db.execute("SELECT * FROM residents WHERE id = ?", (resident_id,)).fetchone()
    active_notices = db.execute("SELECT COUNT(*) c FROM notices").fetchone()["c"]
    my_pending = db.execute("SELECT COUNT(*) c FROM complaints WHERE resident_id=? AND status='Pending'", (resident_id,)).fetchone()["c"]
    my_resolved = db.execute("SELECT COUNT(*) c FROM complaints WHERE resident_id=? AND status='Resolved'", (resident_id,)).fetchone()["c"]
    emergency_count = db.execute("SELECT COUNT(*) c FROM emergency_contacts").fetchone()["c"]

    recent_notices = db.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
    urgent_notices = db.execute("SELECT * FROM notices WHERE priority='Urgent' ORDER BY id DESC").fetchall()
    recent_notifs = db.execute(
        "SELECT * FROM notifications WHERE user_role='resident' OR user_role='all' ORDER BY id DESC LIMIT 5"
    ).fetchall()

    return render_template(
        "resident_dashboard.html",
        resident=resident,
        active_notices=active_notices,
        my_pending=my_pending,
        my_resolved=my_resolved,
        emergency_count=emergency_count,
        recent_notices=recent_notices,
        urgent_notices=urgent_notices,
        recent_notifs=recent_notifs
    )


# -------------------------------------------------------------------
# RESIDENT MANAGEMENT (Admin only)
# -------------------------------------------------------------------
@app.route("/residents")
@admin_required
def residents():
    db = get_db()
    query = request.args.get("q", "").strip()

    if query:
        like = f"%{query}%"
        rows = db.execute(
            "SELECT * FROM residents WHERE full_name LIKE ? OR flat_number LIKE ? OR wing LIKE ? ORDER BY id DESC",
            (like, like, like)
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM residents ORDER BY id DESC").fetchall()

    return render_template("residents.html", residents=rows, query=query)


@app.route("/residents/add", methods=["GET", "POST"])
@admin_required
def residents_add():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO residents (full_name, flat_number, wing, phone, email, resident_type) VALUES (?, ?, ?, ?, ?, ?)",
            (request.form["full_name"], request.form["flat_number"], request.form["wing"],
             request.form["phone"], request.form["email"], request.form["resident_type"])
        )
        db.commit()
        flash("Resident added successfully.", "success")
        return redirect(url_for("residents"))

    return render_template("resident_form.html", resident=None)


@app.route("/residents/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def residents_edit(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            "UPDATE residents SET full_name=?, flat_number=?, wing=?, phone=?, email=?, resident_type=? WHERE id=?",
            (request.form["full_name"], request.form["flat_number"], request.form["wing"],
             request.form["phone"], request.form["email"], request.form["resident_type"], id)
        )
        db.commit()
        flash("Resident updated successfully.", "success")
        return redirect(url_for("residents"))

    resident = db.execute("SELECT * FROM residents WHERE id=?", (id,)).fetchone()
    return render_template("resident_form.html", resident=resident)


@app.route("/residents/delete/<int:id>")
@admin_required
def residents_delete(id):
    db = get_db()
    db.execute("DELETE FROM residents WHERE id=?", (id,))
    db.commit()
    flash("Resident deleted successfully.", "success")
    return redirect(url_for("residents"))


@app.route("/residents/view/<int:id>")
@admin_required
def residents_view(id):
    db = get_db()
    resident = db.execute("SELECT * FROM residents WHERE id=?", (id,)).fetchone()
    return render_template("resident_profile.html", resident=resident)


# -------------------------------------------------------------------
# VISITOR MANAGEMENT (Admin only)
# -------------------------------------------------------------------
@app.route("/visitors")
@admin_required
def visitors():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = db.execute("SELECT * FROM visitors WHERE visit_date=? ORDER BY id DESC", (today,)).fetchall()
    return render_template("visitors.html", visitors=rows)


@app.route("/visitors/add", methods=["GET", "POST"])
@admin_required
def visitors_add():
    if request.method == "POST":
        db = get_db()
        now = datetime.now()
        db.execute(
            "INSERT INTO visitors (visitor_name, phone, flat_number, purpose, entry_time, exit_time, status, visit_date) VALUES (?, ?, ?, ?, ?, NULL, 'Inside', ?)",
            (request.form["visitor_name"], request.form["phone"], request.form["flat_number"],
             request.form["purpose"], now.strftime("%H:%M"), now.strftime("%Y-%m-%d"))
        )
        db.commit()
        flash("Visitor entry recorded.", "success")
        return redirect(url_for("visitors"))

    return render_template("visitor_form.html")


@app.route("/visitors/exit/<int:id>")
@admin_required
def visitors_exit(id):
    db = get_db()
    db.execute(
        "UPDATE visitors SET exit_time=?, status='Exited' WHERE id=?",
        (datetime.now().strftime("%H:%M"), id)
    )
    db.commit()
    flash("Visitor marked as exited.", "success")
    return redirect(url_for("visitors"))


# -------------------------------------------------------------------
# WORKER MANAGEMENT
# -------------------------------------------------------------------
@app.route("/workers")
@admin_required
def workers():
    db = get_db()
    rows = db.execute("SELECT * FROM workers ORDER BY id DESC").fetchall()
    return render_template("workers.html", workers=rows)


@app.route("/workers/add", methods=["GET", "POST"])
@admin_required
def workers_add():
    db = get_db()
    if request.method == "POST":
        last = db.execute("SELECT COUNT(*) c FROM workers").fetchone()["c"]
        new_id = f"WRK{last + 1:03d}"
        db.execute(
            "INSERT INTO workers (worker_id, worker_name, phone, worker_type) VALUES (?, ?, ?, ?)",
            (new_id, request.form["worker_name"], request.form["phone"], request.form["worker_type"])
        )
        db.commit()
        flash("Worker added successfully.", "success")
        return redirect(url_for("workers"))

    return render_template("worker_form.html", worker=None)


@app.route("/workers/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def workers_edit(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            "UPDATE workers SET worker_name=?, phone=?, worker_type=? WHERE id=?",
            (request.form["worker_name"], request.form["phone"], request.form["worker_type"], id)
        )
        db.commit()
        flash("Worker updated successfully.", "success")
        return redirect(url_for("workers"))

    worker = db.execute("SELECT * FROM workers WHERE id=?", (id,)).fetchone()
    return render_template("worker_form.html", worker=worker)


@app.route("/workers/delete/<int:id>")
@admin_required
def workers_delete(id):
    db = get_db()
    db.execute("DELETE FROM workers WHERE id=?", (id,))
    db.commit()
    flash("Worker deleted successfully.", "success")
    return redirect(url_for("workers"))


# -------------------------------------------------------------------
# ATTENDANCE
# -------------------------------------------------------------------
@app.route("/attendance")
@admin_required
def attendance():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    workers_list = db.execute("SELECT * FROM workers ORDER BY worker_name").fetchall()
    today_attendance = db.execute(
        "SELECT * FROM worker_attendance WHERE attendance_date=?", (today,)
    ).fetchall()
    attendance_map = {row["worker_id"]: row for row in today_attendance}

    return render_template("attendance.html", workers=workers_list, attendance_map=attendance_map, today=today)


@app.route("/attendance/checkin/<worker_id>")
@admin_required
def attendance_checkin(worker_id):
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    existing = db.execute(
        "SELECT * FROM worker_attendance WHERE worker_id=? AND attendance_date=?", (worker_id, today)
    ).fetchone()

    if not existing:
        db.execute(
            "INSERT INTO worker_attendance (worker_id, attendance_date, check_in, check_out, status) VALUES (?, ?, ?, NULL, 'Present')",
            (worker_id, today, datetime.now().strftime("%H:%M"))
        )
        db.commit()
        flash("Worker checked in successfully.", "success")
    else:
        flash("Worker already checked in today.", "warning")

    return redirect(url_for("attendance"))


@app.route("/attendance/checkout/<worker_id>")
@admin_required
def attendance_checkout(worker_id):
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    db.execute(
        "UPDATE worker_attendance SET check_out=? WHERE worker_id=? AND attendance_date=?",
        (datetime.now().strftime("%H:%M"), worker_id, today)
    )
    db.commit()
    flash("Worker checked out successfully.", "success")
    return redirect(url_for("attendance"))


@app.route("/attendance/history")
@admin_required
def attendance_history():
    db = get_db()
    date_filter = request.args.get("date", "")
    type_filter = request.args.get("type", "")

    query = """
        SELECT wa.*, w.worker_name, w.worker_type
        FROM worker_attendance wa
        JOIN workers w ON wa.worker_id = w.worker_id
        WHERE 1=1
    """
    params = []
    if date_filter:
        query += " AND wa.attendance_date = ?"
        params.append(date_filter)
    if type_filter:
        query += " AND w.worker_type = ?"
        params.append(type_filter)
    query += " ORDER BY wa.id DESC"

    rows = db.execute(query, params).fetchall()
    worker_types = db.execute("SELECT DISTINCT worker_type FROM workers").fetchall()

    return render_template("attendance_history.html", records=rows, worker_types=worker_types,
                            date_filter=date_filter, type_filter=type_filter)


# -------------------------------------------------------------------
# NOTICE BOARD
# -------------------------------------------------------------------
@app.route("/notices")
@login_required
def notices():
    db = get_db()
    rows = db.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    return render_template("notices.html", notices=rows)


@app.route("/notices/add", methods=["GET", "POST"])
@admin_required
def notices_add():
    if request.method == "POST":
        db = get_db()
        title = request.form["title"]
        priority = request.form["priority"]
        db.execute(
            "INSERT INTO notices (title, description, notice_date, priority, created_by) VALUES (?, ?, ?, ?, ?)",
            (title, request.form["description"], request.form["notice_date"], priority, session["username"])
        )
        db.commit()

        notif_type = "Urgent" if priority == "Urgent" else "Notice"
        create_notification(title, f"New notice published: {title}", notif_type, "all")

        flash("Notice published successfully.", "success")
        return redirect(url_for("notices"))

    return render_template("notice_form.html")


@app.route("/notices/delete/<int:id>")
@admin_required
def notices_delete(id):
    db = get_db()
    db.execute("DELETE FROM notices WHERE id=?", (id,))
    db.commit()
    flash("Notice deleted successfully.", "success")
    return redirect(url_for("notices"))


# -------------------------------------------------------------------
# COMPLAINT MANAGEMENT
# -------------------------------------------------------------------
@app.route("/complaints")
@login_required
def complaints():
    db = get_db()
    category_filter = request.args.get("category", "")
    status_filter = request.args.get("status", "")

    if session["role"] == "admin":
        query = "SELECT c.*, r.full_name FROM complaints c LEFT JOIN residents r ON c.resident_id = r.id WHERE 1=1"
        params = []
    else:
        query = "SELECT c.*, r.full_name FROM complaints c LEFT JOIN residents r ON c.resident_id = r.id WHERE c.resident_id = ?"
        params = [session.get("resident_id")]

    if category_filter:
        query += " AND c.category = ?"
        params.append(category_filter)
    if status_filter:
        query += " AND c.status = ?"
        params.append(status_filter)
    query += " ORDER BY c.id DESC"

    rows = db.execute(query, params).fetchall()
    return render_template("complaints.html", complaints=rows, category_filter=category_filter, status_filter=status_filter)


@app.route("/complaints/add", methods=["GET", "POST"])
@login_required
def complaints_add():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO complaints (resident_id, title, description, flat_number, category, complaint_date, status) VALUES (?, ?, ?, ?, ?, ?, 'Pending')",
            (session.get("resident_id"), request.form["title"], request.form["description"],
             request.form["flat_number"], request.form["category"], datetime.now().strftime("%Y-%m-%d"))
        )
        db.commit()
        flash("Complaint submitted successfully.", "success")
        return redirect(url_for("complaints"))

    return render_template("complaint_form.html")


@app.route("/complaints/update/<int:id>", methods=["GET", "POST"])
@admin_required
def complaints_update(id):
    db = get_db()
    if request.method == "POST":
        new_status = request.form["status"]
        db.execute("UPDATE complaints SET status=? WHERE id=?", (new_status, id))
        db.commit()

        complaint = db.execute("SELECT * FROM complaints WHERE id=?", (id,)).fetchone()
        create_notification(
            "Complaint Status Updated",
            f"Your complaint '{complaint['title']}' status changed to {new_status}.",
            "Complaint", "resident"
        )

        flash("Complaint status updated.", "success")
        return redirect(url_for("complaints"))

    complaint = db.execute("SELECT * FROM complaints WHERE id=?", (id,)).fetchone()
    return render_template("complaint_update.html", complaint=complaint)


# -------------------------------------------------------------------
# RENTAL REGISTRATION
# -------------------------------------------------------------------
@app.route("/rentals")
@login_required
def rentals():
    db = get_db()
    if session["role"] == "admin":
        rows = db.execute("SELECT * FROM rentals ORDER BY id DESC").fetchall()
    else:
        rows = db.execute("SELECT * FROM rentals WHERE created_by=? ORDER BY id DESC", (session["username"],)).fetchall()
    return render_template("rentals.html", rentals=rows)


@app.route("/rentals/add", methods=["GET", "POST"])
@login_required
def rentals_add():
    if request.method == "POST":
        db = get_db()
        db.execute("""
            INSERT INTO rentals (tenant_name, flat_number, owner_name, phone, email, move_in_date,
                agreement_start_date, agreement_end_date, rental_status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["tenant_name"], request.form["flat_number"], request.form["owner_name"],
            request.form["phone"], request.form["email"], request.form["move_in_date"],
            request.form["agreement_start_date"], request.form["agreement_end_date"],
            request.form["rental_status"], session["username"]
        ))
        db.commit()
        flash("Rental registration created.", "success")
        return redirect(url_for("rentals"))

    return render_template("rental_form.html", rental=None)


@app.route("/rentals/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def rentals_edit(id):
    db = get_db()
    if request.method == "POST":
        db.execute("""
            UPDATE rentals SET tenant_name=?, flat_number=?, owner_name=?, phone=?, email=?,
                move_in_date=?, agreement_start_date=?, agreement_end_date=?, rental_status=? WHERE id=?
        """, (
            request.form["tenant_name"], request.form["flat_number"], request.form["owner_name"],
            request.form["phone"], request.form["email"], request.form["move_in_date"],
            request.form["agreement_start_date"], request.form["agreement_end_date"],
            request.form["rental_status"], id
        ))
        db.commit()
        flash("Rental registration updated.", "success")
        return redirect(url_for("rentals"))

    rental = db.execute("SELECT * FROM rentals WHERE id=?", (id,)).fetchone()
    return render_template("rental_form.html", rental=rental)


@app.route("/rentals/delete/<int:id>")
@admin_required
def rentals_delete(id):
    db = get_db()
    db.execute("DELETE FROM rentals WHERE id=?", (id,))
    db.commit()
    flash("Rental registration deleted.", "success")
    return redirect(url_for("rentals"))


# -------------------------------------------------------------------
# EMERGENCY CONTACTS
# -------------------------------------------------------------------
@app.route("/emergency")
@login_required
def emergency():
    db = get_db()
    rows = db.execute("SELECT * FROM emergency_contacts ORDER BY id").fetchall()
    return render_template("emergency.html", contacts=rows)


@app.route("/emergency/add", methods=["GET", "POST"])
@admin_required
def emergency_add():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO emergency_contacts (contact_name, contact_type, phone, description) VALUES (?, ?, ?, ?)",
            (request.form["contact_name"], request.form["contact_type"], request.form["phone"], request.form["description"])
        )
        db.commit()
        flash("Emergency contact added successfully.", "success")
        return redirect(url_for("emergency"))

    return render_template("emergency_form.html", contact=None)


@app.route("/emergency/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def emergency_edit(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            "UPDATE emergency_contacts SET contact_name=?, contact_type=?, phone=?, description=? WHERE id=?",
            (request.form["contact_name"], request.form["contact_type"], request.form["phone"],
             request.form["description"], id)
        )
        db.commit()
        flash("Emergency contact updated successfully.", "success")
        return redirect(url_for("emergency"))

    contact = db.execute("SELECT * FROM emergency_contacts WHERE id=?", (id,)).fetchone()
    return render_template("emergency_form.html", contact=contact)


@app.route("/emergency/delete/<int:id>")
@admin_required
def emergency_delete(id):
    db = get_db()
    db.execute("DELETE FROM emergency_contacts WHERE id=?", (id,))
    db.commit()
    flash("Emergency contact deleted successfully.", "success")
    return redirect(url_for("emergency"))


# -------------------------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------------------------
@app.route("/notifications")
@login_required
def notifications():
    db = get_db()
    role = session["role"]
    rows = db.execute(
        "SELECT * FROM notifications WHERE user_role=? OR user_role='all' ORDER BY id DESC",
        (role,)
    ).fetchall()
    return render_template("notifications.html", notifications=rows)


@app.route("/notifications/read/<int:id>")
@login_required
def notifications_read(id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("notifications"))


@app.route("/notifications/read-all")
@login_required
def notifications_read_all():
    db = get_db()
    role = session["role"]
    db.execute("UPDATE notifications SET is_read=1 WHERE user_role=? OR user_role='all'", (role,))
    db.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications"))


# -------------------------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_panel():
    return render_template("admin.html")


# -------------------------------------------------------------------
# SETTINGS
# -------------------------------------------------------------------
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        db = get_db()
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

        if user["password"] != hash_password(current_password):
            flash("Current password is incorrect.", "danger")
        elif new_password != confirm_password:
            flash("New password and confirm password do not match.", "danger")
        else:
            db.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), session["user_id"]))
            db.commit()
            flash("Password changed successfully.", "success")

        return redirect(url_for("settings"))

    return render_template("settings.html")


# -------------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)